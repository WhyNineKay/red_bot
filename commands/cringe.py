import random
import logging
import globs

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'cringe'
description = "Tests the cringe level of @user"

async def execute(bot, msg):
	if msg.content.find(' ') > 0:
		msgtrim = msg.content[msg.content.find(' ')+1:]

		if ('red_back' in msgtrim or
				'natey' in msgtrim or
				'208038162180734976' in msgtrim or
				'851816132801331260' in msgtrim):
			await msg.reply(f'{msgtrim} is -100% cringe')
			await msg.reply(f'{msg.author.mention} is 100% cringe')
		elif 'red__' in msgtrim:
			await msg.reply("who's that?")
			await msg.reply(f'also {msg.author.mention} is 100% cringe')
		elif '@everyone' in msgtrim or '@here' in msgtrim:
			await msg.reply(f'nice try')
			await msg.reply(f'{msg.author.mention} is 100% cringe')
		else:
			if msg.author.id == 208038162180734976:
				chance = 100
			else:
				chance = random.randrange(101)

			await msg.reply(f'{msgtrim} is {chance}% cringe')
			log.info(f'cringed text: {msgtrim}')


	else:
		await msg.reply(f'{msg.author.mention} is 100% cringe')
		log.info('Attempted to cringe, but was missing text')
