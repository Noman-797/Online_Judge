import threading
import time
from queue import Queue, Empty
from django.utils import timezone
from submissions.models import Submission
from .evaluator import evaluate_submission
from .secure_evaluator import SecureCodeEvaluator
from .multi_language_evaluator import MultiLanguageEvaluator

class SubmissionQueue:
    def __init__(self, max_workers=5):
        self.queue = Queue()
        self.max_workers = max_workers
        self.active_workers = 0
        self.workers = []
        self.running = False
        self.lock = threading.Lock()
    
    def start(self):
        """Start the queue processing"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop the queue processing"""
        self.running = False
    
    def add_submission(self, submission_id):
        """Add submission to queue"""
        self.queue.put(submission_id)
    
    def get_queue_position(self, submission_id):
        """Get position of submission in queue"""
        try:
            submission = Submission.objects.get(id=submission_id)
            if submission.verdict not in ['QUEUED']:
                return 0
            
            # Count queued submissions before this one
            position = Submission.objects.filter(
                verdict='QUEUED',
                submitted_at__lt=submission.submitted_at
            ).count() + 1
            
            return position
        except Submission.DoesNotExist:
            return 0
    
    def get_queue_size(self):
        """Get current queue size"""
        return Submission.objects.filter(verdict='QUEUED').count()
    
    def _worker(self):
        """Worker thread to process submissions"""
        while self.running:
            try:
                submission_id = self.queue.get(timeout=1)
                
                with self.lock:
                    self.active_workers += 1
                
                try:
                    self._process_submission(submission_id)
                finally:
                    with self.lock:
                        self.active_workers -= 1
                    self.queue.task_done()
                    
            except Empty:
                continue
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Worker error processing submission {submission_id}: {e}")
    
    def _process_submission(self, submission_id):
        """Process a single submission"""
        try:
            submission = Submission.objects.get(id=submission_id)
            
            # Update status to judging
            submission.verdict = 'JUDGING'
            submission.save()
            
            # Use multi-language evaluator
            evaluator = MultiLanguageEvaluator()
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
            submission.judged_at = timezone.now()
            submission.save()
            
        except Submission.DoesNotExist:
            pass
        except Exception as e:
            # Mark submission as error
            try:
                submission = Submission.objects.get(id=submission_id)
                submission.verdict = 'RE'
                submission.runtime_error = f'System error: {str(e)}'
                submission.judged_at = timezone.now()
                submission.save()
            except Exception as recovery_error:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to update submission {submission_id} after error: {recovery_error}")

# Global queue instance - adjust based on hosting platform
# PythonAnywhere: 2-3 workers (threading limitations)
# Railway/Render: 10-20 workers
# DigitalOcean/AWS: 20-50+ workers
submission_queue = SubmissionQueue(max_workers=2)