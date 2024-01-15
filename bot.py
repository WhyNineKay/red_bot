import os
import traceback
import logging
import json
import discord
from dotenv import load_dotenv
import globs

globs.init()
DEF_PREFIX = globs.DEF_PREFIX
CREATOR = globs.CREATOR
# import a dictionary of all commands
# this allows me to link a string to a module
import commands.index as cmd_index

load_dotenv()
TOKEN = os.getenv('TOKEN')


logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

log.info(f'Prefix: {DEF_PREFIX}')


class MyClient(discord.Client):
	async def on_ready(self):
		log.info(f'logged in as {self.user}')

	async def on_message(self, msg):

		# make sure the message isn't from this bot
		# or an empty message
		if msg.author == self.user or msg.content is None or msg.content == '':
			return

		if msg.content == '':
			return

		# pointless dumb command
		if msg.content == 'yo wuddup' and msg.author.id == CREATOR:
			await msg.channel.send('yo wuddup')
			log.info("said 'yo wuddup'")

		# actual useful commands
		elif msg.content[0] == DEF_PREFIX:

			# get the first word of the command, without the leading DEF_PREFIX
			if msg.content.find(' ') > 0:
				command = msg.content[1:msg.content.find(' ')]
			else:
				command = msg.content[1:]

			log.info(f'Command: {command}, called from: {msg.channel.name} \
in {msg.guild.name} by {msg.author.name}#{msg.author.discriminator}')

			# special case commands

			# help: Displays all available commands
			if command == 'help':
				log.info('Generating help message')
				helpmsgdesc = f'{DEF_PREFIX}help: Displays this list\n';

				if msg.guild == None:
					guild = None

				else:
					guild = msg.guild.id

				log.debug(f"guild ID: {guild}")


				for key in cmd_index.cmds.keys():

					if cmd_index.cmds[key].check_perms(msg):
						helpmsgdesc += f"{DEF_PREFIX}{key}: "

						if not cmd_index.cmds[key].name == key:
							helpmsgdesc += f'Alias for {cmd_index.cmds[key].name}\n'

						else:
							helpmsgdesc += f'{cmd_index.cmds[key].description}\n'


				helpmsg = discord.Embed(title="Commands",
					description=helpmsgdesc)

				log.info(helpmsg)
				await msg.channel.send(embed=helpmsg)

				return


			# regular commands
			try:

				if cmd_index.cmds.get(command, False):
					log.debug(cmd_index.cmds[command])

					# forward to the next step (in commands/index.py)
					await cmd_index.cmds[command].execute(self, msg)
					log.info(f"Command executed: {command}")

				else:
					log.info(f"Invalid command {command}")

			except Exception as err:

				log.warning(f"Command {command} had a problem:")
				log.warning(traceback.format_exc())
				log.warning(err)




	async def on_raw_reaction_add(self, payload):

		if self.user.id == payload.user_id:
			return

		# set guild based on payload.guild_id
		guild = self.get_guild(payload.guild_id)

		# get the role based on guild, message and emoji/reaction
		role = get_reaction_role(guild,
				str(payload.message_id), str(payload.emoji))


		if role is False:
			log.debug("No role, nothing to do")
			return


		user = guild.get_member(payload.user_id)

		if not has_role(user, role):

			await user.add_roles(role)





	async def on_raw_reaction_remove(self, payload):

		# set guild based on payload.guild_id
		guild = self.get_guild(payload.guild_id)

		# get the role based on guild, message and emoji/reaction
		role = get_reaction_role(guild,
				str(payload.message_id), str(payload.emoji))


		if role is False:
			log.debug("No role, nothing to do")
			return


		user = guild.get_member(payload.user_id)

		if has_role(user, role):

			await user.remove_roles(role)




def get_reaction_role(guild, message_id : str, emoji : str):
	log.debug("finding role")


	rrPath = "reaction_roles.json"

	# if file exists, open and dump json to data
	if os.path.isfile(rrPath):
		with open(rrPath, mode='rt', encoding='utf-16') as file:
			data = json.load(file)

		log.debug('read from file')
		log.debug(data.keys())

	else:
		log.debug(f'file did not exist, exiting')
		return False


	# get the value for this message
	rrMessage = data.get(f"{guild.id},{message_id}")

	log.debug(rrMessage)
	log.debug(str(emoji))

	# if the value didn't exist, quit
	if rrMessage is None:
		log.debug("Message not for reaction roles, exiting")
		return False


	# get the id of the role for this emoji
	rrRole_id = rrMessage.get(emoji)

	log.debug(f"role id: {rrRole_id}")

	# get the role
	rrRole = guild.get_role(int(rrRole_id))

	log.debug(f"role object: {rrRole}")

	# if we got a role, return it
	if rrRole is not None:
		log.info(f"got role: {rrRole}")

		#return role object
		return rrRole

	log.info(f"no role for emoji")

	return False



def has_role(user, role):

	for userRole in user.roles[1:]:
		if userRole == role:
			return True

	return False





def main():

	intents = discord.Intents().all()
	intents.presences = False

	log.info(intents)

	client = MyClient(intents=intents)
	client.run(TOKEN)


if __name__ == "__main__":
	main()

