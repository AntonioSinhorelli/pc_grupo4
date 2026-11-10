from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from loja import views

router = DefaultRouter()
router.register("categorias", views.CategoriaViewSet, basename="categoria")
router.register("produtos", views.ProdutoViewSet, basename="produto")
router.register("clientes", views.ClienteViewSet, basename="cliente")
router.register("pedidos", views.PedidoViewSet, basename="pedido")
router.register("itens-pedido", views.ItemPedidoViewSet, basename="itempedido")
router.register("entregadores", views.EntregadorViewSet, basename="entregador")
router.register("entregas", views.EntregaViewSet, basename="entrega")
router.register("eventos", views.EventoRastreamentoViewSet, basename="evento")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("health/", views.health, name="health"),
]
