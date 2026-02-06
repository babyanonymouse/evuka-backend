# courses/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, Enrollment, Lesson
# Import the service (safe, no circular dependency at top level)
from ai_assistant.vector_store import VectorStoreService

@receiver(post_save, sender=Course)
def index_course_on_save(sender, instance, **kwargs):
    """
    Real-time updates: Index the course in ChromaDB whenever it is saved.
    """
    # Only index published courses? Or all? Let's index all for now so draft search works for tutors.
    # Format content for embedding
    text_content = f"Course: {instance.title}\n"
    text_content += f"Description: {instance.short_description}\n"
    if instance.long_description:
        text_content += f"Details: {instance.long_description[:1000]}"
    
    metadata = {
        "title": instance.title,
        "type": "course",
        "url": f"/courses/{instance.slug}", # Hypothetical URL
        "id": instance.id
    }
    
    # Update Vector DB
    VectorStoreService.index_content(
        content_id=f"course_{instance.id}",
        text=text_content,
        metadata=metadata
    )

@receiver(post_save, sender=Lesson)
def index_lesson_on_save(sender, instance, **kwargs):
    """
    Real-time updates: Index the lesson in ChromaDB whenever it is saved.
    """
    # Format content
    course_title = instance.module.course.title if instance.module and instance.module.course else "Unknown Course"
    
    text_content = f"Lesson: {instance.title}\n"
    text_content += f"Course: {course_title}\n"
    
    # weight content heavily
    if instance.content:
        text_content += f"Content: {instance.content[:2000]}\n"
    if instance.transcript:
        text_content += f"Transcript: {instance.transcript[:2000]}"
        
    metadata = {
        "title": instance.title,
        "type": "lesson",
        "url": f"/lessons/{instance.id}",
        "id": instance.id
    }
    
    # Update Vector DB
    VectorStoreService.index_content(
        content_id=f"lesson_{instance.id}",
        text=text_content,
        metadata=metadata
    )

@receiver(post_save, sender=Course)
def auto_enroll_org_members(sender, instance, created, **kwargs):
    """
    Auto-enrolls active student members of the related organization
    when a new course is created or published.
    """
    from organizations.models import OrgMembership

    # 1. Only proceed if the course belongs to an organization and is published/created
    if not instance.organization:
        return

    # Check for relevant status changes (e.g., draft -> published)
    is_published = instance.status == 'published'
    is_level_required = bool(instance.org_level)

    if not is_published:
        return

    # 2. Find all active student members of this organization
    members_qs = OrgMembership.objects.filter(
        organization=instance.organization,
        is_active=True,
        role='student'
    )

    # 3. Apply level filtering before iterating
    if is_level_required:
        members_qs = members_qs.filter(level=instance.org_level)

    # Iterate and enroll
    for membership in members_qs:
        # Create enrollment for the member
        Enrollment.objects.get_or_create(
            user=membership.user,
            course=instance,
            defaults={
                'role': 'student',
                'status': 'active'
            }
        )