"""
Reply to this message with a directory name to change directory there!
"""

import sys

message = sys.argv[1]

if not message.endswith('/'):
    message = message + '/'

print(message)
