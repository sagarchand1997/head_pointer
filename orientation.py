import numpy
import cv2
import sys
import os

from deepgaze.face_landmark_detection import faceLandmarkDetection

#import matplotlib.pyplot as plt
import dlib

P3D_RIGHT_SIDE = numpy.float32([-100.0, -77.5, -5.0]) #0
P3D_GONION_RIGHT = numpy.float32([-110.0, -77.5, -85.0]) #4
P3D_MENTON = numpy.float32([0.0, 0.0, -122.7]) #8
P3D_GONION_LEFT = numpy.float32([-110.0, 77.5, -85.0]) #12
P3D_LEFT_SIDE = numpy.float32([-100.0, 77.5, -5.0]) #16
P3D_FRONTAL_BREADTH_RIGHT = numpy.float32([-20.0, -56.1, 10.0]) #17
P3D_FRONTAL_BREADTH_LEFT = numpy.float32([-20.0, 56.1, 10.0]) #26
P3D_SELLION = numpy.float32([0.0, 0.0, 0.0]) #27
P3D_NOSE = numpy.float32([21.1, 0.0, -48.0]) #30
P3D_SUB_NOSE = numpy.float32([5.0, 0.0, -52.0]) #33
P3D_RIGHT_EYE = numpy.float32([-20.0, -65.5,-5.0]) #36
P3D_RIGHT_TEAR = numpy.float32([-10.0, -40.5,-5.0]) #39
P3D_LEFT_TEAR = numpy.float32([-10.0, 40.5,-5.0]) #42
P3D_LEFT_EYE = numpy.float32([-20.0, 65.5,-5.0]) #45
#P3D_LIP_RIGHT = numpy.float32([-20.0, 65.5,-5.0]) #48
#P3D_LIP_LEFT = numpy.float32([-20.0, 65.5,-5.0]) #54
P3D_STOMION = numpy.float32([10.0, 0.0, -75.0]) #62

TRACKED_POINTS = (0, 4, 8, 12, 16, 17, 26, 27, 30, 33, 36, 39, 42, 45, 62)
ALL_POINTS = list(range(0,68)) #Used for debug only

#Open the video file
video_capture = cv2.VideoCapture(0)

cv2.namedWindow('Video')
cv2.moveWindow('Video', 20, 20)

#Obtaining the CAM dimension
cam_w = int(video_capture.get(3))
cam_h = int(video_capture.get(4))

c_x = cam_w / 2
c_y = cam_h / 2
f_x = c_x / numpy.tan(60/2 * numpy.pi / 180)
f_y = f_x

#Estimated camera matrix values.
camera_matrix = numpy.float32([[f_x, 0.0, c_x],
                               [0.0, f_y, c_y], 
                               [0.0, 0.0, 1.0] ])

print("Estimated camera matrix: \n" + str(camera_matrix) + "\n")
#Distortion coefficients
camera_distortion = numpy.float32([0.0, 0.0, 0.0, 0.0, 0.0])

landmarks_3D = numpy.float32([P3D_RIGHT_SIDE,
                              P3D_GONION_RIGHT,
                              P3D_MENTON,
                              P3D_GONION_LEFT,
                              P3D_LEFT_SIDE,
                              P3D_FRONTAL_BREADTH_RIGHT,
                              P3D_FRONTAL_BREADTH_LEFT,
                              P3D_SELLION,
                              P3D_NOSE,
                              P3D_SUB_NOSE,
                              P3D_RIGHT_EYE,
                              P3D_RIGHT_TEAR,
                              P3D_LEFT_TEAR,
                              P3D_LEFT_EYE,
                              P3D_STOMION])

#Declaring the two classifiers
#my_cascade = haarCascade("./etc/haarcascade_frontalface_alt.xml", "./etc/haarcascade_profileface.xml")
my_detector = faceLandmarkDetection("shape_predictor_68_face_landmarks.dat")
my_face_detector = dlib.get_frontal_face_detector()

while(True):

    # Capture frame-by-frame
    ret, frame = video_capture.read()
    #gray = cv2.cvtColor(frame[roi_y1:roi_y2, roi_x1:roi_x2], cv2.COLOR_BGR2GRAY)
    if ret == False :
    	break 

    faces_array = my_face_detector(frame, 0)
    if len(faces_array) == 1 :
    	
    	for i, pos in enumerate(faces_array):	
	        face_x1 = pos.left()
	        face_y1 = pos.top()
	        face_x2 = pos.right()
	        face_y2 = pos.bottom()
	        text_x1 = face_x1
	        text_y1 = face_y1 - 3

	        landmarks_2D = my_detector.returnLandmarks(frame, face_x1, face_y1, face_x2, face_y2, points_to_return=TRACKED_POINTS)
	        retval, rvec, tvec = cv2.solvePnP(landmarks_3D, 
	                                              landmarks_2D, 
	                                              camera_matrix, camera_distortion)
	        print "--",rvec , "--",retval ,"--", tvec
	        axis = numpy.float32([[50,0,0], 
	                                  [0,50,0], 
	                                  [0,0,50]])

	        imgpts, jac = cv2.projectPoints(axis, rvec, tvec, camera_matrix, camera_distortion)

	        sellion_xy = (landmarks_2D[7][0], landmarks_2D[7][1])
	        cv2.line(frame, sellion_xy, tuple(imgpts[1].ravel()), (0,255,0), 3) #GREEN
	        cv2.line(frame, sellion_xy, tuple(imgpts[2].ravel()), (255,0,0), 3) #BLUE
	        cv2.line(frame, sellion_xy, tuple(imgpts[0].ravel()), (0,0,255), 3) #RED
	        # print  sellion_xy , tuple(imgpts[0]) , axis[1]

	        # cv2.line(frame, sellion_xy, tuple(), (0,0,255), 3) #RED

    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

video_capture.release()
print("Bye...")
