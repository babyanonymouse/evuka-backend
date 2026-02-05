from django.core.management.base import BaseCommand
from courses.models import Course, Lesson
from ai_assistant.vector_store import VectorStoreService

class Command(BaseCommand):
    help = 'Rebuilds the ChromaDB vector index from Course and Lesson content'

    def handle(self, *args, **options):
        self.stdout.write("Starting Vector Index Rebuild...")

        # 1. Clear existing
        self.stdout.write("Clearing existing collection...")
        try:
            VectorStoreService.clear_collection()
            self.stdout.write(self.style.SUCCESS("Collection cleared."))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Collection clean warning: {e}"))

        # 2. Index Courses
        courses = Course.objects.all()
        self.stdout.write(f"Indexing {courses.count()} courses...")
        for course in courses:
            text = f"Course: {course.title}. {course.short_description} {course.long_description}"
            meta = {
                "source": "course",
                "title": course.title,
                "db_id": str(course.id),
                "type": "course"
            }
            VectorStoreService.index_content(f"course_{course.id}", text, meta)
        
        # 3. Index Lessons
        lessons = Lesson.objects.select_related('module__course').all()
        self.stdout.write(f"Indexing {lessons.count()} lessons...")
        for lesson in lessons:
            # Combine content for embedding
            content_snippet = lesson.content[:1000] if lesson.content else ""
            transcript_snippet = lesson.transcript[:1000] if lesson.transcript else ""
            
            text = f"Lesson: {lesson.title}. Course: {lesson.module.course.title}. {content_snippet} {transcript_snippet}"
            
            meta = {
                "source": "lesson",
                "title": lesson.title,
                "course": lesson.module.course.title,
                "db_id": str(lesson.id),
                "type": "lesson"
            }
            VectorStoreService.index_content(f"lesson_{lesson.id}", text, meta)

        self.stdout.write(self.style.SUCCESS("Successfully rebuilt vector index!"))
