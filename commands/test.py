import logging
import globs

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'test'
description = 'a test command'
permissions = "creator"

async def execute(bot, msg):
	await msg.channel.send('Test successful')
	log.info('sent message: Test successful')