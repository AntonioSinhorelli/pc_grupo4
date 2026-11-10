from rest_framework import serializers

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


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)

    class Meta:
        model = Produto
        fields = [
            "id", "sku", "nome", "preco", "estoque", "ativo",
            "categoria", "categoria_nome", "atributos", "criado_em",
        ]
        read_only_fields = ["criado_em"]

    def validate_atributos(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "atributos deve ser um objeto JSON (chave/valor)."
            )
        return value


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = "__all__"


class EntregadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entregador
        fields = "__all__"


class EventoRastreamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoRastreamento
        fields = [
            "id", "entrega", "status", "latitude", "longitude",
            "dados", "registrado_em",
        ]
        read_only_fields = ["registrado_em"]

    def validate_dados(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("dados deve ser um objeto JSON.")
        return value


class EventoEntradaSerializer(serializers.Serializer):
    """Entrada de POST /api/entregas/<id>/eventos/ (app do entregador)."""

    status = serializers.ChoiceField(choices=Entrega.Status.choices)
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    dados = serializers.DictField(required=False, default=dict)


class EntregaSerializer(serializers.ModelSerializer):
    # Serializer aninhado: histórico de eventos dentro da entrega
    eventos = EventoRastreamentoSerializer(many=True, read_only=True)

    class Meta:
        model = Entrega
        fields = [
            "id", "pedido", "entregador", "status",
            "criada_em", "atualizada_em", "eventos",
        ]
        read_only_fields = ["status", "criada_em", "atualizada_em"]


class ItemPedidoSerializer(serializers.ModelSerializer):
    produto_sku = serializers.CharField(source="produto.sku", read_only=True)
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = ItemPedido
        fields = [
            "id", "produto", "produto_sku", "produto_nome",
            "quantidade", "preco_unitario", "subtotal",
        ]


class PedidoSerializer(serializers.ModelSerializer):
    # Serializers aninhados (somente leitura): itens e entrega do pedido
    itens = ItemPedidoSerializer(many=True, read_only=True)
    entrega = EntregaSerializer(read_only=True)

    class Meta:
        model = Pedido
        fields = [
            "id", "cliente", "status", "total", "endereco_entrega",
            "criado_em", "itens", "entrega",
        ]
        read_only_fields = ["cliente", "total", "criado_em"]


class ItemEntradaSerializer(serializers.Serializer):
    produto = serializers.PrimaryKeyRelatedField(queryset=Produto.objects.all())
    quantidade = serializers.IntegerField(min_value=1)


class PedidoCheckoutSerializer(serializers.Serializer):
    """Entrada de POST /api/pedidos/ (checkout transacional)."""

    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    endereco_entrega = serializers.CharField(max_length=255)
    itens = ItemEntradaSerializer(many=True, allow_empty=False)
