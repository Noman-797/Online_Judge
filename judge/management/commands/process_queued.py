from django.core.management.base import BaseCommand
from submissions.models import Submission
from judge.multi_language_evaluator import MultiLanguageEvaluator


class Command(BaseCommand):
    help = 'Process all queued submissions with direct evaluation'

    def handle(self, *args, **options):
        queued_submissions = Submission.objects.filter(verdict='QUEUED')
        count = queued_submissions.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No queued submissions found.'))
            return
        
        self.stdout.write(f'Processing {count} queued submissions...')
        
        evaluator = MultiLanguageEvaluator()
        processed = 0
        
        for submission in queued_submissions:
            try:
                test_cases = submission.problem.test_cases.all()
                
                result = evaluator.evaluate_submission(
                    code=submission.code,
                    language=submission.language,
                    test_cases=test_cases,
                    time_limit=submission.problem.time_limit,
                    memory_limit=submission.problem.memory_limit
                )
                
                # Update submission with result
                submission.verdict = result['verdict']
                submission.execution_time = result.get('execution_time')
                submission.memory_used = result.get('memory_used')
                submission.compilation_error = result.get('compilation_error', '')
                submission.runtime_error = result.get('runtime_error', '')
                submission.test_cases_passed = result.get('test_cases_passed', 0)
                submission.total_test_cases = result.get('total_test_cases', 0)
                submission.save()
                
                processed += 1
                self.stdout.write(f'Processed submission #{submission.id} - {submission.verdict}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing submission #{submission.id}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {processed}/{count} submissions.')
        )