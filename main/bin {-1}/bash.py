"""
Executes a bash command
"""

import sys
import subprocess

message = sys.argv[1]

result = subprocess.check_output(message, shell=True)

print(result.decode())
