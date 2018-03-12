import numpy as np
import cv2
from Label import Frame
import processingBar as pb
import math


class Canvas:
	#width, height are about the size of the canvas;
	#Videos is a list of videos
	def __init__(self, width, height, Videos, initSpeed, initStep, wName, labels):
		self.width = width		#default 2150 in practice
		self.height = height		#default 900 in practice
		self.Videos = Videos
		self.speed = initSpeed
		self.step = initStep
		self.default_margin = 25
		self.toleranceW = 650		#minimum width for each video region
		self.toleranceH = 650		#minimum height for each video region
		self.canvas = np.zeros((height, width, 3), np.uint8)
		self.frameIDX = 0	
		self.wName = wName
		self.pause = True
		self.Labels = labels
		self.Frames = []
		#self.Frames.append(Frame(0,1))
		self.tempID = 0
		
		self.l1 = 0
		self.l2 = 0
		self.l3 = 0	
		self.barName1 = "Frame"
		self.barName2 = "Speed"

		self.lc = False
		self.mc = False
		self.rc = False


	#the length of records cannot be 0!
	def DumpRecordsToFrames(self, records):
		for r in records:
			frame = Frame(r[0], r[1])
			frame.setLC(bool(r[2]))
			frame.setMC(bool(r[3]))
			frame.setRC(bool(r[4]))
			self.Frames.append(frame)

		if len(records) != 0:
			self.frameIDX = self.Frames[-1].getNum() + 1
			print('test2 ', self.frameIDX)
			self.lc = self.Frames[-1].getLC()
			self.mc = self.Frames[-1].getMC()
			self.rc = self.Frames[-1].getRC()
			self.tempID = self.Frames[-1].getID()


	def ConvertFramesToSimpleList(self):
		recordsList = []
		for f in self.Frames:
			tuplet = f.constructTuple()
			recordsList.append(tuplet)

		return recordsList

	
	def GetFrames(self):
		return self.Frames
	
	
	def TestFrames(self):
		temp = -1
		for f in self.Frames:
			if f.getNum() - 1 != temp:
				print('error!!!!!!!!!!!!!!!!! ', f.getNum())
				break
			else:
				temp = f.getNum()

	
	#This method is used for erasing the content after # of frames.
	#fNum is the # of current frame in self.Frames.
	def ErasingFrames(self, fNum):
		length = len(self.Frames)
		del self.Frames[fNum-length:]

		
	#fNum is the # of current frame in self.Frames.
	def FillingFrames(self, fNum):
		length = len(self.Frames)
		if length != 0:
			frameLast = self.Frames[-1]
			##print('last 1st: ', frameLast.getNum())
			
		else:
			frameLast = Frame(0,0)
		l = length
		while l < fNum:
			##print('insert at ', l)
			aFrame = Frame(l, frameLast.getID())
			aFrame.setLC(self.lc)
			aFrame.setMC(self.mc)
			aFrame.setRC(self.rc)
			self.Frames.append(aFrame)	
			l += 1
	

	def UpdateFrames(self):
		if self.frameIDX < len(self.Frames):
			self.ErasingFrames(self.frameIDX)
		elif self.frameIDX > len(self.Frames):
			self.FillingFrames(self.frameIDX)	


	def GetLabelNums(self):
		return len(self.Labels)


	def GetVideoSize(self, cap):
		vWidth = cap.get(3)		#get frame width
		vHeight = cap.get(4)		#get frame height
		
		#get the total frames in the given video	
		length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		return vWidth, vHeight, length


	def GetRatioBetweenWidthHeight(self, vWidth, vHeight):
		ratio = vWidth/vHeight
		return ratio


	#suppose all videos have same size -- width and height
	def ResizeToFitCanvas(self, cap, width_threshold):
		vWidth, vHeight, length = self.GetVideoSize(cap)
		if vWidth < width_threshold:
			return vWidth, vHeight, length
		else:
			#resize it to width_threshold, and keep the ratio
			ratio = self.GetRatioBetweenWidthHeight(vWidth, vHeight)
			height_threshold = int(width_threshold / ratio)
			return width_threshold, height_threshold, length


	def ResizeFrame(self, frame, w, h):
		resFrame = cv2.resize(frame, (w, h), interpolation = cv2.INTER_CUBIC)
		return resFrame


	def KeyControl(self, k, signal_write, theFrame):
		if k & 0xFF == ord('w'):
			self.pause = True
			signal_write = True

		if k & 0xFF == 32 and (not self.pause):
			self.pause = True
		elif k & 0xFF == 32 and self.pause:
			self.pause = False

		keyIterator = 1
		while keyIterator <= self.GetLabelNums():
			if k & 0xFF == 48 + keyIterator:
				theFrame.setID(keyIterator)
				self.tempID = keyIterator
				break
			elif k & 0xFF == 48:
				theFrame.setID(0)
				self.tempID = 0
				break
			keyIterator += 1	

		if k & 0xFF == ord('b') and not self.lc:
			self.lc = True
		elif k & 0xFF == ord('b') and self.lc:
			self.lc = False

		if k & 0xFF == ord('n') and not self.mc:
			self.mc = True
		elif k & 0xFF == ord('n') and self.mc:
			self.mc = False
		
		if k & 0xFF == ord('m') and not self.rc:
			self.rc = True
		elif k & 0xFF == ord('m') and self.rc:
			self.mc = False

		theFrame.setLC(self.lc)
		theFrame.setMC(self.mc)
		theFrame.setRC(self.rc)

		if k & 0xFF == 43:
			if self.frameIDX < self.l1 - 50 and self.frameIDX < self.l2 - 50 and self.frameIDX < self.l3 - 50:
				self.frameIDX += 50
			else:
				self.frameIDX = min(self.l1 - 1, self.l2 - 1, self.l3 - 1)
		elif k & 0xFF == 44:
			if self.frameIDX > 11:
				self.frameIDX -= 11
			else:
				self.frameIDX = 0
		elif k & 0xFF == 45:
			if self.frameIDX > 29:
				self.frameIDX -= 29
			else:
				self.frameIDX = 0
		elif k & 0xFF == 46:
			if self.frameIDX < self.l1 - 20 and self.frameIDX < self.l2 - 20 and self.frameIDX < self.l3 - 20:
				#print('press at ', self.frameIDX)
				self.frameIDX += 20
			else:
				self.frameIDX = min(self.l1 - 1, self.l2 - 1, self.l3 - 1)
		theFrame.setNum(self.frameIDX)


		return theFrame


	#def ReadVideo(self, region, cap, w, h):
	#	cap.set(1, self.frameIDX)
	#	ret, frame = cap.read()
	#		
	#	if not ret:
	#		return -1,-1
	#
	#	region = self.ResizeFrame(frame, w, h)
	#	
	#	if not self.pause:
	#		self.frameIDX += self.step
	#
	#	return 1, region

	def PickCategoryColor(self, idx, switch):
		if idx >= len(self.Frames):
			return (0,0,0)
		if switch:
			x = self.Frames[idx].getID()
		
			if x == 1:
				return (255, 0, 0)
			elif x == 2:
				return (0, 255, 0)
			elif x == 0:
				return (0, 0, 255)
			else:
				return (0, 0, 0)
		else:
			camPos = (self.Frames[idx].getLC(), self.Frames[idx].getMC(), self.Frames[idx].getRC())		
			if camPos == (False, False, False):
				return (128,128,128)
			elif camPos == (True, False, False):
				return (0, 128, 128)
			elif camPos == (False, True, False):
				return (128, 0, 128)
			elif camPos == (False, False, True):
				return (128, 128, 0)
			elif camPos == (True, True, False):
				return (0, 0, 128)
			elif camPos == (True, False, True):
				return (0, 128, 0)
			elif camPos == (False, True, True):
				return (128, 0, 0)
			elif camPos == (True, True, True):
				return (0, 0, 0)
			else:
				return (0,0,0)


	def DrawProcessBar(self, region, switch):
		ratio = self.width/min(self.l1, self.l2, self.l3)
		h,_,_ = region.shape
		x = 1
		temp_start = 0
		
		while switch and x < len(self.Frames):
			if self.Frames[x-1].getID() != self.Frames[x].getID():
				temp_start = math.floor((x-1) * ratio)
			color = self.PickCategoryColor(x-1, switch)
			cv2.rectangle(region, (temp_start, 0), (math.ceil(x * ratio), h), color, -1 )
			cv2.rectangle(region, (math.floor(x * ratio), 0), (self.width, h), (0,0,0), -1 )
			x += 1

		x = 1
		temp_start = 0
		while not switch and x < len(self.Frames):
			#print('test ', temp_start)
			if self.Frames[x-1].constructTuple()[-3:] != self.Frames[x].constructTuple()[-3:]:
				temp_start = math.floor((x-1) * ratio)
				#print('test ', temp_start)
			color = self.PickCategoryColor(x-1, switch)
			cv2.rectangle(region, (temp_start, 0), (math.ceil(x * ratio), h), color, -1 )
			cv2.rectangle(region, (math.floor(x * ratio), 0), (self.width, h), (0,0,0), -1 )
			x += 1
		return region


	def pace(self, x):
		if x == 0:
			x = 1
		self.speed = 121 - x


	def ctr(self, x):
		if x != self.frameIDX:
			self.pause = True
			self.frameIDX = x
		
	
	def LoadVideos(self):
		#get target Size
		if len(self.Videos) == 0:
			return
		w, h, self.l1 = self.ResizeToFitCanvas(self.Videos[0], self.toleranceW)  
		_,_,self.l2 = self.GetVideoSize(self.Videos[1])
		_,_,self.l3 = self.GetVideoSize(self.Videos[2]) 		

		
		cv2.createTrackbar(self.barName1, self.wName, 0, min(self.l1, self.l2, self.l3) - 1, self.ctr)
		cv2.createTrackbar(self.barName2, self.wName, self.speed, 120, self.pace)

		#extract canvas layout
		regionList = self.DesignCanvasLayout(w, h)
		if (len(regionList) != len(self.Videos)):
			print('something wrong!')
			return
		else:
			while(self.Videos[0].isOpened() and self.Videos[1].isOpened() and self.Videos[2].isOpened()):
				self.Videos[0].set(1, self.frameIDX)
				self.Videos[1].set(1, self.frameIDX)
				self.Videos[2].set(1, self.frameIDX)				

				ret1, frame1 = self.Videos[0].read()
				ret2, frame2 = self.Videos[1].read()
				ret3, frame3 = self.Videos[2].read()

				if (not ret1) and (not ret2) and (not ret3):
					break
				
				framesSet = [frame1, frame2, frame3]
				self.canvas[10:30,:,:] = self.DrawProcessBar(self.canvas[10:30,:,:], True)
				self.canvas[45:65,:,:] = self.DrawProcessBar(self.canvas[45:65,:,:], False)
				for i in range(3):
					self.canvas[200 : 200 + h, i * (w + self.default_margin) : i * (w + self.default_margin) + w, : ] = self.ResizeFrame(framesSet[i], w, h)

				cv2.imshow(self.wName, self.canvas)
				cv2.setTrackbarPos(self.barName1, self.wName, self.frameIDX)
				#self.UpdateFrames()
				key = cv2.waitKey(self.speed)
				
						
				theFrame = Frame(self.frameIDX, self.tempID)
				#print('frameIDX: ', self.frameIDX)
				theFrame = self.KeyControl(key, False, theFrame)

				if not self.pause:
					#print('frameIDX: ', self.frameIDX)
					self.UpdateFrames()
					self.Frames.append(theFrame)
					##print('frame: ', theFrame.getNum(), '     idx: ', self.frameIDX)
					#self.UpdateFrames()
					#self.TestFrames()
					self.frameIDX += self.step
					#self.UpdateFrames()
				else:
					self.UpdateFrames()

				if key & 0xFF == ord('q'):
					break
				
				del frame1, frame2, frame3, framesSet[:]

		return
			

	def DesignCanvasLayout(self, w, h):
		regionList = []

		#default margin between two sub-video regions is set to 25 pixels
		if (self.width - (2 * self.default_margin))/len(self.Videos) >= self.toleranceW:
			for i in range(len(self.Videos)):
				#region = self.canvas[200 : 200 + h, i * (w + self.default_margin) : i * (w + self.default_margin) + w, : ]
				#regionList.append(region)
				regionList.append(self.canvas[200 : 200 + h, i * (w + self.default_margin) : i * (w + self.default_margin) + w, : ])
		else:
			print('too many videos to play in the same window!')

		return regionList
