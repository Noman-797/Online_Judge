"""
Windows-specific security implementations
Since Windows doesn't have resource module, we use alternative methods
"""

import subprocess
import threading
import time
import psutil
import os

class WindowsSecurityManager:
    """Windows-specific security manager"""
    
    @staticmethod
    def kill_process_tree(pid):
        """Kill process and all its children"""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.kill()
                except:
                    pass
            try:
                parent.kill()
            except:
                pass
        except:
            pass
    
    @staticmethod
    def monitor_process(process, time_limit, memory_limit):
        """Monitor process for time and memory limits"""
        start_time = time.time()
        
        while process.poll() is None:
            try:
                # Check time limit
                if time.time() - start_time > time_limit:
                    WindowsSecurityManager.kill_process_tree(process.pid)
                    return 'TLE', time_limit, 0
                
                # Check memory limit
                try:
                    proc = psutil.Process(process.pid)
                    memory_mb = proc.memory_info().rss / (1024 * 1024)
                    if memory_mb > memory_limit:
                        WindowsSecurityManager.kill_process_tree(process.pid)
                        return 'MLE', time.time() - start_time, memory_mb
                except:
                    pass
                
                time.sleep(0.1)  # Check every 100ms
                
            except:
                break
        
        # Process finished normally
        execution_time = time.time() - start_time
        try:
            proc = psutil.Process(process.pid)
            memory_used = proc.memory_info().rss / 1024  # KB
        except:
            memory_used = 0
            
        return 'OK', execution_time, memory_used
    
    @staticmethod
    def secure_execute(cmd, cwd, input_data, time_limit, memory_limit):
        """Execute command with Windows security monitoring"""
        start_time = time.time()
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Communicate with timeout
            try:
                stdout, stderr = process.communicate(
                    input=input_data.encode('utf-8') if input_data else None,
                    timeout=time_limit
                )
                
                execution_time = time.time() - start_time
                
                # Get memory usage
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
                WindowsSecurityManager.kill_process_tree(process.pid)
                return 'TLE', time_limit, 0, "Time limit exceeded"
                
        except Exception as e:
            return 'RE', 0, 0, f"Execution error: {str(e)}"