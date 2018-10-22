"""
The main tytg module.
"""

import argparse
import logging
import telegram.ext
import time
import os
import os.path
import json
import ast
import subprocess
from glob import glob
from telegram import ReplyKeyboardMarkup as RKM
from telegram import KeyboardButton as KB


class User:
	"""
	This class represent an user that's using the bot.
	"""
	
	extensions = ('.txt', '.html', '.jpg', '.png', '.bmp', '.mp4',
				  '.mp3', '.gif', '.tgfile', '.py')
	
	def __init__(self, user):
		"""
		Check if the userfile already exists.
		If so, read the data.
		Otherwise, create a new file with data.
		"""
		# start with standard values
		# mess_to_file is a map from a message to the filename
		# that contains that content
		self.data = {'id': user.id, 'username': user.username, 
			'path': args['root'], 'mess_to_file': {}}
		self.file_path = os.path.join(args['root'], f'.{user.id}.user')
		if os.path.exists(self.file_path):
			# Read the json data from the file.
			with open(self.file_path, 'r') as file:
				# Update with data from the file
				self.data.update(json.loads(file.read()))
		else:
			self.data = {}
		# Write data about user to the file.
		self.save_data()
				
	def save_data(self):
		"""
		This saves the current data on the userfile.
		"""
		with open(self.file_path, 'w') as file:
			json.dump(self.data, file)
		
				
	def cd(self, directory, bot):
		"""
		Manage the file that has been selected,
		according to the filetype.
		"""
		# If the back_label, such as "Back" is clicked,
		# we're expected to change directory to ..
		path = os.path.join(self.data['path'], directory)
		# Directories sorted using {*} at the end, gets
		# their {*} removed. Glob checks if a dir that
		# ends with {*} exists, and if so, replaces path.
		if glob(path+' {*}/'):
			path = glob(path+' {*}')[0]
		if (directory == args['back_label'] and 
			self.data['path']!=args['root']):
			# The first element of os.path.split is the .. directory
			self.data['path'] = os.path.split(self.data['path'])[0]
		# If file is a directoy, open it
		elif os.path.exists(path):
			self.data['path'] = path
		self.ls(bot)
		self.save_data()
			
	def ls(self, bot):
		"""
		Send all the text, images and files on the
		current directory.
		"""
		# Put a back button if not in root
		back = ([[KB(args['back_label'])]] 
		  if self.data['path'] != args['root'] else [])
		directories = smartsort(next(os.walk(self.data['path']))[1])
		keyboard = RKM([[KB(dir)] for dir in directories]+back)
		# All messages should be sent to this id, and with a keyboard
		# with a list of one element: a list of directories.
		pars = {'chat_id': self.data['id'],
			'reply_markup': keyboard}
		# Quanti file NON abbiamo spedito, perché non riconosciuti?
		not_sent = 0
		for filepath in os.listdir(self.data['path']):
			try:
				# Avoid hidden file
				if filepath.startswith('.'):
					not_sent += 1
					continue
				filepath = os.path.join(self.data['path'], filepath)
				self.send(filepath, bot, pars)
			except Exception as e:
				print(f"File upload failed due to {e}")
				not_sent += 1
		if len(os.listdir(self.data['path'])) == not_sent:
			# No file has been sent. Standard message here.
			bot.send_message(text=args['standard-message'], **pars)
			
	def send(self, filepath, bot, pars):
		# If file is a .txt, send the content
		if filepath.endswith('.txt'):
			mess = open(filepath, 'r', encoding="UTF-8").read()
			bot.send_message(text=mess, **pars)
			self.data['mess_to_file'][mess] = filepath
		# If file is a .html, send the content as html
		elif filepath.endswith('.html'):
			mess = text=open(filepath, 'r', encoding="UTF-8").read()
			bot.send_message(text=mess, parse_mode='HTML', **pars)
			self.data['mess_to_file'][mess] = filepath
		# If file is in .png, .jpg, .bmp send the image
		elif filepath[-4:] in ('.jpg', '.png', '.bmp'):
			bot.send_photo(photo=open(filepath, 'rb'), **pars)
		# If file is a .mp4 send it as video
		elif filepath.endswith('.mp4'):
			bot.send_video(video=open(filepath, 'rb'), **pars)
		# If file is a .mp3 send it as audio
		elif filepath.endswith('.mp3'):
			bot.send_voice(voice=open(filepath, 'rb'), **pars)
		# If file is a .gif, send it as file (it will display as a gif)
		elif filepath.endswith('.gif'):
			bot.send_document(document=open(filepath, 'rb'), **pars)
		# If file is a .tgfile, it contains the telegram file id:
		elif filepath.endswith('.tgfile'):
			bot.send_document(document=open(filepath, 'r').read(), **pars)
		elif filepath.endswith('.py'):
			mess = filepath.replace('.py', '')
			code = open(filepath, 'r').read()
			if get_docstring(code):
				mess = get_docstring(code)
			bot.send_message(text=mess, **pars)
			self.data['mess_to_file'][mess] = filepath
		elif '.' not in filepath:
			pass
		else:
			raise TypeError(f'Cannot send file {filepath} due to '
				   'unknow extension')
		
	def call(self, message, args, update, bot):
		"""
		Call a file with some arguments, e.g.
		replying "-rf /" to the message sent
		from the file "/bin/rm"
		"""
		if message not in self.data['mess_to_file']:
			return
		# Check to what file is the reply referring to
		file = self.data['mess_to_file'][message]
		# Call the python file, and write the output back
		if file.endswith('.py'):
			cmd = f'python3 "{file}" "{args}"'
			out = subprocess.check_output(cmd, shell=True)
			out = out.decode().split('\n')
			for line in [*out]:
				# If any line output is a filename, send it
				if any(line.endswith(ext) for ext in self.extensions):
					out.remove(line)
					line = os.path.join(self.data['path'], line)
					self.send(line, bot, {'chat_id': update.message.chat_id})
				# If any line is a path, open it
				elif line.endswith('/'):
					out.remove(line)
					self.cd(line, bot)
			out = '\n'.join(out)
			if out:
				update.message.reply_text(out, parse_mode='HTML')
		# Calls are not supported on this file. ignore
		
		
	def run_bin(self, message, update, bot):
		"""
		Search for a bin* directory in main/,
		and call the command* file inside it with
		the arguments.
		Example could be: /rm .
		Will search for main/bin*/rm*, and find
		main/bin {-1}/rm.py, and call it with
		argument .
		"""
		command, sep, arguments = message.partition(' ')
		# remove the /
		command = command[1:]
		script = glob(f"{args['root']}/bin*/{command}*")
		# No script found? That's the end.
		if not script: 
			return print(f"Command not recognized: {command}")
		# Otherwise, get first result
		script = script[0]
		# Save the script name inside the 'mess_to_file' dictionary
		# in order to make it recognizable to User.call
		self.data['mess_to_file'][script] = script
		self.call(script, arguments, update, bot)
				
				
