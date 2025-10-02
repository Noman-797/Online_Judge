#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from judge.multi_language_evaluator import MultiLanguageEvaluator
from problems.models import Problem, TestCase

def test_evaluator():
    print("Testing MultiLanguageEvaluator...")
    
    # Get the contest problem we created
    try:
        problem = Problem.objects.get(slug='contest-hello-world')
        print(f"Found problem: {problem.title}")
        print(f"Contest only: {problem.contest_only}")
        
        # Get test cases
        test_cases = problem.test_cases.all()
        print(f"Test cases: {len(test_cases)}")
        
        # Test C code
        c_code = '''#include <stdio.h>
int main() {
    printf("Hello World");
    return 0;
}'''
        
        # Test C++ code
        cpp_code = '''#include <iostream>
using namespace std;
int main() {
    cout << "Hello World";
    return 0;
}'''
        
        # Test Python code
        python_code = '''print("Hello World")'''
        
        evaluator = MultiLanguageEvaluator()
        
        # Test each language
        for lang, code in [('c', c_code), ('cpp', cpp_code), ('python', python_code)]:
            print(f"\nTesting {lang.upper()}:")
            result = evaluator.evaluate_submission(
                code=code,
                language=lang,
                test_cases=test_cases,
                time_limit=problem.time_limit,
                memory_limit=problem.memory_limit
            )
            
            print(f"  Verdict: {result['verdict']}")
            print(f"  Test cases passed: {result.get('test_cases_passed', 0)}/{result.get('total_test_cases', 0)}")
            if result.get('execution_time'):
                print(f"  Execution time: {result['execution_time']:.3f}s")
            if result.get('memory_used'):
                print(f"  Memory used: {result['memory_used']}KB")
            if result.get('compilation_error'):
                print(f"  Compilation error: {result['compilation_error']}")
            if result.get('runtime_error'):
                print(f"  Runtime error: {result['runtime_error']}")
        
        print("\nEvaluation test completed!")
        
    except Problem.DoesNotExist:
        print("Contest problem not found. Run test_contest_setup.py first.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_evaluator()