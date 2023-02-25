from datetime import *
import logging
import globs

from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = 'deposit'
description = 'Put points into your bank. You can only use this once per day'
servers = []


# give a user 500 points, usable once per day
async def execute(bot, msg, path):

	# check if there's a argument
	if not ' ' in msg.content[msg.content.find(' ')+1:]:
		log.info('User did not give an amount')
		await msg.reply(
			'How much would you like to deposit? (`all` for maximum amount)')
		return


	userData = UserData.getUserData(path, msg.author)
	log.debug(userData)

	user = msg.author.name + "#" + msg.author.discriminator


	today = date.today()
	maxBank = userData.walletMax * UserData.bankMaxMul
	minWallet = userData.walletMax * UserData.walletMinMul

	if minWallet < 2000:
		minWallet = 2000


	# check if the user has already done this today
	if not userData.lastDeposit < today:

		log.info(
			f'{user} has already deposited today')
		await msg.reply('Sorry, you can only use this once per day')
		return

	# check if the user is able to store more in their bank
	elif userData.bank >= maxBank:
		log.info(
			f'{user}\'s bank is already full: ' +
			f'{userData.bank} >= {maxBank}')
		await msg.reply('Your bank is already full')
		return

	# see if the user has enough in their wallet to deposit
	elif (userData.wallet <= minWallet or
			userData.wallet <= 2000):
		log.info(
			f'{user}\'s wallet is too empty: {userData.wallet} ' +
			f'<= {minWallet}')
		await msg.reply('Your wallet is too empty for this')
		return


	maxDep = int(userData.wallet - minWallet)

	if maxDep < userData.wallet - minWallet:
		maxDep = int(userData.wallet - minWallet)

	if maxDep > maxBank - userData.bank:
		maxDep = int(maxBank - userData.bank)


	# set args list
	args = msg.content[msg.content.find(' ')+1:].split()

	log.debug(args)

	# set dep
	if args[1] == 'all':
		dep = maxDep
	else:
		try:
			dep = int(args[1])
		except ValueError:
			log.info('User entered non integer')
			await msg.reply(
				f'{args[1]} is not a number. ' +
				f'Please type all, or enter the amount you\'d like to deposit')
			return

		if dep > maxDep:
			dep = maxDep

	log.info(f'Depositing {dep} points')

	# set all userdata values
	userData.lastDeposit = today
	userData.wallet -= dep
	userData.bank += dep

	await msg.reply(f'Deposited {dep} points')

	# write userdata
	userData.saveUserData(path)