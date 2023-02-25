import logging
import globs
from importlib import reload
import discord

from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'top'
description = 'Shows a leaderboard'
servers = []

BAD_USER = type('', (), {})()

# the leaderboard command
async def execute(bot, msg, path):

	userDatas = UserData.getAllFromGuild(bot, path)

	# make sure there's actually information in the server
	if userDatas == []:
		log.info('No data available for this server')
		await msg.reply('No information available')
		return

	worths = {}


	# calculate total value of each user
	for userData in userDatas:
		log.debug(userData)
		if userData.user is None:
			userData._user = BAD_USER
			userData.user.name = "USER_NOT_FOUND"

		log.debug(f'adding user: {userData.user.name}')
		# worth = bank + wallet // in future may include some
		worth = int(userData.wallet + userData.bank)
		worths[userData.user] = worth

	log.debug(worths)


	topDes = ''
	i = 0
	foundAuthor = False

	# run through users in order of worth (most to least)
	for user in sorted(worths, key=worths.get, reverse=True):
		log.debug(f'{user}: {worths[user]}')
		i += 1

		# check if the userID is the msg author; allow exit if true
		if not foundAuthor and msg.author == user:
			foundAuthor = True

		# place the top 10 users
		if i <= 10:
			topDes += f'\n{i}. {worths[user]}, {user.name}'

			if foundAuthor and i == 10:
				break

		# place the author if not in top 10
		elif foundAuthor:
			topDes += f'\n\n{i}. {worths[user]}, {user.name}'
			foundAuthor = False


	top = discord.Embed(title='Leaderboard', description=topDes)


	log.debug(top)
	await msg.reply(embed=top)



