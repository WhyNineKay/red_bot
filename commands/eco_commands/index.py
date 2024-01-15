from importlib import import_module
from commands.index import Command
import logging
import globs

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

path = 'commands.eco_commands.'

"""
eco_command:
	An subclass of command designed specifically for .eco commands
"""
class EcoCommand(Command):

	"""
	Execute the command if permissions are met
	"""
	async def execute(self, bot, msg, path):

		if self.check_perms(msg):
			await self._execute(bot, msg, path)
		else:
			await msg.channel.send(
				"Command failed: you don't have the necessary permissions")
			log.info(
				f"Command failed: {self.name}, " +
				f"{msg.author.name} doesn't have the necessary permissions")



ecocmds = {
	'daily': EcoCommand(import_module(f'{path}daily')),
	'balance': EcoCommand(import_module(f'{path}balance')),
	'steal': EcoCommand(import_module(f'{path}steal')),
	'deposit': EcoCommand(import_module(f'{path}deposit')),
	'inventory': EcoCommand(import_module(f'{path}inventory')),
	'top': EcoCommand(import_module(f'{path}top')),
	'give': EcoCommand(import_module(f'{path}give')),
	'withdraw': EcoCommand(import_module(f'{path}withdraw')),
	'item': EcoCommand(import_module(f'{path}item')),
	'use': EcoCommand(import_module(f'{path}use')),
}

# aliases
ecocmds.update({
	'bal': ecocmds['balance'],
	'rob': ecocmds['steal'],
	'dep': ecocmds['deposit'],
	'inv': ecocmds['inventory'],
	'wd': ecocmds['withdraw'],
})