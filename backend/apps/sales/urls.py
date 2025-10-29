from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'sales'

router = DefaultRouter()
router.register(r'talk-scripts', views.TalkScriptViewSet, basename='talk-script')
router.register(r'outcomes', views.SalesOutcomeViewSet, basename='sales-outcome')
router.register(r'training-sessions', views.TrainingSessionViewSet, basename='training-session')

urlpatterns = [
    path('', include(router.urls)),
]

