import cv2
from tqdm import trange
import random
import time 

#this script takes a video input, blurs it in random intensity at random intervals.
#then it tryes to detect if the image is blured or not, if it is blured it simulates focus adjustment untill the picture is in focus again



# used to record the time when we processed last frame 
prev_frame_time = 0
# used to record the time at which we processed current frame 
new_frame_time = 0
# font
font = cv2.FONT_HERSHEY_SIMPLEX
# org
org = (20, 20)
# fontScale
fontScale = 1
# Blue color in BGR
color = (0, 0, 255)
# Line thickness of 2 px
thickness = 2

# select video input here
#enable this for camera input (experimental)
#cap = cv2.VideoCapture(0) 
#put input filename here
cap = cv2.VideoCapture('input_deer.mp4')  
#save .txt with laplace value for each frame
f = open('results.txt', 'w')		

#select size to save, needs to be correct size or record will fail
size = (1280, 720)
#choose codec, just use XVID for avi it works
fourcc = cv2.VideoWriter_fourcc(*'XVID')
#name of the output file here
out = cv2.VideoWriter('output_file.avi', fourcc, 30.0, size)

# blur factor simulates out of focus lens
blur_factor = 1
#rotation counter used for randomized bluring events
rotation_counter = 0
#not uses for now but may be usefull for PID controll later on
overshot_damping = 0
#blurryness threshhold, not static, this is just here for first loop
fm_thresh = 50
#frame counter
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

#mainloop here

for i in trange(frame_count, unit=' frames', leave=False, dynamic_ncols=True, desc='Calculating blur ratio'):
	#read input frame
	ret, frame = cap.read()
	#increment rotation_counter
	rotation_counter = rotation_counter + 1
	
	# set blur factor random in random time intervals
	if rotation_counter > random.randint(210, 400):
		blur_factor = random.randint(15, 100)
		#reset rotation counter
		rotation_counter = 1
		print("counter_reset")
	
	#apply blur factor to frame
	frame = cv2.blur(frame,(blur_factor,blur_factor))
	
	#gray out frame
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#calculate laplacian value, this is the point there we get our blurryness indicator "fm"
	fm = cv2.Laplacian(gray, cv2.CV_64F).var()
	
	#this is here for FPS display reasons
	new_frame_time = time.time() 
	fps = 1/(new_frame_time-prev_frame_time) 
	prev_frame_time = new_frame_time 
	fps = int(fps) 
	fps = str(fps) 
	cv2.putText(frame, 'FPS:', (20,250), font, fontScale, color, thickness, cv2.LINE_AA)
	cv2.putText(frame, str(fps), (220,250), font, fontScale, color, thickness, cv2.LINE_AA)
	
	#display other data
	cv2.putText(frame, 'Blur Factor:', (20,50), font, fontScale, color, thickness, cv2.LINE_AA)
	cv2.putText(frame, str(blur_factor), (220,50), font, fontScale, color, thickness, cv2.LINE_AA)
	cv2.putText(frame, 'Laplaceian:', (20,100), font, fontScale, color, thickness, cv2.LINE_AA)
	cv2.putText(frame, str(fm), (220,100), font, fontScale, color, thickness, cv2.LINE_AA)
	cv2.putText(frame, 'Threshold:', (20,150), font, fontScale, color, thickness, cv2.LINE_AA)
	cv2.putText(frame, str(fm_thresh), (220,150), font, fontScale, color, thickness, cv2.LINE_AA)
	# Sample quality bar. Parameters adjusted manually to fit horizontal image size
	#cv2.rectangle(frame, (0, 280), (int(fm*1.2), 300), (0,0,255), thickness=cv2.FILLED)
	#cv2.putText(frame, str(fm), org, font, fontScale, color, thickness, cv2.LINE_AA)
	
	
	#if blur is over threshold, reduce blur factor (turn focus motor)
	if fm < fm_thresh and blur_factor >= 2:
		cv2.putText(frame, 'Out of Focus', org, font, fontScale, color, thickness, cv2.LINE_AA)
		blur_factor = blur_factor - 1
		print("blur_factor:", blur_factor)
		
	#Overshoot correction
	if fm < fm_thresh and blur_factor < 2:
		cv2.putText(frame, 'Overshoot', (20,200), 4, fontScale, color, thickness, cv2.LINE_AA)
		overshot_damping = overshot_damping + 1
		#increase threshhold
		fm_thresh = fm_thresh - 0.5
	#reduce threshhold overtime
	fm_thresh = fm_thresh + 0.01
	#im = cv2.resize(frame, None,fx=0.0, fy=0.0, interpolation = cv2.INTER_CUBIC)
	#display main output
	cv2.imshow("Output", frame)
	#save output to file
	out.write(frame)

	#write laplacian value for he frame to the txt file
	f.write(str(fm)+'\r')
	print(fm)
	
	#escape function
	k = cv2.waitKey(1) & 0xff
	if k == 27:
		break 
		out.release()
out.release()
