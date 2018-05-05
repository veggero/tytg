"""
Announces a message to all the users.
"""

import os


ADMINS = (123456789, 13374242)
USERS_DIR = 'users/'
ERROR_MSSG = 'This command is only for admins.'


def announce(bot, update) -> bool:
    """
    It creates an "Announce", or
    still better, it notices all users
    about something.

    :param bot: A python-telegram-bot bot instance
    :param update: The update where the announce comes from
    :return: True if all succeeded, False if not
    :rtype: bool
    """
    if update.message.chat_id not in ADMINS:
        update.message.reply_text('This command is only for admins.')
        return
    try:
        for username in os.listdir(USERS_DIR):
            try:
                user_file = open('%s%s' % (USERS_DIR, username), 'r')
                data = {line.split(': ')[0]: line.split(': ')[1]
                        for line in user_file.read().split('\n')}
                message = update.message.reply_to_message
                if message.photo:
                    bot.send_photo(
                        chat_id=data['id'],
                        caption=message.caption,
                        photo=message.photo.file_id,
                        parse_mode='HTML')
                else:
                    bot.send_message(
                        chat_id=data['id'],
                        text=message.text,
                        parse_mode='HTML')
            except FileNotFoundError:
                print('Announcement: %s%s not found' % (USERS_DIR, username))
            except BaseException as exception:
                print('Announcement: ' + str(exception) + ' for %s' % username)
            finally:
                print('Announcement: %s noticed' % username)
        print('Announcement: all succeeded')
    except BaseException as exception:
        print('Announcement: failed due to ' + str(exception))
    return
