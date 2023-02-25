import traceback
from importlib import import_module, util
import globs
import logging

from commands.eco_commands.eco_common import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)

name = "use"
description = "Use items"
permissions = "creator"


"""
A command to use items
"""
async def execute(bot, msg, path):
	args = msg.content.split(' ')

	# check that the user gave an item name
	if len(args) < 3:
		await msg.reply("What item do you want to use?")
		log.info("User did not specify what item to use")
		return


	item = args[2]


	# check that the item exists
	if item not in Item.itemTypes.keys():
		await msg.reply("That item doesn't exist")
		log.info("User tried to use an item that doesn't exist")
		return


	userData = UserData.getUserData(path, msg.author)
	i = userData.searchInventory(item)


	# check if the user has that item
	if i < 0:
		await msg.reply("You don't have that item")
		log.info("User tried to use an item they don't have")
		return


	if len(args) > 3:
		qty = args[3]
	else:
		qty = 1


	if userData.inventory[i].qty < qty:
		await msg.reply("You don't have that many of that item")
		log.info("User tried to use more of an item than they have")
		return


	rqty = Item.itemTypes[item].use(qty)

	if rqty < 0:
		await msg.reply("That item doesn't have a use")
		log.info("User tried to use an item that " +
			"doesn't override the `use` method")

