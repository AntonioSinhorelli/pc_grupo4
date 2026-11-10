"""Modelo de dados da plataforma de e-commerce com logística last-mile.

Paradigmas combinados no mesmo PostgreSQL:
  * Relacional (ACID): Categoria, Produto, Cliente, Pedido, ItemPedido,
    Entregador e Entrega.
  * Documento (JSONB): ``Produto.atributos`` (especificações flexíveis por
    tipo de produto) e ``EventoRastreamento.dados`` (payload dos eventos
    logísticos que, na arquitetura alvo, ficariam no DynamoDB). Ambos têm
    índice GIN criado por migration.
"""
from decimal import Decimal

from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="produtos"
    )
    sku = models.CharField(max_length=40, unique=True)
    nome = models.CharField(max_length=200)
    preco = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    estoque = models.PositiveIntegerField(default=0)
    # Modelo documento: atributos variam por categoria (cor, voltagem, peso...)
    atributos = models.JSONField(default=dict, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        indexes = [GinIndex(fields=["atributos"], name="produto_atributos_gin")]

    def __str__(self):
        return f"{self.sku} - {self.nome}"


class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    class Status(models.TextChoices):
        CRIADO = "criado", "Criado"
        PAGO = "pago", "Pago"
        EM_ENTREGA = "em_entrega", "Em entrega"
        ENTREGUE = "entregue", "Entregue"
        CANCELADO = "cancelado", "Cancelado"

    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name="pedidos"
    )
    # Relacionamento N:N com atributos (quantidade e preço) via ItemPedido
    produtos = models.ManyToManyField(
        Produto, through="ItemPedido", related_name="pedidos"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CRIADO
    )
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    endereco_entrega = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Pedido #{self.pk} ({self.get_status_display()})"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="itens"
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, related_name="itens"
    )
    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    # Preço congelado no momento da compra
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pedido", "produto"], name="item_unico_por_pedido"
            )
        ]

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.produto.sku} no pedido #{self.pedido_id}"


class Entregador(models.Model):
    class Veiculo(models.TextChoices):
        MOTO = "moto", "Moto"
        BICICLETA = "bicicleta", "Bicicleta"
        CARRO = "carro", "Carro"
        VAN = "van", "Van"

    nome = models.CharField(max_length=150)
    veiculo = models.CharField(
        max_length=20, choices=Veiculo.choices, default=Veiculo.MOTO
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name_plural = "entregadores"

    def __str__(self):
        return self.nome


class Entrega(models.Model):
    class Status(models.TextChoices):
        AGUARDANDO = "aguardando", "Aguardando coleta"
        EM_ROTA = "em_rota", "Em rota"
        ENTREGUE = "entregue", "Entregue"
        FALHOU = "falhou", "Tentativa frustrada"

    pedido = models.OneToOneField(
        Pedido, on_delete=models.CASCADE, related_name="entrega"
    )
    entregador = models.ForeignKey(
        Entregador, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="entregas",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AGUARDANDO
    )
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criada_em"]

    def __str__(self):
        return f"Entrega do pedido #{self.pedido_id} ({self.get_status_display()})"


class EventoRastreamento(models.Model):
    """Evento de última milha (status, geolocalização, ocorrências)."""

    entrega = models.ForeignKey(
        Entrega, on_delete=models.CASCADE, related_name="eventos"
    )
    status = models.CharField(max_length=20, choices=Entrega.Status.choices)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    # Modelo documento: payload livre enviado pelo app do entregador
    dados = models.JSONField(default=dict, blank=True)
    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-registrado_em"]
        indexes = [GinIndex(fields=["dados"], name="evento_dados_gin")]

    def __str__(self):
        return f"{self.get_status_display()} - entrega #{self.entrega_id}"
