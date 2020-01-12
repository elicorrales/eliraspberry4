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
import json

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
robotMessagingUrl = 'http://10.0.0.58:8085/messaging/api'
robotIsReadyToDrive = False
robotDriveServerConnectionRefusedNumberOfTimes = 0;
messagingServerConnectionRefusedNumberOfTimes = 0;
thisVisionControlProgramIsReadyForNextCommand = True

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
def sendGetMessage(completeUriString):

    global messagingServerConnectionRefusedNumberOfTimes

    try:
        #print(robotMessagingUrl + completeUriString)
        response = requests.get(url=robotMessagingUrl + completeUriString, timeout=httpTimeout)
        messagingServerConnectionRefusedNumberOfTimes = 0;
        return response.text
    except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        cleanUp()
    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        time.sleep(0.20)
        messagingServerConnectionRefusedNumberOfTimes += 1;
        if messagingServerConnectionRefusedNumberOfTimes > 3:
            cleanUp()
        return 'Refused'
    except:
        track = traceback.format_exc()
        print(track)
        say('Other Communication Error', 0)
        cleanUp()


##################################################################
def sendPostMessage(completeUriString, dataString = None):

    global messagingServerConnectionRefusedNumberOfTimes

    try:
        if dataString != None:
            #print(dataString)
            data = json.dumps(dataString)
            #print('sendPostMessage(): dataString to json data: ')
            #print(data)
            #headers = {'Content-type': 'application/json, text/plain', 'Accept': 'text/plain, application/json'}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            response = requests.post(url=robotMessagingUrl + completeUriString, data=data, headers=headers, timeout=httpTimeout)
            return response.text
        else:
            print(robotMessagingUrl + completeUriString)
            response = requests.post(url=robotMessagingUrl + completeUriString, timeout=httpTimeout)
            return response.text

        messagingServerConnectionRefusedNumberOfTimes = 0;
        return response.text
    except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        cleanUp()
    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        time.sleep(0.20)
        messagingServerConnectionRefusedNumberOfTimes += 1;
        if messagingServerConnectionRefusedNumberOfTimes > 3:
            cleanUp()
        return 'Refused'
    except:
        track = traceback.format_exc()
        print(track)
        say('Other Communication Error', 0)
        cleanUp()


##################################################################
def sendDeleteMessage(completeUriString):

    global messagingServerConnectionRefusedNumberOfTimes

    print('')
    print('')
    print('')
    print('sendDeleteMessage():')

    try:
        print(robotMessagingUrl + completeUriString)
        response = requests.delete(url=robotMessagingUrl + completeUriString, timeout=httpTimeout)
        return response.text

        messagingServerConnectionRefusedNumberOfTimes = 0;
        return response.text
    except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        cleanUp()
    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        time.sleep(0.20)
        messagingServerConnectionRefusedNumberOfTimes += 1;
        if messagingServerConnectionRefusedNumberOfTimes > 3:
            cleanUp()
        return 'Refused'
    except:
        track = traceback.format_exc()
        print(track)
        say('Other Communication Error', 0)
        cleanUp()




##################################################################
def tryToGetJsonResponseFromRobotStatus():

    print('')
    print('')
    print('')
    print('tryToGetJsonResponseFromRobotStatus():')

    possibleJsonResp = sendRobotUrl('/nodejs/api/data')

    if '"volts":-1' in possibleJsonResp:
        say('Arduino is Up, but Not Roboclaw')
        possibleJsonResp = sendPostMessage('/vision/status?from=vision', possibleJsonResp)
        print(possibleJsonResp)
        cleanUp()

    try:
        response = json.loads(possibleJsonResp)
    except:
        track = traceback.format_exc()
        print(track)
        print('')
        print('')
        print('')
        print('error response back from to getting robot status: ' + possibleJsonResp)
        print('')
        print('')
        cleanUp()

    return response

##################################################################
def tryToGetLatestAndGoodStatusResponseFromRobot():

    tries = 0
    while tries < 2:
        response = tryToGetJsonResponseFromRobotStatus()
        #print(response)
        if type(response) is dict and 'error':
            if response['error'] == '' or response['error'] == 'NEEDINIT':
                break
        tries += 1
        time.sleep(0.2)

    return response

##################################################################
def updateMessagingAndQuit():

    print('')
    print('')
    print('')
    print('updateMessagingAndQuit()')
    print('')
    print('')
    print('')
    possibleJsonResp = sendPostMessage('/vision/status/quit?from=vision')

    print(possibleJsonResp)
    print('')
    print('')
    print('')

    cleanUp()


##################################################################
def clearMessagingNewCommandIsAvailable():

    print('')
    print('')
    print('')
    print('clearMessagingNewComnandIsAvailable()')

    possibleJsonResp = sendDeleteMessage('/vision/new?from=vision')
    if 'ok' not in possibleJsonResp:
        print('')
        print('')
        print('')
        print('error response back from clearMessagingNewCommandIsAvailable: ')
        print(possibleJsonResp)
        cleanUp()


##################################################################
def clearMessagingLatestVisionCommand():
    possibleJsonResp = sendDeleteMessage('/vision/command?from=vision')
    if 'ok' not in possibleJsonResp:
        print('')
        print('')
        print('')
        print('error response back from clearMessagingLatestVisionCommand: ')
        print(possibleJsonResp)
        cleanUp()


##################################################################
def tellMessagingThatVisionControlIsReadyForNewCommand():

    global thisVisionControlProgramIsReadyForNextCommand

    possibleJsonResp = sendPostMessage('/vision/ready?from=vision')
    if 'ok' not in possibleJsonResp:
        print('')
        print('')
        print('')
        print('error response back from telling Messsaging That Vision was ready for new command: ')
        print(possibleJsonResp)
        cleanUp()

    thisVisionControlProgramIsReadyForNextCommand = True


