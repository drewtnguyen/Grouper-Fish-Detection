# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class CentroidTracker():
	def __init__(self, maxDisappeared=4, frame_size = (1920, 1080)): 
		# initialize the next unique object ID along with two ordered
		# dictionaries used to keep track of mapping a given object
		# ID to its centroid and number of consecutive frames it has
		# been marked as "disappeared", respectively
		self.frame_size = frame_size #(W,H)
		self.nextObjectID = 0
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()
		self.visible_detection_nums = OrderedDict() #keeps the detection number and object id of just those seen
		self.objects_rects = OrderedDict()

		# store the number of maximum consecutive frames a given
		# object is allowed to be marked as "disappeared" until we
		# need to deregister the object from tracking
		self.maxDisappeared = maxDisappeared

	def register(self, centroid, detect_num, rect):
		# when registering an object we use the next available object
		# ID to store the centroid
		self.objects[self.nextObjectID] = centroid
		self.objects_rects[self.nextObjectID] = rect
		self.visible_detection_nums[self.nextObjectID] = detect_num
		self.disappeared[self.nextObjectID] = 0
		self.nextObjectID += 1


	def deregister(self, objectID):
		# to deregister an object ID we delete the object ID from
		# both of our respective dictionaries
		del self.objects[objectID]
		del self.disappeared[objectID]
		del self.objects_rects[objectID]

	def update(self, num_rects):

		# check to see if the list of input bounding box rectangles
		# is empty
		if len(num_rects) == 0:
			# loop over any existing tracked objects and mark them
			# as disappeared
			for objectID in list(self.disappeared.keys()):
				self.disappeared[objectID] += 1

				# if we have reached a maximum number of consecutive
				# frames where a given object has been marked as
				# missing, deregister it
				if self.disappeared[objectID] > self.maxDisappeared:
					self.deregister(objectID)
			self.visible_detection_nums = OrderedDict()

			# return early as there are no centroids or tracking info
			# to update
			return (self.visible_detection_nums, self.objects)

		detect_nums = [elt[0] for elt in num_rects]
		rects = [elt[1] for elt in num_rects]

		# initialize an array of input centroids for the current frame
		inputCentroids = np.zeros((len(rects), 2), dtype="int")
		inputRects = np.array(rects, dtype='int')

		# loop over the bounding box rectangles
		for (i, (startX, startY, endX, endY)) in enumerate(rects):
			# use the bounding box coordinates to derive the centroid
			cX = int((startX + endX) / 2.0)
			cY = int((startY + endY) / 2.0)
			inputCentroids[i] = (cX, cY)

		# if we are currently not tracking any objects take the input
		# centroids and register each of them
		if len(self.objects) == 0:
			for i in range(0, len(inputCentroids)):
				self.register(inputCentroids[i], detect_nums[i], inputRects[i])

		# otherwise, are are currently tracking objects so we need to
		# try to match the input centroids to existing object
		# centroids
		else:
			# grab the set of object IDs and corresponding centroids
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())
			objectRects = list(self.objects_rects.values())
			unmatchedRows, unmatchedCols = match_centroids(self, detect_nums, rects)

			#########EDGE CASE (drew). suppose that there is object centroid 0, 1 and input centroid 0, 1, and in decreasing eucliean distance, have (1,0) and (0,0). so both 1 and 0 (objects) want to match to 0
			######(input), while 1 (input) is real far away from both. i think we should register 1 (input) in this case, which the original code doesn't do. 
			#####################you could also imagine (1,0) and (1,1), so 1 wants to match to both 0 and 1, and 0 (object) goes unused. under the current code, it does not disappear. 

			# loop over the unused row indexes
			for row in unmatchedRows:
				# grab the object ID for the corresponding row
				# index and increment the disappeared counter
				objectID = objectIDs[row]
				if objectID in self.visible_detection_nums:
					del self.visible_detection_nums[objectID]
				self.disappeared[objectID] += 1

				# check to see if the number of consecutive
				# frames the object has been marked "disappeared"
				# for warrants deregistering the object
				if self.disappeared[objectID] > self.maxDisappeared:
					self.deregister(objectID)

			#register all the unused columns (input centroids); these guys did not get matched to anyone because they were farthest away
			#if D.shape[0] < D.shape[1]:
			for col in unmatchedCols:
				self.register(inputCentroids[col], detect_nums[col], inputRects[col])

		# return the set of trackable objects
		#print(self.objects, self.objects_rects)
		#import pdb; pdb.set_trace()
		return (self.visible_detection_nums, self.objects)



def match_centroids(ct, detect_nums, rects):
	inputCentroids = np.zeros((len(rects), 2), dtype="int")
	inputRects = np.array(rects, dtype='int')
	#print(inputRects)
	#import pdb; pdb.set_trace()

	# loop over the bounding box rectangles
	for (i, (startX, startY, endX, endY)) in enumerate(rects):
		# use the bounding box coordinates to derive the centroid
		cX = int((startX + endX) / 2.0)
		cY = int((startY + endY) / 2.0)
		inputCentroids[i] = (cX, cY)

	objectIDs = list(ct.objects.keys())
	objectCentroids = list(ct.objects.values())
	objectRects = list(ct.objects_rects.values())

	W = ct.frame_size[0]
	H = ct.frame_size[1]

	#define some nested conditions

	def area_check_fails(row, col, low = 0.5, up = 2): #fish is not allowed to grow arbitrarily
		min_x_obj, min_y_obj, max_x_obj, max_y_obj = objectRects[row]
		min_x_inp, min_y_inp, max_x_inp, max_y_inp = inputRects[col]
		object_area = (max_x_obj - min_x_obj)*(max_y_obj - min_y_obj)
		input_area = (max_x_inp - min_x_inp)*(max_y_inp - min_y_inp)

		if low*object_area <= input_area <= up*object_area:
			return False
		else: return True

	def speed_check_fails(row, col, lowx = 0.2, lowy = 0.2): #fish is not allowed to teleport
		cX_obj, cY_obj = objectCentroids[row]
		cX_inp, cY_inp = inputCentroids[col]
		dx = np.abs(cX_obj - cX_inp)
		dy = np.abs(cY_obj - cY_inp)

		if dx < lowx*W and dy < lowy*H:
			return False
		else: return True




	D = dist.cdist(np.array(objectCentroids), inputCentroids)

	rows = D.min(axis=1).argsort()
	cols = D.argmin(axis=1)[rows]

	matchedRows = set()
	matchedCols = set()

	for (row, col) in zip(rows, cols): #these index the euclidean distances in decreasing order, with row corresponding to object indices and columns corresponding to input indices

		if row in matchedRows or col in matchedCols:
			continue

		# otherwise, check some conditions:
		if	area_check_fails(row, col) or speed_check_fails(row,col):
			continue

		else:
			#grab the object ID for the current row,
			# set its new centroid, and reset the disappeared
			# counter
			objectID = objectIDs[row]	
			ct.objects[objectID] = inputCentroids[col]
			ct.objects_rects[objectID] = inputRects[col]
			ct.visible_detection_nums[objectID] = detect_nums[col]
			ct.disappeared[objectID] = 0
			# indicate that we have matched each of the row and
			# column indexes, respectively, so that we don't match any centroids twice
			matchedRows.add(row)
			matchedCols.add(col)

	# compute both the row and column index we have NOT yet
	# examined
	unmatchedRows = set(range(0, D.shape[0])).difference(matchedRows)
	unmatchedCols = set(range(0, D.shape[1])).difference(matchedCols)
	return (unmatchedRows, unmatchedCols)