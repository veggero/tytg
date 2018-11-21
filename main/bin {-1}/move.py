"""
Moves a file
"""

import sys
import subprocess
import os

newfilename, oldfilename = sys.argv[1].split('\n')

if not newfilename.endswith('.tgfile'):
	newfilename += '.tgfile'

if not oldfilename.endswith('.tgfile'):
	print('Only tgfiles can be moved with this script right now!')
else:
	os.rename(oldfilename, newfilename)
