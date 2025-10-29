from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('test-openai/', views.test_openai_connection, name='test_openai_connection'),
    path('ai-chat/', views.ai_chat_test, name='ai_chat_test'),
    path('ai-chat/send/', views.ai_chat_send, name='ai_chat_send'),
]

