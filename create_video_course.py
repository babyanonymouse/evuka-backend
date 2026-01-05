import os
import django
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DVuka_Backend.settings")
django.setup()

from django.contrib.auth import get_user_model
from courses.models import (
    GlobalCategory, GlobalSubCategory, GlobalLevel, 
    Course, Module, Lesson, Enrollment
)

User = get_user_model()

def create_video_course():
    print("--- 1. Setting up Users ---")
    creator, _ = User.objects.get_or_create(username="timmy")

    print("\n--- 2. Setting up Metadata ---")
    cat, _ = GlobalCategory.objects.get_or_create(name="Arts", defaults={"slug": "arts"})
    subcat, _ = GlobalSubCategory.objects.get_or_create(name="Film", category=cat, defaults={"slug": "film"})
    level, _ = GlobalLevel.objects.get_or_create(name="Intermediate", defaults={"order": 2})

    print("\n--- 3. Creating MultiMedia Course ---")
    course, created = Course.objects.get_or_create(
        title="Cinematography 101",
        defaults={
            "creator": creator,
            "status": "published",
            "global_subcategory": subcat,
            "global_level": level,
            "short_description": "Learn to film with style.",
            "long_description": "# Lights, Camera, Action!\n\nA course about filming.",
            "price": 99.99,
            "is_public": True,
            "course_type": "independent"
        }
    )
    
    if created:
        print(f"Created Course: {course.title} (ID: {course.id})")
    else:
        print(f"Found existing Course: {course.title} (ID: {course.id})")
        
    print("\n--- 4. Attaching Video Lesson ---")
    mod1, _ = Module.objects.get_or_create(course=course, title="Camera Work", order=1)
    
    # Path to the dummy video we created
    video_path = 'media/lesson_videos/dummy_video.mp4'
    
    # Check if we should create the lesson
    if not Lesson.objects.filter(module=mod1, title="The Rule of Thirds").exists():
        with open(video_path, 'rb') as f:
            lesson = Lesson(
                module=mod1,
                title="The Rule of Thirds",
                order=1,
                content="Always place your subject on the intersecting lines.",
                transcript="In this video, I will show you how to frame your shot. Look at where the lines cross."
            )
            # We attach the file specifically
            lesson.video_file.save("dummy_video.mp4", File(f), save=True)
            print("Created Video Lesson: 'The Rule of Thirds'")
    else:
        print("Lesson 'The Rule of Thirds' already exists.")

    Enrollment.objects.get_or_create(user=creator, course=course, defaults={"status": "active"})
    
    print("\n--- DONE ---")
    print(f"Course ID for testing: {course.id}")

if __name__ == "__main__":
    create_video_course()
