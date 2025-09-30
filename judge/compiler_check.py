#!/usr/bin/env python3
"""
GCC Compiler Checker for Online Judge System
Verifies that GCC and G++ are properly installed and configured
"""

import subprocess
import sys
import os
from pathlib import Path

def check_compiler(compiler_name, test_code, file_extension):
    """Check if a compiler is available and working"""
    print(f"\n{'='*50}")
    print(f"Checking {compiler_name.upper()} Compiler")
    print(f"{'='*50}")
    
    # Check if compiler is in PATH
    try:
        result = subprocess.run([compiler_name, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[OK] {compiler_name} is installed")
            print(f"Version: {result.stdout.split()[0]} {result.stdout.split()[1] if len(result.stdout.split()) > 1 else ''}")
        else:
            print(f"[ERROR] {compiler_name} version check failed")
            return False
    except FileNotFoundError:
        print(f"[ERROR] {compiler_name} not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {compiler_name} version check timed out")
        return False
    
    # Test compilation
    temp_dir = Path("temp_compiler_test")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Write test code
        test_file = temp_dir / f"test.{file_extension}"
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        # Compile
        executable = temp_dir / "test"
        if os.name == 'nt':  # Windows
            executable = executable.with_suffix('.exe')
        
        compile_cmd = [compiler_name, str(test_file), '-o', str(executable)]
        if compiler_name == 'g++':
            compile_cmd.extend(['-std=c++17', '-O2'])
        else:
            compile_cmd.extend(['-std=c11', '-O2'])
        
        result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"[OK] {compiler_name} compilation successful")
            
            # Test execution
            if executable.exists():
                exec_result = subprocess.run([str(executable)], 
                                           capture_output=True, text=True, timeout=5)
                if exec_result.returncode == 0 and exec_result.stdout.strip() == "Hello, World!":
                    print(f"[OK] {compiler_name} execution successful")
                    print(f"Output: {exec_result.stdout.strip()}")
                    return True
                else:
                    print(f"[ERROR] {compiler_name} execution failed")
                    print(f"Expected: Hello, World!")
                    print(f"Got: {exec_result.stdout.strip()}")
                    return False
            else:
                print(f"[ERROR] {compiler_name} executable not created")
                return False
        else:
            print(f"[ERROR] {compiler_name} compilation failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {compiler_name} test failed: {str(e)}")
        return False
    finally:
        # Cleanup
        try:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except:
            pass
    
    return False

def check_python():
    """Check if Python is available and working"""
    print(f"\n{'='*50}")
    print(f"Checking PYTHON Interpreter")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(['python', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[OK] Python is installed")
            print(f"Version: {result.stdout.strip()}")
        else:
            print(f"[ERROR] Python version check failed")
            return False
    except FileNotFoundError:
        print(f"[ERROR] Python not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Python version check timed out")
        return False
    
    # Test execution
    temp_dir = Path("temp_python_test")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        test_file = temp_dir / "test.py"
        with open(test_file, 'w') as f:
            f.write('print("Hello, World!")')
        
        result = subprocess.run(['python', str(test_file)], 
                               capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip() == "Hello, World!":
            print(f"[OK] Python execution successful")
            print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"[ERROR] Python execution failed")
            print(f"Expected: Hello, World!")
            print(f"Got: {result.stdout.strip()}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Python test failed: {str(e)}")
        return False
    finally:
        try:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except:
            pass
    
    return False

def check_java():
    """Check if Java is available and working"""
    print(f"\n{'='*50}")
    print(f"Checking JAVA Compiler/Runtime")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(['javac', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[OK] Java compiler is installed")
            print(f"Version: {result.stderr.strip()}")
        else:
            print(f"[ERROR] Java compiler check failed")
            return False
    except FileNotFoundError:
        print(f"[ERROR] Java compiler not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Java compiler check timed out")
        return False
    
    # Test compilation and execution
    temp_dir = Path("temp_java_test")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        test_file = temp_dir / "HelloWorld.java"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.print("Hello, World!");\n    }\n}')
        
        # Compile
        result = subprocess.run(['javac', 'HelloWorld.java'], 
                               capture_output=True, text=True, timeout=10, cwd=temp_dir)
        
        if result.returncode != 0:
            print(f"[ERROR] Java compilation failed")
            print(f"Stderr: {result.stderr}")
            print(f"Stdout: {result.stdout}")
            return False
        
        print(f"[OK] Java compilation successful")
        
        # Run
        result = subprocess.run(['java', 'HelloWorld'], 
                               capture_output=True, text=True, timeout=5, cwd=temp_dir)
        
        if result.returncode == 0 and result.stdout.strip() == "Hello, World!":
            print(f"[OK] Java execution successful")
            print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"[ERROR] Java execution failed")
            print(f"Return code: {result.returncode}")
            print(f"Stdout: '{result.stdout}'")
            print(f"Stderr: '{result.stderr}'")
            return False
            
    except Exception as e:
        print(f"[ERROR] Java test failed: {str(e)}")
        return False
    finally:
        try:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except:
            pass
    
    return False



def main():
    """Main function to check all compilers"""
    print("Online Judge Compiler Verification")
    print("This script checks if GCC and G++ are properly installed and configured.")
    
    # Test code samples
    c_code = '''#include <stdio.h>
int main() {
    printf("Hello, World!");
    return 0;
}'''
    
    cpp_code = '''#include <iostream>
using namespace std;
int main() {
    cout << "Hello, World!";
    return 0;
}'''
    
    # Test Python
    python_code = '''print("Hello, World!")'''
    
    # Check compilers
    gcc_ok = check_compiler('gcc', c_code, 'c')
    gpp_ok = check_compiler('g++', cpp_code, 'cpp')
    python_ok = check_python()
    java_ok = check_java()
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    
    if gcc_ok and gpp_ok and python_ok and java_ok:
        print("All compilers are working correctly!")
        print("[OK] GCC (C compiler) - OK")
        print("[OK] G++ (C++ compiler) - OK")
        print("[OK] Python interpreter - OK")
        print("[OK] Java compiler/runtime - OK")
        print("\nYour Online Judge system is ready to compile and execute C/C++/Python/Java code.")
        return 0
    else:
        print("Some compilers are not working properly:")
        print(f"{'[OK]' if gcc_ok else '[ERROR]'} GCC (C compiler)")
        print(f"{'[OK]' if gpp_ok else '[ERROR]'} G++ (C++ compiler)")
        print(f"{'[OK]' if python_ok else '[ERROR]'} Python interpreter")
        print(f"{'[OK]' if java_ok else '[ERROR]'} Java compiler/runtime")
        
        if not gcc_ok or not gpp_ok or not python_ok or not java_ok:
            print("\nInstallation Instructions:")
            if not gcc_ok or not gpp_ok:
                print("C/C++ Compilers:")
                print("  Windows: Install MinGW-w64 or TDM-GCC")
                print("  Ubuntu/Debian: sudo apt install gcc g++")
                print("  CentOS/RHEL: sudo yum install gcc gcc-c++")
                print("  macOS: xcode-select --install")
            if not python_ok:
                print("Python Interpreter:")
                print("  Windows: Download from https://python.org")
                print("  Ubuntu/Debian: sudo apt install python3")
                print("  CentOS/RHEL: sudo yum install python3")
                print("  macOS: brew install python3")
            if not java_ok:
                print("Java Compiler/Runtime:")
                print("  Windows: Download JDK from https://openjdk.org")
                print("  Ubuntu/Debian: sudo apt install openjdk-11-jdk")
                print("  CentOS/RHEL: sudo yum install java-11-openjdk-devel")
                print("  macOS: brew install openjdk@11")
            print("\nMake sure all tools are added to your system PATH.")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())