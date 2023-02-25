import logging
import globs

from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = "withdraw"
description = "Withdraw points from bank"

async def execute(bot, msg, path):

	# check if there's a argument
	if not ' ' in msg.content[msg.content.find(' ')+1:]:

		log.info('User did not give an amount')
		await msg.reply('How much would you like to withdraw?')
		return

	args = msg.content[msg.content.find(' ')+1:].split()

	try:
		amount = int(args[1])

	except ValueError:
		log.info("User entered NaN")
		await msg.reply("")
		return


	userData = UserData.getUserData(path, msg.author)
	log.debug(userData)

	if userData.bank < amount:
		log.info(f"User did not have {amount} in their bank ({userData.bank})")
		await msg.reply("You don't have that much in your bank")
		return

	userData.bank -= amount
	userData.wallet += amount

	userData.saveUserData(path)
	log.info(f"moved {amount} from bank to wallet")
	await msg.reply(
		f"Successfully moved {amount} points from your bank to your wallet")

