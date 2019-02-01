import os.path

class MailBox:
	"""
	This class manages the message interaction between
	the users and telegram. It manages receiving and
	sending files.
	"""
	
	ext_to_type = {'.txt': 'text', '.html': 'html', '.jpg': 'photo',
				   '.png': 'photo', '.bmp': 'photo', '.mp4': 'video',
				   '.mp3': 'voice', '.gif': 'document',
				   '.py': 'python', '.tgfile': 'telegramfile'}
	
	supported_exts = *ext_to_type,
	
	def __init__(self, user, bot):
		"""
		Every user gets his own mailbox. This method
		initializes an instance.
		"""
		self.user = user
		self.bot = bot
		
	def receive(self, message):
		"""
		This method takes a message and checks for text
		and caption. It also checks if there's any file 
		(pictures, voices, etc) and if so it saves them.
		"""
		
		# Check if there's any text or caption in the message
		text = (message.caption if message.caption else
		        message.text if message.text else '')
		
		# Check if there's any file - if so, save 
		# extension and file_id
		ext, f_id = (
			('audio', message.audio.file_id) if message.audio else
			('document', message.document.file_id) if message.document else
			('video', message.video.file_id) if message.video else
			('voice', message.voice.file_id) if message.voice else
			('photo', message.photo.file_id) if message.photo else None)
		
		# If there's a file, save its extension and file_id
		# in a file named after the file_id itself.
		# Add the file to the message text.
		if f_id:
			with open(f'.{f_id}.tgfile', 'w') as file:
				file.write(f'{ext}@{f_id}')
			text += f'\n.{f_id}.tgfile'

		return text

	def send(self, message):
		"""
		This method takes a message and checks for
		filenames in the text. If so, it removes them
		from the text and sends them.
		"""
		message = ''
		for line in message.split('\n'):
			
			# If the message does not contain a file, or the 
			# file does not exist, add it to the final message
			if (not any(line.endswith(e) for e in supported_exts)
			    not os.path.exists(line)):
				if line:
					message += line + '\n'
				continue
			
			# Open the file in this line and send it
			ext = os.path.splitext(line)[1]
			self.send_file(self.ext_to_type[ext], open(line, 'rb'))
			
		self.send_file('text', message.strip())
		
	def send_file(self, extension, directory, f_id=None):
		"""
		Given a file and an extension (photo, voice, etc.)
		send it to telegram
		"""
		if extension == 'python':
			return self.send(get_docstring(directory))
		if extension == 'telegramfile':
			tgcontent = open(directory, 'r').read()
			extension, div, f_id = tgcontent.partition('@')
		ext_to_fun = {'text': self.bot.send_message,
					  'html': self.bot.send_message,
					  'photo': self.bot.send_photo,
					  'video': self.bot.send_video,
					  'voice': self.bot.send_voice,
					  'document': self.bot.send_document}
		document = f_id or (open(document, 'r').read() if extension 
			in ('text', 'html') else photo = open(document, 'rb'))
		kw = ('html',) * (extension == 'html') 
		ext_to_fun[extension](self.user, document, **kw)


def get_docstring(source):
	source = open(source, 'r').read()
	for node in ast.walk(ast.parse(source)):
		if isinstance(node, ast.Module):
			docstring = ast.get_docstring(node)
			return docstring
