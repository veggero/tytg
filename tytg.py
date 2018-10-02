"""
The main tytg module.
"""

import argparse
import logging
import telegram.ext
import os
import os.path
import json


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
        self.file_path = os.path.join(ROOT, f'.{user.id}.user')
        if os.path.exists(self.file_path):
            # Read the json data from the file.
            with open(self.file_path, 'r') as file:
                self.data = json.read(file.read())
        else:
            # Write data about user to the file.
            # root is the standard directory for new users.
            self.data = {'id': user.id, 'username': user.username, 'path': ROOT}
            self.save_data()
                
    def save_data(self):
        """
        This saves the current data on the userfile.
        """
        with open(self.file_path, 'w') as file:
            file.write(json.dump(sef.data))
        
                
    def cd(self, directory, bot):
        """
        Manage the file that has been selected,
        according to the filetype.
        """
        # If the back_label, such as "Back" is clicked,
        # we're expected to change directory to ..
        path = os.path.join(self.data['path'], directary)
        if directory == BACK_LABEL:
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
        for filepath in os.listdir(self.data['path']):
            # Put a back button if not in root
            back = [[BACK_LABEL]] if self.data['path'] != ROOT else []
            # All messages should be sent to this id, and with a keyboard
            # with a list of one element: a list of directories.
            pars = {'chat_id': self.data['id'],
                'reply_markup': [next(os.walk(self.data['path']))[0]]+back}
            with open(filepath, 'r') as file:
                content = file.read()
            # If file is a .txt, send the content
            if filepath.endswith('.txt'):
                bot.send_message(content, **pars)
            # If file is a .html, send the content as html
            elif filepath.endswith('.html'):
                bot.send_message(parse_mode='HTML', **pars)
            # If file is in .png, .jpg, .bmp send the image
            elif filepath[:-4] in ('.jpg', '.png', 'bmp'):
                bot.send_photo(open(filepath, 'rb'), **pars)
            # If file is a .mp4 send it as video
            elif filepath.endswith('.mp4'):
                bot.send_video(open(filepath, 'rb'), **pars)
            # If file is a .mp3 send it as audio
            elif filepath.endswith('.mp3'):
                bot.send_voice(open(filepath, 'rb'), **pars)
            # If file is a .gif, send it as file (it will display as a gif)
            elif filepath.endswith('.gif'):
                bot.send_document(open(filepath, 'rb'), **pars)
            # If file is a .tgfile, it contains the telegram file id:
            elif filepath.endswith('.tgfile'):
                bot.send_document(content, **pars)

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
    parser.add_argument('token', help='The bot token given by botfather.')
    parser.add_argument('--back-label', metavar='TEXT', dest='back_label', default='Back', 
        help='Il messaggio presente nel bottone che rappresenta la directory ..')
    args = parser.parse_args()
    ROOT = args.root
    TOKEN = args.token
    BACK_LABEL = args.back_label
    
    # Get the updater using te token, and set up the message handler,
    # in a quite verbose way.
    updater = telegram.ext.Updater(token=TOKEN)
    update.dispatcher.add_handler(telegram.ext.MessageHandler(
        telegram.ext.Filters.all, on_message))
    
    # Actually start the bot.
    updater.start_polling()
