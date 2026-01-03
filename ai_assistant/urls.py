from django.urls import path
from .views import AskAIView, ChatHistoryView

urlpatterns = [
    path('ask/', AskAIView.as_view(), name='ask-ai'),
    path('history/<int:course_id>/', ChatHistoryView.as_view(), name='get-chat-history'),
]