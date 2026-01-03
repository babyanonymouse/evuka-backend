import google.generativeai as genai
from django.conf import settings
import logging
from .tools import tool_get_platform_stats, tool_list_categories, tool_search_courses, tool_get_my_progress

logger = logging.getLogger(__name__)

class AITutorService:
    """
    Core AI Service for the Course Tutor feature.
    
    Architecture Note:
    We use a Class-based approach here to maintain state (user, course) 
    and to allow for easy extension (e.g., adding more context sources later).
    """
    def __init__(self, user, course=None):
        self.user = user
        self.course = course
        self.configure_gemini()
        
    def configure_gemini(self):
        if not settings.GEMINI_API_KEY:
             logger.error("GEMINI_API_KEY is not set.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
    def get_model(self):
        # We use 'gemini-flash-latest' which corresponds to the latest Flash model
        return genai.GenerativeModel(
            model_name='gemini-flash-latest',
            generation_config={
                "temperature": 0.2, # Low temperature reduces "creativity", preventing hallucinations.
                "max_output_tokens": 8192,
            }
        )

    def format_history(self, history_list):
        """
        Converts stored JSON history to XML format for the context.
        XML is preferred by Gemini for structured data over plain text.
        """
        xml = "<history>\n"
        # Limit to last 10 exchanges to save tokens/sanity
        for msg in history_list[-10:]: 
            role = "user" if msg['role'] == 'user' else "model"
            xml += f"  <{role}>{msg['content']}</{role}>\n"
        xml += "</history>"
        return xml

    def build_course_context(self):
        """
        Fetches all lessons and transcripts, formatting them as XML.
        
        Why XML?
        It allows the AI to clearly distinguish between 'notes' and 'transcript'
        and reference specific lesson IDs in its answers.
        """
        if not self.course:
            return ""
            
        lessons = self.course.lessons.exclude(content="", transcript="")
        context_xml = f"<course_context id='{self.course.id}' title='{self.course.title}'>\n"
        
        for lesson in lessons:
            context_xml += f"  <lesson id='{lesson.id}' title='{lesson.title}'>\n"
            if lesson.content:
                context_xml += f"    <notes>{lesson.content}</notes>\n"
            if lesson.transcript:
                context_xml += f"    <transcript>{lesson.transcript}</transcript>\n"
            context_xml += "  </lesson>\n"
            
        context_xml += "</course_context>"
        return context_xml

    def ask(self, user_query, previous_history=[]):
        """
        Main entry point for asking the AI.
        
        Args:
            user_query (str): The current question.
            previous_history (list): List of dicts [{'role': 'user', 'content': '...'}, ...]
        """
        model = self.get_model()
        
        # 1. Build the System Context
        course_data = self.build_course_context()
        history_xml = self.format_history(previous_history)
        
        # 2. Construct the Mega-Prompt
        system_instruction = (
            "You are Evuka AI, an intelligent and helpful course tutor.\n"
            "Your goal is to help the student understand the material provided in the <course_context> tags.\n\n"
            "STRICT RULES:\n"
            "1. Answer ONLY based on the information in <course_context>.\n"
            "2. If the answer is not in the notes or transcript, say: 'I cannot find that information in this course's content.'\n"
            "3. Use the <history> to understand previous context (e.g., if user says 'tell me more', look at the last model response).\n"
            "4. Be encouraging and concise.\n"
        )
        
        prompt = f"{system_instruction}\n\n{course_data}\n\n{history_xml}\n\nSTUDENT QUESTION: {user_query}"
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.exception("AI Generation Error")
            return "I'm having trouble thinking right now. Please try again."

class AISystemService(AITutorService):
    """Specialized service for General System Questions."""
    
    def ask_general(self, user_query):
        model = self.get_model()
        
        # 1. Gather System Intel
        stats = tool_get_platform_stats()
        cats = tool_list_categories()
        
        # Simple RAG for search
        search_results = ""
        if "course" in user_query.lower() or "learn" in user_query.lower():
             search_results = f"Search Context: {tool_search_courses(user_query)}"

        system_instruction = (
            "You are Evuka AI, the platform guide.\n"
            f"SYSTEM STATUS:\n- {stats}\n- Categories: {cats}\n{search_results}\n\n"
            "Answer questions about available courses and platform stats."
        )
        
        prompt = f"{system_instruction}\n\nUSER QUESTION: {user_query}"
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
             logger.exception(f"Gemini System Chat Error: {e}")
             return f"System busy. Error: {e}"
