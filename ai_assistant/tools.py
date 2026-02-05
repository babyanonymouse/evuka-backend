from courses.models import Course, GlobalCategory, Enrollment
from live.models import LiveLesson
from django.utils import timezone

def tool_check_live_schedule(course_title_query=None):
    """
    Checks for upcoming live lessons. 
    If course_title_query is provided, filters by that course.
    Returns a formatted list of the next 3 lessons.
    """
    now = timezone.now()
    lessons = LiveLesson.objects.filter(
        date__gte=now.date(), 
        is_active=True
    ).select_related('live_class__course').order_by('date', 'start_time')
    
    if course_title_query:
        lessons = lessons.filter(live_class__course__title__icontains=course_title_query)
        
    lessons = lessons[:3]
    
    if not lessons.exists():
        return "No upcoming live lessons found."
        
    results = "UPCOMING LIVE LESSONS:\n"
    for l in lessons:
        results += f"- {l.title} ({l.live_class.course.title}): {l.date} from {l.start_time} to {l.end_time}. Link: {l.jitsi_meeting_link}\n"
        
    return results

def tool_search_courses(query):
    """Searches for published courses by title."""
    courses = Course.objects.filter(title__icontains=query, status='published')[:5]
    if not courses.exists():
        return "No courses found matching that name."
    
    results = []
    for c in courses:
        # Assuming you might have a price field or instructor name, add them here.
        # For now, just Title and ID.
        results.append(f"- {c.title} (ID: {c.id})")
    
    return "\n".join(results)

def tool_get_platform_stats():
    """Returns general statistics about the platform."""
    count = Course.objects.filter(status='published').count()
    return f"There are currently {count} published courses available on Evuka."

def tool_list_categories():
    """Lists all available global course categories."""
    categories = GlobalCategory.objects.all().values_list('name', flat=True)
    if not categories:
        return "No categories available yet."
    return ", ".join(categories)

def tool_get_my_progress(user, course_id):
    """Returns the completion percentage for a specific user and course."""
    if not user.is_authenticated:
        return "User is not logged in."
        
    try:
        enrollment = Enrollment.objects.get(user=user, course_id=course_id)
        return f"{enrollment.progress_percent}% completed"
    except Enrollment.DoesNotExist:
        return "Not enrolled in this course."

def tool_web_search(query):
    """
    Searches the web for the query using DuckDuckGo.
    Requires: pip install duckduckgo-search
    """
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=3)
        if not results:
             return "No external results found."
        
        summary = "External Search Results:\n"
        for r in results:
            summary += f"- {r['title']}: {r['body']} ({r['href']})\n"
        return summary
    except ImportError as e:
        return f"Search Error: Missing dependency. {e}. Please run `pip install ddgs`."
    except Exception as e:
        return f"Search Error: {e}"

from ai_assistant.vector_store import VectorStoreService

def tool_query_database(query):
    """
    Searches the internal project database (Lessons, Courses) for the query 
    using Semantic Vector Search (ChromaDB).
    Returns formatted context.
    """
    return VectorStoreService.search(query)
