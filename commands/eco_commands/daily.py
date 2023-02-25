from datetime import date
import logging
import globs
from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'daily'
description = 'Get points daily!'
servers = []


# give a user 500 points, usable once per day
async def execute(bot, msg, path):

	userData = UserData.getUserData(path, msg.author)
	log.debug(userData)

	# get todays date, to be used in the if, and to set lastDaily
	today = date.today()

	lastDaily = userData.lastDaily
	log.debug(f'lastDaily: {lastDaily}, today: {today.isoformat()}')

	if lastDaily is None:
		lastDaily = date.min
	else:
		lastDaily = lastDaily


	# check lastDaily, if it's before today wallet + 500, otherwise do nothing
	if lastDaily < today:

		#set lastDaily then add 500 to users wallet
		userData.lastDaily = today
		userData.wallet += UserData.dailyAmount
		
		await msg.reply(f'You got {UserData.dailyAmount} points! Your total is now {userData.wallet}')

		log.info(f'Gave {msg.author.name}#{msg.author.discriminator} 500 points')

		# write new userdata
		userData.saveUserData(path)

	else:
		await msg.reply('Oops! You\'ve already done this today, try again tomorrow!')
		log.info(f'{msg.author.name} has already claimed they\'re points')
