import os
from importlib import import_module, util
import json
import logging
from datetime import *
import discord

import globs

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)



class ItemType:
	type: str
	description: str
	cost: int


	_path = "commands.eco_commands.use_item."


	def __init__(self, type, description, cost):
		self._type = type
		self._description = description
		self._cost = cost

		if util.find_spec(f"{self._path}{type}"):
			self.use = import_module(f'{self._path}{type}').use
			log.debug(f"overrode {type}")



	@property
	def type(self):
		return self._type

	@property
	def description(self):
		return self._description

	@property
	def cost(self):
		return self._cost

	"""
	A function to be overriden by a function from a file
	"""
	def use(self, qty):
		log.debug("Used an item with no use")
		return -1


	def describe(self):
		return f"Cost: {self._cost}\n{self.description}"



class Item:
	"""
	An item to go into UserData.inventory
	"""
	type: str
	description: str
	qty: int


	# a dictionary of all itemTypes
	# used as a reference for `.eco shop` as well as for adding items
	# as well as certain Item methods
	itemTypes = {
		# "type": ItemType("type", "description", cost)
		"stuff": ItemType("stuff", "A bunch of useless stuff (don't buy)", 100),
		"pickaxe": ItemType("pickaxe", "Seems kinda blunt", 5000)
	}

	blankItemType = ItemType("none", "This item doesn't exist", None)


	def __init__(self, type : str, qty=1):
		self._type = type
		self._qty = qty


	@property
	def type(self):
		return self._type

	@property
	def description(self):
		return self.itemTypes.get(self._type, self.blankItemType).description

	@property
	def qty(self):
		return self._qty

	@qty.setter
	def qty(self, qty):
		self._qty = qty


	def describe(self):
		return f"Quantity: {self._qty}\n{self.description}"



