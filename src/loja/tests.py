"""Testes automatizados (rodam em PostgreSQL: python manage.py test)."""
import os
from decimal import Decimal
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from rest_framework.test import APITestCase

from loja import services
from loja.models import (
    Categoria,
    Cliente,
    Entrega,
    EventoRastreamento,
    Pedido,
    Produto,
)

User = get_user_model()


def criar_catalogo():
    cat = Categoria.objects.create(nome="Eletrônicos", slug="eletronicos")
    fone = Produto.objects.create(
        categoria=cat, sku="ELE-001", nome="Fone", preco=Decimal("100.00"),
        estoque=10, atributos={"cor": "preto", "peso_kg": 0.25},
    )
    relogio = Produto.objects.create(
        categoria=cat, sku="ELE-002", nome="Relógio", preco=Decimal("300.00"),
        estoque=2, atributos={"cor": "azul", "peso_kg": 0.05,
                              "dimensoes": {"altura": 5}},
    )
    cliente = Cliente.objects.create(nome="Ana", email="ana@example.com")
    return cat, fone, relogio, cliente


class ModeloDocumentoTests(TestCase):
    """A3: JSONB + índice GIN criado por migration."""

    def test_indices_gin_existem_no_banco(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT indexname, indexdef FROM pg_indexes "
                "WHERE indexname IN ('produto_atributos_gin', 'evento_dados_gin')"
            )
            indices = dict(cursor.fetchall())
        self.assertEqual(len(indices), 2)
        for definicao in indices.values():
            self.assertIn("USING gin", definicao)

    def test_jsonfield_aceita_consulta_por_chave(self):
        _, fone, relogio, _ = criar_catalogo()
        azuis = Produto.objects.filter(atributos__cor="azul")
        self.assertEqual(list(azuis), [relogio])
        self.assertEqual(
            list(Produto.objects.filter(atributos__contains={"cor": "preto"})),
            [fone],
        )


