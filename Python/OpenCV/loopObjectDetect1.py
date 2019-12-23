import sys
import argparse
import cv2
import cv2.aruco as aruco
import numpy as np

parser = argparse.ArgumentParser(prog=sys.argv[0], description='detect object with webcam & opencv', allow_abbrev=False)
parser.add_argument('--width',type=int, dest='width', required=True)
parser.add_argument('--height',type=int, dest='height', required=True)
parser.add_argument('--FPS',type=int, dest='FPS', required=True)
parser.add_argument('--limit-buffer',dest='limitBuffer', action='store_true')
args = parser.parse_args()

width=args.width
height=args.height
FPS=args.FPS
limitBuffer=args.limitBuffer

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FPS, FPS)
if limitBuffer:
    cap.set(cv2.CAP_PROP_BUFFERSIZE,1)

            
face_xml = '/home/devchu/.virtualenvs/cv/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_xml)

aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

# only attempt to read if it is opened
if cap.isOpened:
    while(True):
        ret, frame = cap.read()
    
        if ret:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(img, aruco_dict, parameters=parameters)
            #faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            #for (x,y,w,h) in faces:
                #img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                #roi_gray = gray[y:y+h, x:x+w]
                #roi_color = img[y:y+h, x:x+w]

            img2 = aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.imshow('image',img2)
            cv2.waitKey(1) & 0xFF == ord('q')
        else:
            print("Error reading capture device")
            break

    cap.release()
    cv2.destroyAllWindows()
else:
    print("Failed to open capture device")

