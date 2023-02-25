import traceback
from importlib import import_module, util
import logging
import globs

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'script'
description = 'Run abitrary scripts'
permissions = "creator"

path = "commands.execute_scripts."


async def execute(bot, msg):

	if not ' ' in msg.content:
		await msg.channel.send(
			'Runs abitrary scripts, give a script as an argument')
		log.info('No subcommand given')
		return


	iCMDEnd = msg.content.find(' ')+1
	iScriptEnd = msg.content[iCMDEnd:].find(' ')

	# find the second word in msg.content:
	# go from 1 more than the index of the first space,
	# to the index of the next space
	if not iScriptEnd == -1:
		script = msg.content[iCMDEnd:iScriptEnd]
	else:
		script = msg.content[iCMDEnd:]

	log.info(f'Subcommand: {script}')


	try:

		if util.find_spec(f'{path}{script}'):
			module = import_module(f'{path}{script}')
			result = module.main(bot)

			await msg.reply(result)
			log.info(result)
		else:
			await msg.channel.send("File does not exist")
			log.info(
				f"Failed to execute script: {script}, file does not exist")

	except Exception as err:

		await msg.channel.send(f"Failed to execute script: ```{err}```")
		log.warning(f"Failed to execute script: {script}")
		log.warning(traceback.format_exc())
		log.warning(err)

