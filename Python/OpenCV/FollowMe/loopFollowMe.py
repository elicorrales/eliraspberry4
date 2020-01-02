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
parser.add_argument('--lSpeed',type=int, dest='leftSpeed', required=True)
parser.add_argument('--rSpeed',type=int, dest='rightSpeed', required=True)
parser.add_argument('--fbSpeed',type=int, dest='fwdBakSpeed', required=True)
parser.add_argument('--loopDelay',type=float, dest='loopDelay', required=True)
parser.add_argument('--min-dist',type=int, dest='minDist', required=True)
parser.add_argument('--max-dist',type=int, dest='maxDist', required=True)
parser.add_argument('--limit-buffer',dest='limitBuffer', action='store_true')
parser.add_argument('--speak',dest='speak', action='store_true')
args = parser.parse_args()

width=args.width
height=args.height
FPS=args.FPS
httpTimeout=args.httpTimeout
leftSpeed=args.leftSpeed
rightSpeed=args.rightSpeed
fwdBakSpeed=args.fwdBakSpeed
loopDelay=args.loopDelay
minDist=args.minDist
maxDist=args.maxDist
limitBuffer=args.limitBuffer
speak=args.speak

robotDriveUrl = 'http://10.0.0.58:8084'
robotIsReadyToDrive = False
robotDriveServerConnectionRefusedNumberOfTimes = 0;

cap = None

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
faceIsJustRight= False

lastTimeMoved = time.time()

tts = pyttsx3.init()

##################################################################
def initCamera():
    global cap
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    if limitBuffer:
        cap.set(cv2.CAP_PROP_BUFFERSIZE,1)


##################################################################
def cleanUpCamera():
    cap.release()
    cv2.destroyAllWindows()

##################################################################
def cleanUp():
    cleanUpCamera()
    print('Done. Bye,bye.')
    sys.exit(0)


##################################################################
def signalHandler(signalReceived, frame):
    print('Got CTRL-C...')
    cleanUp()


##################################################################
def say(phrase):
    if speak:
        tts.say(phrase)
        tts.runAndWait()
    print(phrase)

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
        cleanUp()

##################################################################
def initRobotDrive():
    respText = sendRobotUrl('/nodejs/api/data')
    if '"volts":-1' in respText:
        say('Arduino is Up, but Not Roboclaw')
        cleanUp()
    time.sleep(0.5)
    respText = sendRobotUrl('/arduino/api/clr.usb.err')
    if 'Cmd Sent To Arduino' in respText:
        time.sleep(1)
        respText = sendRobotUrl('/nodejs/api/data')
        if 'NEEDINIT' in respText:
            return False
        say('Robot Is Ready.')
        return True
    else:
        print(respText)
        say(respText)
    return False

##################################################################
def sendRobotDriveCommand(direction, mySpeed):
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
def moveLeftOrRightToCenterOnFace(deltaLastTimeMoved, deltaLeftRight, leftEdge, rightEdge):
    global lastTimeMoved
    global faceMovedRight
    global faceMovedLeft

    if deltaLastTimeMoved > loopDelay and deltaLeftRight > 45:

        if leftEdge > rightEdge:
            if not faceMovedRight:
                say('right')
                faceMovedRight = True
            sendRobotDriveCommand('right',rightSpeed)
        else:
            if not faceMovedLeft:
                say('left')
                faceMovedLeft = True
            sendRobotDriveCommand('left',leftSpeed)

        lastTimeMoved = time.time()


##################################################################
def moveMoveForwardOrBackForCorrectDistanceAway():
    global lastTimeMoved
    global faceCentered
    global faceIsJustRight
    global faceTooClose
    global faceTooFar

    if not faceCentered:
        say('center')
        faceCentered = True

    if w > minDist and deltaLastTimeMoved > loopDelay:
        faceIsJustRight = False
        if not faceTooClose:
            say('close')
            faceTooClose = True
        sendRobotDriveCommand('backward',fwdBakSpeed)
        lastTimeMoved = time.time()
    elif w < maxDist and deltaLastTimeMoved > loopDelay:
        faceIsJustRight = False
        if not faceTooFar:
            say('far')
            faceTooFar = True
        sendRobotDriveCommand('forward',fwdBakSpeed)
        lastTimeMoved = time.time()
    elif w >= maxDist and w<=minDist:
        faceTooClose = False
        faceTooFar = False
        if not faceIsJustRight:
            faceIsJustRight = True
            say('Stay there')


##################################################################
##################################################################
# main program
##################################################################
##################################################################

if __name__ == '__main__':
    signal(SIGINT, signalHandler)

initCamera()

robotIsReadyToDrive = initRobotDrive()
if not robotIsReadyToDrive:
    robotIsReadyToDrive = initRobotDrive()
    if not robotIsReadyToDrive:
        robotIsReadyToDrive = initRobotDrive()

if not robotIsReadyToDrive:
    say('Robot not initialized')
    cleanUp()


# only attempt to read if it is opened
if cap.isOpened:
    while(True):
        ret, frame = cap.read()

        gray = None
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except:
            cleanUpCamera()
            time.sleep(0.5)
            initCamera()

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
            faceIsJustRight = False
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

            if deltaLeftRight <= 45:

                faceMovedLeft = False
                faceMovedRight = False

            else:
                faceCentered = False
                faceIsJustRight = False

            moveMoveForwardOrBackForCorrectDistanceAway()

 
            moveLeftOrRightToCenterOnFace(deltaLastTimeMoved, deltaLeftRight, leftEdge, rightEdge)
 
else:
    print("Failed to open capture device")

