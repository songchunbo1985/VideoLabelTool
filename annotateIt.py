import numpy as np
import cv2
import sys
import signal
import copy
import os.path
from operator import itemgetter, attrgetter
import processingBar as pb

wName = 'video'
GWindowWidth = 1600
#GWindowHeightMargin = 300
GWindowHeight = 800


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
			for line in fb:
				pass
			last = line.decode('ascii')
			
			i = 0
			for x in last:
				if x == ",":
					break
				i += 1	

			bff = int(last[:i])

	return bff


def UPressKey(key, pause, wfilename, bfilename, totalFrames):
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
		#print('g', GframeCount, ' ', colorChoice)
		#WriteFramesLabel(wfilename, GframeCount, colorChoice)
		#print('test ', len(cutlist))
		#print('test2 ', len(colorResult))
		#pause = True
	#elif key & 0xFF == ord('w') and pause == True:
		#pause = False
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
	#OrganizeCutlist()
	#print('cutlist: ', cutlist)
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

	if writeFlag:
		i = 0
		while i < len(cutlist) - 1:
			j = cutlist[i]
			while j < cutlist[i+1] or j == cutlist[-1]:
				WriteFramesLabel(wfilename, j, colorResult[i])
				j += 1
			i += 1	
		k = cutlist[-1]
		while k <= GframeCount:
			WriteFramesLabel(wfilename, k, colorChoice)		
			k += 1

		WriteBallCameraPos(bfilename, ballFrames)
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



def WriteBallCameraPos(bfilename, ballFrames):
	f = open(bfilename, 'a')
	for b in ballFrames:
		b1 = 0
		b2 = 0
		b3 = 0
		if b[1]:
			b1 = "1"
		else:
			b1 = "0"
		if b[2]:
			b2 = "1"
		else:
			b2 = "0"
		if b[3]:
			b3 = "1"
		else:
			b3 = "0"	
		f.write(str(b[0])+","+b1+","+b2+","+b3+'\n' )



def LoadVideo(vName1, vName2, vName3, wName, wfilename, bfilename):
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
	cv2.createTrackbar(barName1, wName, 0, numFrames1, ctr)

	canvas = makeCanvas(GWindowHeight)
	uWidth = int((GWindowWidth - 100)/3.0)

	pause = True
	fcount = 0
	trackFrameTimer = fcount

	tempR = 0
	tempG = 0
	tempB = 0	

	page = LoadFile(bfilename, wfilename)
	
	if page != 0:
		GframeCount = page
	else:
		GframeCount = 0

	while(cap1.isOpened() and cap2.isOpened() and cap3.isOpened()):
		global GframeCount

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
		canvas[200:200+uHeight2, uWidth + 50 : 2*uWidth + 50, :] = cv2.resize(frame2, (uWidth, uHeight2), interpolation = cv2.INTER_CUBIC)
		canvas[200:200+uHeight3, 2*uWidth + 100 : 3*uWidth + 100, :] = cv2.resize(frame3, (uWidth, uHeight3), interpolation = cv2.INTER_CUBIC)

		cv2.imshow(wName, canvas)
		cv2.setTrackbarPos(barName1, wName, fcount)
		key = cv2.waitKey(1)		

		if key & 0xFF == ord('q'):
			break
		pause = UPressKey(key, pause, wfilename, bfilename, numFrames1)


	cap1.release()
	cap2.release()
	cap3.release()	
	cv2.destroyAllWindows()		
		

def main(argv):
	print('Start Working...')
	cv2.namedWindow(wName, cv2.WINDOW_AUTOSIZE)

	LoadVideo(argv[0], argv[1], argv[2], wName, argv[3], argv[4])
	#print('test4: ', ballFrames)
	#WriteBallCameraPos(argv[4], ballFrames)


if __name__ == '__main__':
	main(sys.argv[1:])
