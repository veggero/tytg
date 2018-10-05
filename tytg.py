"""
The main tytg module.
"""

import argparse
import logging
import telegram.ext
import os
import os.path
import json
from glob import glob
from telegram import ReplyKeyboardMarkup as RKM
from telegram import KeyboardButton as KB


class User:
	"""
	This class represent an user that's using the bot.
	"""
	
	def __init__(self, user):
		"""
		Check if the userfile already exists.
		If so, read the data.
		Otherwise, create a new file with data.
		"""
		self.file_path = os.path.join(args['root'], f'.{user.id}.user')
		if os.path.exists(self.file_path):
			# Read the json data from the file.
			with open(self.file_path, 'r') as file:
				self.data = json.loads(file.read())
		else:
			# Write data about user to the file.
			# root is the standard directory for new users.
			self.data = {'id': user.id, 'username': user.username, 
				'path': args['root']}
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
		if directory == args['back_label'] and self.data['path']!=args['root']:
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
		for filepath in os.listdir(self.data['path']):
			# Avoid hidden file
			if filepath.startswith('.'):
				continue
			filepath = os.path.join(self.data['path'], filepath)
			# If file is a .txt, send the content
			if filepath.endswith('.txt'):
				bot.send_message(text=open(filepath, 'r').read(), **pars)
			# If file is a .html, send the content as html
			elif filepath.endswith('.html'):
				bot.send_message(text=open(filepath, 'r').read(), 
					 parse_mode='HTML', **pars)
			# If file is in .png, .jpg, .bmp send the image
			elif filepath[-4:] in ('.jpg', '.png', 'bmp'):
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
				

def smartsort(buttons):
    """
    Sort a list of buttons. It will check for:
    - Alphabetical order (a, b, c)
    - Numeric order (1, 2, 3)
    - Specified order (b {0}, c {1}, a {2})
    """
    numbers, specified, words = [], [], []
    for button in buttons:
        if button.split(' ')[-1].isdigit():
            numbers.append(button)
        elif '{' in button:
            specified.append(button)
        else:
            words.append(button)
    numbers.sort(key=lambda x: int(x.split(' ')[-1]))
    specified.sort(key=lambda x: int(x[x.index('{') + 1:x.index('}')]))
    specified = [word[:word.index('{')-1] for word in specified]
    words.sort()
    return specified + numbers + words


def on_message(bot, update):
	"""
	Answer to a message sent to the bot.
	"""
	user = User(update.message.from_user)
	user.cd(update.message.text, bot)


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
		help='Il messaggio presente nel bottone che rappresenta la directory ..')
	args = vars(parser.parse_args())
	
	# Load data from .args file inside main/
	if os.path.exists(os.path.join(args['root'], '.args.json')):
		with open(os.path.join(args['root'], '.args.json')) as file:
			newargs = json.loads(file.read())
		args.update(newargs)
		
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
