import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000/ai/ask/"

def call_ai(message, course_id=None):
    data = {"message": message}
    if course_id:
        data["course_id"] = course_id
        
    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "No response field found.")
    except urllib.error.URLError as e:
        return f"Error: {e}"

def main():
    print("--- Evuka AI Verification Tool ---\n")
    
    # 1. Test System Mode
    print("1. Testing System Navigator (General Question)...")
    q1 = "How many courses are available on the platform?"
    print(f"   Question: {q1}")
    ans1 = call_ai(q1)
    print(f"   AI Answer: {ans1}\n")
    
    # 2. Test Course Mode
    print("2. Testing Course Tutor (Context-Aware)...")
    course_id = input("   Enter a Course ID to test (or press Enter to skip): ").strip()
    
    if course_id:
        q2 = input("   What would you like to ask about this course? (Default: Summarize this course): ").strip()
        if not q2: q2 = "Summarize the content of this course."
        
        print(f"   Sending query for Course ID {course_id}...")
        ans2 = call_ai(q2, course_id)
        print(f"   AI Answer: {ans2}\n")
    else:
        print("   Skipping Course Tutor test.\n")
        
    print("--- Test Complete ---")

if __name__ == "__main__":
    main()
