#ball left camera (255,255,0),press 'z'
#ball middle camera (255,0,255),press 'x'
#ball right camera (0,255,255), press 'y'
#ball unknown position (0,0,0)


import numpy as np
import cv2
import sys
import signal
import copy
from operator import itemgetter, attrgetter

from annotationStruct import Triplet
from BallCams import BallCamera


BallFrameFile = "ball.txt"

WidthSet = 600
wName = 'video'
Gcount = 0
GframeCount = 0
Categories = 0
cutlist = [0]
colorChoice = 0
GColor = (0,0,0)
GColorChoiceHist = []
paceSetting = 30
bl = BallCamera()
bm = BallCamera()
br = BallCamera()
BallCameraPos = []

#Given a list of labels, this method will produce corresponding IDs from 0.
def LoadLabelsFromFile(filename, labelIDList):
	f = open(filename,"r")
	content = f.readlines()
	dictLabel = {}
	ID = 0
	for x in enumerate(content):
		length = len(x[1])
		if length != 1 and x[1][length-1] == '\n':
			dictLabel[x[1][:-1]] = ID
			ID += 1

	print('Establishing Label ID: ', dictLabel)
	return dictLabel


		
#make triplet {start, end, ID}, seperate by a white space
def writeLabelClip(start, end, ID, outputName):
	f = open(outputName, "w")
	f.write(start + " " + end + " " + ID)



#get the total frames in the given video	
def getVideoLength(cap):
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	return length - 1


###this method should be removed.
#KeyBoard control
def PressKey(key, frameCount, breakStart, triplet):
	if key & 0xFF == ord('w'):
		input("Press the <ENTER> key to continue...")
	if key & 0xFF == ord('s') and breakStart == False:
		breakStart = True
		triplet2 = Triplet()
		if frameCount != 0:
			triplet2.setStart(frameCount)
			triplet.setEnd(frameCount - 1)
			###set ID for triplet
		print(frameCount)
		return breakStart, triplet, triplet2
	elif key & 0xFF == ord('e') and breakStart == True:
		print(frameCount)
		breakStart = False 
		triplet2 = Triplet()

		triplet.setEnd(frameCount)
		triplet2.setStart(frameCount + 1)

		return breakStart, triplet, triplet2

	return breakStart, Triplet(), Triplet()



def SettleColor():
	Colors = [(0,0,255), (0,255,0),(255,0,0),(0,255,255),(255,0,255),(255,255,0),(255,255,255)]
	#print(len(Colors))
	if Categories <= len(Colors):
		return Colors[0:Categories + 1]
	else:
		print('please make new colors labels.')
		return Colors



def PickColor():
	if colorChoice == 1:
		return GColor[1]
	elif colorChoice == 2:
		return GColor[2]
	elif colorChoice == 3:
		return GColor[3]
	elif colorChoice == 4:
		return GColor[4]
	else:
		return GColor[0]



def AssignColor(currentFrame, canvas, totalFrames):
	myColor = PickColor()
	h,w,c = canvas.shape
	wr = w/totalFrames	
	if currentFrame > cutlist[-1]:
		i = cutlist[-1]
		while i <= currentFrame:
			canvas = DrawVerticalLine(canvas, i, myColor[0], myColor[1], myColor[2])
			i += 1
	return canvas




