from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson, GlobalCategory, GlobalLevel, GlobalSubCategory
from .tools import tool_query_database
from .services import AITutorService
from unittest.mock import patch, MagicMock

User = get_user_model()

class AIAssistantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Setup Course dependencies
        self.category = GlobalCategory.objects.create(name="Tech", slug="tech")
        self.subcategory = GlobalSubCategory.objects.create(category=self.category, name="Web", slug="web")
        self.level = GlobalLevel.objects.create(name="Beginner", order=1)
        
        self.course = Course.objects.create(
            title="Intro to Python",
            creator=self.user,
            status="published",
            global_subcategory=self.subcategory,
            global_level=self.level
        )
        self.module = Module.objects.create(course=self.course, title="Basics")
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Variables",
            content="Variables are containers for storing data values.",
            transcript="In this video we talk about variables."
        )

    def test_tool_query_database(self):
        # 1. Test exact match
        result = tool_query_database("Variables")
        self.assertIn("INTERNAL PROJECT DATABASE RESULTS", result)
        self.assertIn("Variables", result)
        self.assertIn("Intro to Python", result)
        
        # 2. Test content match
        result = tool_query_database("storing data")
        self.assertIn("Variables are containers", result)

        # 3. Test no match
        result = tool_query_database("Banana")
        self.assertIn("No internal project data found", result)

    @patch('ai_assistant.services.genai')
    def test_service_context(self, mock_genai):
        # Mock configure to avoid errors
        service = AITutorService(self.user, self.course)
        
        context = service.build_course_context()
        self.assertIn("<course_context", context)
        self.assertIn("Intro to Python", context)
        self.assertIn("Variables", context)
