import os
import sys
import subprocess
import tempfile
import shutil
import time
import psutil
from pathlib import Path
from django.utils._os import safe_join

class MultiLanguageEvaluator:
    """Multi-language code evaluator with enhanced security"""
    
    def __init__(self):
        self.temp_dir = None
        self.language_configs = {
            'c': {
                'extension': '.c',
                'compile_cmd': ['gcc', '-std=c11', '-O2', '-Wall', '-o', '{exe}', '{source}'],
                'run_cmd': ['{exe}'],
                'timeout': 10
            },
            'cpp': {
                'extension': '.cpp', 
                'compile_cmd': ['g++', '-std=c++17', '-O2', '-Wall', '-o', '{exe}', '{source}'],
                'run_cmd': ['{exe}'],
                'timeout': 10
            },
            'python': {
                'extension': '.py',
                'compile_cmd': None,  # No compilation needed
                'run_cmd': ['python', '{source}'],
                'timeout': 5
            }
        }
        
        # Security patterns
        self.dangerous_patterns = {
            'python': [
                'import os', 'import sys', 'import subprocess',
                'import socket', 'import urllib', 'import requests',
                '__import__', 'eval(', 'exec(', 'compile(',
                'open(', 'file(', 'while True:', 'range(1000000'
            ],
            'c': [
                '#include <stdlib.h>', 'system(', 'exec(',
                'while(1)', 'for(;;)', 'malloc(999999'
            ],
            'cpp': [
                '#include <cstdlib>', 'system(', 'exec(',
                'while(true)', 'while(1)', 'for(;;)', 'new char[999999'
            ]
        }
    
    def create_secure_environment(self):
        """Create isolated temporary directory"""
        self.temp_dir = tempfile.mkdtemp(prefix='judge_')
        os.chmod(self.temp_dir, 0o700)
        return self.temp_dir
    
    def cleanup_environment(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def validate_code_security(self, code, language):
        """Check for dangerous code patterns"""
        if language not in self.dangerous_patterns:
            return True, "Language not in security check"
        
        patterns = self.dangerous_patterns[language]
        code_lower = code.lower()
        
        for pattern in patterns:
            if pattern.lower() in code_lower:
                return False, f"Dangerous pattern detected: {pattern}"
        
        return True, "Code appears safe"
    
    def compile_code(self, code, language, base_filename):
        """Compile code if needed"""
        config = self.language_configs[language]
        
        # Write source file
        source_file = base_filename + config['extension']
        
        source_path = safe_join(self.temp_dir, source_file)
        if not source_path or not source_path.startswith(self.temp_dir):
            return False, "Invalid file path", None
        
        with open(source_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # No compilation needed for Python
        if config['compile_cmd'] is None:
            return True, "", source_file
        
        # Prepare compilation command
        exe_name = base_filename + ('.exe' if os.name == 'nt' else '')
        
        compile_cmd = []
        for part in config['compile_cmd']:
            if '{exe}' in part:
                compile_cmd.append(part.format(exe=exe_name))
            elif '{source}' in part:
                compile_cmd.append(part.format(source=source_file))
            else:
                compile_cmd.append(part)
        
        try:
            # Run compilation
            process = subprocess.Popen(
                compile_cmd,
                cwd=self.temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(timeout=config['timeout'])
            
            if process.returncode != 0:
                return False, stderr.decode('utf-8', errors='ignore'), None
            
            return True, "", exe_name
            
        except subprocess.TimeoutExpired:
            process.kill()
            return False, "Compilation timeout", None
        except Exception as e:
            return False, f"Compilation error: {str(e)}", None
    
    def execute_code(self, language, executable, input_data, time_limit=5, memory_limit=128):
        """Execute code with security monitoring"""
        config = self.language_configs[language]
        
        # Prepare run command
        run_cmd = []
        for part in config['run_cmd']:
            if '{exe}' in part:
                if language in ['c', 'cpp']:
                    # Use full path for C/C++ executables
                    exe_path = os.path.join(self.temp_dir, executable)
                    run_cmd.append(exe_path)
                else:
                    run_cmd.append(part.format(exe=executable))
            elif '{source}' in part:
                run_cmd.append(part.format(source=executable))

            else:
                run_cmd.append(part)
        
        start_time = time.time()
        
        try:
            process = subprocess.Popen(
                run_cmd,
                cwd=self.temp_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Execute with timeout
            stdout, stderr = process.communicate(
                input=input_data.encode('utf-8') if input_data else None,
                timeout=time_limit
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
                error_msg = stderr.decode('utf-8', errors='ignore')
                return 'RE', execution_time, memory_used, error_msg
            
            output = stdout.decode('utf-8', errors='ignore')
            return 'OK', execution_time, memory_used, output
            
        except subprocess.TimeoutExpired:
            try:
                process.kill()
                process.wait()
            except:
                pass
            return 'TLE', time_limit, 0, "Time limit exceeded"
        except Exception as e:
            return 'RE', 0, 0, f"Execution error: {str(e)}"
    
    def evaluate_submission(self, code, language, test_cases, time_limit=5, memory_limit=128):
        """Main evaluation function"""
        try:
            # Validate language
            if language not in self.language_configs:
                return {
                    'verdict': 'CE',
                    'compilation_error': f"Unsupported language: {language}",
                    'test_cases_passed': 0,
                    'total_test_cases': len(test_cases)
                }
            
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
            
            # Compile code
            compile_success, compile_error, executable = self.compile_code(code, language, 'solution')
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
            
            for test_case in test_cases:
                status, exec_time, memory, output = self.execute_code(
                    language, executable, test_case.input_data, time_limit, memory_limit
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