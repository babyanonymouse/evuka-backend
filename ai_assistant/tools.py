from courses.models import Course, GlobalCategory, Enrollment

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

def tool_query_database(query):
    """
    Searches the internal project database (Lessons, Courses) for the query.
    Returns formatted context.
    """
    from django.db.models import Q
    
    # 1. Search Lessons (Title, Content, Transcript)
    # We prioritize lessons as they are the "meat" of the knowledge base.
    lessons = Lesson.objects.filter(
        Q(title__icontains=query) | 
        Q(content__icontains=query) | 
        Q(transcript__icontains=query)
    ).select_related('module__course')[:5] # Limit to top 5 matches
    
    # 2. Search Courses (Title, Description)
    courses = Course.objects.filter(
        Q(title__icontains=query) |
        Q(long_description__icontains=query)
    )[:3]
    
    if not lessons.exists() and not courses.exists():
        return "No internal project data found matching that query."
        
    results = "INTERNAL PROJECT DATABASE RESULTS:\n"
    
    if lessons.exists():
        results += "--- LESSON MATCHES ---\n"
        for l in lessons:
            course_title = l.module.course.title if l.module and l.module.course else "Unknown Course"
            # Extract a snippet if content is long? For now, we trust the LLM to handle it or we can truncate.
            # Let's truncate content/transcript to avoid blowing context limits too hard in one go, 
            # though 8k tokens is generous.
            snippet = l.content[:500] if l.content else l.transcript[:500]
            results += f"Lesson: {l.title} (Course: {course_title})\nSnippet: {snippet}...\n\n"
            
    if courses.exists():
        results += "--- COURSE MATCHES ---\n"
        for c in courses:
             results += f"Course: {c.title}\nDescription: {c.short_description}\n\n"
             
    return results
