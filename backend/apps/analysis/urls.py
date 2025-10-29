from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'analysis'

router = DefaultRouter()
router.register(r'csv-uploads', views.CSVUploadViewSet, basename='csv-upload')
router.register(r'analyses', views.AnalysisViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
]

