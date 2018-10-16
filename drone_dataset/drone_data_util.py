import numpy as np 
import cv2
import os 
import sys
sys.path.insert(0,'/home/abhisek/Study/Robotics/gym-ballenv')
import ballenv_pygame as BE

'''
create a class for subject. It should have the following properties:

1.postition list
2.velocity list // subtract position at t from position at t+1
3.preferred speed // magnitude of mean velocity
4.chosen destination // the position at the last frame (tuple?)
5.Start frame
6.End frame
7.Set of pedestrians in the same group. ???? Manual annotation / K-means clustering
8.

How I try to identify people who are in a group?
1. They move together, they stop together. Stable relative motion.
Must be within some threshold.
2. 

'''

class pedestrian():

	def __init__(self):
		self.subject = -1
		self.position_list = []
		self.velocity_list = []
		self.preferred_speed = -1
		self.chosen_destination = None
		self.start_frame = -1
		self.stop_frame = -1
		self.pedestrian_group = []

	def extractTrajectoryOfSubject(self,annotationfile , subject):

		start_flag = False
		self.subject = subject
		if not os.path.isfile(annotationfile):
			print ("The annotation file does not exist.")
			return 0

		annotation_list = []
		annotation_dict = {}
		#print "Loading annotation file . . ."
		with open(annotationfile) as f:
			for line in f:
				line = line.strip().split(' ')
				#print line
				#print "break"
				annotation_list.append(line)

		#The position is the midpoint of the bounding box
		for i in range(len(annotation_list)-1): #this is not taking the last frame!
			old_pos = (-1,-1)
			listval = annotation_list[i]
			listval_fut = annotation_list[i+1]
			speed = 0
			counter = 0
		#	print type(listval[0])
			if int(listval[0]) == subject:
				if start_flag == False:
					self.start_frame = int(listval[5])
					start_flag = True
				#print "here"
				cur_pos = ((float(listval[3])+float(listval[1]))/2 , (float(listval[4]) + float(listval[2]))/2)
				self.position_list.append(cur_pos)#update the position_list
				fut_pos = ((float(listval_fut[3])+float(listval_fut[1]))/2 , (float(listval_fut[4]) + float(listval_fut[2]))/2)
				cur_vel = (fut_pos[0] - cur_pos[0] , fut_pos[1] - cur_pos[1]) 
				cur_speed = np.hypot(cur_vel[0],cur_vel[1])
				speed += cur_speed
				counter += 1
				self.velocity_list.append(cur_vel)

			
			if int(listval_fut[0]) != subject and start_flag==True:

				self.velocity_list[-1] = (0,0)
				self.stop_frame = int(listval[5])
				self.preferred_speed = speed/counter
				self.chosen_destination = cur_pos

				break




	def plotSubjectInvideo(self,videofile):

		if not os.path.isfile(videofile):
			print ("The video file does not exist.")
			return 0
		videocap = cv2.VideoCapture(videofile)
		success,image = videocap.read()
		framecounter = 0
		counter = 0
		success = True
		while success:
			if self.start_frame <= framecounter <= self.stop_frame:
				
				cv2.rectangle(image , (int(self.position_list[counter][0])-20 , int(self.position_list[counter][1])-20 ),(int(self.position_list[counter][0])+20 , int(self.position_list[counter][1])+ 20 ) ,(0,255,0) , 2)
				cv2.imshow("frame", image)
				cv2.waitKey(1)
				counter+=1
			framecounter+=1
			success,image = videocap.read()
			if framecounter%500==0:
				print framecounter
			if framecounter > self.stop_frame:

				videocap.release()
				cv2.destroyAllWindows()


		#should plot the subject in the vidoe, ideally just show that part of the video
		return None


def takeFrameNumber(element):
	return element[5]

def place_annotation(image , annotation_dict , frame, color_dict):
	print frame
	font = cv2.FONT_HERSHEY_COMPLEX_SMALL
	frame_info = annotation_dict[frame]
	print "The frame info :"
	print frame_info
	for element in frame_info:
		if element[6] != 1 and element[7] != 1 and element[8] != 1:
			cv2.rectangle(image , (int(element[1]),int(element[2])),(int(element[3]),int(element[4])) , color_dict[element[9]] , 2)
			cv2.putText(image,element[0],(int(element[1])-2,int(element[2])-2),font,1,color_dict[element[9]])

def annotateVideo( videofile , annotationfile):

	color_dict = {'"Biker"':(0,0,255), '"Pedestrian"' : (0,255,0), '"Car"' : (255,255,0) , '"Bus"' : (0,0,0) , '"Skateboarder"' : (100,100,255) , '"Cart"':(255,255,255)}
	if not os.path.isfile(videofile):
		print ("The video file does not exist.")
		return 0
	if not os.path.isfile(annotationfile):
		print ("The annotation file does not exist.")
		return 0

	videocap = cv2.VideoCapture(videofile)
	annotation_list = []
	annotation_dict = {}
	print "Loading annotation file"
	with open(annotationfile) as f:
		for line in f:
			line = line.strip().split(' ')
			#print line
			#print "break"
			annotation_list.append(line)
	
	for entry in annotation_list:
		if entry[5] not in annotation_dict:
			annotation_dict[entry[5]] = []

		annotation_dict[entry[5]].append(entry)

	annotation_list.sort(key=takeFrameNumber)
	success, image = videocap.read()
	count = 0
	success = True
	while success:

		place_annotation(image , annotation_dict , str(count) , color_dict)
		cv2.imshow("frame" , image)
		success, image = videocap.read()
		cv2.waitKey(1)
		if cv2.waitKey(10) == 27:
			break
		print "Read image"
	
		count += 1
	videocap.release()
	cv2.destroyAllWindows()



def populatepyGameEnvironment(annotationfile):

	color_dict = {'"Biker"':(0,0,255), '"Pedestrian"' : (0,255,0), '"Car"' : (255,255,0) , '"Bus"' : (0,0,0) , '"Skateboarder"' : (100,100,255) , '"Cart"':(255,255,255)}
	if not os.path.isfile(annotationfile):
		print ("The annotation file does not exist.")
	





videofile1 = '/media/abhisek/DATA/Study/Masters/Thesis/stanford_campus_dataset/videos/bookstore/video0/video.mov'
videofile = '/media/abhisek/Elements/Local Disk(E) Backup/xx/HoLLywood/Up (2009) [1080p]/up.mp4'
annotationfile = '/media/abhisek/DATA/Study/Masters/Thesis/stanford_campus_dataset/annotations/bookstore/video0/annotations.txt'
#annotateVideo(videofile1,annotationfile)


'''
pt1 = pedestrian()
# subjetc 2 - starts alone ,meets a friend, leaves alone 
pt1.extractTrajectoryOfSubject(annotationfile , 1)
print "here"
print(pt1.start_frame)
print(pt1.stop_frame)
print(pt1.preferred_speed)
#print(pt1.position_list)
#print(pt1.velocity_list)
pt1.plotSubjectInvideo(videofile1)
'''



cb = BE.createBoardperFrame(annotationfile)

cb.reset()
done = False
while not cb.done and not done:

	cb.render()
	#print cb.frame
	action  = cb.take_action_from_user()
	reward ,done, _ = cb.step(action)
	print action





