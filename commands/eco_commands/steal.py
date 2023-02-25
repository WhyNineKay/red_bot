from datetime import *
import random
import math
import logging
import globs

from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = "steal"
description = "Steal points from another player"
servers = []


# how much more chance there is to steal then to fail given all equals
ADD_SUCC = 50

FAIL_WEIGHT = 50
NOTHING_WEIGHT = 5
BONUS_WEIGHT = 0


# steal points from another player
async def execute(bot, msg, path):

	# check who to steal from
	if msg.mentions == []:
		await msg.reply(
			'Who are you stealing from? usage: `.eco steal <@user>`')
		log.info('no user to steal from')
		return

	elif msg.mentions[0] == msg.author:
		await msg.reply('You can\'t steal from yourself!')
		log.info('user tried to steal from themself')
		return

	# get data for the user stealing
	stealerData = UserData.getUserData(path, msg.author)
	log.debug(f'stealer: {stealerData}')



	# *************************************************************************
	# check time

	# set lastSteal and now
	now = datetime.today()
	lastSteal = stealerData.lastSteal

	# when lastSteal is None, set lastSteal to the earliest possible time
	# when it's not none, attempt to convert it to datetime and add 1 hour
	if lastSteal is None:
		lastSteal = datetime.min

	log.debug(f"lastSteal: {lastSteal}, now: {now.isoformat()}")


	# check lastSteal, if it's been less then an hour, return
	if lastSteal >= now - timedelta(hours=1):

		minutes = 60 - math.floor((now - lastSteal).seconds / 60)
		log.info(f'Steal failed: Hasn\'t been an hour, {minutes} minutes left')
		await msg.reply(f'Oops! You have to wait another {minutes} minutes')
		return


	# set lastSteal to now
	stealerData.lastSteal = now
	# *************************************************************************




	# read data of the user to steal from
	stealeeData = UserData.getUserData(path, msg.mentions[0])
	log.debug(f'Stealee: {stealeeData}')


	# check if the user has enough points to steal from
	if stealeeData.wallet < UserData.minWallet:
		log.info(f"not enough in stealee\'s wallet ({stealeeData.wallet})")
		await msg.reply('Try stealing from someone who has points')
		return



	# set succWeight

	walletRatio = stealeeData.wallet / stealerData.wallet

	# as walletRatio approaches 0, succWeight approaches FAIL_WEIGHT
	succWeight = int(walletRatio * ADD_SUCC + FAIL_WEIGHT)


	# get a number to decide if we succeed, fail, do nothing or bonus
	result = random.randrange(succWeight + FAIL_WEIGHT +
		NOTHING_WEIGHT + BONUS_WEIGHT)


	# chance to take money
	if result < succWeight:

		percent = _percent()
		log.debug(percent)

		# multiply the less of the 2 wallets by the percentage
		steal = int(min(stealeeData.wallet, stealerData.wallet) * percent)


		# set the new values
		stealerData.wallet += steal
		stealeeData.wallet -= steal


		log.info(f'Steal success: stealing {steal} points')
		await msg.reply(f"success, stealing {steal} " +
			f"points from {stealeeData.user.mention}")

	# chance to give money
	elif result < FAIL_WEIGHT + succWeight:


		percent = _percent()

		log.debug(percent)


		# choose which wallet we get the amount from
		if stealerData.wallet > stealeeData.wallet:
			steal = int(stealeeData.wallet * percent)
			log.debug(
				f'using stealee wallet: '
				f'{stealeeData.wallet} * {percent} = {steal}')
		else:
			steal = int(stealerData.wallet * percent)
			log.debug(
				f'using stealer wallet: ' +
				f'{stealerData.wallet} * {percent} = {steal}')


		# set the new values
		stealerData.wallet -= steal
		stealeeData.wallet += steal


		log.info(f'Steal fail: stealing -{steal} points')
		await msg.reply('oops, got caught, you gave ' +
			f"{steal} points to {stealeeData.user.mention}")

	# chance to do nothing
	elif result < NOTHING_WEIGHT + FAIL_WEIGHT + succWeight:

		log.info(f'Steal failed: Nothing happened')
		await msg.reply(f'You broke in, but forgot to steal anything')

	# chance for bonus
	else:
		# something that's uncommon but increadibly undesirable
		# shouldn't change wallet, and shouldn't effect things
		# with a cooldown
		# once .eco inv is implemented, this will actually do
		# something interesting
		log.warning('BONUS UNIMPLEMENTED')
		await msg.reply('Bonus: Unimplemented')
		return


	# write new userdata
	log.debug('Writing userdata')
	UserData.saveUserDatas([stealerData, stealeeData], path)



def _percent():

	# get a percentage between 1% and ~50%, distributed on the low end

	p1 = random.randrange(10, 37, 1) / 10 # get a random number from 1 to 3.6
	p2 = random.randrange(10, 37, 1) / 10
	p3 = random.randrange(10, 37, 1) / 10

	# multiply them all together and divide the whole thing by 100 to
	# get a number between 0 and ~0.5
	return p1 * p2 * p3 / 100