class ProdutoAPITests(APITestCase):
    """A5: CRUD + filtro por campo JSON."""

    def setUp(self):
        self.cat, self.fone, self.relogio, self.cliente = criar_catalogo()
        self.admin = User.objects.create_superuser("admin", "a@a.com", "senha-forte-123")

    def test_filtro_por_campo_json(self):
        resp = self.client.get("/api/produtos/?atributos__cor=azul")
        self.assertEqual(resp.status_code, 200)
        skus = [p["sku"] for p in resp.json()["results"]]
        self.assertEqual(skus, ["ELE-002"])

    def test_filtro_json_numerico_e_aninhado(self):
        resp = self.client.get("/api/produtos/?atributos__peso_kg__lte=0.1")
        self.assertEqual([p["sku"] for p in resp.json()["results"]], ["ELE-002"])
        resp = self.client.get("/api/produtos/?atributos__dimensoes__altura=5")
        self.assertEqual([p["sku"] for p in resp.json()["results"]], ["ELE-002"])

    def test_filtro_igualdade_usa_operador_de_contencao_do_gin(self):
        """Igualdade vira `@>` (que o índice GIN acelera), não `->`."""
        from loja.views import ProdutoViewSet
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request

        request = Request(APIRequestFactory().get("/api/produtos/?atributos__cor=azul"))
        view = ProdutoViewSet()
        view.request = request
        sql = str(view.filter_json(Produto.objects.all()).query)
        self.assertIn("@>", sql)

    def test_filtro_aceita_valor_numerico_guardado_como_texto(self):
        Produto.objects.filter(sku="ELE-001").update(atributos={"tamanho": "42"})
        resp = self.client.get("/api/produtos/?atributos__tamanho=42")
        self.assertEqual([p["sku"] for p in resp.json()["results"]], ["ELE-001"])

    def test_filtro_json_rejeita_chave_invalida(self):
        resp = self.client.get("/api/produtos/?atributos__a-b=1")
        self.assertEqual(resp.status_code, 400)

    def test_escrita_exige_autenticacao_e_crud_funciona(self):
        payload = {
            "sku": "ELE-009", "nome": "Mouse", "preco": "49.90", "estoque": 5,
            "categoria": self.cat.pk, "atributos": {"cor": "branco"},
        }
        self.assertEqual(self.client.post("/api/produtos/", payload, format="json").status_code, 403)

        self.client.force_authenticate(self.admin)
        criado = self.client.post("/api/produtos/", payload, format="json")
        self.assertEqual(criado.status_code, 201)
        pk = criado.json()["id"]
        self.assertEqual(self.client.patch(f"/api/produtos/{pk}/", {"estoque": 7}, format="json").json()["estoque"], 7)
        self.assertEqual(self.client.delete(f"/api/produtos/{pk}/").status_code, 204)

    def test_atributos_precisa_ser_objeto(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post(
            "/api/produtos/",
            {"sku": "X", "nome": "X", "preco": "1.00", "categoria": self.cat.pk,
             "atributos": ["nao", "objeto"]},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)


class CheckoutTransacaoTests(APITestCase):
    """A4: transação em várias tabelas com rollback em violação de regra."""

    def setUp(self):
        _, self.fone, self.relogio, self.cliente = criar_catalogo()
        self.admin = User.objects.create_superuser("admin", "a@a.com", "senha-forte-123")
        self.client.force_authenticate(self.admin)

    def _checkout(self, itens):
        return self.client.post(
            "/api/pedidos/",
            {"cliente": self.cliente.pk, "endereco_entrega": "Rua A, 1", "itens": itens},
            format="json",
        )

    def test_checkout_grava_varias_tabelas_e_baixa_estoque(self):
        resp = self._checkout([
            {"produto": self.fone.pk, "quantidade": 3},
            {"produto": self.relogio.pk, "quantidade": 1},
        ])
        self.assertEqual(resp.status_code, 201)
        corpo = resp.json()
        self.assertEqual(Decimal(corpo["total"]), Decimal("600.00"))
        self.assertEqual(len(corpo["itens"]), 2)
        self.assertEqual(corpo["entrega"]["status"], "aguardando")
        self.assertEqual(len(corpo["entrega"]["eventos"]), 1)

        self.fone.refresh_from_db()
        self.relogio.refresh_from_db()
        self.assertEqual((self.fone.estoque, self.relogio.estoque), (7, 1))
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(Entrega.objects.count(), 1)
        self.assertEqual(EventoRastreamento.objects.count(), 1)

    def test_estoque_insuficiente_faz_rollback_completo(self):
        # 1º item é válido (grava pedido, item e baixa estoque); o 2º estoura
        # o estoque => tudo precisa ser desfeito.
        resp = self._checkout([
            {"produto": self.fone.pk, "quantidade": 3},
            {"produto": self.relogio.pk, "quantidade": 99},
        ])
        self.assertEqual(resp.status_code, 409)
        self.assertIn("Estoque insuficiente", resp.json()["detail"])

        self.fone.refresh_from_db()
        self.assertEqual(self.fone.estoque, 10)
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertEqual(Entrega.objects.count(), 0)
        self.assertEqual(EventoRastreamento.objects.count(), 0)

    def test_falha_no_meio_da_transacao_desfaz_tudo(self):
        with mock.patch.object(
            services.Entrega.objects, "create", side_effect=RuntimeError("falha")
        ):
            with self.assertRaises(RuntimeError):
                services.criar_pedido(
                    cliente=self.cliente, endereco_entrega="Rua A",
                    itens=[{"produto": self.fone.pk, "quantidade": 2}],
                )
        self.fone.refresh_from_db()
        self.assertEqual(self.fone.estoque, 10)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_pedido_sem_itens_e_invalido(self):
        self.assertEqual(self._checkout([]).status_code, 400)

    def test_cancelar_devolve_estoque(self):
        pedido_id = self._checkout([{"produto": self.fone.pk, "quantidade": 4}]).json()["id"]
        self.fone.refresh_from_db()
        self.assertEqual(self.fone.estoque, 6)

        resp = self.client.post(f"/api/pedidos/{pedido_id}/cancelar/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "cancelado")
        self.fone.refresh_from_db()
        self.assertEqual(self.fone.estoque, 10)

        # cancelar de novo viola regra de negócio
        self.assertEqual(self.client.post(f"/api/pedidos/{pedido_id}/cancelar/").status_code, 409)


class RastreamentoTests(APITestCase):
    """Eventos de última milha (JSONB) e sincronismo de status."""

    def setUp(self):
        _, self.fone, _, self.cliente = criar_catalogo()
        self.admin = User.objects.create_superuser("admin", "a@a.com", "senha-forte-123")
        self.client.force_authenticate(self.admin)
        self.pedido = services.criar_pedido(
            cliente=self.cliente, endereco_entrega="Rua A",
            itens=[{"produto": self.fone.pk, "quantidade": 1}],
        )

    def test_registrar_evento_atualiza_entrega_e_pedido(self):
        entrega_id = self.pedido.entrega.pk
        resp = self.client.post(
            f"/api/entregas/{entrega_id}/eventos/",
            {"status": "em_rota", "latitude": "-23.0", "longitude": "-43.3",
             "dados": {"velocidade_kmh": 30, "bateria": 80}},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.pedido.refresh_from_db()
        self.pedido.entrega.refresh_from_db()
        self.assertEqual(self.pedido.entrega.status, "em_rota")
        self.assertEqual(self.pedido.status, "em_entrega")

    def test_filtro_json_em_eventos(self):
        self.client.post(
            f"/api/entregas/{self.pedido.entrega.pk}/eventos/",
            {"status": "em_rota", "dados": {"velocidade_kmh": 30}}, format="json",
        )
        resp = self.client.get("/api/eventos/?dados__velocidade_kmh__gte=20")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["results"]), 1)
        resp = self.client.get("/api/eventos/?dados__origem=checkout")
        self.assertEqual(len(resp.json()["results"]), 1)

    def test_pedido_cancelado_nao_recebe_eventos(self):
        services.cancelar_pedido(self.pedido)
        resp = self.client.post(
            f"/api/entregas/{self.pedido.entrega.pk}/eventos/",
            {"status": "em_rota"}, format="json",
        )
        self.assertEqual(resp.status_code, 409)


class AdminEComandosTests(TestCase):
    """A6 (Admin) e A8 (seed) + variáveis de ambiente (A7)."""

    def test_admin_funcional_para_superusuario(self):
        User.objects.create_superuser("admin", "a@a.com", "senha-forte-123")
        self.client.login(username="admin", password="senha-forte-123")
        for rota in ("/admin/", "/admin/loja/produto/", "/admin/loja/pedido/",
                     "/admin/loja/eventorastreamento/"):
            self.assertEqual(self.client.get(rota).status_code, 200, rota)

    def test_criar_superusuario_via_ambiente_e_idempotente(self):
        env = {"DJANGO_SUPERUSER_USERNAME": "root",
               "DJANGO_SUPERUSER_PASSWORD": "senha-forte-123",
               "DJANGO_SUPERUSER_EMAIL": "root@example.com"}
        with mock.patch.dict(os.environ, env):
            call_command("criar_superusuario", stdout=StringIO())
            call_command("criar_superusuario", stdout=StringIO())
        self.assertEqual(User.objects.filter(username="root", is_superuser=True).count(), 1)

    def test_criar_superusuario_sem_variaveis_nao_falha(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DJANGO_SUPERUSER_USERNAME", None)
            os.environ.pop("DJANGO_SUPERUSER_PASSWORD", None)
            call_command("criar_superusuario", stdout=StringIO())
        self.assertFalse(User.objects.exists())

    def test_seed_e_idempotente(self):
        call_command("seed_dados", stdout=StringIO())
        contagem = (Produto.objects.count(), Cliente.objects.count(), Pedido.objects.count())
        call_command("seed_dados", stdout=StringIO())
        self.assertEqual(
            contagem,
            (Produto.objects.count(), Cliente.objects.count(), Pedido.objects.count()),
        )
        self.assertEqual(contagem, (8, 3, 2))
        # dados de exemplo respeitam o estoque (ELE-001: 40 - 1)
        self.assertEqual(Produto.objects.get(sku="ELE-001").estoque, 39)

    def test_health(self):
        resp = self.client.get("/health/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok", "banco": "ok"})
