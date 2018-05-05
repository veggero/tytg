from telegram import ReplyKeyboardMarkup as RKM
from os.path import isfile, isdir, join, split
from os import listdir
from subprocess import call
import telegram


# TODO: Move into a configuration file

TOKEN = '459073331:AAH5amVnuD2g8Amw779T73DfP2jzx4-Pb2E'
BACK_LABEL = 'Back'
USERS_DIR = 'users/'
STATS_FILE = 'stats/downloads.txt'
STD_MSSG = 'Select anything:'
AUTO_MOVE = False
KEYS = 5


class User:

    def __init__(self, directory='', username='unknow', downloads={}, id=-1, **kw):
        self.directory = directory[:-1] if directory.endswith('/') else directory
        self.username = username if username else str(id)
        self.downloads = downloads
        self.id = id
        self.backup()

    def load_file(username):
        with open(username) as userfile:
            data = {line.split(': ')[0]: eval(line.partition(': ')[-1])
                    for line in userfile.read().split('\n')}
        return User(**data)

    def backup(self):
        with open('%s%s.user' % (USERS_DIR, self.username), 'w') as userfile:
            userfile.write('username: %s\n' % repr(self.username))
            userfile.write('directory: %s\n' % repr(self.directory))
            userfile.write('id: %s\n' % repr(self.id))
            userfile.write('downloads_number: %s\n' % repr(len(self.downloads)))
            userfile.write('downloads: %s' % repr(self.downloads))

    def get(self, subdir):
        if subdir == BACK_LABEL: self.back()
        elif subdir not in self.ls():
            self.manage_dir()
        else:
            self.directory = join(self.directory, 
                next(f for f in listdir(self.directory) if f.startswith(subdir)))
            if (AUTO_MOVE and len(self.ls(files=False)) == 1 
                and not 'script.py' in self.ls()):
                self.get(self.ls(files=False)[0])
            else: self.manage_dir()
            if (AUTO_MOVE and len(self.ls(files=False)) == 0 
                and not 'script.py' in self.ls()):
                self.back()
        self.backup()

    def back(self):
        if self.directory.count('/') > 0: 
            self.directory = split(self.directory)[0]
        if (AUTO_MOVE and len(self.ls(files=False)) == 1 
            and self.directory != 'main'):
            return self.back()
        self.manage_dir()

    def manage_dir(self):
        Lass = telegram.Bot(TOKEN)
        data = {'reply_markup': [d
                for d in [BACK_LABEL] * (self.directory != 'main') + self.ls(files=False)],
               'chat_id': self.id, 'parse_mode': 'html'}
        data['reply_markup'] = RKM([data['reply_markup'][i::KEYS] for i in range(KEYS)])
        if any('.txt' in f for f in self.ls()) == 0:
            Lass.send_message(text=STD_MSSG, **data)
        for document in self.ls(dirs=False):
            document = join(self.directory, document)
            if document[-3:] in ('jpg', 'png', 'bmp'):
                Lass.send_photo(self.id, open(document, 'rb'))
            elif document.endswith('.txt'):
                Lass.send_message(text=open(document, 'r').read(), **data)
            elif document.endswith('.tgfile'):
                try: Lass.send_video(self.id, open(document, 'r').read())
                except: Lass.send_document(self.id, open(document, 'r').read())
                self.log(self.directory)

    def log(self, document):
        document = document.replace(': ', ' - ')
        if document not in self.downloads:
            self.downloads[document] = 0
        self.downloads[document] += 1
        call(['touch', STATS_FILE])
        with open(STATS_FILE, 'r') as logfile:
            downloads = {line.split(': ')[0]: int(line.split(': ')[1])
                         for line in logfile.read().split('\n')
                         if len(line.split(': ')) > 1}
        if document not in downloads:
            downloads[document] = 0
        downloads[document] += 1
        with open(STATS_FILE, 'w') as logfile:
            logfile.write('\n'.join([
                '%s: %s' % (key, downloads[key])
                for key in sorted(downloads, 
                key=downloads.get, reverse=True)]))
            
    def ls(self, dirs=True, files=True):
        return smartsort([f for f in listdir(self.directory)
            if ((dirs and not '.' in f) or (files and '.' in f))
            and not f.startswith('_')])


def smartsort(buttons):
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
