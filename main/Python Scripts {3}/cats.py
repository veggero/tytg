"""
Reply a number to this message to have a cat picture sent back to you that number of times!
"""

import sys

message = sys.argv[1]

if not message.isdigit():
    print("Pleasy reply with a number")

else:
    for i in range(int(message)):
        print("../cat.jpg")