class UserData:
	"""
	A set of data associated with a user, specific to guild
	"""

	wallet: int
	bank: int
	walletMax: int
	lastDaily: date
	lastDeposit: date
	lastSteal: datetime
	inventory: list[Item]

	# a few values that are useful to be able to access
	bankMaxMul = 5
	walletMinMul = 0.2
	dailyAmount = 500
	minWallet = dailyAmount * 4
	REFUND_RATE = 0.5
	defUserData = {
		'wallet': minWallet,
		'bank': 0
	}


	def __init__(self, user, userData):
		self._user = user
		self._wallet = int(userData['wallet'])
		self._bank = int(userData['bank'])
		self._walletMax = int(userData.get('walletMax', self._wallet))

		if userData.get('lastDaily') is None:
			self._lastDaily = date.min
		else:
			self._lastDaily = date.fromisoformat(userData['lastDaily'])

		if userData.get('lastDeposit') is None:
			self._lastDeposit = date.min
		else:
			self._lastDeposit = date.fromisoformat(userData['lastDeposit'])

		if userData.get('lastSteal') is None:
			self._lastSteal = datetime.min
		else:
			self._lastSteal = datetime.fromisoformat(userData['lastSteal'])



		if isinstance(userData.get('inventory', None), list):
			self._inventory = []
			return

		invList = []

		for item in userData.get('inventory', {}).keys():
			invList.append(Item(item, userData['inventory'][item]))

		# this should be a lot more complicated
		self._inventory = invList


	def toDict(self):
		return {
			"wallet": self._wallet,
			"bank": self._bank,
			"walletMax": self._walletMax,
			"lastDaily": self._lastDaily.isoformat(),
			"lastDeposit": self._lastDeposit.isoformat(),
			"lastSteal": self._lastSteal.isoformat(),
			"inventory": self.invToDict()
		}


	def invToDict(self):
		invDict = {}

		for item in self._inventory:
			invDict[item.type] = item.qty

		return invDict


	@property
	def user(self):
		return self._user

	@property
	def wallet(self):
		return int(self._wallet)

	@wallet.setter
	def wallet(self, wallet : int):
		self._wallet = int(wallet)
		if wallet > self._walletMax:
			self._walletMax = int(wallet)

	@property
	def bank(self):
		return int(self._bank)

	@bank.setter
	def bank(self, bank : int):
		self._bank = int(bank)

	@property
	def walletMax(self):
		return int(self._walletMax)

	@property
	def lastDaily(self):
		return self._lastDaily

	@lastDaily.setter
	def lastDaily(self, lastDaily : date):
		self._lastDaily = lastDaily

	@property
	def lastDeposit(self):
		return self._lastDeposit

	@lastDeposit.setter
	def lastDeposit(self, lastDeposit : date):
		self._lastDeposit = lastDeposit

	@property
	def lastSteal(self):
		return self._lastSteal

	@lastSteal.setter
	def lastSteal(self, lastSteal : datetime):
		self._lastSteal = lastSteal

	@property
	def inventory(self):
		return self._inventory


	"""
	returns the index of a given item type or -1 if it's not found
	"""
	def searchInventory(self, itemType: str):
		# iterate through the inventory, using the enumerate method.
		for i, item in enumerate(self._inventory):
			if item.type == itemType:
				return i  # item is found, return the index.
		else:
			return -1  # item is not found, return -1.

	"""
	method for adding an item to the inventory property
	"""
	def invAddItem(self, itemType: str, qty=1):
		# loop through list, if item is found, add qty to it, if not, add item to list
		itemIndex = self.searchInventory(itemType)

		if itemIndex == -1:
			# the user has no item of this type in their inventory,
			# so we add a new item to the inventory.
			self._inventory.append(Item(itemType, qty))
		else:
			# the user has an item of this type in their inventory,
			# so we add the qty to the existing item.
			self._inventory[itemIndex].qty += qty

	"""
	method for removing an item from the inventory property
	will return the ammount removed
	"""
	def invRemoveItem(self, itemType : str, qty=1):
		# search for the item in the inventory
		itemIndex = self.searchInventory(itemType)

		if itemIndex == -1:
			# the user has no item of this type in their inventory, so we return 0
			return 0

		# the user has an item of this type in their inventory, so we remove the qty from the item
		self._inventory[itemIndex].qty -= qty

		removedQty = qty  # positive int

		# if the item qty is 0 or less, we remove the item from the inventory
		if self._inventory[itemIndex].qty <= 0:
			removedQty += self._inventory[itemIndex].qty  # qty is negative int

			del self._inventory[itemIndex]

		# return the qty removed
		return removedQty

	@classmethod
	def getUserData(cls, path : str, user : discord.abc.User):

		log.debug(f'path:{path}, userID:{user.id}')
		# check the file exists, + timedelta(hours=1)f it doesn't, create a default profile
		if os.path.isfile(path):
			with open(path, mode='rt', encoding='utf-8') as file:
				data = json.load(file)

			log.info('read from file')
			log.debug(data.keys())
			userData = data.get(str(user.id), UserData.defUserData)
			log.debug(userData)

		else:
			log.info(f'file did not exist, using defualt')
			userData = UserData.defUserData


		return UserData(user, userData)


	@classmethod
	def getAllFromGuild(cls, bot: discord.Client, path: str):

		# check the file exists
		# if it does, read in all the userdata, then turn it into
		# UserData objects and return a list of those
		# else return an empty list
		if os.path.isfile(path):
			with open(path, mode='rt', encoding='utf-8') as file:
				data = json.load(file)
				log.info('read from file')

		else:
			log.info("file didn't exist; using empty dict")
			data = {}

		userDatas = []

		for userID in data.keys():
			userDatas.append(
				UserData(bot.get_user(int(userID)), data[userID]))

		return userDatas


	def saveUserData(self, path):

		userDatasDict = {}

		userDatasDict[str(self.user.id)] = self.toDict()
		log.debug(f"userData: {userDatasDict[str(self.user.id)]}")

		self._saveUserData(path, userDatasDict)


	@classmethod
	def _saveUserData(cls, path, userDatas):
		# check if the file exists
		# file doesn't exist
		if not os.path.isfile(path):
			# the file doesn't exist; create it, write in userdata

			folder = path[:path.rfind('/')]
			if not os.path.exists(folder):
				os.mkdir(folder)
				log.debug(f'Created folder: {folder}')


			with open(path, mode='x', encoding='utf-8') as file:
				json.dump(userDatas, file, indent=4)
				log.info(f'Created and wrote to file: {path}')

		# file does exist
		else:
			# the file does exist; read it, insert new userdata, write to file
			with open(path, mode='r+t', encoding='utf-8') as file:
				# read file then move buffer back to the bigining
				fileUserDatas = json.load(file)
				file.seek(0)

				# write in userdata
				fileUserDatas.update(userDatas)
				# write to file
				log.debug(json.dumps(fileUserDatas))
				json.dump(fileUserDatas, file, indent=4)
				file.truncate()
				log.info(f'Wrote to existing file: {path}')


	@classmethod
	def saveUserDatas(cls, userDatas : list[UserData], path : str):
		"""
		save a list of userDatas to file @ path
		path:
			the file, including path, to save to
		userDatas:
			a list of UserData objects to save
		"""
		userDatasDict = {}

		for userData in userDatas:
			userDatasDict[str(userData.user.id)] = userData.toDict()
			log.debug(f"userData: {userDatasDict[str(userData.user.id)]}")

		log.debug(f'dict = {userDatasDict}')


		cls._saveUserData(path, userDatasDict)

