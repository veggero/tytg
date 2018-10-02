from setuptools import setup

setup(name='tytg',
      version='0.2',
      description='Telegram bot making without any line of code.',
      url='http://github.com/veggero/tytg',
      author='veggero',
      author_email='niccolo@venerandi.com',
      license='unlicenced',
      packages=['tytg'],
      install_requires=[
          'python-telegram-bot',
      ],
      zip_safe=False)
