"""Regras de negócio transacionais da loja.

Cada função aqui grava em várias tabelas dentro de ``transaction.atomic()``:
se qualquer regra for violada (ex.: estoque insuficiente em um dos itens),
a exceção propaga e o banco desfaz TUDO (rollback), sem pedido pela metade.
"""
from decimal import Decimal

from django.db import transaction
from django.db.models import F

from .models import Entrega, EventoRastreamento, ItemPedido, Pedido, Produto


class RegraDeNegocioError(Exception):
    """Violação de regra de negócio (vira HTTP 409 na API)."""


@transaction.atomic
def criar_pedido(*, cliente, endereco_entrega, itens):
    """Cria Pedido + ItemPedido + Entrega + EventoRastreamento e baixa estoque.

    ``itens`` é uma lista de dicts ``{"produto": <id>, "quantidade": <int>}``.
    Grava em 5 tabelas (pedido, item, produto, entrega, evento).
    """
    if not itens:
        raise RegraDeNegocioError("O pedido precisa ter ao menos um item.")

    # Consolida linhas repetidas do mesmo produto
    quantidades = {}
    for item in itens:
        pid = item["produto"]
        quantidades[pid] = quantidades.get(pid, 0) + item["quantidade"]

    # Trava as linhas dos produtos (evita venda simultânea do mesmo estoque).
    # Ordenar por id evita deadlock entre pedidos concorrentes.
    produtos = {
        p.pk: p
        for p in Produto.objects.select_for_update()
        .filter(pk__in=quantidades.keys())
        .order_by("pk")
    }

    pedido = Pedido.objects.create(
        cliente=cliente, endereco_entrega=endereco_entrega
    )

    total = Decimal("0")
    for pid, qtd in quantidades.items():
        produto = produtos.get(pid)
        if produto is None or not produto.ativo:
            raise RegraDeNegocioError(f"Produto {pid} indisponível.")
        if produto.estoque < qtd:
            raise RegraDeNegocioError(
                f"Estoque insuficiente para {produto.sku}: "
                f"pedido {qtd}, disponível {produto.estoque}."
            )
        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            quantidade=qtd,
            preco_unitario=produto.preco,
        )
        Produto.objects.filter(pk=pid).update(estoque=F("estoque") - qtd)
        total += produto.preco * qtd

    pedido.total = total
    pedido.save(update_fields=["total"])

    entrega = Entrega.objects.create(pedido=pedido)
    EventoRastreamento.objects.create(
        entrega=entrega,
        status=Entrega.Status.AGUARDANDO,
        dados={"origem": "checkout", "mensagem": "Pedido criado"},
    )
    return pedido


@transaction.atomic
def cancelar_pedido(pedido):
    """Cancela o pedido, devolve o estoque e encerra a entrega."""
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if pedido.status in (Pedido.Status.ENTREGUE, Pedido.Status.CANCELADO):
        raise RegraDeNegocioError(
            f"Pedido {pedido.pk} não pode ser cancelado "
            f"(status atual: {pedido.get_status_display()})."
        )

    for item in pedido.itens.all():
        Produto.objects.filter(pk=item.produto_id).update(
            estoque=F("estoque") + item.quantidade
        )

    pedido.status = Pedido.Status.CANCELADO
    pedido.save(update_fields=["status"])

    entrega = pedido.entrega
    entrega.status = Entrega.Status.FALHOU
    entrega.save(update_fields=["status", "atualizada_em"])
    EventoRastreamento.objects.create(
        entrega=entrega,
        status=Entrega.Status.FALHOU,
        dados={"origem": "cancelamento", "mensagem": "Pedido cancelado"},
    )
    return pedido


@transaction.atomic
def registrar_evento(*, entrega, status, latitude=None, longitude=None, dados=None):
    """Registra evento de rastreamento e sincroniza status da entrega/pedido."""
    entrega = Entrega.objects.select_for_update().select_related("pedido").get(
        pk=entrega.pk
    )
    if entrega.pedido.status == Pedido.Status.CANCELADO:
        raise RegraDeNegocioError("Pedido cancelado não recebe novos eventos.")

    evento = EventoRastreamento.objects.create(
        entrega=entrega,
        status=status,
        latitude=latitude,
        longitude=longitude,
        dados=dados or {},
    )

    entrega.status = status
    entrega.save(update_fields=["status", "atualizada_em"])

    novo_status_pedido = {
        Entrega.Status.EM_ROTA: Pedido.Status.EM_ENTREGA,
        Entrega.Status.ENTREGUE: Pedido.Status.ENTREGUE,
    }.get(status)
    if novo_status_pedido:
        entrega.pedido.status = novo_status_pedido
        entrega.pedido.save(update_fields=["status"])
    return evento
