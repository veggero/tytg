"""
Answer to this message to get your text weirded out.
"""

import sys

message = sys.argv[1]

for c in ('a', 'e', 'i', 'o', 'u'):
	message = message.replace(c, f'{c}f{c}')
	
print(message)
