"""Carrega dados de exemplo do tema (catálogo, clientes, entregadores, pedidos).

Idempotente: cadastros usam get_or_create e os pedidos de exemplo só são
criados se ainda não houver nenhum pedido.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from loja import services
from loja.models import (
    Categoria,
    Cliente,
    Entrega,
    Entregador,
    Pedido,
    Produto,
)

CATEGORIAS = [
    ("Eletrônicos", "eletronicos"),
    ("Moda", "moda"),
    ("Casa e Cozinha", "casa-cozinha"),
]

PRODUTOS = [
    # (sku, nome, categoria_slug, preco, estoque, atributos JSONB)
    ("ELE-001", "Fone Bluetooth Pro", "eletronicos", "249.90", 40,
     {"cor": "preto", "bluetooth": "5.3", "bateria_h": 30, "peso_kg": 0.25}),
    ("ELE-002", "Smartwatch Fit 2", "eletronicos", "599.00", 25,
     {"cor": "azul", "bluetooth": "5.2", "bateria_h": 72, "peso_kg": 0.05,
      "resistente_agua": True}),
    ("ELE-003", "Caixa de Som Portátil", "eletronicos", "189.90", 60,
     {"cor": "azul", "potencia_w": 20, "bateria_h": 12, "peso_kg": 0.8}),
    ("MOD-001", "Camiseta Algodão", "moda", "59.90", 120,
     {"cor": "branco", "tamanho": "M", "material": "algodão", "peso_kg": 0.2}),
    ("MOD-002", "Tênis Corrida", "moda", "329.90", 35,
     {"cor": "preto", "tamanho": "42", "material": "mesh", "peso_kg": 0.6}),
    ("CAS-001", "Panela de Pressão 4L", "casa-cozinha", "139.90", 30,
     {"cor": "prata", "capacidade_l": 4, "material": "alumínio", "peso_kg": 2.1,
      "dimensoes": {"altura": 22, "largura": 30}}),
    ("CAS-002", "Cafeteira Elétrica", "casa-cozinha", "219.00", 20,
     {"cor": "preto", "voltagem": "220V", "capacidade_l": 1.2, "peso_kg": 1.8,
      "dimensoes": {"altura": 32, "largura": 20}}),
    ("CAS-003", "Jogo de Facas 6 peças", "casa-cozinha", "99.90", 50,
     {"cor": "prata", "material": "inox", "peso_kg": 1.0}),
]

CLIENTES = [
    ("Ana Souza", "ana.souza@example.com", "21999990001"),
    ("Bruno Lima", "bruno.lima@example.com", "21999990002"),
    ("Carla Mendes", "carla.mendes@example.com", "21999990003"),
]

ENTREGADORES = [
    ("Carlos Moto", "moto"),
    ("Dani Bike", "bicicleta"),
    ("Eduardo Van", "van"),
]


class Command(BaseCommand):
    help = "Carrega dados de exemplo (idempotente)."

    @transaction.atomic
    def handle(self, *args, **options):
        cats = {}
        for nome, slug in CATEGORIAS:
            cats[slug], _ = Categoria.objects.get_or_create(
                slug=slug, defaults={"nome": nome}
            )

        for sku, nome, slug, preco, estoque, atributos in PRODUTOS:
            Produto.objects.get_or_create(
                sku=sku,
                defaults={
                    "nome": nome, "categoria": cats[slug], "preco": preco,
                    "estoque": estoque, "atributos": atributos,
                },
            )

        clientes = []
        for nome, email, telefone in CLIENTES:
            cliente, _ = Cliente.objects.get_or_create(
                email=email, defaults={"nome": nome, "telefone": telefone}
            )
            clientes.append(cliente)

        entregadores = []
        for nome, veiculo in ENTREGADORES:
            entregador, _ = Entregador.objects.get_or_create(
                nome=nome, defaults={"veiculo": veiculo}
            )
            entregadores.append(entregador)

        if not Pedido.objects.exists():
            self._criar_pedidos_exemplo(clientes, entregadores)

        self.stdout.write(self.style.SUCCESS("Dados de exemplo carregados."))

    def _criar_pedidos_exemplo(self, clientes, entregadores):
        p = {x.sku: x for x in Produto.objects.all()}

        pedido1 = services.criar_pedido(
            cliente=clientes[0],
            endereco_entrega="Av. das Américas, 1000 - Barra da Tijuca, Rio de Janeiro",
            itens=[
                {"produto": p["ELE-001"].pk, "quantidade": 1},
                {"produto": p["MOD-001"].pk, "quantidade": 2},
            ],
        )
        Entrega.objects.filter(pk=pedido1.entrega.pk).update(entregador=entregadores[0])
        services.registrar_evento(
            entrega=pedido1.entrega, status=Entrega.Status.EM_ROTA,
            latitude="-23.000372", longitude="-43.365894",
            dados={"origem": "app_entregador", "velocidade_kmh": 28, "bateria": 81},
        )

        pedido2 = services.criar_pedido(
            cliente=clientes[1],
            endereco_entrega="Rua Voluntários da Pátria, 200 - Botafogo, Rio de Janeiro",
            itens=[{"produto": p["CAS-002"].pk, "quantidade": 1}],
        )
        Entrega.objects.filter(pk=pedido2.entrega.pk).update(entregador=entregadores[1])
