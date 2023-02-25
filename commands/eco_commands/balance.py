import logging
import globs
import discord

from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'balance'
description = 'Check your balances'
servers = []


# check the balance of a users wallet and bank
async def execute(bot, msg, path):

	log.debug(msg.mentions)

	if msg.mentions == []:
		user = msg.author
	else:
		user = msg.mentions[0]

	userdata = UserData.getUserData(path, user)
	log.debug(userdata)

	# find the max bank
	maxBank = userdata.walletMax * 5

	balances = discord.Embed(title=f'{user.name}\'s Balances')

	balances.add_field(name='Wallet', value=userdata.wallet)
	balances.add_field(name='Bank', value=f"{userdata.bank}/{maxBank}")


	await msg.reply(embed=balances)
	log.info(balances)