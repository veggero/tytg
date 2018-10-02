"""
This module defines the User class. It manages user requests, loads data from file, saves,
and send messages to the telegram user.
"""

from os.path import join, split
from os import listdir
from subprocess import call
from telegram import ReplyKeyboardMarkup as RKM
import telegram
import glob


TOKEN = '459073331:AAFXSK91rmLEe3ZKZUS3PMp4TQ8yvpJPf4k'
BACK_LABEL = 'Back'
USERS_DIR = 'users/'
STATS_FILE = 'stats/downloads.txt'
STD_MSSG = 'Select anything:'
AUTO_MOVE = False
KEYS = 5


class User:
    """
    The User class manages loading, saving, and sending messages.
    """

    def __init__(self, direct, downloads_number=0, **kw):
        self.directory = direct[:-1] if direct.endswith('/') else direct
        self.username = kw['username'] if kw['username'] else str(kw['tg_id'])
        self.downloads = kw['downloads']
        self.downloads_number = downloads_number
        self.tg_id = kw['tg_id']
        self.backup()

    @staticmethod
    def load_file(username):
        """
        Creates a User instance loading data from a file.
        """
        with open(username) as userfile:
            data = {line.split(': ')[0]: eval(line.partition(': ')[-1])
                    for line in userfile.read().split('\n')}
        return User(**data)

    def backup(self):
        """
        Saves User instance to a file.
        """
        with open('%s%s.user' % (USERS_DIR, self.username), 'w') as userfile:
            userfile.write('username: %s\n' % repr(self.username))
            userfile.write('directory: %s\n' % repr(self.directory))
            userfile.write('tg_id: %s\n' % repr(self.tg_id))
            userfile.write('downloads_number: %s\n' %
                           repr(len(self.downloads)))
            userfile.write('downloads: %s' % repr(self.downloads))

    def get(self, subdir):
        """
        This is a bash 'cd': it changes directory.
        """
        if subdir == BACK_LABEL:
            self.back()
        elif subdir not in self.ls():
            self.manage_dir()
        else:
            self.directory = join(self.directory,
                                  next(f for f in listdir(self.directory) if f.startswith(subdir)))
            if (AUTO_MOVE and len(self.ls(files=False)) == 1
                    and not 'script.py' in self.ls()):
                self.get(self.ls(files=False)[0])
            else:
                self.manage_dir()
            if (AUTO_MOVE and not self.ls(files=False)
                    and not 'script.py' in self.ls()):
                self.back()
        self.backup()

    def back(self):
        """
        This is a bash 'cd ..': it gets to its father directory.
        """
        if self.directory.count('/') > 0:
            self.directory = split(self.directory)[0]
        if (AUTO_MOVE and len(self.ls(files=False)) == 1
                and self.directory != 'main'):
            return self.back()
        return self.manage_dir()

    def manage_dir(self):
        """
        Looks into the directory and sends all the supported files.
        """
        bot = telegram.Bot(TOKEN)
        back = [BACK_LABEL] if (self.directory != 'main') else []
        data = {'reply_markup': [d for d in back + self.ls(files=False)],
                'chat_tg_id': self.tg_id, 'parse_mode': 'html'}
        data['reply_markup'] = RKM(
            [data['reply_markup'][i::KEYS] for i in range(KEYS)])
        if any('.txt' in f for f in self.ls()) == 0:
            bot.send_message(text=STD_MSSG, **data)
        for document in self.ls(dirs=False):
            document = join(self.directory, document)
            if document[-3:] in ('jpg', 'png', 'bmp'):
                bot.send_photo(self.tg_id, open(document, 'rb'))
            elif document.endswith('.txt'):
                bot.send_message(text=open(document, 'r').read(), **data)
            elif document.endswith('.tgfile'):
                try:
                    bot.send_video(self.tg_id, open(document, 'r').read())
                except BaseException:
                    bot.send_document(self.tg_id, open(document, 'r').read())
                self.log(self.directory)

    def log(self, document):
        """
        Logs what the user has downloaded.
        """
        document = document.replace(': ', ' - ')
        call(['touch', STATS_FILE])
        with open(STATS_FILE, 'r') as logfile:
            downloads = {line.split(': ')[0]: int(line.split(': ')[1])
                         for line in logfile.read().split('\n')
                         if len(line.split(': ')) > 1}
        if document not in downloads:
            downloads[document] = 0
        downloads[document] += 1
        if document not in self.downloads:
            self.downloads[document] = 0
        self.downloads[document] += 1
        with open(STATS_FILE, 'w') as logfile:
            logfile.write('\n'.join([
                '%s: %s' % (key, downloads[key])
                for key in sorted(downloads,
                                  key=downloads.get, reverse=True)]))

    def ls(self, dirs=True, files=True):
        """
        Return the list of files and dirs in the self.directory.
        """
        return smartsort([f for f in listdir(self.directory)
                          if ((dirs and not '.' in f) or (files and '.' in f))
                          and not f.startswith('_')])


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
