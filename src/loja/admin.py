from django.contrib import admin

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

admin.site.site_header = "Plataforma E-commerce Last-Mile"
admin.site.site_title = "Last-Mile Admin"


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("sku", "nome", "categoria", "preco", "estoque", "ativo")
    list_filter = ("categoria", "ativo")
    search_fields = ("sku", "nome")


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "telefone")
    search_fields = ("nome", "email")


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "status", "total", "criado_em")
    list_filter = ("status",)
    inlines = [ItemPedidoInline]


@admin.register(Entregador)
class EntregadorAdmin(admin.ModelAdmin):
    list_display = ("nome", "veiculo", "ativo")
    list_filter = ("veiculo", "ativo")


class EventoInline(admin.TabularInline):
    model = EventoRastreamento
    extra = 0
    readonly_fields = ("registrado_em",)


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ("id", "pedido", "entregador", "status", "atualizada_em")
    list_filter = ("status",)
    inlines = [EventoInline]


@admin.register(EventoRastreamento)
class EventoRastreamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "entrega", "status", "registrado_em")
    list_filter = ("status",)
