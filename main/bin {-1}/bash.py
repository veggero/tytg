"""
Executes a bash command
"""

import sys
import subprocess

message = sys.argv[1]

try:
	result = subprocess.check_output(message, shell=True)
	print(result.decode())
except subprocess.CalledProcessError as e:
	print(f"Command failed due to {e}")
