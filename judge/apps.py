from django.apps import AppConfig

class JudgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'judge'
    
    def ready(self):
        # Skip queue startup during migrations
        import sys
        if any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'collectstatic']):
            return
            
        try:
            from django.db import connection
            # Test database connection
            connection.ensure_connection()
            
            from .queue_manager import submission_queue
            submission_queue.start()
            
            from submissions.models import Submission
            queued_submissions = Submission.objects.filter(verdict='QUEUED').order_by('submitted_at')
            for submission in queued_submissions:
                submission_queue.add_submission(submission.id)
        except Exception:
            pass