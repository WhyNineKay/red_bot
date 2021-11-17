import os
import json
import logging
from datetime import *
from typing import overload
import discord

import globs

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(globs.LOGLEVEL)


class UserData():
	pass


class ItemType():
	type: str
	desciption: str
	cost: int


	def __init__(self, type, description, cost):
		self._type = type
		self._description = description
		self._cost = cost


	@property
	def type(self):
		return self._type

	@property
	def description(self):
		return self._description

	@property
	def cost(self):
		return self._cost


itemTypes = {
	"test": ItemType("test", "description", 1)
}


class Item():
	"""
	An item to go into UserData.inventory
	"""
	type: str
	qty: int


	def __init__(self, type):
		self.type = type
		self.qty = 1




	def describe(self):
		return f"Quantity: {self._qty}\n{self.description}"



class UserData():
	"""
	A set of data associated with a user, specific to guild
	"""

	wallet : int
	bank : int
	walletMax : int
	lastDaily : date
	lastDeposit : date
	lastSteal : datetime
	inventory : list[Item]

	# a few values that are useful to be able to access
	bankMaxMul = 5
	walletMinMul = 0.1
	dailyAmount = 500
	minWallet = dailyAmount * 4
	defUserData = {
		'wallet': minWallet,
		'bank': 0
	}


	def __init__(self, user, userData):
		self._user = user
		self._wallet = userData['wallet']
		self._bank = userData['bank']
		self._walletMax = userData.get('walletMax', self._wallet)

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


		self._inventory = userData.get('inventory', [])


	def toDict(self):
		return {
			"wallet": self._wallet,
			"bank": self._bank,
			"walletMax": self._walletMax,
			"lastDaily": self._lastDaily.isoformat(),
			"lastDeposit": self._lastDeposit.isoformat(),
			"lastSteal": self._lastSteal.isoformat(),
			"inventory": self._inventory
		}


	@property
	def user(self):
		return self._user

	@property
	def wallet(self):
		return self._wallet

	@wallet.setter
	def wallet(self, wallet : int):
		self._wallet = wallet
		if wallet > self._walletMax:
			self._walletMax = wallet

	@property
	def bank(self):
		return self._bank

	@bank.setter
	def bank(self, bank : int):
		self._bank = bank

	@property
	def walletMax(self):
		return self._walletMax

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

	# method for adding an item to the inventory property
	def invAddItem(self, type : str, qty=1):
		try:
			self._inventory[self._inventory.index(type)].qty += qty

		except ValueError:
			index = len(self._inventory)
			self._inventory.append(type)
			self._inventory[index].qty = qty


	# method for removing an item from the inventory property
	# will return the ammount removed
	def invRemoveItem(self, item : Item, qty=1):
		try:
			# set the items index then use to remove 1 from inventory
			index = self._inventory.index(item)
			self._inventory[index].qty -= qty

			if self._inventory[index].qty <= 0:
				qty = qty + self._inventory.qty
				self._inventory.pop(index)

			return qty
		except ValueError:
			return 0


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