#press key
def UPressKey(key, frameCount, pause, lf, mf, rf):
	global cutlist
	global colorChoice
	global GColorChoiceHist	
	global bl
	global bm
	global br
	cutIt = False
	
	global BallCameraPos

	cChoice = 0
		
	if key & 0xFF == ord('w') and pause == False:
		pause = True
	elif key & 0xFF == ord('w') and pause == True:
		pause = False
	#set cutting point
	if key & 0xFF == ord('s'):
		cutlist.append(frameCount)
		GColorChoiceHist.append(colorChoice)
		colorChoice = 0
		cChoice = 0
		#GColorChoiceHist.append(colorChoice)
		#print('invoke1')
		cutIt = True
	elif key & 0xFF == ord('1'):
		#print('press 1')
		colorChoice = 1
		cChoice = 1
		#GColorChoiceHist.append(cChoice)
		#print('invoke2')
		#if cutIt == True:
		#	GColorChoiceHist.append(colorChoice)
		#	cutIt = False
		#else:
		#	if len(GColorChoiceHist) != 0:
		#		del GColorChoiceHist[-1]
		#	GColorChoiceHist.append(colorChoice)

	elif key & 0xFF == ord('2'):
		#print('press 2')
		colorChoice = 2
		cChoice = 2
		#print('invoke3')
		#GColorChoiceHist.append(cChoice)
		#if cutIt == True:
		#	GColorChoiceHist.append(colorChoice)
		#	cutIt = False
		#else:
		#	if len(GColorChoiceHist) != 0:
		#		del GColorChoiceHist[-1]
		#	GColorChoiceHist.append(colorChoice)

	elif key & 0xFF == ord('0'):
		#print('press 0')
		colorChoice = 0
		cChoice = 0
		#print('invoke4')
		#GColorChoiceHist.append(cChoice)
		#if cutIt == True:
		#	GColorChoiceHist.append(colorChoice)
		#	cutIt = False
		#else:
		#	if len(GColorChoiceHist) != 0:
		#		del GColorChoiceHist[-1]
		#	GColorChoiceHist.append(colorChoice)
	elif key & 0xFF == ord('z'):
		if not lf:
			print('ball is captured in left camera at frame: ', frameCount)
			lf = True
			bl.setCamera(lf,mf,rf)
			bl.setStart(frameCount)
		else:
			#the ball is out of the left camera
			bl.setEnd(frameCount)
			tbl = copy.deepcopy(bl)
			BallCameraPos.append(tbl)
			bl = BallCamera()
			lf = False
	elif key & 0xFF == ord('x'):
		if not mf:
			print('ball is captured in middle camera at frame: ', frameCount)
			mf = True
			bm.setCamera(lf,mf,rf)
			bm.setStart(frameCount)
		else:
			#the ball is out of the middle camera
			bm.setEnd(frameCount)
			tbm = copy.deepcopy(bm)
			BallCameraPos.append(tbm)
			bm = BallCamera()
			mf = False
	elif key & 0xFF == ord('c'):
		if not rf:
			print('ball is captured in right camera at frame: ', frameCount)
			rf = True
			br.setCamera(lf,mf,rf)
			br.setStart(frameCount)
		else:
			#the ball is out of the right camera
			br.setEnd(frameCount)
			tbr = copy.deepcopy(br)
			BallCameraPos.append(tbr)
			br = BallCamera()
			rf = False

		
	else:
		cutIt = False
	#print('test!!! ', cChoice)
	#GColorChoiceHist.append(cChoice)
	return pause, lf, mf, rf



#def CapBallCam(frameCount, lf, mf, rf):
def FindVacancy(totalFrames):
	tempS = 0
	tempE = 0
	
	idx = 0
	ballres = []
	test = sorted(BallCameraPos, key=attrgetter('start'))
	print('len test: ', len(test))

	#if len(test) == 1:
	#	ballres.append(test[0])
	
	EndTimeStamp = 0
	while idx < len(test):
		if EndTimeStamp < test[idx].getStart():
			tempB = BallCamera()
			tempB.setStart(EndTimeStamp)
			tempB.setEnd(test[idx].getStart()-1)
			EndTimeStamp = test[idx].getEnd()+1

			ballres.append(tempB)
			ballres.append(test[idx])

		else:
			EndTimeStamp = test[idx].getEnd()
			ballres.append(test[idx])

		idx += 1

	idx = 0
	tempC = 0
	while idx < len(ballres):
		if tempC >= totalFrames - 1:
			break
		else:
			tempC = ballres[idx].getEnd()
			idx += 1
			
	if tempC < totalFrames - 1:
		tt = BallCamera()
		tt.setStart(tempC + 1)
		tt.setEnd(totalFrames - 1)
		ballres.append(tt)

		########
		#if test[idx].getStart() > test[idx-1].getEnd():
		#	#vacancy
		#	tempB = BallCamera()
		#	tempB.setStart(test[idx-1].getEnd())
		#	tempB.setEnd(test[idx].getStart()-1)
		#	ballres.append(test[idx-1])
		#	ballres.append(tempB)
		#else:
		#	ballres.append(test[idx-1])
		#if idx + 1 == len(test):
		#	ballres.append(test[idx])
	
		#idx += 1

	#if idx + 1 == len(test):
	#	ballres.append(test[idx])

	print('len res: ', len(ballres))

	for xx in ballres:
		print('b start ',xx.getStart())
		print('b end ', xx.getEnd())
	return ballres
	



def MakeTimeInterval():
	TimeIntervalList = []
	x = 1
	while x < len(cutlist):
		triplet = Triplet()
		triplet.setStart(cutlist[x - 1])
		triplet.setEnd(cutlist[x] - 1)
	
		TimeIntervalList.append(triplet)
		x += 1

	return TimeIntervalList



def ctr(x):
	global GframeCount
	if x != GframeCount:
		GframeCount = x

def pace(x):
	global paceSetting
	if x == 0:
		x = 1
	paceSetting = 121 - x



