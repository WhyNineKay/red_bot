import globs
import logging

from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = "shop"
description = "Buy or view available items"
usage = f"{globs.DEF_PREFIX}eco shop [buy|sell <item> [quantity=1]]"


"""
Buy or view items
"""
async def execute(bot, msg, path):

	# create args
	args = msg.content[msg.content.find(' ') + 1 + len(name):].split()
	log.debug(args)


	# if we have no args, display the items in the shop
	if len(args) == 0:
		shop = discord.Embed(title="Shop")

		# if there are no items, tell the user that
		if len(Item.itemTypes.keys()) == 0:
			shop.description = "Sorry, no items in the shop"

		else:
			# add each item to the discord embed
			for itemKey in Item.itemTypes.keys():
				item = Item.itemTypes[itemKey]
				shop.add_field(name=item.type, value=item.describe())

			# tell the user how to buy an item
			shop.description = "To buy something do " + \
				f"`{globs.DEF_PREFIX}eco shop buy <itemName> [quantity]`"


		await msg.reply(embed=shop)
		log.info("Displayed shop")
		return


	# check that the user specified to buy
	if args[0] == "buy":

		# check if there's enough arguments
		if len(args) < 2:
			await msg.reply(
				f"Please specify what you'd like to buy. Usage: {usage}")
			log.info("User didn't specify what to buy")
			return


		# parse args[1] as itemType
		try:
			itemType = Item.itemTypes[args[1]]

		except KeyError:
			await msg.reply(f"That's not a valid item")
			log.info("User gave an invalid itemtype")
			return


		# parse qty if it exists, otherwise set it to 1
		if len(args) > 2:
			try:
				qty = int(args[2])

			except ValueError:
				await msg.reply("Quantity must be a number")
				log.info("User specified bad quantity")
				return

			# if we've parsed qty, make sure it's more than 1
			if qty < 1:
				await msg.reply("You must buy at least 1 item")
				log.info("User tried to buy less than 1 item")
				return

		else:
			qty = 1


		# get userData and set totalCost
		totalCost = itemType.cost * qty
		userData = UserData.getUserData(path, msg.author)


		# check if the user has enough points
		if userData.wallet < totalCost:
			await msg.reply("You don't have enough points to do that")
			log.info("User tried to buy, but didn't have enough points")
			return


		# all cases checked, do the calculations
		userData.wallet -= totalCost
		userData.invAddItem(args[1], qty)

		await msg.reply(f"Bought {qty} x {args[1]} for {totalCost} points")
		log.info(f"User bought {qty} x {args[1]} for {totalCost}")


		userData.saveUserData(path)
		return

	elif args[0] == "sell":
		# check if there's enough arguments
		if len(args) < 2:
			await msg.reply(
				f"Please specify what you'd like to buy. Usage: {usage}")
			log.info("User didn't specify what to buy")
			return


		# parse args[1] as itemType
		try:
			itemType = Item.itemTypes[args[1]]

		except KeyError:
			await msg.reply(f"That's not a valid item")
			log.info("User gave an invalid itemtype")
			return


		# parse qty if it exists, otherwise set it to 1
		if len(args) > 2:
			try:
				qty = int(args[2])

			except ValueError:
				await msg.reply("Quantity must be a number")
				log.info("User specified bad quantity")
				return

			# if we've parsed qty, make sure it's more than 1
			if qty < 1:
				await msg.reply("You must sell at least 1 item")
				log.info("User tried to sell less than 1 item")
				return

		else:
			qty = 1

		# get userData and set totalCost
		totalCost = int(itemType.cost * qty * UserData.REFUND_RATE)
		userData = UserData.getUserData(path, msg.author)


		i = userData.searchInventory(itemType.type)

		# check if the user has enough points
		if  i < 0:
			await msg.reply("You don't have any of that item")
			log.info("User tried to sell an item they don't have")
			return

		if userData.inventory[i].qty < qty:
			await msg.reply("You don't have that much of that item")
			log.info("User tried to sell more of an item than they have")
			return


		# all cases checked, do the calculations
		userData.wallet += totalCost
		userData.invRemoveItem(args[1], qty)

		await msg.reply(f"Sold {qty} x {args[1]} and recieved {totalCost} points")
		log.info(f"User sold {qty} x {args[1]} for {totalCost}")


		userData.saveUserData(path)
		return



	# if args[1] is neither 'sell' or 'buy'
	await msg.reply(f"Invalid option {usage}; try either `sell` or `buy`")
	log.info(f"User gave an invalid argument `{globs.DEF_PREFIX}eco shop [badArg]`")
	return