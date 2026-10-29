from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from tarefas.views import TarefaViewSet

router = DefaultRouter()
router.register("tarefas", TarefaViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]