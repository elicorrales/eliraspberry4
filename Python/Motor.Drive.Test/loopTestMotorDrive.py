import sys
import argparse
import pyttsx3
from signal import signal, SIGINT
import requests
import traceback
import socket
import urllib3
import random
import time

parser = argparse.ArgumentParser(prog=sys.argv[0], description='detect object with webcam & opencv', allow_abbrev=False)
#parser.add_argument('--width',type=int, dest='width', required=True)
#parser.add_argument('--height',type=int, dest='height', required=True)
#parser.add_argument('--FPS',type=int, dest='FPS', required=True)
#parser.add_argument('--limit-buffer',dest='limitBuffer', action='store_true')
#args = parser.parse_args()

#width=args.width
#height=args.height
#FPS=args.FPS
#limitBuffer=args.limitBuffer

robotDriveUrl = 'http://10.0.0.58:8084'
robotIsReadyToDrive = False


tts = pyttsx3.init()

random.seed(0)

##################################################################
def cleanUp():
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
def sendRobotUrl(command, mytimeout = 0.1):

    try:
        response = requests.get(robotDriveUrl + command, timeout=mytimeout)
        return response.text
    except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        #track = traceback.format_exc()
        #print(track)
        say('The request timed out.')
        return ''
    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        say('Connection Refused. Did You start the node J S server?')
        cleanUp()
    except:
        track = traceback.format_exc()
        print(track)
        say('Other Communication Error')

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
def sendRobotDriveCommand(direction):
    global robotIsReadyToDrive
    if not robotIsReadyToDrive:
        robotIsReadyToDrive = initRobotDrive()
    if robotIsReadyToDrive:
        respText = sendRobotUrl('/arduino/api/' + direction + '/100')
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

# only attempt to read if it is opened
if robotIsReadyToDrive:

    while(True):
        rand = random.randint(1,100)
        if rand >= 1 and rand < 25:
            #say('right')
            sendRobotDriveCommand('right')
        elif rand >= 25 and rand < 50:
            #say('left')
            sendRobotDriveCommand('left')
        elif rand >=50 and rand < 75:
            #say('closer')
            sendRobotDriveCommand('backward')
        elif rand >=75 and rand <= 100:
            #say('farther')
            sendRobotDriveCommand('forward')
        else:
            say('random was ' + rand)

        time.sleep(0.08)

else:
    print('Failed to initialize robot drive')

