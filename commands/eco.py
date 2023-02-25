import traceback
import logging
import discord
import globs

import commands.eco_commands.index as ecocmd_index

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

PREFIX = globs.DEF_PREFIX

name = 'eco'
description = f'A set of economy commands. {PREFIX}eco help for more'



async def execute(bot, msg):

	path = './commands/eco_commands/guilds/'

	if msg.guild == None:
		await msg.reply(f'Unable to use `{PREFIX}eco` in DMs')
		log.info('Attempted to use .eco in DMs')
		return

	else:
		path += str(msg.guild.id) + '.json'

	log.debug(path)


	if not ' ' in msg.content.strip():
		await msg.reply(f'Do `{PREFIX}eco help` for available commands')
		log.info('No subcommand given')
		return


	subcmd = msg.content.split(' ')[1]


	# special case sub commands

	# help
	# loops through all ecocmds and prints their descriptions
	if subcmd == 'help':

		log.info('Generating help message')
		helpmsgdesc = f'{PREFIX}eco help: Displays this list\n';


		for key in ecocmd_index.ecocmds.keys():

			if ecocmd_index.ecocmds[key].check_perms(msg):
				helpmsgdesc += f'{PREFIX}eco {key}: '

				# if the subcmd points to another subcmd, call it an alias
				if not ecocmd_index.ecocmds[key].name == key:
					helpmsgdesc += f'Alias for {ecocmd_index.ecocmds[key].name}\n'

				else:
					helpmsgdesc += f'{ecocmd_index.ecocmds[key].description}\n'


		helpmsg = discord.Embed(title='Eco Commands', description=helpmsgdesc)

		log.info(helpmsg)
		await msg.reply(embed=helpmsg)

		return


	# regular sub commands
	try:
		if ecocmd_index.ecocmds.get(subcmd, False):
			log.debug(ecocmd_index.ecocmds[subcmd])
			# run sub command
			await ecocmd_index.ecocmds[subcmd].execute(bot, msg, path)
			log.info(f'Sub command executed: {subcmd}')

		else:
			await msg.reply(
				f'Invalid command; Do {PREFIX}eco help for available commands')
			log.info(f'Invalid sub command: {subcmd}')

	except Exception as err:
		log.warning(f'Command {subcmd} had a problem:')
		log.warning(traceback.format_exc())
		log.warning(err)


