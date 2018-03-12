import numpy as np
import cv2

class Frame:
	def __init__(self, num, labelID):
		self.num = num
		self.ID = labelID
		self.lc = False
		self.mc = False
		self.rc = False

	def getNum(self):
		return self.num

	def getID(self):
		return self.ID

	def setNum(self, num):
		self.num = num

	def setID(self, ID):
		self.ID = ID

	def getLC(self):
		return self.lc

	def getMC(self):
		return self.mc

	def getRC(self):
		return self.rc

	def setLC(self, lc):
		self.lc = lc

	def setMC(self, mc):
		self.mc = mc

	def setRC(self, rc):
		self.rc = rc

	def constructTuple(self):
		return (self.num, self.ID, self.lc, self.mc, self.rc)
