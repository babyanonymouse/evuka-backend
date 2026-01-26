import google.generativeai as genai
from django.conf import settings
import logging
from .tools import tool_get_platform_stats, tool_list_categories, tool_search_courses, tool_get_my_progress, tool_query_database
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
        Implements a "Reasoning Loop" (ReAct pattern) to handle Database Search and Web Search.
        """
        from .tools import tool_web_search
        model = self.get_model()
        
        # 1. Build the System Context
        course_data = self.build_course_context()
        history_xml = self.format_history(previous_history)
        
        # 2. First Pass: Analysis & Strategy
        # User defined Persona and Operational Guidelines
        system_instruction = (
            "You are a software engineer creating a sophisticated, conversational AI assistant.\n"
            "Your primary goal is to provide accurate, helpful, and context-aware responses by leveraging two key resources: your internal Project Database and Google Search.\n\n"
            "# OPERATIONAL GUIDELINES\n"
            "1. **Database-First Approach**: For any query related to project specifics, internal data, or previously stored information, check the Database first.\n"
            "   - Use `QUERY_DATABASE: <query>` for this.\n"
            "2. **Web Augmentation**: If the user asks about current events, specific external topics not found in the database, or requires real-time validation, use Google Search.\n"
            "   - Use `GOOGLE_SEARCH: <query>` for this.\n"
            "3. **Be Conversational**: Maintain a natural, friendly, and professional tone. Do not sound like a robot; respond like a helpful peer.\n"
            "4. **Historical Context**: You are provided with the conversation history. Use this to maintain continuity.\n"
            "   - DO NOT re-introduce yourself if a conversation is already in progress.\n"
            "   - Refer back to previous points (e.g., 'As we discussed earlier...').\n\n"
            "# TOOL USAGE RULES\n"
            "- If you need internal project facts or 'evuka' info -> Reply with `QUERY_DATABASE: <exact query>`.\n"
            "- If you need general knowledge, technical docs, or news -> Reply with `GOOGLE_SEARCH: <exact query>`.\n"
            "- If the answer is already in the context/history, just answer directly.\n"
            "- **Conflict Resolution**: If database and web search conflict, prioritize the database for project-specific facts.\n\n"
            "# CONSTRAINTS\n"
            "- Always cite whether your information came from the 'Project Database' or 'Live Web Search' if you used a tool."
        )
        
        prompt = f"{system_instruction}\n\nCURRENT COURSE CONTEXT (if any):\n{course_data}\n\nCONVERSATION HISTORY:\n{history_xml}\n\nSTUDENT QUESTION: {user_query}"
        
        try:
            response_1 = model.generate_content(prompt)
            text_1 = response_1.text.strip()
            
            # --- Logic Branching ---
            
            if "QUERY_DATABASE:" in text_1:
                # Handle Database Query
                search_query = text_1.split("QUERY_DATABASE:")[1].strip()
                logger.info(f"AI requested DB search for: {search_query}")
                
                db_results = tool_query_database(search_query)
                
                # Synthesis Pass
                final_instruction = (
                    "You have received internal database results.\n"
                    "Integrate these results to answer the user's question.\n"
                    "Remember to cite 'Project Database' as your source."
                )
                
                final_prompt = (
                    f"{system_instruction}\n\nCONVERSATION HISTORY:\n{history_xml}\n\n"
                    f"STUDENT QUESTION: {user_query}\n\n"
                    f"{db_results}\n\n"
                    f"{final_instruction}"
                )
                
                response_2 = model.generate_content(final_prompt)
                return response_2.text

            elif "GOOGLE_SEARCH:" in text_1 or "SEARCH_EXTERNAL:" in text_1:
                # Handle Web Search (Support both tags for robustness)
                if "GOOGLE_SEARCH:" in text_1:
                    search_query = text_1.split("GOOGLE_SEARCH:")[1].strip()
                else:
                    search_query = text_1.split("SEARCH_EXTERNAL:")[1].strip()
                    
                logger.info(f"AI requested Google search for: {search_query}")
                
                # Execute Search
                search_results = tool_web_search(search_query)
                
                if "Search Error" in search_results:
                    return f"I wanted to search for '{search_query}', but I encountered an error: {search_results}"

                # Synthesis Pass
                final_instruction = (
                    "You have received external search results.\n"
                    "Integrate these results to answer the user's question.\n"
                    "Remember to cite 'Live Web Search' as your source."
                )
                
                final_prompt = (
                    f"{system_instruction}\n\nCONVERSATION HISTORY:\n{history_xml}\n\n"
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
