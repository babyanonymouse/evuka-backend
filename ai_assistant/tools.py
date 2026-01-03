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
