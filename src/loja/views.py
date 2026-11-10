from django.db import connection
from django.http import JsonResponse
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .filters import JSONFieldFilterMixin
from .models import (
    Categoria,
    Cliente,
    Entrega,
    Entregador,
    EventoRastreamento,
    ItemPedido,
    Pedido,
    Produto,
)
from .serializers import (
    CategoriaSerializer,
    ClienteSerializer,
    EntregadorSerializer,
    EntregaSerializer,
    EventoEntradaSerializer,
    EventoRastreamentoSerializer,
    ItemPedidoSerializer,
    PedidoCheckoutSerializer,
    PedidoSerializer,
    ProdutoSerializer,
)


def health(request):
    """Verificação simples de saúde: app no ar e banco respondendo."""
    try:
        connection.ensure_connection()
        banco = "ok"
    except Exception:  # noqa: BLE001 - qualquer falha de conexão = indisponível
        banco = "indisponivel"
    codigo = 200 if banco == "ok" else 503
    return JsonResponse({"status": "ok" if codigo == 200 else "erro", "banco": banco},
                        status=codigo)


def _conflito(erro):
    return Response({"detail": str(erro)}, status=status.HTTP_409_CONFLICT)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ProdutoViewSet(JSONFieldFilterMixin, viewsets.ModelViewSet):
    """CRUD de produtos. Filtro JSONB: ``?atributos__cor=azul``."""

    serializer_class = ProdutoSerializer
    json_field = "atributos"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nome", "sku"]
    ordering_fields = ["nome", "preco", "estoque"]

    def get_queryset(self):
        qs = Produto.objects.select_related("categoria")
        categoria = self.request.query_params.get("categoria")
        if categoria:
            qs = qs.filter(categoria__slug=categoria)
        return self.filter_json(qs)


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nome", "email"]


class EntregadorViewSet(viewsets.ModelViewSet):
    queryset = Entregador.objects.all()
    serializer_class = EntregadorSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    """CRUD de pedidos.

    ``POST /api/pedidos/`` é o checkout transacional: grava pedido, itens,
    entrega e evento inicial e baixa o estoque dentro de ``atomic()``.
    Estoque insuficiente => 409 e nenhuma linha é gravada.
    """

    queryset = Pedido.objects.select_related("cliente", "entrega").prefetch_related(
        "itens__produto", "entrega__eventos"
    )
    serializer_class = PedidoSerializer

    def create(self, request, *args, **kwargs):
        entrada = PedidoCheckoutSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        dados = entrada.validated_data
        try:
            pedido = services.criar_pedido(
                cliente=dados["cliente"],
                endereco_entrega=dados["endereco_entrega"],
                itens=[
                    {"produto": i["produto"].pk, "quantidade": i["quantidade"]}
                    for i in dados["itens"]
                ],
            )
        except services.RegraDeNegocioError as erro:
            return _conflito(erro)
        pedido = self.get_queryset().get(pk=pedido.pk)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """Cancela o pedido e devolve o estoque (transacional)."""
        pedido = self.get_object()
        try:
            services.cancelar_pedido(pedido)
        except services.RegraDeNegocioError as erro:
            return _conflito(erro)
        pedido = self.get_queryset().get(pk=pedido.pk)
        return Response(PedidoSerializer(pedido).data)


class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.select_related("produto", "pedido")
    serializer_class = ItemPedidoSerializer


class EntregaViewSet(viewsets.ModelViewSet):
    queryset = Entrega.objects.select_related("pedido", "entregador").prefetch_related(
        "eventos"
    )
    serializer_class = EntregaSerializer

    @action(detail=True, methods=["get", "post"])
    def eventos(self, request, pk=None):
        """GET lista o histórico; POST registra evento (app do entregador)."""
        entrega = self.get_object()
        if request.method == "GET":
            serializer = EventoRastreamentoSerializer(
                entrega.eventos.all(), many=True
            )
            return Response(serializer.data)

        entrada = EventoEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        try:
            evento = services.registrar_evento(entrega=entrega, **entrada.validated_data)
        except services.RegraDeNegocioError as erro:
            return _conflito(erro)
        return Response(
            EventoRastreamentoSerializer(evento).data, status=status.HTTP_201_CREATED
        )


class EventoRastreamentoViewSet(JSONFieldFilterMixin, viewsets.ModelViewSet):
    """Eventos de última milha. Filtro JSONB: ``?dados__origem=checkout``."""

    serializer_class = EventoRastreamentoSerializer
    json_field = "dados"

    def get_queryset(self):
        qs = EventoRastreamento.objects.select_related("entrega")
        entrega = self.request.query_params.get("entrega")
        if entrega:
            qs = qs.filter(entrega_id=entrega)
        return self.filter_json(qs)

    def create(self, request, *args, **kwargs):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        dados = entrada.validated_data
        try:
            evento = services.registrar_evento(
                entrega=dados["entrega"],
                status=dados["status"],
                latitude=dados.get("latitude"),
                longitude=dados.get("longitude"),
                dados=dados.get("dados"),
            )
        except services.RegraDeNegocioError as erro:
            return _conflito(erro)
        return Response(
            self.get_serializer(evento).data, status=status.HTTP_201_CREATED
        )
