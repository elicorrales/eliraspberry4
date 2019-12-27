import sys
import argparse
import os
import pyttsx3
import numpy as np
import cv2
import time
from signal import signal, SIGINT
import requests
import traceback
import socket
import urllib3

parser = argparse.ArgumentParser(prog=sys.argv[0], description='detect object with webcam & opencv', allow_abbrev=False)
parser.add_argument('--width',type=int, dest='width', required=True)
parser.add_argument('--height',type=int, dest='height', required=True)
parser.add_argument('--FPS',type=int, dest='FPS', required=True)
parser.add_argument('--http-timeout',type=float, dest='httpTimeout', required=True)
parser.add_argument('--speed',type=int, dest='speed', required=True)
parser.add_argument('--loopDelay',type=float, dest='loopDelay', required=True)
parser.add_argument('--min-dist',type=int, dest='minDist', required=True)
parser.add_argument('--max-dist',type=int, dest='maxDist', required=True)
parser.add_argument('--limit-buffer',dest='limitBuffer', action='store_true')
args = parser.parse_args()

width=args.width
height=args.height
FPS=args.FPS
httpTimeout=args.httpTimeout
speed=args.speed
loopDelay=args.loopDelay
minDist=args.minDist
maxDist=args.maxDist
limitBuffer=args.limitBuffer

robotDriveUrl = 'http://10.0.0.58:8084'
robotIsReadyToDrive = False
robotDriveServerConnectionRefusedNumberOfTimes = 0;

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FPS, FPS)

if limitBuffer:
    cap.set(cv2.CAP_PROP_BUFFERSIZE,1)



xml_path = '/home/devchu/.virtualenvs/cv/lib/python3.7/site-packages/cv2/data/'
face_cascade = cv2.CascadeClassifier(xml_path + 'haarcascade_frontalface_default.xml')


##################################################################
# these program flow control, mainly just to make sure we do not
# repeat(say) something uneccesarily.
noFaceDetected = False
faceDetected   = False
faceCentered   = False
tooManyFaces   = False
faceMovedLeft  = False
faceMovedRight = False
faceTooClose   = False
faceTooFar     = False

lastTimeMoved = time.time()

tts = pyttsx3.init()

##################################################################
def cleanUp():
    cap.release()
    cv2.destroyAllWindows()
    print('Done.')
    sys.exit(0)


##################################################################
def signalHandler(signalReceived, frame):
    print('Got CTRL-C...')
    cleanUp()


##################################################################
def say(phrase):
    tts.say(phrase)
    tts.runAndWait()

##################################################################
def sendRobotUrl(command):

    global robotDriveServerConnectionRefusedNumberOfTimes

    try:
        response = requests.get(robotDriveUrl + command, timeout=httpTimeout)
        robotDriveServerConnectionRefusedNumberOfTimes = 0;
        return response.text
    except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        return 'Timeout'
    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        time.sleep(0.20)
        robotDriveServerConnectionRefusedNumberOfTimes += 1;
        if robotDriveServerConnectionRefusedNumberOfTimes > 3:
            cleanUp()
        return 'Refused'
    except:
        track = traceback.format_exc()
        print(track)
        say('Other Communication Error')
        cleanup()

##################################################################
def initRobotDrive():
    respText = sendRobotUrl('/arduino/api/clr.usb.err')

    if 'Cmd Sent To Arduino' in respText:
        say('Robot Is Ready.')
        return True
    else:
        print(respText)
        say(respText)

    return False

##################################################################
def sendRobotDriveCommand(direction, mySpeed=speed):
    global robotIsReadyToDrive
    if not robotIsReadyToDrive:
        robotIsReadyToDrive = initRobotDrive()
    if robotIsReadyToDrive:
        respText = sendRobotUrl('/arduino/api/' + direction + '/' + str(mySpeed))
        if not 'Cmd Sent To Arduino' in respText:
            print(respText)
            say(respText)

##################################################################
def sendRobotNodeJsCommand(command, resultExpected, sayOnGoodResult):
    global robotIsReadyToDrive
    if not robotIsReadyToDrive:
        robotIsReadyToDrive = initRobotDrive()
    if robotIsReadyToDrive:
        respText = sendRobotUrl('/nodejs/api/' + command)
        if not 'volts\":12' in respText:
            print(respText)
            say(respText)
        else:
            say(sayOnGoodResult)





##################################################################
##################################################################
# main program
##################################################################
##################################################################

if __name__ == '__main__':
    signal(SIGINT, signalHandler)


robotIsReadyToDrive = initRobotDrive()
robotIsReadyToDrive = initRobotDrive()
robotIsReadyToDrive = initRobotDrive()

# only attempt to read if it is opened
if cap.isOpened:
    while(True):
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        if len(faces) < 1:
            if not noFaceDetected:
                say('No one')
                noFaceDetected = True
            faceDetected = False
            tooManyFaces = False
            faceCentered = False
            faceMovedLeft = False
            faceMovedRight = False
            faceTooClose   = False
            faceTooFar     = False
            continue

        elif len(faces) > 2:
            if not tooManyFaces:
                say('too many faces')
                tooManyFaces = True
            noFaceDetected = False
            faceDetected = False
            continue

        elif len(faces) > 0:
            noFaceDetected = False
            if not faceDetected:
                say('I see you')
                faceDetected = True
                #continue

        tooManyFaces = False
        faceIdx = 0
        for (x, y, w, h) in faces:

            noFaceDetected = False

            leftEdge = x
            rightEdge = width - (x + w)
            print(leftEdge,' ',rightEdge)
            deltaLeftRight = abs(leftEdge - rightEdge)

            deltaLastTimeMoved = time.time() - lastTimeMoved

            ####################################################
            # only if already centered, do we move toward or away
            if deltaLeftRight <= 40:

                faceMovedLeft = False
                faceMovedRight = False

                if not faceCentered:
                    say('center')
                    faceCentered = True

                if w > minDist and deltaLastTimeMoved > loopDelay:
                    if not faceTooClose:
                        say('close')
                        faceTooClose = True
                    sendRobotDriveCommand('backward', 43)
                    lastTimeMoved = time.time()
                elif w < maxDist and deltaLastTimeMoved > loopDelay:
                    if not faceTooFar:
                        say('far')
                        faceTooFar = True
                    sendRobotDriveCommand('forward', 43)
                    lastTimeMoved = time.time()

 
            else:
                faceCentered = False
                if deltaLastTimeMoved > loopDelay:

                    if leftEdge > rightEdge:
                        if not faceMovedRight:
                            say('right')
                            faceMovedRight = True
                        sendRobotDriveCommand('right')
                    else:
                        if not faceMovedLeft:
                            say('left')
                            faceMovedLeft = True
                        sendRobotDriveCommand('left')

                    lastTimeMoved = time.time()
 
else:
    print("Failed to open capture device")

