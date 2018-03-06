import numpy as np
import cv2


def DrawVerticalLine(img, w, r, g, b):
	height, width, channels = img.shape
	cv2.line(img, (w,0), (w,height), (r,g,b),1)
	return img

def DrawRectBar(img, start, end, r, g, b):
	height, width, channels = img.shape
	cv2.rectangle(img, (start,0), (end,height), (r,g,b), -1)
	return img	

def DrawProcessingBar(img, cutlist, currentPos, r, g, b, ratio):
	height, width, channels = img.shape
	if len(cutlist) == 0:
		return img
	if int(cutlist[-1] * ratio) < currentPos:
		DrawRectBar(img, int(cutlist[-1]*ratio), currentPos, r, g, b)
	
	DrawRectBar(img, currentPos, width, 0, 0, 0)
	return img



def DrawBallCameraPosBar(img, ballFrames,ratio, currentPos):
	height, width, channels = img.shape
	if len(ballFrames) == 0:
		return img
	else:
		#if ballFrames[-1] < currentPos:
			
		x = 1
		ts = 0
		while x < len(ballFrames):
			if ballFrames[ts][-3:] == ballFrames[x][-3:]:
				r = PickColor(ballFrames[x])[0]
				g = PickColor(ballFrames[x])[1]
				b = PickColor(ballFrames[x])[2]
				cv2.rectangle(img, (int(ballFrames[ts][0]*ratio), 0),(int(ballFrames[x][0]*ratio), height), (r,g,b),-1)
				x += 1
				#continue
			else:
				ts = x
				r = PickColor(ballFrames[x])[0]
				g = PickColor(ballFrames[x])[1]
				b = PickColor(ballFrames[x])[2]
				cv2.line(img, (int(x*ratio),0), (int(x*ratio),height), (r,g,b),1)
				x += 1		

	DrawRectBar(img, int(currentPos*ratio), width, 0,0,0)

	return img


def PickColor(x):
	#if len(ballFrames) == 0:
	#	return (0,0,0)
	#else:
	#	for x in ballFrames:
			#print(x[-3:])
	if x[-3:] == (False, False, False):
		#print('aaa', x[0])
		return (255,255,255)
	elif x[-3:] == (True, False, False):
		return (0,255,255)
	elif x[-3:] == (False, True, False):
		return (255,0,255)
	elif x[-3:] == (False, False, True):
		return (255,255,0)
	elif x[-3:] == (True, True, False):
		return (127,127,255)
	elif x[-3:] == (True, False, True):
		return (127,255,127)
	elif x[-3:] == (False, True, True):
		return (255,127,127)
	else:
		return (127,127,127)

	#return (0,0,0) 




def mytest():
	print('scb')
