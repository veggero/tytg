from setuptools import setup

setup(name='tytg',
      version='0.2.4',
      description='Telegram bot making without any line of code.',
      url='http://github.com/veggero/tytg',
      author='veggero',
      author_email='niccolo@venerandi.com',
      license='unlicenced',
      packages=['tytg'],
      long_description=open('README.md', 'r').read(),
	  long_description_content_type="text/markdown",
      install_requires=[
          'python-telegram-bot',
      ],
		entry_points='''
			[console_scripts]
			tytg=tytg:tytg
		''',
      zip_safe=False)
