# import os
# import django
# import random

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DVuka_Backend.settings")
# django.setup()

# from django.contrib.auth import get_user_model
# from courses.models import (
#     GlobalCategory, GlobalSubCategory, GlobalLevel, 
#     Course, Module, Lesson, Enrollment
# )
# from django.utils.text import slugify

# User = get_user_model()

# def create_course():
#     print("--- 1. Setting up Users ---")
#     # Ensure we have a user to be the creator
#     creator, created = User.objects.get_or_create(
#         username="timmy",
#         defaults={"email": "timmy@example.com", "is_staff": True, "is_superuser": True}
#     )
#     if created:
#         creator.set_password("admin")
#         creator.save()
#         print("Created superuser 'timmy' (pass: admin)")
#     else:
#         print("Using existing user 'timmy'")

#     print("\n--- 2. Setting up Metadata ---")
#     cat, _ = GlobalCategory.objects.get_or_create(
#         name="Technology",
#         defaults={"slug": "technology", "description": "Tech courses"}
#     )
    
#     subcat, _ = GlobalSubCategory.objects.get_or_create(
#         name="Programming",
#         category=cat,
#         defaults={"slug": "programming"}
#     )
    
#     level_beg, _ = GlobalLevel.objects.get_or_create(name="Beginner", defaults={"order": 1})
#     level_adv, _ = GlobalLevel.objects.get_or_create(name="Advanced", defaults={"order": 3})

#     print("\n--- 3. Creating Course ---")
#     course_title = "Python for AI Beginners"
#     course, created = Course.objects.get_or_create(
#         title=course_title,
#         defaults={
#             "creator": creator,
#             "status": "published",
#             "global_subcategory": subcat,
#             "global_level": level_beg,
#             "short_description": "Learn Python from scratch and build AI apps.",
#             "long_description": "# Python for AI\n\nThis course covers everything you need to know.",
#             "price": 49.99,
#             "is_public": True,
#             "course_type": "independent"
#         }
#     )
    
#     if created:
#         print(f"Created Course: {course.title} (ID: {course.id})")
#     else:
#         print(f"Found existing Course: {course.title} (ID: {course.id})")
        
#     print("\n--- 4. Creating Modules & Lessons ---")
#     # Module 1
#     mod1, _ = Module.objects.get_or_create(course=course, title="Basics of Python", order=1)
    
#     l1, _ = Lesson.objects.get_or_create(
#         module=mod1, 
#         title="Introduction to Python",
#         defaults={
#             "order": 1,
#             "content": "Python is a high-level, interpreted programming language known for its readability.",
#             "transcript": "Hello students! Welcome to Python. Today we will install Python and print Hello World."
#         }
#     )
    
#     l2, _ = Lesson.objects.get_or_create(
#         module=mod1,
#         title="Variables and Types",
#         defaults={
#             "order": 2,
#             "content": "Variables allow you to store data. Common types: int, float, str, bool.",
#             "transcript": "Okay, let's talk about buckets. Variables are like buckets where you put your data."
#         }
#     )
    
#     # Module 2
#     mod2, _ = Module.objects.get_or_create(course=course, title="AI Fundamentals", order=2)
    
#     l3, _ = Lesson.objects.get_or_create(
#         module=mod2,
#         title="What is an LLM?",
#         defaults={
#             "order": 1,
#             "content": "Large Language Models (LLMs) are deep learning algorithms that can recognize, summarize, translate, predict, and generate text.",
#             "transcript": "Imagine a really well-read parrot. That's kind of like an LLM, but much smarter. It predicts the next word."
#         }
#     )
    
#     print(f"Ensured {mod1.lessons.count() + mod2.lessons.count()} lessons exist.")

#     print("\n--- 5. Enrolling User ---")
#     enrollment, _ = Enrollment.objects.get_or_create(
#         user=creator,
#         course=course,
#         defaults={"status": "active", "progress_percent": 15.0} # Fake some progress
#     )
#     print(f"User 'timmy' enrolled in course '{course.title}'")
    
#     print("\n--- SUCCESS ---")
#     print(f"Test data is ready. You can now test the AI using Course ID: {course.id}")

# if __name__ == "__main__":
#     create_course()
