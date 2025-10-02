from django.core.management.base import BaseCommand
from django.utils import timezone
from submissions.models import Submission

class Command(BaseCommand):
    help = 'Process queued submissions manually (PythonAnywhere compatible)'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Number of submissions to process')

    def handle(self, *args, **options):
        limit = options['limit']
        
        queued_submissions = Submission.objects.filter(verdict='QUEUED').order_by('submitted_at')[:limit]
        
        if not queued_submissions:
            self.stdout.write(self.style.SUCCESS('No queued submissions found.'))
            return
        
        processed = 0
        failed = 0
        
        for submission in queued_submissions:
            self.stdout.write(f'Processing submission {submission.id} by {submission.user.username}...')
            
            try:
                # Process submission directly
                from judge.evaluator import CodeEvaluator
                evaluator = CodeEvaluator(submission)
                submission.verdict = 'JUDGING'
                submission.save()
                
                evaluator.evaluate()
                submission.judged_at = timezone.now()
                submission.save()
                
                success = submission.verdict != 'RE'
                if success:
                    processed += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Submission {submission.id}: {submission.verdict}'))
                else:
                    failed += 1
                    self.stdout.write(self.style.ERROR(f'✗ Submission {submission.id} failed'))
            except Exception as e:
                failed += 1
                submission.verdict = 'RE'
                submission.runtime_error = str(e)
                submission.judged_at = timezone.now()
                submission.save()
                self.stdout.write(self.style.ERROR(f'✗ Submission {submission.id} error: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nProcessed: {processed}, Failed: {failed}'))