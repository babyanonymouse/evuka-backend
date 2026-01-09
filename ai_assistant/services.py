import google.generativeai as genai
from django.conf import settings
import logging
from .tools import tool_get_platform_stats, tool_list_categories, tool_search_courses, tool_get_my_progress
from courses.models import Lesson

logger = logging.getLogger(__name__)

class AITutorService:
    # ... (init and config methods remain same) ...
    def __init__(self, user, course=None):
        self.user = user
        self.course = course
        self.configure_gemini()
        
    def configure_gemini(self):
        if not settings.GEMINI_API_KEY:
             logger.error("GEMINI_API_KEY is not set.")
        genai.configure(api_key=settings.GEMINI_API_KEY)

    def get_model(self):
        # We use 'gemini-1.5-flash' which corresponds to the latest Flash model
        return genai.GenerativeModel(
            model_name='models/gemini-flash-lite-latest',
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
        """
        if not self.course:
            return ""
            
        # FIX: Access lessons via Module relationship
        lessons = Lesson.objects.filter(module__course=self.course).exclude(content="", transcript="")
        
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
        Implements a "Reasoning Loop" (ReAct pattern) to handle Search and Strictness.
        """
        from .tools import tool_web_search
        model = self.get_model()
        
        # 1. Build the System Context
        course_data = self.build_course_context()
        history_xml = self.format_history(previous_history)
        
        # 2. First Pass: Analysis & Strategy
        system_instruction = (
            "You are Evuka AI, an intelligent and conversational tutor.\n"
            "Your goal is to help the student learn the material in <course_context>.\n\n"
            "CORE INSTRUCTIONS:\n"
            "1. **CHECK HISTORY FIRST**: If the user asks 'tell me more', 'why?', 'explain', etc., assume they are talking about the LAST topic discussed in <history>.\n"
            "2. **BE CONVERSATIONAL**: Do not just repeat lists. If asked to 'tell me more', pick a specific concept from the previous answer and explain it in depth using the notes.\n"
            "3. **TOPIC FILTER**: \n"
            "   - If the question is clearly OFF-TOPIC (e.g. Sports, Politics), reply 'OFF_TOPIC'.\n"
            "   - If the question is about the course topic but details are missing from notes, reply 'SEARCH_EXTERNAL: <query>'.\n"
            "   - Otherwise, answer using the context.\n"
        )
        
        prompt = f"{system_instruction}\n\n{course_data}\n\n{history_xml}\n\nSTUDENT QUESTION: {user_query}"
        
        try:
            response_1 = model.generate_content(prompt)
            text_1 = response_1.text.strip()
            
            # --- Logic Branching ---
            
            if "OFF_TOPIC" in text_1:
                return "I'm sorry, but that question is outside the scope of this course. Let's stick to the topic!"
                
            elif "SEARCH_EXTERNAL:" in text_1:
                # The AI wants to search!
                search_query = text_1.split("SEARCH_EXTERNAL:")[1].strip()
                logger.info(f"AI requested search for: {search_query}")
                
                # Execute Search
                search_results = tool_web_search(search_query)
                
                # Double-check: If search tool failed (e.g. missing lib), warn user
                if "Search Error" in search_results:
                    return f"I wanted to search the web for '{search_query}', but the search tool is not configured.\n({search_results})"

                # 3. Second Pass: Synthesis
                # We feed the search results back to the AI
                final_instruction = (
                    "You have received external search results to help answer the student's deep-dive question.\n"
                    "Integrate these results with the course context to provide a comprehensive answer.\n"
                    "Ensure the answer remains relevant to the course."
                )
                
                final_prompt = (
                    f"{system_instruction}\n\n{course_data}\n\n{history_xml}\n\n"
                    f"STUDENT QUESTION: {user_query}\n\n"
                    f"EXTERNAL SEARCH RESULTS:\n{search_results}\n\n"
                    f"{final_instruction}"
                )
                
                response_2 = model.generate_content(final_prompt)
                return response_2.text
                
            else:
                # Standard Answer found in context
                return text_1
                
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
             if "429" in str(e) or "ResourceExhausted" in str(e):
                 return "AI Busy: Platform capacity reached. Please try again in a minute."
             logger.exception(f"Gemini System Chat Error: {e}")
             return f"System busy. Error: {e}"
