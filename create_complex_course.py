import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DVuka_Backend.settings")
django.setup()

from django.contrib.auth import get_user_model
from courses.models import (
    GlobalCategory, GlobalSubCategory, GlobalLevel, 
    Course, Module, Lesson, Enrollment
)

User = get_user_model()

def create_complex_course():
    print("--- 1. Setting up Users ---")
    creator, _ = User.objects.get_or_create(username="timmy")

    print("\n--- 2. Setting up Metadata ---")
    cat, _ = GlobalCategory.objects.get_or_create(name="Science", defaults={"slug": "science"})
    subcat, _ = GlobalSubCategory.objects.get_or_create(name="Rocketry", category=cat, defaults={"slug": "rocketry"})
    level, _ = GlobalLevel.objects.get_or_create(name="Expert", defaults={"order": 5})

    print("\n--- 3. Creating Complex Course ---")
    course, created = Course.objects.get_or_create(
        title="Advanced Rocket Science",
        defaults={
            "creator": creator,
            "status": "published",
            "global_subcategory": subcat,
            "global_level": level,
            "short_description": "Orbital mechanics and propulsion systems.",
            "long_description": "# Rocket Science\n\nDeep dive into how rockets fly.",
            "price": 199.99,
            "is_public": True,
            "course_type": "independent"
        }
    )
    
    if not created:
        print(f"Course '{course.title}' already exists. Skipping creation.")
        return

    print(f"Created Course: {course.title} (ID: {course.id})")

    # Module 1: Propulsion
    mod1 = Module.objects.create(course=course, title="Propulsion Systems", order=1)
    
    Lesson.objects.create(
        module=mod1,
        title="Solid vs Liquid Fuel",
        order=1,
        content="""
        # Fuel Types
        
        **Solid Propellants**: Simple, storable, high thrust. Once lit, cannot be stopped. Used in boosters (SRBs).
        **Liquid Propellants**: Complex plumbing, controllable throttle, stoppable. Used in main engines (SSME).
        
        Key formula: F = m_dot * v_e + (p_e - p_a) * A_e
        """,
        transcript="In this lecture, we compare the two main types of chemical propulsion. Think of solid fuel like a firecracker - once it goes, it goes. Liquid is like a car engine, you can control the gas flow."
    )
    
    Lesson.objects.create(
        module=mod1,
        title="Specific Impulse (Isp)",
        order=2,
        content="""
        # Specific Impulse
        
        Isp is the efficiency of a rocket engine. It represents the change in momentum per unit of propellant mass.
        Measured in seconds.
        
        *   Higher Isp = More efficient (Ion thrusters)
        *   Lower Isp = Less efficient but high thrust (Chemical rockets)
        """,
        transcript="Specific Impulse is the miles-per-gallon of rocketry. If you have a high Isp, you can go to Mars with less fuel."
    )

    # Module 2: Orbital Mechanics
    mod2 = Module.objects.create(course=course, title="Orbital Mechanics", order=2)
    
    Lesson.objects.create(
        module=mod2,
        title="Kepler's Laws",
        order=1,
        content="""
        # Kepler's Laws of Planetary Motion
        
        1.  **The Law of Ellipses**: The orbit of a planet is an ellipse with the Sun at one of the two foci.
        2.  **The Law of Equal Areas**: A line segment joining a planet and the Sun sweeps out equal areas during equal intervals of time.
        3.  **The Law of Harmonies**: The square of the orbital period of a planet is proportional to the cube of the semi-major axis of its orbit.
        """,
        transcript="Kepler figured this out way before Newton. Basically, nothing moves in a perfect circle. Everything is slightly squashed, or elliptical."
    )

    Lesson.objects.create(
        module=mod2,
        title="Hohmann Transfer",
        order=2,
        content="""
        # Hohmann Transfer Orbit
        
        The most efficient way to move between two orbits.
        Requires two burns:
        1.  **Prograde burn**: Raise apoapsis to target altitude.
        2.  **Circularization burn**: Raise periapsis to match target orbit.
        """,
        transcript="To get from Earth to Mars, you don't just point and shoot. You have to wait for the planets to align and use a Hohmann transfer."
    )
    
    # Enroll Timmy
    Enrollment.objects.get_or_create(user=creator, course=course, defaults={"status": "active"})
    print("Enrolled 'timmy' in the course.")
    
    print("\n--- DONE ---")
    print(f"Course ID for testing: {course.id}")

if __name__ == "__main__":
    create_complex_course()
