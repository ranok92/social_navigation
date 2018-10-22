import numpy as np 
import cv2
import os 
import time


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
				line = line.strip().split('  ')
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
					self.start_frame = int(float(listval[0]))
					start_flag = True
				#print "here"
				cur_pos = ( listval[2], listval[4])
				self.position_list.append(cur_pos)#update the position_list
				#fut_pos = ((float(listval_fut[3])+float(listval_fut[1]))/2 , (float(listval_fut[4]) + float(listval_fut[2]))/2)
				cur_vel = (listval[5] , listval[7]) 
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



def takeFrameNumber(element):
	return element[0]


def place_annotation(image, annotation_dict , frame):
	font = cv2.FONT_HERSHEY_COMPLEX_SMALL
	if frame in annotation_dict:
		frame_info = annotation_dict[frame]
		for element in frame_info:
			cv2.rectangle(image , (int(float(element[2]))-20,int(float(element[4]))-20),(int(float(element[2]))+20,int(float(element[4]))+20) , (0,255,0) , 1)
			cv2.putText(image,element[1],(int(element[2])-22,int(element[4])-22),font,1,(0,255,255))


	return 0


def annotate_video(annotationfile , videofile , homography_file):

	if not os.path.isfile(videofile):
		print ("The video file does not exist.")
		return 0
	if not os.path.isfile(annotationfile):
		print ("The annotation file does not exist.")
		return 0

	if not os.path.isfile(homography_file):
		print "The homography_file does not exist."
		return 0

	homo_matrix = np.linalg.inv(np.loadtxt(homography_file));

	print homo_matrix

#[frame_number pedestrian_ID pos_x pos_z pos_y v_x v_z v_y ]
	videocap = cv2.VideoCapture(videofile)
	annotation_list = []
	annotation_dict = {}
	fps = videocap.get(cv2.CAP_PROP_FPS)
	width = videocap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
	height = videocap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
	with open(annotationfile) as f:

		for line in f:
			line = line.strip().split('  ')
			annotation_list.append(line)

	for entry in annotation_list:
		if str(int(float(entry[0]))) not in annotation_dict:
			annotation_dict[str(int(float(entry[0])))] = []
			print "Adding ",str(int(float(entry[0])))
		#print type(entry[2] , entry[4] , entry[3])
		#print repr(entry[2])
		#print repr(entry[3])
		#print repr(entry[4])
		pos_mat = np.asarray([float(entry[2]),float(entry[4]),1])
		vel_mat = np.asarray([float(entry[5]) , float(entry[7]),1])
		#print "*******************************"
		#print repr(pos_mat)
		new_posmat = np.matmul(homo_matrix , pos_mat)
		new_velmat = np.matmul(homo_matrix , vel_mat)
		#print new_posmat
		entry[2] = (new_posmat[1]/new_posmat[2])#-width/2
		entry[4] = (new_posmat[0]/new_posmat[2])#-height/2

		entry[5] = (new_velmat[1]/new_velmat[2])
		entry[7] = (new_velmat[0]/new_velmat[2])

		annotation_dict[str(int(float(entry[0])))].append(entry)
	
	print len(annotation_dict)
	#success, image = videocap.read()

	print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)
	count = 0
	success = True

	while success:
		success, image = videocap.read()

		#if (count)%1==1:
		place_annotation(image , annotation_dict , str(count))
		cv2.imshow("frame" , image)
				
		print count	

		count += 1
		cv2.waitKey(1)
		if cv2.waitKey(1) & 0xFF == ord('p'):
			while cv2.waitKey(1) & 0xFF != ord('r'):
				time.sleep(1)
		if cv2.waitKey(1) & 0xFF == ord('s'):
			time.sleep(.5)
			#print success
			#print "Read image"
		
	videocap.release()
	cv2.destroyAllWindows()


annotationfile = "/home/abhisek/Study/Robotics/social_navigation/otherdatasets/eth/ewap_dataset/seq_eth/obsmat.txt"
videofile = "/home/abhisek/Study/Robotics/social_navigation/otherdatasets/eth/ewap_dataset/seq_eth/seq_eth.avi"
homography_file = "/home/abhisek/Study/Robotics/social_navigation/otherdatasets/eth/ewap_dataset/seq_eth/H.txt"

annotate_video(annotationfile,videofile,homography_file)
