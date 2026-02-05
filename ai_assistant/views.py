from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from .services import AITutorService, AISystemService
from .models import ChatHistory
from courses.models import Course

class AskAIView(APIView):
    """
    V2 AI Endpoint.
    Body: { "message": "...", "course_id": 123 (optional) }
    """
    permission_classes = [AllowAny] # V1: AllowAny for demo. V2: Should be IsAuthenticated.

    def post(self, request):
        message = request.data.get('message')
        course_id = request.data.get('course_id')

        if not message:
            return Response({"error": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

        response_text = ""

        if course_id:
            # --- Course Tutor Mode (Secure) ---
            
            # 1. Security Check: Is user enrolled? (Disabled for V1 Demo if user is anonymous)
            if request.user.is_authenticated:
                is_enrolled = request.user.enrollments.filter(course_id=course_id).exists()
                # For demo purposes, we might skip this strict check or warn.
                # if not is_enrolled: return Response({"error": "Not enrolled."}, status=403)
            
            course = get_object_or_404(Course, id=course_id)
            
            # 2. Get/Create Chat History
            # If anonymous, we can't save history easily.
            previous_history = []
            chat_obj = None
            
            if request.user.is_authenticated:
                chat_obj, created = ChatHistory.objects.get_or_create(
                    user=request.user, 
                    course=course
                )
                previous_history = chat_obj.history_json
            
            # 3. Call AI Service
            service = AITutorService(user=request.user, course=course)
            response_text = service.ask(message, previous_history)
            
                # 4. Save History (Append new exchange)
            if chat_obj:
                new_exchange = [
                    {'role': 'user', 'content': message},
                    {'role': 'model', 'content': response_text}
                ]
                # Important: Reassign the list so Django knows the field changed
                history = chat_obj.history_json
                history.extend(new_exchange)
                chat_obj.history_json = history
                chat_obj.save()

        else:
            service = AISystemService(user=request.user)
            response_text = service.ask_general(message)

        return Response({"response": response_text})

class ChatHistoryView(APIView):
    """
    GET /api/ai/history/<course_id>/
    Returns conversation history for the user and course.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        chat_obj = get_object_or_404(ChatHistory, user=request.user, course_id=course_id)
        return Response(chat_obj.history_json)
 