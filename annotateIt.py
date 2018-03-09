import numpy as np
import cv2
import sys
import signal
import copy
import os.path
from operator import itemgetter, attrgetter
import processingBar as pb

wName = 'video'
GWindowWidth = 2050
#GWindowHeightMargin = 300
GWindowHeight = 800
paceSetting = 120

numFrames1 = 0
numFrames2 = 0
numFrames3 = 0
GframeCount = 0
cutlist = [0]
colorChoice = 1
ColorSet = [(127,127,127), (255,0,0), (0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(255,255,255)]
colorResult = []
lcb = False	#ball in left camera
mcb = False	#ball in middle camera
rcb = False	#ball in right camera
ballFrames = []


def makeCanvas(height):
	canvas = np.zeros((height, GWindowWidth, 3), np.uint8)
	return canvas


def OrganizeCutlist():
	global cutlist
	
	idx = 0
	while idx < len(cutlist):
		if GframeCount < cutlist[idx]:
			del cutlist[idx]
		else:
			idx += 1
	idx = 0
	while idx < len(cutlist) - 1:
		if cutlist[idx] == cutlist[idx + 1]:
			del cutlist[idx + 1]
		else:
			idx += 1


def OrganizeBallList(currentFrame, historyList):
	#print('hist: ', historyList)
	i = 0
	while i < len(historyList):
		if currentFrame < historyList[i][0]:
			del historyList[i]
		else:
			if currentFrame - 1 == historyList[-1][0]:
				historyList.append((currentFrame, lcb, mcb, rcb))
			i += 1
	#print('hist: ', historyList)
	return historyList


def LoadFile(bfilename, ffilename):
	bff = 0
	if os.path.isfile(bfilename) and os.path.isfile(ffilename):
		with open(bfilename, 'rb') as fb:
			line = fb.readlines()
	return bff


def UPressKey(key, pause, wfilename, bfilename, totalFrames, page, resultSet):
	global cutlist
	global colorChoice
	global colorResult

	global GframeCount	
	global ballFrames
	global lcb
	global mcb
	global rcb

	writeFlag = False
	if key & 0xFF == ord('w'):
		pause = True
		writeFlag = True
	if key & 0xFF == 32 and (not pause):
		pause = True
	elif key & 0xFF == 32 and pause:
		pause = False

	if key & 0xFF == ord('s'):
		cutlist.append(GframeCount)
		colorResult.append(colorChoice)
		colorChoice = 1
		if not pause:
			pause = True
	elif GframeCount == totalFrames - 1:
		cutlist.append(totalFrames-1)
		colorResult.append(colorChoice)	
	elif key & 0xFF == ord('1'):
		colorChoice = 1
	elif key & 0xFF == ord('2'):
		colorChoice = 2
	elif key & 0xFF == ord('0'):
		colorChoice = 0

	#ball in left camera
	if key & 0xFF == ord('b'):
		if not lcb:
			lcb = True
		else:
			lcb = False

	#ball in middle camera:
	elif key & 0xFF == ord('n'):
		if not mcb:
			mcb = True
		else:
			mcb = False

	#ball in right camera
	elif key & 0xFF == ord('m'):
		if not rcb:
			rcb = True
		else:
			rcb = False


	if key & 0xFF == 43:
		if GframeCount < numFrames1-50 and GframeCount < numFrames2-50 and GframeCount < numFrames3-50:
			GframeCount += 50
		else:
			GframeCount = min(numFrames1-1, numFrames2-1, numFrames3-1)
	elif key & 0xFF == 45:
		if GframeCount > 29:
			GframeCount -= 29
		else:
			GframeCount = 0
	elif key & 0xFF == 46:
		if GframeCount < numFrames1-20 and GframeCount < numFrames2-20 and GframeCount < numFrames3-20:
			GframeCount += 20
		else:
			GframeCount = min(numFrames1-1, numFrames2-1, numFrames3-1)
	elif key & 0xFF == 44:
		if GframeCount > 11:
			GframeCount -= 11
		else:
			GframeCount = 0



	if not pause:
		if len(ballFrames) == 0:
			ballFrames.append((GframeCount, lcb, mcb, rcb))
		else:
			jj = ballFrames[-1][0] + 1
			while jj <= GframeCount:
				ballFrames.append((jj, lcb, mcb, rcb))
				jj += 1

	#print('b1 ', ballFrames)
	ballFrames = OrganizeBallList(GframeCount, ballFrames)
	#print('b2 ', resultSet)
	i = 0
	if writeFlag:
		KeepRecord(resultSet, bfilename)
		writeFlag = False	

	return pause



def PickColor(colorChoice):
	return ColorSet[colorChoice]


def ctr(x):
	global GframeCount
	global ballFrames

	if x != GframeCount:
		GframeCount = x



#get the total frames in the given video	
def getVideoLength(cap):
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	return length - 1


def getFPS(video):
	# Find OpenCV version
	(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
	# With webcam get(CV_CAP_PROP_FPS) does not work.
	# Let's see for ourselves.

	if int(major_ver)  < 3 :
		fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
		print ("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
	else :
		fps = video.get(cv2.CAP_PROP_FPS)
		print ("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
    
	return fps 


def PauseVideoAtTheEnd(totalFrames, pause):
	if GframeCount == totalFrames:
		pause = True
	return pause


#the format of a label is "Frame NO. Label"
def WriteFramesLabel(wfilename, frameNO, label):
	f = open(wfilename, 'a')
	f.write(str(frameNO) + "," + str(label) + '\n')


def pace(x):
	global paceSetting
	if x == 0:
		x = 1
	paceSetting = 121 - x



def WriteBallCameraPos(bfilename, ballFrames, page):
	if page == 0:
		f = open(bfilename, 'w')
	else:
		f = open(bfilename, 'a')
	idx = page
	while idx < len(ballFrames):
		b1 = 0
		b2 = 0
		b3 = 0
		if ballFrames[1]:
			b1 = "1"
		else:
			b1 = "0"
		if ballFrames[2]:
			b2 = "1"
		else:
			b2 = "0"
		if ballFrames[3]:
			b3 = "1"
		else:
			b3 = "0"	
		f.write(str(ballFrames[idx][0])+","+b1+","+b2+","+b3+'\n' )
		idx += 1



def LoadVideo(vName1, vName2, vName3, wName, wfilename, bfilename):
	global numFrames1
	global numFrames2
	global numFrames3
	global GframeCount
	global colorChoice ###
	global lcb
	global mcb
	global rcb
	resultSet = []
	print('Prepare video: ', vName1)
	print('Prepare video: ', vName2)
	print('Prepare video: ', vName3)

	cap1 = cv2.VideoCapture(vName1)
	cap2 = cv2.VideoCapture(vName2)
	cap3 = cv2.VideoCapture(vName3)

	##Get # of frames for each video
	numFrames1 = getVideoLength(cap1)
	numFrames2 = getVideoLength(cap2)
	numFrames3 = getVideoLength(cap3)

	print('Frame1: ', numFrames1)
	print('Frame2: ', numFrames2)
	print('Frame3: ', numFrames3)

	fps1 = getFPS(cap1)
	fps2 = getFPS(cap2)
	fps3 = getFPS(cap3)

	barName1 = 'Frame'
	cv2.createTrackbar(barName1, wName, 0, numFrames1 - 1, ctr)
	cv2.createTrackbar('Speed:', wName, paceSetting, 120, pace)


	canvas = makeCanvas(GWindowHeight)
	uWidth = int((GWindowWidth - 100)/3.0)

	pause = True
	fcount = 0
	#trackFrameTimer = fcount

	tempR = 0
	tempG = 0
	tempB = 0	

	page, colorChoice, lcb, mcb, rcb, resultSet = LoadRecord(bfilename)
	if page != 0:
		GframeCount = page
	else:
		GframeCount = 0

	while(cap1.isOpened() and cap2.isOpened() and cap3.isOpened()):

		if pause:
			cap1.set(1, GframeCount)
			cap2.set(1, GframeCount)
			cap3.set(1, GframeCount)
			fcount = GframeCount
		else:
			fcount = GframeCount
			#print('frame: ', fcount)############################################
			cap1.set(1, fcount)
			cap2.set(1, fcount)
			cap3.set(1, fcount)
			fcount += 4

		if GframeCount == numFrames1 - 1:
			pause = True

		ret1, frame1 = cap1.read()
		ret2, frame2 = cap2.read()
		ret3, frame3 = cap3.read()

		if (not ret1) and (not ret2) and (not ret3):
			break
		
		fH1, fW1, fC1 = frame1.shape
		fH2, fW2, fC2 = frame2.shape
		fH3, fW3, fC3 = frame3.shape
		ratio1 = float(fH1)/float(fW1)
		ratio2 = float(fH2)/float(fW2)		
		ratio3 = float(fH3)/float(fW3)

		uHeight1 = int(uWidth * ratio1)
		uHeight2 = int(uWidth * ratio2)
		uHeight3 = int(uWidth * ratio3)


		#test
		tempR = PickColor(colorChoice)[0]
		tempG = PickColor(colorChoice)[1]
		tempB = PickColor(colorChoice)[2]
		canvas[10:30, :, :] = pb.DrawProcessingBar(canvas[10:30, :, :], cutlist, int(GframeCount*float(GWindowWidth)/float(numFrames1)), tempR,tempG,tempB, float(GWindowWidth)/float(numFrames1))

		OrganizeCutlist()

		canvas[50:70, :, :] = pb.DrawBallCameraPosBar(canvas[50:70, :, :], ballFrames, float(GWindowWidth)/float(numFrames1), GframeCount)
		
		#test end pass

		canvas[200:200+uHeight1, 0:uWidth, :] = cv2.resize(frame1, (uWidth, uHeight1), interpolation = cv2.INTER_CUBIC)
		canvas[200:200+uHeight2, uWidth + 20 : 2*uWidth + 20, :] = cv2.resize(frame2, (uWidth, uHeight2), interpolation = cv2.INTER_CUBIC)
		canvas[200:200+uHeight3, 2*uWidth + 40 : 3*uWidth + 40, :] = cv2.resize(frame3, (uWidth, uHeight3), interpolation = cv2.INTER_CUBIC)

		cv2.imshow(wName, canvas)
		cv2.setTrackbarPos(barName1, wName, fcount)
		key = cv2.waitKey(paceSetting)		

		if key & 0xFF == ord('q'):
			break
		pause = UPressKey(key, pause, wfilename, bfilename, numFrames1, fcount, resultSet)
		if not pause:
			resultSet = maintainResultSet(GframeCount, resultSet)
			#print(str(GframeCount), str(colorChoice), lcb, mcb, rcb)
			#print('result1 ', resultSet)
			resultSet.append((GframeCount, colorChoice, lcb, mcb, rcb))
			#print('result2 ', resultSet)
		#resultSet = maintainResultSet(GframeCount, resultSet)
		#print('debug1: ', resultSet)
		del frame1, frame2, frame3

	#print('resultSet ', resultSet)
	cap1.release()
	cap2.release()
	cap3.release()	
	cv2.destroyAllWindows()		


def KeepRecord(resultSet, bfilename):
	f = open(bfilename, 'w')
	for x in resultSet:
		b1 = 0
		b2 = 0
		b3 = 0
		if x[2]:
			b1 = "1"
		else:
			b1 = "0"
		if x[3]:
			b2 = "1"
		else:
			b2 = "0"
		if x[4]:
			b3 = "1"
		else:
			b3 = "0"	
		f.write(str(x[0])+","+str(x[1])+","+b1+","+b2+","+b3+'\n' )


def extractItems(line):
	y = line.split(',')
	return y


#seek the last line
#return next frame, play/break, left camera, middle camera, right camera. 
def LoadRecord(bfilename):
	currentF = 0
	currentPB = 1
	currentLC = 0
	currentMC = 0
	currentRC = 0

	resSet = []

	if os.path.isfile(bfilename):
		f = open(bfilename, 'r')
		line = f.read().split('\n')
		for item in line:
			elems = item.split(',')
			if len(elems) == 5:
				resSet.append((int(elems[0]), int(elems[1]), int(elems[2]), int(elems[3]), int(elems[4])))

	if os.path.isfile(bfilename):
		f = open(bfilename, 'r')
		line = f.readlines()
		y = extractItems(line[-1])	
		currentF = int(y[0])
		currentPB = int(y[1])
		currentLC = int(y[2])
		currentMC = int(y[3])
		currentRC = int(y[4])
	else:
		resSet = []
		return currentF, currentPB, currentLC, currentMC, currentRC, resSet
	
	return currentF + 1, currentPB, currentLC, currentMC, currentRC, resSet


def maintainResultSet(GframeCount, resultSet):
	if len(resultSet) < GframeCount and len(resultSet) != 0:
		tc = resultSet[-1][1]
		tlb = resultSet[-1][2]
		tmb = resultSet[-1][3]
		trb = resultSet[-1][4]

		fce = GframeCount
		fcs = len(resultSet)
		while fcs < fce:
			resultSet.append((fcs, tc, tlb, tmb, trb))
			fcs += 1

		return resultSet
	elif len(resultSet) > GframeCount:
		fcs = 0
		while fcs < len(resultSet):
			if (fcs > GframeCount):
				del resultSet[fcs]
			else:
				fcs+=1
		return resultSet
	#elif len(resultSet) == 0:
	#	resultSet.append((0,colorChoice,lcb,mcb,rcb))
	#	return resultSet
	else:
		return resultSet

def main(argv):
	print('Start Working...')
	cv2.namedWindow(wName, cv2.WINDOW_AUTOSIZE)

	LoadVideo(argv[0], argv[1], argv[2], wName, argv[3], argv[4])


if __name__ == '__main__':
	main(sys.argv[1:])
