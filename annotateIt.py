import numpy as np
import cv2
import sys
import signal
import copy
import os.path
from operator import itemgetter, attrgetter
import processingBar as pb

wName = 'video'
GWindowWidth = 1800
#GWindowHeightMargin = 300
GWindowHeight = 800
paceSetting = 30

GframeCount = 0
cutlist = [0]
colorChoice = 0
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
	i = 0
	while i < len(historyList):
		if currentFrame < historyList[i][0]:
			del historyList[i]
		else:
			if currentFrame - 1 == historyList[-1][0]:
				historyList.append((currentFrame, lcb, mcb, rcb))
			i += 1
	return historyList


def LoadFile(bfilename, ffilename):
	bff = 0
	if os.path.isfile(bfilename) and os.path.isfile(ffilename):
		with open(bfilename, 'rb') as fb:
			#for line in fb:
			#	pass
			line = fb.readlines()
		last = line
		#last = last.decode('ascii')
			
		#i = 0
		#for x in last:
		#	if x == ",":
		#		break
		#	i += 1	

		#bff = last[:i]
		#print('last ',last)

	return bff


def UPressKey(key, pause, wfilename, bfilename, totalFrames, page, resultSet):
	global cutlist
	global colorChoice
	global colorResult
	
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
		#colorChoice = 0
		cutlist.append(GframeCount)
		colorResult.append(colorChoice)
		colorChoice = 0
		if not pause:
			pause = True
	elif GframeCount == totalFrames - 1:
		cutlist.append(totalFrames-1)
		colorResult.append(colorChoice)	
	if key & 0xFF == ord('1'):
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
	if key & 0xFF == ord('n'):
		if not mcb:
			mcb = True
		else:
			mcb = False

	#ball in right camera
	if key & 0xFF == ord('m'):
		if not rcb:
			rcb = True
		else:
			rcb = False

	if not pause:
		if len(ballFrames) == 0:
			ballFrames.append((GframeCount, lcb, mcb, rcb))
		else:
			jj = ballFrames[-1][0] + 1
			while jj <= GframeCount:
				ballFrames.append((jj, lcb, mcb, rcb))
				jj += 1
		#ballFrames.append((GframeCount, lcb, mcb, rcb))

	ballFrames = OrganizeBallList(GframeCount, ballFrames)
	#pb.PickColor(ballFrames)
	i = 0
	if writeFlag:
		KeepRecord(resultSet, bfilename)
		#i = page
		#while i < len(cutlist) - 1:
		#	j = cutlist[i]
		#	while j < cutlist[i+1] or j == cutlist[-1]:
		#		WriteFramesLabel(wfilename, j, colorResult[i])
		#		j += 1
		#	i += 1	
		#k = cutlist[-1]
		#while k <= GframeCount:
		#	WriteFramesLabel(wfilename, k, colorChoice)		
		#	k += 1

		#WriteBallCameraPos(bfilename, ballFrames, page)
		writeFlag = False	

	return pause



def PickColor(colorChoice):
	#print('test ', colorChoice) pass
	#print('test ', ColorSet[colorChoice]) pass
	return ColorSet[colorChoice]


def ctr(x):
	global GframeCount
	global ballFrames
#	if x > ballFrames[-1][0]:
#		i = ballFrames[-1][0]
#		t = ballFrames[-1]
#		while i <= x:
#			ballFrames.append(t)
#			i += 1
#	elif x < ballFrames[-1][0]:
#		i = ballFrames[-1][0]
#		while i > x:
#			del ballFrames[-1]
#			i -= 1

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
	#for b in ballFrames:
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
	trackFrameTimer = fcount

	tempR = 0
	tempG = 0
	tempB = 0	

	#page = 0#LoadFile(bfilename, wfilename)
	page, colorChoice, lcb, mcb, rcb, resultSet = LoadRecord(bfilename)
	if page != 0:
		GframeCount = page
	else:
		GframeCount = 0

	while(cap1.isOpened() and cap2.isOpened() and cap3.isOpened()):
		#global GframeCount

		if pause:
			cap1.set(1, GframeCount)
			cap2.set(1, GframeCount)
			cap3.set(1, GframeCount)
			#trackFrameTimer = fcount
			fcount = GframeCount
			#GframeCount = fcount
		else:
			#trackFrameTimer = fcount - 1
			fcount = GframeCount
			cap1.set(1, fcount)
			cap2.set(1, fcount)
			cap3.set(1, fcount)
			#GframeCount = fcount
			#print('frame: ', GframeCount)
			fcount += 1

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
			print(str(GframeCount), str(colorChoice), lcb, mcb, rcb)
			resultSet.append((GframeCount, colorChoice, lcb, mcb, rcb))
		resultSet = maintainResultSet(GframeCount, resultSet)
		#print(resultSet)
		del frame1, frame2, frame3
			#print('released.')
		#maintainResultSet(GframeCount, resultSet)
		#resultSet.append()
	#print('gf: ', GframeCount)
	#resultSet = maintainResultSet(GframeCount, resultSet)
	#print('result: ', resultSet)

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
	#print(y)
	return y


#seek the last line
#return next frame, play/break, left camera, middle camera, right camera. 
def LoadRecord(bfilename):
	currentF = 0
	currentPB = 0
	currentLC = 0
	currentMC = 0
	currentRC = 0

	resSet = []

	if os.path.isfile(bfilename):
		f = open(bfilename, 'r')
		line = f.read().split('\n')
	#print('line: ', line)
	#for item in line.split(','):
		for item in line:
			#print('test1 ', item)	
			elems = item.split(',')
			#print('test1 ', item)
			if len(elems) == 5:
				#print('test3 ', elems)
				resSet.append((int(elems[0]), int(elems[1]), int(elems[2]), int(elems[3]), int(elems[4])))
	#print('test2 ', resSet)	

	if os.path.isfile(bfilename):
		f = open(bfilename, 'r')
		line = f.readlines()
		#print('line: ', line[-1])
		y = extractItems(line[-1])	
		currentF = int(y[0])
		currentPB = int(y[1])
		currentLC = int(y[2])
		currentMC = int(y[3])
		currentRC = int(y[4])
	else:
		#print('empty')
		resSet = []
		return currentF, currentPB, currentLC, currentMC, currentRC, resSet
	
	#print('test ',currentF, currentPB, currentLC, currentMC, currentRC)
	return currentF + 1, currentPB, currentLC, currentMC, currentRC, resSet


def maintainResultSet(GframeCount, resultSet):
	if len(resultSet) < GframeCount:
		tc = resultSet[-1][1]
		tlb = resultSet[-1][2]
		tmb = resultSet[-1][3]
		trb = resultSet[-1][4]

		fce = GframeCount
		fcs = len(resultSet)
		while fcs <= fce:
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
	else:
		return resultSet

def main(argv):
	print('Start Working...')
	cv2.namedWindow(wName, cv2.WINDOW_AUTOSIZE)

	LoadVideo(argv[0], argv[1], argv[2], wName, argv[3], argv[4])
	#print('test4: ', ballFrames)
	#WriteBallCameraPos(argv[4], ballFrames)


if __name__ == '__main__':
	main(sys.argv[1:])
