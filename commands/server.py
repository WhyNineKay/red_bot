import socket
import urllib.request as request
import discord
import logging
import globs

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

from mcstatus import JavaServer

name = 'server'
description = 'Pings minecraft servers'


async def execute(bot, msg):

	# create args list, a list of all words after the command
	if not ' ' in msg.content:
		await msg.channel.send('You need to specify a server to ping')
		log.info('No server given')
		return
	args = msg.content[msg.content.find(' ')+1:].split()

	log.info(f'checking status of: {args[0]}')


	server = JavaServer.lookup(args[0])

	try:
		status = server.status()
	except:
		await msg.channel.send('Server offline')
		log.info('Server offline')
		return

	info = infoBuilder(status, args)
	await msg.channel.send(embed=info)


# takes the response of a ping and puts it in a nice format for discord
def infoBuilder(res, args):


	resultdesc = ''

	desc = res.description.splitlines();

	log.debug(desc[0])

	while desc[0].find("§") >= 0:

		n = desc[0].find("§")
		desc[0] = desc[0][:n] + desc[0][n+2:]

		log.debug(desc[0])

	result = discord.Embed(title=desc[0])

	result.add_field(name='IP', value=f'{args[0]}\n')

	# clean any whitespace and remove color selectors (§)
	for line in desc[1:]:

		log.debug(line)

		while line.find("§") >= 0:

			n = line.find("§")
			line = line[:n] + line[n+2:]

			log.debug(line)


		resultdesc += f'{line.strip()}\n'

	result.add_field(name='Version', value=res.version.name)

	# list names of all players in res.players.sample[]
	# in the format (player1, player2, player3)
	if not res.players.sample == None:

		userNames = []
		for user in res.players.sample:

			username = user.name

			i = -2

			log.debug(username)

			while username[i+2:].find("_") >= 0:

				i = username.find("_")

				username = username[:i] + "\\" + username[i:]

				log.debug(username)

				if i < 0: break


			userNames.append(username)

		result.add_field(name='Players',
			value=f'{res.players.online}/{res.players.max} ({", ".join(userNames)})')
	else:
		result.add_field(name='Players', value=f'{res.players.online}/{res.players.max}')

	result.description = resultdesc

	return result


