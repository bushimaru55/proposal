from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'products'

router = DefaultRouter()
router.register(r'categories', views.ProductCategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'knowledge', views.ProductKnowledgeViewSet, basename='knowledge')

urlpatterns = [
    path('', include(router.urls)),
]

