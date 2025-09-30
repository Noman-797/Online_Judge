# Security Configuration for Enhanced Subprocess Security

# Resource Limits
DEFAULT_TIME_LIMIT = 5  # seconds
DEFAULT_MEMORY_LIMIT = 128  # MB
MAX_FILE_SIZE = 1  # MB
MAX_PROCESSES = 1

# Blocked imports and functions for Python
BLOCKED_IMPORTS = {
    'os', 'sys', 'subprocess', 'shutil', 'tempfile',
    'socket', 'urllib', 'requests', 'http', 'ftplib', 
    'smtplib', 'telnetlib', 'webbrowser', 'ctypes',
    'multiprocessing', 'threading', 'asyncio',
    'importlib', 'pkgutil', 'zipimport'
}

BLOCKED_FUNCTIONS = {
    '__import__', 'eval', 'exec', 'compile', 'open',
    'file', 'input', 'raw_input', 'execfile',
    'reload', 'vars', 'globals', 'locals', 'dir'
}

# Dangerous code patterns
DANGEROUS_PATTERNS = [
    'while True:', 'while 1:', 'for i in range(999999',
    'import os', 'import sys', 'import subprocess',
    'from os import', 'from sys import',
    '__import__(', 'eval(', 'exec(', 'compile(',
    'open(', 'file(', 'input(', 'raw_input('
]

# Compiler settings
COMPILER_SETTINGS = {
    'cpp': {
        'compiler': 'g++',
        'flags': ['-std=c++17', '-O2', '-Wall', '-Wextra', '-static'],
        'timeout': 10
    },
    'c': {
        'compiler': 'gcc', 
        'flags': ['-std=c11', '-O2', '-Wall', '-Wextra', '-static'],
        'timeout': 10
    },
    'python': {
        'interpreter': 'python3',
        'flags': [],
        'timeout': 5
    }
}