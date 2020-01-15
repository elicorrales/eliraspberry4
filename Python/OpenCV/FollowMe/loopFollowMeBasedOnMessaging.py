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

frameWidth=args.width
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

deltaLeftRightLimit = 90

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
faceIsTooClose = False
faceIsTooFar   = False
faceJustFine   = False
faceIsToTheLeft = False
faceIsToTheRight = False
faceWidth = 0
comeHere = False

lastTimeMoved = time.time()

tts = pyttsx3.init()

##################################################################
def initCamera():
    global cap
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frameWidth)
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
    possibleJsonResp = sendDeleteMessage('/vision/status/quit?from=vision')

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

    print('')
    print('')
    print('')
    print('moveLeftOrRightToCenterOfFace()');
    print('')
    print('')

    global lastTimeMoved
    global faceMovedRight
    global faceMovedLeft

    if deltaLastTimeMoved > loopDelay and deltaLeftRight > deltaLeftRightLimit:

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
def getFaceIsLeftOrRightOrCentered(deltaLeftRight):
    global faceCentered
    global faceMovedLeft
    global faceMovedRight
    global faceIsJustRight
    global faceIsToTheLeft
    global faceIsToTheRight

    # face in more or less in center
    if deltaLeftRight <= deltaLeftRightLimit:

        faceCentered = True
        faceMovedLeft = False
        faceMovedRight = False

    #face is to one side or another
    else:
        faceCentered = False
        faceIsJustRight = False

        if leftEdge > rightEdge:
            faceIsToTheRight = True
            faceIsToTheLeft = False
        else:
            faceIsToTheLeft = True
            faceIsToTheRight = False

##################################################################
def getIsFaceTooCloseOrTooFarOrJustFine():
    global faceWidth
    if faceWidth > minDist:
        faceJustFine  = False
        faceIsTooClose = True
    elif faceWidth < maxDist:
        faceJustFine  = False
        faceIsTooFar = True
    elif faceWidth >= maxDist and w<=minDist:
        faceIsTooClose = False
        faceIsTooFar = False
        faceJustFine  = True


##################################################################
def moveForwardOrBackForCorrectDistanceAway():

    print('')
    print('')
    print('')
    print('moveForwardOrBackForCorrectDistanceAway()');
    print('')
    print('')

    global lastTimeMoved
    global faceJustFine 
    global faceIsTooClose
    global faceIsTooFar
    global faceWidth


    if faceWidth > minDist and deltaLastTimeMoved > loopDelay:
        faceJustFine  = False
        if not faceIsTooClose:
            say('close')
            faceIsTooClose = True
        sendRobotDriveCommand('backward',fwdBakSpeed)
        lastTimeMoved = time.time()
    elif faceWidth < maxDist and deltaLastTimeMoved > loopDelay:
        faceJustFine  = False
        if not faceIsTooFar:
            say('far')
            faceIsTooFar = True
        sendRobotDriveCommand('forward',fwdBakSpeed)
        lastTimeMoved = time.time()
    elif faceWidth >= maxDist and w<=minDist:
        faceIsTooClose = False
        faceIsTooFar = False
        if not faceJustFine :
            faceJustFine  = True
            say('Stay there')


##################################################################
##################################################################
# functions related to messaging commands
##################################################################
##################################################################