def CreateTrackBar(wName, nFrames, barName):
	cv2.createTrackbar(barName, wName, 0, nFrames, ctr)


def MakeCanvas(frames):
	height, width, channels = frames[0].shape
	ratio = height/width
	
	CHeight = int(WidthSet*ratio)
	#canvas = np.zeros((height + 200, width, channels), np.uint8)
	canvas = np.zeros((CHeight + 300, WidthSet * 3 + 50, channels), np.uint8)

	return canvas, CHeight, WidthSet



def DrawVerticalLine(img, w, r, g, b):
	height, width, channels = img.shape
	cv2.line(img, (w,0), (w,height), (r,g,b),1)
	return img




#A giant method
#load video
def LoadVideo(vName1, vName2, vName3, vName4, outputName, wName):
	print(vName1)
	cap = cv2.VideoCapture(vName1)
	cap2 = cv2.VideoCapture(vName2)
	cap3 = cv2.VideoCapture(vName3)
	cap4 = cv2.VideoCapture(vName4)

	NumFrames = getVideoLength(cap)
	print('total number of frames: ', NumFrames)

	NumFrames2 = getVideoLength(cap2)
	print('total number of frames: ', NumFrames2)

	NumFrames3 = getVideoLength(cap3)
	print('total number of frames: ', NumFrames3)

	NumFrames4 = getVideoLength(cap4)
	print('total number of frames: ', NumFrames4)

	count = 0
	frameCount = 0
	breakStart = False
	frames = []
	frames2 = []
	frames3 = []
	frames4 = []
	lf = False
	mf = False
	rf = False
	
	CreateTrackBar(wName, NumFrames - 1, 'Frame:')
	cv2.createTrackbar('Speed:', wName, 60, 120, pace)


	while(cap.isOpened()):
		ret, frame = cap.read()
		frames.append(frame)
		if not ret:
			break

	while(cap2.isOpened()):
		ret2, frame2 = cap2.read()
		frames2.append(frame2)
		if not ret2:
			break

	while(cap3.isOpened()):
		ret3, frame3 = cap3.read()
		frames3.append(frame3)
		if not ret3:
			break

	#while(cap4.isOpened()):
	#	ret4, frame4 = cap4.read()
	#	frames4.append(frame4)
	#	if not ret4:
	#		break


	global Gcount
	global GframeCount
	global GColorChoiceHist
	triplet = Triplet()
	pause = False
	global bl
	global bm
	global br

	canvas, uheight, uwidth = MakeCanvas(frames)
	r = 0
	g = 0
	b = 0

	cheight, cwidth, cchannels = canvas.shape
	
	while(1):
		if(frameCount + 1 > NumFrames):
			global cutlist
			cutlist.append(frameCount)
			triplet.end = frameCount
			GColorChoiceHist.append(colorChoice)

			TISet = MakeTimeInterval()
			#print(TISet)
			labels = AssignLabel(TISet)

			if bl.getStart() != 0 and bl.getEnd() == 0:
				bl.setEnd(frameCount)
				BallCameraPos.append(bl)
			elif bl.getEnd() != 0 and bl.getEnd() != frameCount:
				empball = BallCamera()
				empball.setEnd(frameCount)
				BallCameraPos.append(empball)
			if bm.getStart() != 0 and bm.getEnd() == 0:
				bm.setEnd(frameCount)
				BallCameraPos.append(bm)
			elif bm.getEnd() != 0 and bm.getEnd() != frameCount:
				empball = BallCamera()
				empball.setEnd(frameCount)
				BallCameraPos.append(empball)
			if br.getStart() != 0 and br.getEnd() == 0:
				br.setEnd(frameCount)
				BallCameraPos.append(br)
			elif br.getEnd() != 0 and br.getEnd() != frameCount:
				empball = BallCamera()
				empball.setEnd(frameCount)
				BallCameraPos.append(empball)
			if bl.getStart() == 0 and bm.getStart() == 0 and br.getStart() == 0 and len(BallCameraPos) == 0:
				empball = BallCamera()
				empball.setEnd(frameCount)
				BallCameraPos.append(empball)
			input("Press the <ENTER> key to continue...")
			#end of cutlist
			#print('test1: ', len(cutlist))
			#print('test2: ', len(GColorChoiceHist))	
			break
	
		#trackbar control	
		count = GframeCount
		histFrame = frameCount
		if(GframeCount != frameCount - 1):
			frameCount = GframeCount

		tempCut = 0

		#update cutlist
		#delete some cuts, if the trackbar moved before some existing cuts.
		#and delete corresponding boundaries.
		idx = 0
		tidx = cwidth + 1
		while idx < len(cutlist):
			if frameCount < cutlist[idx]:
				tidx = frameCount
				canvas[10:50, :, :] = DrawVerticalLine(canvas[10:50, :, :], cutlist[idx], 0, 0, 0)
				del cutlist[idx]
			else:
				idx += 1


		if cutlist[-1] != tempCut:
			tempCut = cutlist[-1]
			canvas[10:50, :, :] = DrawVerticalLine(canvas[10:50, :, :], tempCut, 255, 255, 255)

		if tempCut == 0 or GframeCount > tempCut:
			tcut = histFrame - 1
			#while tcut <= GframeCount:	
			#	canvas[50:180, :, :] = DrawVerticalLine(canvas[50:180, :, :], tcut, 0, 0, 255)
			#	tcut += 1
			canvas[10:50, :, :] = AssignColor(frameCount, canvas[10:50, :, :], NumFrames)

		if histFrame-1 > GframeCount:
			tcut = GframeCount
			while tcut <= histFrame:
				canvas[10:50, :, :] = DrawVerticalLine(canvas[10:50, :, :], tcut, 0, 0, 0)
				tcut += 1
			
		
		tf1 = cv2.resize(frames[frameCount], (uwidth, uheight), interpolation = cv2.INTER_CUBIC)
		tf2 = cv2.resize(frames2[frameCount], (uwidth, uheight), interpolation = cv2.INTER_CUBIC)
		tf3 = cv2.resize(frames3[frameCount], (uwidth, uheight), interpolation = cv2.INTER_CUBIC)
		#tf4 = cv2.resize(frames4[frameCount], (3 * uwidth, uheight), interpolation = cv2.INTER_CUBIC)
		
		canvas[200:200+uheight, 0:uwidth, :] = tf1
		canvas[200:200+uheight, uwidth+25:2*uwidth + 25, :] = tf2
		canvas[200:200+uheight, 2*uwidth+50:3*uwidth + 50, :] = tf3
		#canvas[250+uheight:250+(2*uheight), 25:3*uwidth+25, :] = tf4

		cv2.imshow(wName, canvas)
	
		cv2.setTrackbarPos('Frame:', wName, frameCount)
		key = cv2.waitKey(paceSetting)

		if key & 0xFF == ord('q'):
			del cutlist[:]
			labels = []
			break

		#breakStart, triplet, triplet2 = PressKey(key, frameCount, breakStart, triplet)
		pause, lf, mf, rf = UPressKey(key, frameCount, pause, lf, mf, rf)

		if(pause == False):
			frameCount += 1
			count += 1

	print(cutlist)
	cap.release()
	cv2.destroyAllWindows()
	return labels, NumFrames, NumFrames2, NumFrames3, NumFrames4




