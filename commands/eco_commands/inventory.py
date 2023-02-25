import logging
import discord
import globs

from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'inventory'
description = 'View inventory contents'
servers = []


# reply's with the inventory of the given user (default msg author)
async def execute(bot, msg, path):

	log.debug(msg.mentions)


	# test if the user made any mentions, if so use the first mention
	if msg.mentions == []:
		user = msg.author
	else:
		user = msg.mentions[0]

	userData = UserData.getUserData(path, user)
	log.debug(userData)


	# check if the users inventory is empty
	if userData.inventory == []:
		await msg.reply(f'<@!{msg.author.id}>\'s inventory is empty')
		log.info('User\'s inventory is empty')
		return


	inventory = discord.Embed(title='Inventory')

	for item in userData.inventory:
		inventory.add_field(name=f"Name: {item.type}", value=item.describe())


	await msg.reply(embed=inventory)
	log.debug(inventory)
