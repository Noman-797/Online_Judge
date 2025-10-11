import os
import subprocess
import tempfile
import time
import signal
import psutil
import shutil
from django.conf import settings
from submissions.models import Submission
from problems.models import TestCase


class CodeEvaluator:
    def __init__(self, submission):
        self.submission = submission
        self.problem = submission.problem
        self.temp_dir = settings.JUDGE_TEMP_DIR
        self.time_limit = self.problem.time_limit
        self.memory_limit = self.problem.memory_limit * 1024 * 1024  # Convert MB to bytes
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Compiler flags
        self.gcc_flags = ['-O2', '-Wall', '-Wextra', '-std=c11']
        self.gpp_flags = ['-O2', '-Wall', '-Wextra', '-std=c++17']
        self.python_cmd = ['python', '-u']

    
    def evaluate(self, sample_only=False):
        """Main evaluation function"""
        try:
            # Compile the code
            if not self.compile_code():
                return
            
            # Run test cases
            self.run_test_cases(sample_only=sample_only)
            
        except Exception as e:
            self.submission.verdict = 'RE'
            self.submission.runtime_error = str(e)
            self.submission.save()
        finally:
            self.cleanup()
    
    def compile_code(self):
        """Compile C/C++/Python/Java code"""
        # Handle Python
        if self.submission.language == 'python':
            source_file = os.path.join(self.temp_dir, f"solution_{self.submission.id}.py")
            try:
                with open(source_file, 'w', encoding='utf-8') as f:
                    if len(self.submission.code) > 100000:
                        self.submission.verdict = 'CE'
                        self.submission.compilation_error = 'Code size exceeds limit (100KB)'
                        self.submission.save()
                        return False
                    f.write(self.submission.code)
                self.executable = source_file
                return True
            except Exception as e:
                self.submission.verdict = 'CE'
                self.submission.compilation_error = f'Error writing source file: {str(e)}'
                self.submission.save()
                return False
        

        
        # Create temporary files for C/C++
        if self.submission.language == 'c':
            source_file = os.path.join(self.temp_dir, f"solution_{self.submission.id}.c")
            compiler = 'gcc'
            flags = self.gcc_flags
        else:  # cpp
            source_file = os.path.join(self.temp_dir, f"solution_{self.submission.id}.cpp")
            compiler = 'g++'
            flags = self.gpp_flags
        
        executable = os.path.join(self.temp_dir, f"solution_{self.submission.id}")
        if os.name == 'nt':  # Windows
            executable += '.exe'
        
        # Write code to file with security checks
        try:
            with open(source_file, 'w', encoding='utf-8') as f:
                # Basic security: limit code size
                if len(self.submission.code) > 100000:  # 100KB limit
                    self.submission.verdict = 'CE'
                    self.submission.compilation_error = 'Code size exceeds limit (100KB)'
                    self.submission.save()
                    return False
                f.write(self.submission.code)
        except Exception as e:
            self.submission.verdict = 'CE'
            self.submission.compilation_error = f'Error writing source file: {str(e)}'
            self.submission.save()
            return False
        
        # Enhanced compile command with security flags
        compile_cmd = [compiler] + flags + [source_file, '-o', executable]
        
        try:
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=5,  # Reduced timeout for faster processing
                cwd=self.temp_dir
            )
            
            if result.returncode != 0:
                self.submission.verdict = 'CE'
                # Clean up compilation error message
                error_msg = result.stderr.strip()
                if len(error_msg) > 2000:  # Limit error message size
                    error_msg = error_msg[:2000] + '...'
                # Remove file paths from error message
                error_msg = self._clean_error_message(error_msg)
                self.submission.compilation_error = error_msg
                self.submission.save()
                return False
            
            # Check if executable was created
            if not os.path.exists(executable):
                self.submission.verdict = 'CE'
                self.submission.compilation_error = 'Executable not generated'
                self.submission.save()
                return False
            
            self.executable = executable
            return True
            
        except subprocess.TimeoutExpired:
            self.submission.verdict = 'CE'
            self.submission.compilation_error = 'Compilation timeout (5s exceeded)'
            self.submission.save()
            return False
        except Exception as e:
            self.submission.verdict = 'CE'
            self.submission.compilation_error = f'Compilation error: {str(e)}'
            self.submission.save()
            return False
    
    def run_test_cases(self, sample_only=False):
        """Run code against test cases"""
        if sample_only:
            # Only run sample test cases (is_sample=True) + problem's sample_input/output
            test_cases = list(TestCase.objects.filter(problem=self.problem, is_sample=True))
            
            # Add problem's sample_input/output as a test case if exists
            if self.problem.sample_input and self.problem.sample_output:
                from types import SimpleNamespace
                sample_case = SimpleNamespace()
                sample_case.input_data = self.problem.sample_input
                sample_case.expected_output = self.problem.sample_output
                test_cases.insert(0, sample_case)  # Add as first test case
        else:
            # Run all test cases + problem's sample_input/output
            test_cases = list(TestCase.objects.filter(problem=self.problem))
            
            # Add problem's sample_input/output as a test case if exists
            if self.problem.sample_input and self.problem.sample_output:
                from types import SimpleNamespace
                sample_case = SimpleNamespace()
                sample_case.input_data = self.problem.sample_input
                sample_case.expected_output = self.problem.sample_output
                test_cases.insert(0, sample_case)  # Add as first test case
            
        total_cases = len(test_cases)
        passed_cases = 0
        max_time = 0
        max_memory = 0
        
        for test_case in test_cases:
            verdict, exec_time, memory = self.run_single_test(test_case)
            
            if verdict == 'AC':
                passed_cases += 1
            else:
                # If any test case fails, set the verdict and break
                self.submission.verdict = verdict
                break
            
            max_time = max(max_time, exec_time)
            max_memory = max(max_memory, memory)
        
        # If all test cases passed
        if passed_cases == total_cases:
            self.submission.verdict = 'AC'
        
        self.submission.test_cases_passed = passed_cases
        self.submission.total_test_cases = total_cases
        self.submission.execution_time = max_time
        self.submission.memory_used = max_memory
        self.submission.save()
    
    def run_single_test(self, test_case):
        """Run code against a single test case with enhanced monitoring"""
        input_file = os.path.join(self.temp_dir, f"input_{self.submission.id}.txt")
        output_file = os.path.join(self.temp_dir, f"output_{self.submission.id}.txt")
        error_file = os.path.join(self.temp_dir, f"error_{self.submission.id}.txt")
        
        try:
            # Write input to file
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(test_case.input_data)
            
            # Run the executable with enhanced monitoring
            start_time = time.time()
            max_memory = 0
            
            with open(input_file, 'r') as input_f, \
                 open(output_file, 'w') as output_f, \
                 open(error_file, 'w') as error_f:
                
                # Different execution for different languages
                if self.submission.language == 'python':
                    cmd = self.python_cmd + [self.executable]
                else:
                    cmd = [self.executable]
                
                process = subprocess.Popen(
                    cmd,
                    stdin=input_f,
                    stdout=output_f,
                    stderr=error_f,
                    text=True,
                    cwd=self.temp_dir
                )
                
                try:
                    # Monitor process with psutil for better resource tracking
                    ps_process = psutil.Process(process.pid)
                    
                    while process.poll() is None:
                        try:
                            # Check memory usage
                            memory_info = ps_process.memory_info()
                            current_memory = memory_info.rss  # Resident Set Size
                            max_memory = max(max_memory, current_memory)
                            
                            # Check memory limit
                            if current_memory > self.memory_limit:
                                process.kill()
                                return 'MLE', time.time() - start_time, current_memory // 1024  # Convert to KB
                            
                            # Check time limit
                            if time.time() - start_time > self.time_limit:
                                process.kill()
                                return 'TLE', self.time_limit, max_memory // 1024
                            
                            time.sleep(0.005)  # Smaller delay for faster processing
                            
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            break
                    
                    # Wait for process to complete
                    process.wait(timeout=0.1)
                    exec_time = time.time() - start_time
                    
                    if process.returncode != 0:
                        # Read error output
                        with open(error_file, 'r') as f:
                            error_output = f.read().strip()
                        return 'RE', exec_time, max_memory // 1024
                    
                    # Check output
                    with open(output_file, 'r', encoding='utf-8') as f:
                        actual_output = f.read().strip()
                    
                    expected_output = self._strip_html_tags(test_case.expected_output).strip()
                    
                    # Enhanced output comparison with detailed logging
                    if self._compare_outputs(actual_output, expected_output):
                        return 'AC', exec_time, max_memory // 1024
                    else:
                        # Check for presentation error
                        if self._is_presentation_error(actual_output, expected_output):
                            return 'PE', exec_time, max_memory // 1024
                        else:
                            # Debug: Store actual vs expected for debugging
                            self.submission.runtime_error = f"Expected: '{expected_output}' | Got: '{actual_output}'"
                            return 'WA', exec_time, max_memory // 1024
                        
                except subprocess.TimeoutExpired:
                    process.kill()
                    return 'TLE', self.time_limit, max_memory // 1024
                except Exception as e:
                    if process.poll() is None:
                        process.kill()
                    return 'RE', time.time() - start_time, max_memory // 1024
                    
        except Exception as e:
            return 'RE', 0, 0
    
    def _compare_outputs(self, actual, expected):
        """Enhanced output comparison with strict matching"""
        # Strategy 1: Exact match (most strict)
        if actual == expected:
            return True
        
        # Strategy 2: Only normalize line endings (Windows vs Unix)
        actual_normalized = actual.replace('\r\n', '\n').replace('\r', '\n')
        expected_normalized = expected.replace('\r\n', '\n').replace('\r', '\n')
        if actual_normalized == expected_normalized:
            return True
        
        # No other automatic corrections - let PE detection handle whitespace issues
        return False
    
    def _is_presentation_error(self, actual, expected):
        """Check if the difference is only in presentation (whitespace/formatting)"""
        import re
        
        # Normalize line endings first
        actual_norm = actual.replace('\r\n', '\n').replace('\r', '\n')
        expected_norm = expected.replace('\r\n', '\n').replace('\r', '\n')
        
        # If already equal after line ending normalization, not a PE
        if actual_norm == expected_norm:
            return False
        
        # Remove all whitespace and compare content
        actual_clean = re.sub(r'\s+', '', actual_norm)
        expected_clean = re.sub(r'\s+', '', expected_norm)
        
        # If content is same after removing all whitespace, it's presentation error
        if actual_clean == expected_clean and actual_clean != '':
            return True
        
        return False
    
    def _strip_html_tags(self, text):
        """Remove HTML tags from text"""
        import re
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        return clean_text
    
    def _clean_error_message(self, error_msg):
        """Remove file paths and clean up error messages"""
        import re
        
        # Remove Windows/Unix file paths
        error_msg = re.sub(r'[A-Za-z]:\\[^\s:]+\\solution_\d+\.(cpp|c|py):', '', error_msg)
        error_msg = re.sub(r'/[^\s:]+/solution_\d+\.(cpp|c|py):', '', error_msg)
        
        # Remove temp directory references
        error_msg = re.sub(r'solution_\d+\.(cpp|c|py):', '', error_msg)
        
        # Clean up multiple spaces and newlines
        error_msg = re.sub(r'\s+', ' ', error_msg).strip()
        
        return error_msg
    
    def cleanup(self):
        """Enhanced cleanup of temporary files"""
        patterns = [
            f"solution_{self.submission.id}",

            f"input_{self.submission.id}.txt",
            f"output_{self.submission.id}.txt",
            f"error_{self.submission.id}.txt"
        ]
        
        for pattern in patterns:
            for file in os.listdir(self.temp_dir):
                if file.startswith(pattern):
                    try:
                        file_path = os.path.join(self.temp_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception:
                        pass  # Ignore cleanup errors


def evaluate_submission(submission):
    """Main function to evaluate a submission"""
    evaluator = CodeEvaluator(submission)
    evaluator.evaluate()
    
    return {
        'verdict': submission.verdict,
        'execution_time': submission.execution_time,
        'memory_used': submission.memory_used,
        'compilation_error': submission.compilation_error,
        'runtime_error': submission.runtime_error,
        'test_cases_passed': submission.test_cases_passed,
        'total_test_cases': submission.total_test_cases
    }