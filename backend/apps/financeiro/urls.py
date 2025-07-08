from rest_framework.routers import DefaultRouter
from .views.conta_view import ContaFinanceiraViewSet
from .views.fornecedor_view import FornecedorViewSet

router = DefaultRouter()
router.register(r'contas', ContaFinanceiraViewSet)
router.register(r'fornecedores', FornecedorViewSet)

urlpatterns = router.urls
