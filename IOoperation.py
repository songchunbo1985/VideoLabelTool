import numpy as np
import cv2
import sys
import signal
import copy
import os.path
from operator import itemgetter, attrgetter


def ReadAllRecordsIntoList(filename):
	recordsList = []
	if os.path.isfile(filename):
		f = open(filename, 'r')
		line = f.read().split('\n')
		for item in line:
			elems = item.split(',')
			if len(elems) == 5:
				recordsList.append((int(elems[0]), int(elems[1]), int(elems[2]), int(elems[3]), int(elems[4])))

	return recordsList


def WriteToFile(recordsList, filename):
	f = open(filename, 'w')
	for x in recordsList:
		f.write(str(x[0]) + "," + str(x[1]) + "," + str(int(x[2])) + "," + str(int(x[3])) + "," + str(int(x[4])) + '\n')


















