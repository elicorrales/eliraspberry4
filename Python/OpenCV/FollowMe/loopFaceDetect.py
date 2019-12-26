import sys
import argparse
import os
import numpy as np
import cv2
import time

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



xml_path = '/home/devchu/.virtualenvs/cv/lib/python3.7/site-packages/cv2/data/'
face_cascade = cv2.CascadeClassifier(xml_path + 'haarcascade_frontalface_default.xml')


faceDetected = False;
noFaceDetected = False;
lastTimeFaceDetected = time.time()
xPrev = 0
wPrev = 0

# only attempt to read if it is opened
if cap.isOpened:
    while(True):
        ret, frame = cap.read()

        if True:
            #cv2.imshow('frame',frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #cv2.imshow('gray',gray)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            if len(faces) < 1 and not noFaceDetected:
                os.system('espeak-ng -s 140 "No one."')
                noFaceDetected = True
                faceDetected = False

            #for each face...
            for (x, y, w, h) in faces:


                if not faceDetected:
                    os.system('espeak-ng -s 140 "I see you."')
                    faceDetected = True
                    noFaceDetected = False
                    xPrev = x
                    wPrev = w
                    lastTimeFaceDetected = time.time()
                else:
                    deltaX = x - xPrev
                    deltaW = w - wPrev
                    now = time.time()
                    deltaTime = now - lastTimeFaceDetected
                    #print(deltaTime,' ',xPrev,' ',x,' ',y,' ',w,' ',h)
                    if deltaTime > 0.3:

                        if abs(deltaX) < 25 and abs(deltaW) > 10:
                            if deltaW > 0:
                                os.system('espeak-ng -s 140 "moving closer."')
                            else:
                                os.system('espeak-ng -s 140 "moving farther."')
                            lastTimeFaceDetected = time.time()
                            xPrev = x
                            wPrev = w

                        elif abs(deltaX) > 25 and deltaW > 10:
                            if deltaX > 0:
                                os.system('espeak-ng -s 140 "moving right closer."')
                            else:
                                os.system('espeak-ng -s 140 "moving left closer."')
                            lastTimeFaceDetected = time.time()
                            xPrev = x
                            wPrev = w

                        elif abs(deltaX) > 25 and deltaW < -10:
                            if deltaX > 0:
                                os.system('espeak-ng -s 140 "moving right farther."')
                            else:
                                os.system('espeak-ng -s 140 "moving left farther."')
                            lastTimeFaceDetected = time.time()
                            xPrev = x
                            wPrev = w
                        elif abs(deltaX) > 25 and abs(deltaW) < 10:
                            if deltaX > 0:
                                os.system('espeak-ng -s 140 "moving right."')
                            else:
                                os.system('espeak-ng -s 140 "moving left."')
                            lastTimeFaceDetected = time.time()
                            xPrev = x
                            wPrev = w




                # draw a rectangle around the face
                #gray = cv2.rectangle(gray, (x, y), (x+w, y+h), (255, 255, 255), 3)
                #frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 3)

            #cv2.imshow('gray', gray)
            #cv2.imshow('frame', frame)
        else:
            print("Error reading capture device")
            break
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
else:
    print("Failed to open capture device")