def get_docstring(source):
	for node in ast.walk(ast.parse(source)):
		if isinstance(node, ast.Module):
			docstring = ast.get_docstring(node)
			return docstring
		

def smartsort(buttons):
	"""
	Sort a list of buttons. It will check for:
	- Alphabetical order (a, b, c)
	- Numeric order (1, 2, 3)
	- Specified order (b {0}, c {1}, a {2})
	"""
	numbers, specified, words = [], [], []
	for button in buttons:
		if button.startswith('.'):
			continue
		if button.split(' ')[-1].isdigit():
			numbers.append(button)
		elif '{' in button:
			specified.append(button)
		else:
			words.append(button)
	numbers.sort(key=lambda x: int(x.split(' ')[-1]))
	specified.sort(key=lambda x: int(x[x.index('{') + 1:x.index('}')]))
	specified = [word[:word.index('{')-1] for word in specified
			  if int(word[word.index('{') + 1:word.index('}')])>0]
	words.sort()
	return specified + numbers + words


def on_message(bot, update):
	"""
	Answer to a message sent to the bot.
	"""
	print("Message received")
	user = User(update.message.from_user)
	if update.message.text.startswith('/'):
		# Command, tell the user to execute it
		user.run_bin(update.message.text, update, bot)
	elif update.message.reply_to_message:
		# It's a call to an older message
		user.call(update.message.reply_to_message.text, 
			update.message.text, update, bot)
	else:
		# What else? Just a directory name to open
		user.cd(update.message.text, bot)
	print("Message handled")


if __name__ == '__main__':
	
	# Set up logging.
	logging.basicConfig(
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		level=logging.INFO)

	# Getting root and token from argument in a very verbose way.
	parser = argparse.ArgumentParser(description='Run the tytg server.')
	parser.add_argument('root', help='The path to the root folder.')
	parser.add_argument('token', help='The bot token given by botfather.',
					 default=None, nargs='?')
	parser.add_argument('--back-label', metavar='TEXT', dest='back_label', 
		default='Back', 
		help='Text in the button representing ..')
	parser.add_argument('--standard-message', metavar='TEXT', 
		dest='standard-message', default='Choose one:', 
		help='Standard message if no file is found in a directory')
	
	args = vars(parser.parse_args())
	
	# Load data from .args file inside main/
	if os.path.exists(os.path.join(args['root'], '.args.json')):
		with open(os.path.join(args['root'], '.args.json'), 'r') as file:
			args = json.load(file)
	
	# Command line args should have priority over .args.data,
	# but only if they're different from None
	args.update({key: value for key, value in 
			  vars(parser.parse_args()).items()
			  if value})
			
	# Save data to file, in order to avoid putting token every time
	with open(os.path.join(args['root'], '.args.json'), 'w') as file:
		json.dump(args, file)
		
	# No token, no party
	if not args['token']:
		print("A token is needed to run the bot. Get one from @botfather.")
		print("Either insert the token as an argument after main/, or")
		print("create a file called .args.json, containing:")
		print("{'token': 'TOKEN HERE'}")
		exit(1)
	
	# Get the updater using te token, and set up the message handler,
	# in a quite verbose way.
	updater = telegram.ext.Updater(token=args['token'])
	updater.dispatcher.add_handler(telegram.ext.MessageHandler(
		telegram.ext.Filters.all, on_message))
	
	# Actually start the bot.
	updater.start_polling()
	
	print("Bot started.")
