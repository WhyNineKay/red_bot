import logging
import globs

from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'give'
description = 'directly add points to users bank or wallet'
usage = f"{globs.DEF_PREFIX}eco give <@USER> <wallet|bank> <AMOUNT>"
permissions = "creator"

# directly add points to users bank or wallet
async def execute(bot, msg, path):

	args = msg.content[msg.content.find(' ') + 1 + len(name):].split()
	log.debug(args)

	if len(args) != 3:

		log.info('Bad args')
		await msg.reply(f"Usage: {usage}")
		return

	# set args[0] directly to msg.mentions[0]
	try:
		args[0] = msg.mentions[0]
		log.debug(f"user: {args[0]}")
	except:
		log.info('Bad args')
		await msg.reply(f"Usage: {usage}")
		return

	if args[0] is None:
		log.info("Bad args")
		await msg.reply(f"Usage: {usage}")
		return

	if args[1] not in ["wallet", "bank"]:
		log.info("Bad args")
		await msg.reply(f"Usage: {usage}")
		return

	try:
		args[2] = int(args[2])

	except ValueError:
		log.info("Bad args")
		await msg.reply(f"Usage: {usage}")
		return

	except:
		log.info("Unexpected Error")
		return

	userData = UserData.getUserData(path, args[0])

	setattr(userData, args[1], getattr(userData, args[1]) + args[2])

	userData.saveUserData(path)
	log.info(f"Added {args[2]} points to {args[0].name}'s {args[1]}")
	await msg.reply(
		f"Gave {args[0].mention} {args[2]} points into their {args[1]}")