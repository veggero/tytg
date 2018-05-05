import logging
import telegram.ext
from os.path import join
from os import listdir
from modules.announce import announce
from User import User


PARENT_DIRECTORY = 'main/'
USERS_DIR = 'users/'
TOKEN = 'insert token here'


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def manage_request(bot, update):
    if update.channel_post: return reply(bot, update) 
    username = (update.message.from_user.username if 
                update.message.from_user.username else str(update.message.chat_id))
    if not username + '.user' in listdir(USERS_DIR):
        user = User(PARENT_DIRECTORY, username, {}, update.message.chat_id)
    else: user = User.load_file('%s%s.user' % (USERS_DIR, username))
    if 'script.py' in user.ls() and update.message.text != 'Indietro':
        global_vars = {}
        with open(join(user.directory, "script.py")) as f:
            exec(f.read(), global_vars)
        return global_vars['_main'](update.message.text, user)
    user.get(update.message.text)


updater = telegram.ext.Updater(token=TOKEN)


[*map(updater.dispatcher.add_handler, (
    telegram.ext.CommandHandler('announce', announce),
    telegram.ext.MessageHandler(
     telegram.ext.Filters.all, manage_request)))]
    
    
updater.start_polling()
