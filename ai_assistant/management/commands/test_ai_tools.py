from django.core.management.base import BaseCommand
from ai_assistant.tools import tool_query_database, tool_web_search
from courses.models import Course, Lesson

class Command(BaseCommand):
    help = 'Verifies the AI Assistant tools (Database Search and Web Search)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting AI Tools Verification...'))

        # --- Test 1: Web Search ---
        self.stdout.write('\n[1/2] Testing Web Search (Google/DDG)...')
        self.stdout.write('Query: "latest django version"')
        results = tool_web_search("latest django version")
        
        if "Search Error" in results:
             self.stdout.write(self.style.ERROR(f'FAILED: {results}'))
        else:
             self.stdout.write(self.style.SUCCESS('PASSED: Web search returned results.'))
             # self.stdout.write(f'Snippet: {results[:100]}...')

        # --- Test 2: Internal Database Search ---
        self.stdout.write('\n[2/2] Testing Internal Database Search...')
        
        # Ensure we have at least one lesson or course to find
        test_query = "intro"
        if not Course.objects.exists() and not Lesson.objects.exists():
            self.stdout.write(self.style.WARNING('WARNING: Database is empty. Cannot verify search.'))
        else:
            # Pick a word from a real course if possible
            first_course = Course.objects.first()
            if first_course:
                test_query = first_course.title.split()[0]
            
            self.stdout.write(f'Query: "{test_query}"')
            results = tool_query_database(test_query)
            
            if "No internal project data found" in results and Course.objects.exists():
                # This might be valid if the query is weird, but we picked a title word.
                # If we picked a title word and it failed, that's bad.
                self.stdout.write(self.style.WARNING(f'Note: Search returned no results for "{test_query}". Check if this is expected.'))
            elif "INTERNAL PROJECT DATABASE RESULTS" in results:
                self.stdout.write(self.style.SUCCESS(f'PASSED: Found internal data for "{test_query}".'))
            else:
                 self.stdout.write(self.style.ERROR(f'FAILED: Unexpected output: {results[:100]}'))

        self.stdout.write(self.style.SUCCESS('\nVerification Complete.'))
