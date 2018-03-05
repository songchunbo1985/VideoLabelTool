import numpy as np


class Triplet:
	def __init__(self):
		self.start = 0
		self.end = 0
		self.id = 0

	def setStart(self, s):
		self.start = s

	def setEnd(self, e):
		if e >= self.start:
			self.end = e
		else:
			print('end must be greater than start.')

	def setID(self, newID):
		self.id = newID

	def getStart(self):
		return self.start

	def getEnd(self):
		return self.end

	def getID(self):
		return self.id