def AssignLabel(TISet):
	#for ti in TISet:
	#	start = ti.getStart()
	#	print(start)
	
	#test
	print('record length: ', len(GColorChoiceHist))
	print('record: ', GColorChoiceHist)	
	x = 0
	while x < len(TISet):
		TISet[x].setID(GColorChoiceHist[x])
		x += 1

	return TISet




#combine consecutive intervals which have a same Label
def CombineConsecutiveInv(labelset):
	result = []
	labels = labelset
	print('test labels length: ', len(labels))
	if len(labels) == 1:
		result.append(labels[0])

	x = 0
	while x < len(labels)-1:
		if labels[x].getID() != labels[x+1].getID():
			result.append(labels[x])
			if x + 2 == len(labels):
				result.append(labels[x+1])
		else:
			labels[x+1].setStart(labels[x].getStart())

			if x + 2 == len(labels):
				result.append(labels[x+1])		

		x += 1
	
	#test
	for r in result:
		print('start ', r.getStart())
		print('end ', r.getEnd())
		print('ID', r.getID())
	#test end

	return result



def WriteRecords(records, filename):
	f = open(filename, 'w')
	for record in records:
		f.write(str((record.getStart(),record.getEnd(),record.getID())) + '\n')



#Entry
def main(argv):
	LabelID = LoadLabelsFromFile(argv[4], "")
	global Categories
	global GColor
	#labels = []
	Categories = len(LabelID)
	GColor = SettleColor()
	print('The # of Categories is: ', Categories)

	print("Loading Video...")
	
	cv2.namedWindow(wName, cv2.WINDOW_AUTOSIZE)
	labels,n1,n2,n3,n4 = LoadVideo(argv[0], argv[1], argv[2], argv[3], argv[5], wName)
	result = CombineConsecutiveInv(labels)	

	ball = FindVacancy(n1)
	WriteRecords(ball, BallFrameFile)

	
	print('result: ', len(result))
	WriteRecords(result, argv[5])



if __name__ == '__main__':
	main(sys.argv[1:])
