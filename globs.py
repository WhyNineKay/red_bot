import os
from dotenv import load_dotenv


def init():
	global DEF_PREFIX
	global CREATOR
	global LOGLEVEL
	load_dotenv()
	DEF_PREFIX = os.getenv('DEF_PREFIX')
	CREATOR = int(os.getenv('CREATOR'))
	LOGLEVEL = os.getenv('LOGLEVEL', 'INFO')