##################################################################
def checkIfMessagingHasNewCommandWaiting():

    global thisVisionControlProgramIsReadyForNextCommand

    possibleJsonResp = sendGetMessage('/vision/new?from=vision')
    try:
        response = json.loads(possibleJsonResp)
    except:
        track = traceback.format_exc()
        print(track)
        print('')
        print('')
        print('')
        print('error response back from messaging request to check if new command is waiting : ' + possibleJsonResp)
        print('')
        print('')
        cleanUp()

        
    if 'newcmdavail' in response.keys():
        if response['newcmdavail'] == True:

            if not thisVisionControlProgramIsReadyForNextCommand:
                track = traceback.format_exc()
                print(track)
                print('')
                print('')
                print('')
                print('error: vision was sent a new command without having posted that it was ready for next command')
                print('')
                print('')
                cleanUp()

            thisVisionControlProgramIsReadyForNextCommand = False
            print('')
            print('')
            print('')
            print('new command is waiting: ' + possibleJsonResp)
            print('')
            print('')
            return True
    else:
        print('')
        print('')
        print('')
        print('error when checking if new command is waiting: ' + possibleJsonResp)
        print('')
        print('')
        cleanUp()


    return False

##################################################################
def executeCommandIfAnyFromMessaging():


    thisVisionControlProgramIsReadyForNextCommand = True

    newCommandWaiting = checkIfMessagingHasNewCommandWaiting()
    if newCommandWaiting:
        print('')
        print('')
        print('')
        print('   executCommandIfAny... possible new vision command is waiting...')
        getVisionMessagingCommandIfAnyAndExecute()


##################################################################
def sendRobotUrl(command):

    print('')
    print('')
    print('')
    print('sendRobotUrl('+command+')')
    print('')
    global robotDriveServerConnectionRefusedNumberOfTimes

    try:
        response = requests.get(robotDriveUrl + command, timeout=httpTimeout)
        robotDriveServerConnectionRefusedNumberOfTimes = 0;
        return response.text
    except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        cleanUp()
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

    print('')
    print('')
    print('')
    print('initRobotDrive()')
    print('')
    respText = sendRobotUrl('/nodejs/api/data')
    if '"volts":-1' in respText:
        say('Arduino is Up, but Not Roboclaw')
        cleanUp()
    time.sleep(1)
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
# functions related to messaging commands
##################################################################
##################################################################

##################################################################
# the main messaging command router to related function
def getVisionMessagingCommandIfAnyAndExecute():

    possibleJsonResp = sendGetMessage('/vision/command?from=vision')

    print('')
    print('')
    print('getVisionMessagingCommandIfAny()...')
    print('')

    try:
        response = json.loads(possibleJsonResp)
    except:
        track = traceback.format_exc()
        print(track)
        print('')
        print('')
        print('')
        print('error response back from messaging request to get latest command to execute: ' + possibleJsonResp)
        print('')
        print('')
        cleanUp()


    if 'command' in response.keys():
        command = response['command']
        if command != '':
            clearMessagingNewCommandIsAvailable()
            clearMessagingLatestVisionCommand()
            if command == 'status':
                getRobotStatusAndUpdateMessaging()
                tellMessagingThatVisionControlIsReadyForNewCommand()
            elif command == 'quit':
                # this part isnt really to accept another command, but rather
                # to make sure the messaging system is in a good state for next run of this program.
                tellMessagingThatVisionControlIsReadyForNewCommand()
                updateMessagingAndQuit()
            elif command == 'initialize':
                initialize()
                tellMessagingThatVisionControlIsReadyForNewCommand()

    else:
        print('error in response back from get new command if any : ')
        print(response)
        cleanUp()

##################################################################
def getRobotStatusAndUpdateMessaging():

    response = tryToGetLatestAndGoodStatusResponseFromRobot()
    """
    print('')
    print('')
    print('')
    print('')
    print(response)
    print('')
    print('')
    print('')
    print('')
    """

    visual = {
            "noFaceDetected": noFaceDetected,
            "faceDetected": faceDetected,
            "faceCentered": faceCentered,
            "tooManyFaces": tooManyFaces,
            "faceMovedLeft": faceMovedLeft,
            "faceMovedRight": faceMovedRight,
            "faceTooClose": faceTooClose,
            "faceTooFar": faceTooFar,
            "faceIsJustRight": faceIsJustRight
    }
    response['visual'] = visual

    """
    print('')
    print('')
    print('')
    print('')
    print(response)
    print('')
    print('')
    print('')
    print('')
    """

    possibleJsonResp = sendPostMessage('/vision/status?from=vision', response)
    if 'ok' not in possibleJsonResp:
        print('error in response back when trying to post updated status to messaging: ')
        print(response)
        cleanUp()


##################################################################
def initialize():
    robotIsReadyToDrive = initRobotDrive()
    if not robotIsReadyToDrive:
        robotIsReadyToDrive = initRobotDrive()
        if not robotIsReadyToDrive:
            robotIsReadyToDrive = initRobotDrive()

    if not robotIsReadyToDrive:
        say('Robot not initialized')


##################################################################
##################################################################
# main program
##################################################################
##################################################################

if __name__ == '__main__':
    signal(SIGINT, signalHandler)

initCamera()


# only attempt to read if it is opened
if cap.isOpened:
    while(True):
        ret, frame = cap.read()

        executeCommandIfAnyFromMessaging()
        
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



            #moveMoveForwardOrBackForCorrectDistanceAway()

 
            #moveLeftOrRightToCenterOnFace(deltaLastTimeMoved, deltaLeftRight, leftEdge, rightEdge)
 
else:
    print("Failed to open capture device")

