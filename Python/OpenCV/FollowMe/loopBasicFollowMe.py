import sys
import argparse
import os
import pyttsx3
import numpy as np
import cv2
import time
from signal import signal, SIGINT

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


faceDetected = False
noFaceDetected = False
positionChanged = False
lastTimeFaceDetected = time.time()
x1Prev = 0
x2Prev = 0
wPrev = 0

tts = pyttsx3.init()

##################################################################
def signalHandler(signalReceived, frame):
    print('Got CTRL-C...')


    cap.release()
    cv2.destroyAllWindows()

    print('Done.')

    sys.exit(0)


##################################################################
def say(phrase):
    #os.system('espeak-ng -s 140 "' + phrase + '"')
    tts.say(phrase)
    tts.runAndWait()

if __name__ == '__main__':
    signal(SIGINT, signalHandler)



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
                say('No one')
                noFaceDetected = True
                faceDetected = False

            #for each face...
            for (x, y, w, h) in faces:


                if not faceDetected:
                    say('I see you')
                    faceDetected = True
                    noFaceDetected = False
                    x1Prev = x
                    x2Prev = x+w
                    wPrev = w
                    lastTimeFaceDetected = time.time()
                else:
                    deltaX1 = x - x1Prev
                    deltaX2 = x+w - x2Prev
                    deltaW = w - wPrev
                    now = time.time()
                    deltaTime = now - lastTimeFaceDetected

                    if deltaTime > 0.3:

                        positionChanged = False


                        if deltaX1 > 25 and deltaX2 > 25:
                            say('right')
                            positionChanged = True

                        elif deltaX1 < -25 and deltaX2 < -25:
                            say('left')
                            positionChanged = True

                        if deltaW > 7:
                            say('closer')
                            positionChanged = True
                        elif deltaW < -7:
                            say('farther')
                            positionChanged = True

                        if positionChanged:
                            lastTimeFaceDetected = time.time()
                            x1Prev = x
                            x2Prev = x+w
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

