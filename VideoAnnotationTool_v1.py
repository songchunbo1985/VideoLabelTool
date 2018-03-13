import numpy as np
import cv2
import sys
import signal
import copy
import os.path
from operator import itemgetter, attrgetter
import processingBar as pb
from Canvas import Canvas
from IOoperation import ReadAllRecordsIntoList, WriteToFile


#global variables
winName = 'Video_Annotation_Tool'	#Window's name


#Given a list of labels, this method will produce corresponding IDs from 0.
def LoadLabelsFromFile(filename):
	f = open(filename,"r")
	content = f.readlines()
	dictLabel = {}
	ID = 1
	for x in enumerate(content):
		length = len(x[1])
		if length != 1 and x[1][length-1] == '\n':
			dictLabel[x[1][:-1]] = ID
			ID += 1

	print('Establishing Label ID: ', dictLabel)
	return dictLabel


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



def LoadVideo(vName):
	print('Prepare video: ', vName)
	cap = cv2.VideoCapture(vName)
	return cap


#get the total frames in the given video	
def getVideoLength(cap):
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	return length - 1


def main(argv):
	print('Start Working...')
	LabelID = LoadLabelsFromFile(argv[-3])
	SubLabelID = LoadLabelsFromFile(argv[-2])
	cv2.namedWindow(winName, cv2.WINDOW_AUTOSIZE)
	
	caps = []
	for v in argv[:-4]:
		caps.append(LoadVideo(v))
	
	recordsList = ReadAllRecordsIntoList(argv[-4])
	start = 0
	if len(recordsList) != 0:
		start = recordsList[-1][0] + 1


	updateFramesFlag = False

	canvas = Canvas(2150, 900, caps, 30, 2, winName, LabelID, SubLabelID, updateFramesFlag)
	canvas.DumpRecordsToFrames(recordsList)
	canvas.LoadVideos()
	test = canvas.GetFrames()
	canvas.TestFrames()

	#while start < len(test):
	#for t in test:
	#	tuplet = test[start].constructTuple()
	#	recordsList.append(tuplet)
	#	start+=1
	recordsList = canvas.ConvertFramesToSimpleList()
	if updateFramesFlag:
		WriteToFile(recordsList, argv[-4], updateFramesFlag)
	else:
		WriteToFile(recordsList, argv[-1], updateFramesFlag)


if __name__ == '__main__':
	main(sys.argv[1:])