##################################################################
# the main messaging command router to related function
def getVisionMessagingCommandIfAnyAndExecute():

    global comeHere

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
            
            print('')
            print('')
            print('')
            print('new command received: ' + command)
            print('')
            print('')
            if command == 'robotstatus':
                getLatestUpdatedRobotStatus = True
                getRobotStatusAndUpdateMessaging(getLatestUpdatedRobotStatus)
                tellMessagingThatVisionControlIsReadyForNewCommand()
            elif command == 'visionstatus':
                getVisionOnlyStatusAndUpdateMessaging()
                tellMessagingThatVisionControlIsReadyForNewCommand()
            elif command == 'quit':
                # this part isnt really to accept another command, but rather
                # to make sure the messaging system is in a good state for next run of this program.
                tellMessagingThatVisionControlIsReadyForNewCommand()
                updateMessagingAndQuit()
            elif command == 'initialize':
                initialize()
                tellMessagingThatVisionControlIsReadyForNewCommand()
            elif command == 'forward':
                sendRobotDriveCommand('forward',fwdBakSpeed)
                tellMessagingThatVisionControlIsReadyForNewCommand()
            elif command == 'backward':
                sendRobotDriveCommand('backward',fwdBakSpeed)
                tellMessagingThatVisionControlIsReadyForNewCommand()
            elif command == 'left':
                sendRobotDriveCommand('left',fwdBakSpeed)
                tellMessagingThatVisionControlIsReadyForNewCommand()
            elif command == 'right':
                sendRobotDriveCommand('right',fwdBakSpeed)
                tellMessagingThatVisionControlIsReadyForNewCommand()
            elif command == 'come.here':
                comeHere = True
                tellMessagingThatVisionControlIsReadyForNewCommand()
            elif command == 'stop':
                comeHere = False
                tellMessagingThatVisionControlIsReadyForNewCommand()




            else:
                print('')
                print('')
                print('')
                print('Unknown command from messaging: ' + command)
                cleanUp()

    else:
        print('error in response back from get new command if any : ')
        print(response)
        cleanUp()

##################################################################
def getVisionOnlyStatusAndUpdateMessaging():
    getRobotStatusAndUpdateMessaging()

##################################################################
def getRobotStatusAndUpdateMessaging(getLatestUpdatedRobotStatus=False):

    if getLatestUpdatedRobotStatus:
        response = tryToGetLatestAndGoodStatusResponseFromRobot()

    else:
        response = {}

    visual = {
            "noFaceDetected": noFaceDetected,
            "faceDetected": faceDetected,
            "faceCentered": faceCentered,
            "tooManyFaces": tooManyFaces,
            "faceMovedLeft": faceMovedLeft,
            "faceMovedRight": faceMovedRight,
            "faceIsTooClose": faceIsTooClose,
            "faceIsTooFar": faceIsTooFar,
            "faceIsToTheLeft": faceIsToTheLeft, 
            "faceIsToTheRight": faceIsToTheRight,
            "faceWidth" : str(faceWidth)
    }

    response['visual'] = visual


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
            noFaceDetected = True
            faceDetected = False
            tooManyFaces = False
            faceCentered = False
            faceMovedLeft = False
            faceMovedRight = False
            faceIsTooClose   = False
            faceIsTooFar     = False
            faceIsJustRight = False
            #continue

        elif len(faces) > 1:
            tooManyFaces = True
            noFaceDetected = False
            faceDetected = False
            #continue

        elif len(faces) > 0:
            noFaceDetected = False
            faceDetected = True
            #continue

        if not tooManyFaces:
            print('')
            print('')
            print('')
            print(faces)
            print('')
            print('')
            print('')
            for (x, y, w, h) in faces:

                faceWidth = w

                leftEdge = x
                rightEdge = frameWidth - (x + w)

                deltaLeftRight = abs(leftEdge - rightEdge)

                deltaLastTimeMoved = time.time() - lastTimeMoved

                print('lr:',deltaLeftRight,'fw:',faceWidth,'lft:',leftEdge,'rht:',rightEdge)

                getFaceIsLeftOrRightOrCentered(deltaLeftRight)

                getIsFaceTooCloseOrTooFarOrJustFine()

                if comeHere:
                    if not robotIsReadyToDrive:
                        robotIsReadyToDrive = initRobotDrive()
                    if robotIsReadyToDrive:
                        moveForwardOrBackForCorrectDistanceAway()
                        moveLeftOrRightToCenterOnFace(deltaLastTimeMoved, deltaLeftRight, leftEdge, rightEdge)
 
else:
    print("Failed to open capture device")

