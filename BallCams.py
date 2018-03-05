import numpy as np

class BallCamera:
	def __init__(self):
		self.start = 0
		self.end = 0
		self.lc = False
		self.mc = False
		self.rc = False
		#self.ID = (self.lc, self.mc, self.rc)

	def setStart(self, s):
		self.start = s

	def setEnd(self, e):
		self.end = e

	def setCamera(self, l, m, r):
		self.lc = l
		self.mc = m
		self.rc =r

	def getStart(self):
		return self.start

	def getEnd(self):
		return self.end

	def getlc(self):
		return self.lc


	def getmc(self):
		return self.mc


	def getrc(self):
		return self.rc

	def getID(self):
		return (self.getlc(), self.getmc(), self.getrc())
