import os
import sys
import subprocess
import tempfile
import shutil
import signal
import time
import psutil
from pathlib import Path
from .windows_security import WindowsSecurityManager

# Windows compatibility
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

class SecureCodeEvaluator:
    """Enhanced security code evaluator without Docker"""
    
    def __init__(self):
        self.temp_dir = None
        self.blocked_imports = {
            'os', 'sys', 'subprocess', 'shutil', 'tempfile', 
            'socket', 'urllib', 'requests', 'http', 'ftplib',
            'smtplib', 'telnetlib', 'webbrowser', 'ctypes',
            '__import__', 'eval', 'exec', 'compile', 'open'
        }
        
    def create_secure_environment(self):
        """Create isolated temporary directory"""
        self.temp_dir = tempfile.mkdtemp(prefix='judge_')
        os.chmod(self.temp_dir, 0o700)  # Only owner can access
        return self.temp_dir
    
    def cleanup_environment(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def validate_code_security(self, code, language):
        """Check for dangerous code patterns"""
        dangerous_patterns = [
            'import os', 'import sys', 'import subprocess',
            'import socket', 'import urllib', 'import requests',
            'import shutil', 'import tempfile', 'import ctypes',
            '__import__', 'eval(', 'exec(', 'compile(',
            'open(', 'file(', 'raw_input(',
            'while True:', 'for i in range(999999', 'range(1000000',
        ]
        
        if language in ['python', 'py']:
            for pattern in dangerous_patterns:
                if pattern in code.lower():
                    return False, f"Dangerous pattern detected: {pattern}"
        
        # Check for infinite loops (basic detection)
        if 'while True' in code or 'while 1' in code:
            return False, "Infinite loop detected"
            
        return True, "Code appears safe"
    
    def set_resource_limits(self, time_limit=5, memory_limit=128):
        """Set process resource limits (Unix only)"""
        def limit_resources():
            if HAS_RESOURCE:
                try:
                    # CPU time limit
                    resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit + 1))
                    
                    # Memory limit (in bytes)
                    memory_bytes = memory_limit * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
                    
                    # File size limit (prevent large file creation)
                    resource.setrlimit(resource.RLIMIT_FSIZE, (1024*1024, 1024*1024))  # 1MB
                    
                    # Number of processes limit
                    resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
                    
                    # Disable core dumps
                    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                except:
                    pass  # Ignore errors on Windows
            
        return limit_resources
    
    def compile_code(self, code, language, filename):
        """Compile code with security restrictions"""
        try:
            if language == 'cpp':
                compile_cmd = [
                    'g++', '-std=c++17', '-O2', '-Wall', '-Wextra',
                    '-static', '-o', f'{filename}.exe', f'{filename}.cpp'
                ]
            elif language == 'c':
                compile_cmd = [
                    'gcc', '-std=c11', '-O2', '-Wall', '-Wextra',
                    '-static', '-o', f'{filename}.exe', f'{filename}.c'
                ]
            else:
                return True, ""  # No compilation needed for Python
            
            # Run compilation with limits
            if os.name == 'posix':  # Unix/Linux
                process = subprocess.Popen(
                    compile_cmd,
                    cwd=self.temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=self.set_resource_limits(time_limit=10, memory_limit=256)
                )
            else:  # Windows
                process = subprocess.Popen(
                    compile_cmd,
                    cwd=self.temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            stdout, stderr = process.communicate(timeout=10)
            
            if process.returncode != 0:
                return False, stderr.decode('utf-8', errors='ignore')
            
            return True, ""
            
        except subprocess.TimeoutExpired:
            process.kill()
            return False, "Compilation timeout"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"
    
    def execute_code(self, language, filename, input_data, time_limit=5, memory_limit=128):
        """Execute code with enhanced security"""
        try:
            # Prepare execution command
            if language == 'cpp' or language == 'c':
                if os.name == 'nt':  # Windows
                    cmd = [f'{filename}.exe']  # Relative path since we set cwd
                else:  # Unix/Linux
                    cmd = [f'./{filename}.exe']
            elif language == 'python':
                cmd = ['python', f'{filename}.py']  # Use 'python' on Windows
            else:
                return 'RE', 0, 0, "Unsupported language"
            
            # Start execution with security limits
            start_time = time.time()
            
            if os.name == 'posix':  # Unix/Linux
                process = subprocess.Popen(
                    cmd,
                    cwd=self.temp_dir,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=self.set_resource_limits(time_limit, memory_limit)
                )
            else:  # Windows
                process = subprocess.Popen(
                    cmd,
                    cwd=self.temp_dir,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Use Windows-specific monitoring on Windows
            if os.name == 'nt':  # Windows
                return WindowsSecurityManager.secure_execute(
                    cmd, self.temp_dir, input_data, time_limit, memory_limit
                )
            
            # Unix/Linux monitoring
            try:
                stdout, stderr = process.communicate(
                    input=input_data.encode('utf-8') if input_data else None,
                    timeout=time_limit + 1
                )
                
                execution_time = time.time() - start_time
                
                # Get memory usage (approximate)
                memory_used = 0
                try:
                    proc = psutil.Process(process.pid)
                    memory_used = proc.memory_info().rss // 1024  # KB
                except:
                    pass
                
                # Check return code
                if process.returncode != 0:
                    if process.returncode == -signal.SIGKILL:
                        return 'TLE', execution_time, memory_used, "Time limit exceeded"
                    elif process.returncode == -signal.SIGSEGV:
                        return 'RE', execution_time, memory_used, "Segmentation fault"
                    else:
                        error_msg = stderr.decode('utf-8', errors='ignore')
                        return 'RE', execution_time, memory_used, error_msg
                
                output = stdout.decode('utf-8', errors='ignore')
                return 'OK', execution_time, memory_used, output
                
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return 'TLE', time_limit, 0, "Time limit exceeded"
                
        except Exception as e:
            return 'RE', 0, 0, f"Execution error: {str(e)}"
    
    def evaluate_submission(self, code, language, test_cases, time_limit=5, memory_limit=128):
        """Main evaluation function with enhanced security"""
        try:
            # Create secure environment
            self.create_secure_environment()
            
            # Validate code security
            is_safe, safety_msg = self.validate_code_security(code, language)
            if not is_safe:
                return {
                    'verdict': 'CE',
                    'compilation_error': f"Security violation: {safety_msg}",
                    'test_cases_passed': 0,
                    'total_test_cases': len(test_cases)
                }
            
            # Write code to file
            filename = 'solution'
            if language == 'cpp':
                code_file = f'{filename}.cpp'
            elif language == 'c':
                code_file = f'{filename}.c'
            elif language == 'python':
                code_file = f'{filename}.py'
            
            code_path = os.path.join(self.temp_dir, code_file)
            with open(code_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Compile if needed
            compile_success, compile_error = self.compile_code(code, language, filename)
            if not compile_success:
                return {
                    'verdict': 'CE',
                    'compilation_error': compile_error,
                    'test_cases_passed': 0,
                    'total_test_cases': len(test_cases)
                }
            
            # Run test cases
            passed = 0
            total_time = 0
            max_memory = 0
            
            for i, test_case in enumerate(test_cases):
                status, exec_time, memory, output = self.execute_code(
                    language, filename, test_case.input_data, time_limit, memory_limit
                )
                
                total_time += exec_time
                max_memory = max(max_memory, memory)
                
                if status == 'TLE':
                    return {
                        'verdict': 'TLE',
                        'execution_time': exec_time,
                        'memory_used': memory,
                        'test_cases_passed': passed,
                        'total_test_cases': len(test_cases)
                    }
                elif status == 'RE':
                    return {
                        'verdict': 'RE',
                        'runtime_error': output,
                        'execution_time': exec_time,
                        'memory_used': memory,
                        'test_cases_passed': passed,
                        'total_test_cases': len(test_cases)
                    }
                elif status == 'OK':
                    # Check output
                    expected = test_case.expected_output.strip()
                    actual = output.strip()
                    
                    if expected == actual:
                        passed += 1
                    else:
                        return {
                            'verdict': 'WA',
                            'execution_time': total_time / len(test_cases),
                            'memory_used': max_memory,
                            'test_cases_passed': passed,
                            'total_test_cases': len(test_cases)
                        }
            
            # All test cases passed
            return {
                'verdict': 'AC',
                'execution_time': total_time / len(test_cases),
                'memory_used': max_memory,
                'test_cases_passed': passed,
                'total_test_cases': len(test_cases)
            }
            
        finally:
            # Always cleanup
            self.cleanup_environment()