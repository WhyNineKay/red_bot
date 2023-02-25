import logging
import globs

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'repeat'
description = "Send a message!"

# repeats text
async def execute(bot, msg):

	if msg.author.id == 208038162180734976:
		if msg.content.find(' ') > 0:
			message = msg.content[msg.content.find(' ')+1:]
			await msg.channel.send(message)
			log.info(f'repeated text: {message}')
		else:
			await msg.channel.send('Add something for me to repeat!')
			log.info('no text to repeat')

	else:
		await msg.channel.send(f'<@!{msg.author.id}> is 100% cringe')
		log.info(f'{msg.author.username}#{msg.author.discriminator} attempted to repeat')
