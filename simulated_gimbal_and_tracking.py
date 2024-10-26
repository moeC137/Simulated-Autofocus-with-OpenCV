import cv2
from tqdm import trange
import random
import time 
import numpy as np
import argparse

cap = cv2.VideoCapture('dummy_video.mp4')
#cap = cv2.VideoCapture(0) #use this for webcam input
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
y=0
x=0
h=200
w=200
ms = 10 #movement speed

font = cv2.FONT_HERSHEY_COMPLEX_SMALL
# org
# fontScale
fontScale = 0.6
# Blue color in BGR
color = (0, 0, 255)
# Line thickness of 2 px
thickness = 1

_, frame = cap.read()
old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Lucas kanade params
lk_params = dict(winSize = (15, 15),
maxLevel = 4,
criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

point_selected = False
point = ()
old_points = np.array([[]])

while(1):
    ret, frame = cap.read()
    
    width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
    
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    if point_selected is True :
        new_points, status, error = cv2.calcOpticalFlowPyrLK(old_gray, gray_frame, old_points, None, **lk_params)
        old_gray = gray_frame.copy()
        old_points = new_points
        
        x2, y2 = new_points.ravel()
        crop2 = frame[int(y2 - h/2):int(y2 + h/2), int(x2 - w/2):int(x2 + w/2)]
        cv2.circle(frame, (int(x2), int(y2)), 10, (0, 255, 0), 1)
        end = (x2, y2)
        if x2 > 95 and y2 > 95 and x2 < width and y2 < height:
            cv2.imshow('crop', crop2)
    
    fpsy = y + 100
    fpsx = x +100
    
    crop = frame[y:y+h, x:x+w]
    crop = cv2.circle(crop,(100,100), 15, (0,0,255), 1)
    cv2.putText(crop, 'Y:', (5,10), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.putText(crop, str(fpsy), (20,10), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.putText(crop, 'X:', (5,20), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.putText(crop, str(fpsx), (20,20), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.imshow('Viewfinder', crop)
    
    #cv2.imshow("Output", frame)
    k = cv2.waitKey(33)
    if k==82 and y > 0:    # up key
        print("up")
        y = y - ms
    if k==84:    # down key
        print("down")
        y = y + ms
    if k==83:    # right key
        print("right")
        x = x + ms
    if k==81 and x > 0:    # left key
        print("left")
        x = x - ms
    if k==32:# space key
        print("space")
        point = (fpsx, fpsy)
        point_selected = True
        old_points = np.array([[fpsx, fpsy]], dtype=np.float32)
        

    elif k==-1:  # normally -1 returned,so don't print it
        continue
    else:
        print(k) # else print its value
