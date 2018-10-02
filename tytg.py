import argparse
import telegram

parser = argparse.ArgumentParser(description='Run the tytg server.')
parser.add_argument('path', help='The path to the main folder.')
parser.add_argument('token', help='The bot token given by botfather.')
args = parser.parse_args()
print(args.path)
