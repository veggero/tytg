"""
Main module of TyTg. It starts the bot.
"""

import logging
from os.path import join
from os import listdir
from user import User
import telegram.ext
from modules.announce import announce


PARENT_DIRECTORY = 'main/'
USERS_DIR = 'users/'
TOKEN = '459073331:AAFXSK91rmLEe3ZKZUS3PMp4TQ8yvpJPf4k'


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def manage_request(_, update):
    """
    Manage a telegram request, creating the User and getting the directory.
    """
    username = (update.message.from_user.username if
                update.message.from_user.username else str(update.message.chat_id))
    if not username + '.user' in listdir(USERS_DIR):
        user = User(PARENT_DIRECTORY, username=username, downloads={}, tg_id=update.message.chat_id)
    else:
        user = User.load_file('%s%s.user' % (USERS_DIR, username))
    if 'script.py' in user.ls() and update.message.text != 'Indietro':
        global_vars = {}
        with open(join(user.directory, "script.py")) as script:
            exec(script.read(), global_vars)
        return global_vars['_main'](update.message.text, user)
    return user.get(update.message.text)


def main():
    """
    Main function. Add the updater
    """
    updater = telegram.ext.Updater(token=TOKEN)

    list(map(updater.dispatcher.add_handler, (
        telegram.ext.CommandHandler('announce', announce),
        telegram.ext.MessageHandler(
            telegram.ext.Filters.all, manage_request))))

    updater.start_polling()

if __name__ == "__main__":
    main()
