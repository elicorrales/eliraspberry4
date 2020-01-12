import sys
import os
import argparse
import pyaudio
import numpy as np
import wave
import statistics 
import json
import pyttsx3
from signal import signal, SIGINT
from pyfiglet import Figlet
from datetime import datetime
import requests
import time
import traceback
import socket
import urllib3

CHUNK = 512
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
#RATE = 16000
RATE = 32000

##################################################################
# set up command-line arguments
##################################################################
parser = argparse.ArgumentParser(prog=sys.argv[0], description='train with phrases', allow_abbrev=False)
parser.add_argument('--phrase', type=str, dest='continuousPhrase')
parser.add_argument('--max-bg-start-volume', type=int, dest='maxBackgroundStartVolume')
parser.add_argument('--max-bg-start-crossings', type=int, dest='maxBackgroundStartCrossings')
parser.add_argument('--length', type=int, dest='seconds')
parser.add_argument('--json-file', type=str, dest='phrasesJsonFile')
parser.add_argument('--find-noise-level', dest='findNoiseLevel', action='store_true')
parser.add_argument('--hands-free', dest='handsFree', action='store_true')
parser.add_argument('--semi-hands-free', dest='semiHandsFree', action='store_true')
parser.add_argument('--http-timeout',type=float, dest='httpTimeout', required=True)
parser.add_argument('--lSpeed',type=int, dest='leftSpeed', required=True)
parser.add_argument('--rSpeed',type=int, dest='rightSpeed', required=True)
parser.add_argument('--fbSpeed',type=int, dest='fwdBakSpeed', required=True)
parser.set_defaults(
        maxBackgroundStartVolume=9, 
        maxBackgroundStartCrossings=24, 
        seconds=5, 
        phrasesJsonFile='phrases.json', 
        continuousPhrase='')

args = parser.parse_args()



##################################################################
#init program global variables
##################################################################
#phrase=''
maxBackgroundStartVolume=args.maxBackgroundStartVolume
maxBackgroundStartCrossings=args.maxBackgroundStartCrossings
seconds=args.seconds
yesNoQuitJsonFile='yes.no.quit.json'
phrasesJsonFile=args.phrasesJsonFile
conversationJsonFile='conversation.json'
continuousPhrase=args.continuousPhrase
findNoiseLevel=args.findNoiseLevel
handsFree=args.handsFree
semiHandsFree=args.semiHandsFree
httpTimeout=args.httpTimeout
leftSpeed=args.leftSpeed
rightSpeed=args.rightSpeed
fwdBakSpeed=args.fwdBakSpeed

findNoiseLevelReadyToBegin = False
foundMaxBackgroundStartVolumeLevel = False
valueOfMaxBackgroundStartVolumeFound = sys.maxsize
foundMaxBackgroundStartCrossingsLevel = False
valueOfMaxBackgroundStartCrossingsFound = sys.maxsize

numActualRecordedFrames = 0
maxFramesBeforeTrim = int(RATE / CHUNK * seconds)
p = pyaudio.PyAudio()  # Create an interface to PortAudio
f = Figlet()
yesNoQuitArray = []
phrasesArray = []
conversationMap = {}

quitProgram = False
newPhraseAddedThisTime = False
newYesNoQuitAddedThisTime = False
saveJsonAndCleanUpAlreadyCalledOnce = False

robotMessagingUrl = 'http://10.0.0.58:8085/messaging/api'
robotIsReadyToDrive = False
robotDriveServerConnectionRefusedNumberOfTimes = 0;

tts = pyttsx3.init()

##################################################################
def say(phrase,waitTime):
    tts.say(phrase)
    tts.runAndWait()
    #print(phrase)
    time.sleep(waitTime)

##################################################################
def listPhrasesTrained(sayPhrases):

    listedPhrases = []
    print('')
    print('============================================================')
    for phrase in phrasesArray:
        phrStr = phrase['phrase']
        if not phrStr in listedPhrases:
            listedPhrases.append(phrStr)
            print(phrStr)
            if sayPhrases and phrStr != 'noise':
                say(phrStr,1)
    print('============================================================')
    print('')


##################################################################
def getUserVoiceInputMetaData():

    frames = recordAudio()
    if len(frames) > 0:
        metaData = getAudioMetaData(frames)
        addFakeAudioMetaDataForFillerFrames(metaData)
        return metaData
    else:
        return None

##################################################################
def getIsThisCorrectUserInput(justGetYesOrNoResponse, triedAgainForYesNo):

    global newYesNoQuitAddedThisTime

    previousPhrase = ''
    numYesNoQuitMatches = 0

    metaData = getUserVoiceInputMetaData()

    numMatches = 0
    isThisCorrect = False
    tryAgainForYesNo = False
    gotClearYesOrNo = False
    difference = sys.maxsize
    if metaData is not None:
        
        global yesNoQuitArray
        if len(yesNoQuitArray) > 0:
            difference, numMatches, bestMatch = findBestMatch(metaData, yesNoQuitArray)
            print('difference: ', difference, ', numMatches: ', numMatches)

        if (difference < 50 and numMatches > 5) or (difference < 300 and numMatches > 10)  or (difference < 400 and numMatches > 13) or (difference < 500 and numMatches > 15):

            newYesNoQuitAddedThisTime = True
            print('Found good match...')
            if bestMatch['phrase'] == 'yes':
                metaData['phrase'] = 'yes'
                isThisCorrect = True
            elif bestMatch['phrase'] == 'no':
                metaData['phrase'] = 'no'
                isThisCorrect = False
            yesNoQuitArray.append(metaData)
            gotClearYesOrNo = True

        elif semiHandsFree:
            if not triedAgainForYesNo:
                say('Yes or No?',.8)
                tryAgainForYesNo = True
            else:
                tryAgainForYesNo = False
                isThisCorrect = False
                if justGetYesOrNoResponse:
                    userResponse = input('Yes or No <y|n|noise> :')
                else:
                    userResponse = input('Correct ? <y|n|noise> :')
                if userResponse == 'y':
                    isThisCorrect = True
                    metaData['phrase'] = 'yes'
                    yesNoQuitArray.append(metaData)
                    newYesNoQuitAddedThisTime = True
                    gotClearYesOrNo = True
                elif userResponse == 'n':
                    metaData['phrase'] = 'no'
                    yesNoQuitArray.append(metaData)
                    newYesNoQuitAddedThisTime = True
                    gotClearYesOrNo = True
                elif userResponse == 'noise':
                    metaData['phrase'] = 'noise'
                    yesNoQuitArray.append(metaData)
                    newYesNoQuitAddedThisTime = True
                    gotClearYesOrNo = False

        elif handsFree:
            if not triedAgainForYesNo:
                say('Yes or No?', 0.8)
                tryAgainForYesNo = True
            else:
                tryAgainForYesNo = False
                isThisCorrect = False

        else:
            if justGetYesOrNoResponse:
                userResponse = input('Yes or No <y|n|noise> :')
            else:
                userResponse = input('Correct ? <y|n|noise> :')
            if userResponse == 'y':
                isThisCorrect = True
                metaData['phrase'] = 'yes'
                yesNoQuitArray.append(metaData)
                newYesNoQuitAddedThisTime = True
                tryAgainForYesNo = False
            elif userResponse == 'n':
                metaData['phrase'] = 'no'
                yesNoQuitArray.append(metaData)
                newYesNoQuitAddedThisTime = True
                tryAgainForYesNo = False
            elif userResponse == 'noise':
                metaData['phrase'] = 'noise'
                yesNoQuitArray.append(metaData)
                newYesNoQuitAddedThisTime = True
                tryAgainForYesNo = False


    return isThisCorrect, tryAgainForYesNo, gotClearYesOrNo

##################################################################
def saveJsonData():

    global newPhraseAddedThisTime
    global phrasesArray

    if newPhraseAddedThisTime and len(phrasesArray) > 0:
        print('Saving phrase meta data as JSON file...')
        phrasesFile = open(phrasesJsonFile,'w')
        phrasesFile.write(json.dumps(phrasesArray, indent=4))
        phrasesFile.close()

    global newYesNoQuitAddedThisTime
    global yesNoQuitArray

    if newYesNoQuitAddedThisTime and len(yesNoQuitArray) > 0:
        print('Saving Yes/No/Quit meta data as JSON file...')
        yesNoFile = open(yesNoQuitJsonFile,'w')
        yesNoFile.write(json.dumps(yesNoQuitArray, indent=4))
        yesNoFile.close()




##################################################################
def cleanUp():

    # Terminate the PortAudio interface
    global p
    p.terminate()
    print('Done.')
    sys.exit(0)

##################################################################
def saveJsonAndCleanUp():

    global saveJsonAndCleanUpAlreadyCalledOnce
    if saveJsonAndCleanUpAlreadyCalledOnce:
        cleanUp()

    saveJsonAndCleanUpAlreadyCalledOnce = True

    print('')
    print('')
    print('saveJsonAndCleanUp()')
    print('')
    print('')

    status = tellRobotVisionDriveControlToQuit()

    print('')
    print('')
    print('')
    print('')
    print('saveJsonAndCleanUp() status returned from telling robot to quit:')
    print(status)
    saveJsonData()

    count = 0
    while status != 'quit' and count < 2:
        print('')
        print('')
        print('')
        print('')
        print('saveJsonAndCleanUp() INSIDE LOOP , status returned from telling robot to quit:')
        print(status)
        status = tellRobotVisionDriveControlToQuit()
        count += 1

    cleanUp()

##################################################################
def signalHandler(signalReceived, frame):
    print('Got CTRL-C...')
    saveJsonAndCleanUp()

##################################################################
def isValidSound(frame, maxBackgroundVolume, maxBackgroundCrossings):
    jsonArray = []
    data = np.frombuffer(frame, dtype=np.int16)
    peak = np.amax(np.abs(data))
    bars = int(255*peak/2**16)
    crossings = numZeroCrossings(data)
    if bars > maxBackgroundVolume:
        return True, 'bars', bars, crossings
    if crossings > maxBackgroundCrossings:
        return True, 'crossings', bars, crossings
    else:
        return False, 'nothing', bars, crossings

##################################################################
def recordAudio():

    stream = p.open(format=sample_format,
                channels=channels,
                rate=RATE,
                frames_per_buffer=CHUNK,
                input=True)

    frames = []  # Initialize array to store frames

    print('recording...')

    isFirstValidSound = False
    lastSoundWasInvalid = False
    findNoiseLevelRecordTimedOut = False
    numConsecutiveInvalidSounds = 0
    if findNoiseLevel:
        startNoiseLevelRecordTime = time.time()
        noiseLevelRecordTime = startNoiseLevelRecordTime
    while not isFirstValidSound:
        if findNoiseLevel:
            noiseLevelRecordTime = time.time()
            if noiseLevelRecordTime - startNoiseLevelRecordTime > seconds:
                # Stop and close the stream 
                stream.stop_stream()
                stream.close()
                return frames
        data = stream.read(CHUNK, exception_on_overflow=False)
        resultTrue, why, bars, crossings = isValidSound(data, maxBackgroundStartVolume, maxBackgroundStartCrossings)
        if resultTrue:
            print('')
            print('')
            print('')
            print('.......capturing..... reason:', why, ' vol:', bars, ' crossings:', crossings)
            isFirstValidSound = True
            frames.append(data)

    for i in range(0, maxFramesBeforeTrim):
        data = stream.read(CHUNK, exception_on_overflow=False)
        isValid, why, bars, crossings = isValidSound(data, maxBackgroundStartVolume, maxBackgroundStartCrossings)
        if lastSoundWasInvalid and not isValid:
            numConsecutiveInvalidSounds += 1
        elif not isValid:
            numConsecutiveInvalidSounds = 1
            lastSoundWasInvalid = True
        else:
            lastSoundWasInvalid = False

        if numConsecutiveInvalidSounds > 25:
            print('...Aborting capture..... reason:', why, ' vol:', bars, ' crossings:', crossings)
            print('')
            print('')
            print('')
            break

        frames.append(data)

    global numActualRecordedFrames
    numActualRecordedFrames = len(frames)
    if numActualRecordedFrames > maxFramesBeforeTrim:
        numActualRecordedFrames = maxFramesBeforeTrim

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()

    return frames

##################################################################
def compareTwoPhraseMetaData(phrase1, phrase2):

    numFrames1 = phrase1['numRecFrames']
    numFrames2 = phrase2['numRecFrames']
    crossingsDiff = 0
    peakDiff = 0
    for i in range(numFrames1):
        try:
            data1 = phrase1['frameData'][i]
            data2 = phrase2['frameData'][i]
        except:
            print('')
            print('')
            print(phrase1)
            print('')
            print(phrase2)
            print('')
            print('')
            print('numFrames1:', numFrames1, ' numFrames2:', numFrames2)
            print('')
            print('i:',i)
            sys.exit(1)

        crDiff = abs(data1['crossings'] - data2['crossings'])
        pkDiff = abs(data1['peak'] - data2['peak'])
        crossingsDiff += crDiff
        peakDiff += pkDiff

    numFramesDiff = abs(phrase1['numRecFrames'] - phrase2['numRecFrames'])
    return crossingsDiff, peakDiff, numFramesDiff

##################################################################
def dictHasKey(dict, key):
    if key in dict:
        return True
    else:
        return False

##################################################################
def findBestMatch(latestPhraseData, phrasesArray):


    numPhrases = len(phrasesArray)

    leastDiff = sys.maxsize
    bestMatchIndex = -1
    previousPhrase = ''
    numMatches = 0
    for i in range(numPhrases):
        phraseData = phrasesArray[i]
        crDiff, pkDiff, numFramesDiff = compareTwoPhraseMetaData(latestPhraseData, phraseData)
        difference = crDiff + pkDiff + numFramesDiff
        if leastDiff > difference:
            leastDiff = difference
            bestMatchIndex = i

            if not dictHasKey(phraseData,'phrase'):
                print('Error: Num Array Items: ', str(numPhrases), ', idx: ', str(i), ' is missing \'phrase\'')
                saveJsonData()
                sys.exit(1)
            if phraseData['phrase'] == previousPhrase:
                numMatches += 1
            else:
                numMatches = 0
                previousPhrase = phraseData['phrase']

            print(phraseData['phrase'], ' ', leastDiff)


    return leastDiff, numMatches, phrasesArray[bestMatchIndex]

##################################################################
def numZeroCrossings(data):
    length = data.size
    i = 0
    crossings = 0
    while i < length - 1:
        if (data[i] > 0 and data[i+1] < 0) or (data[i] < 0 and data[i+1] > 0):
            crossings += 1
        i += 2
    return crossings

##################################################################
def getAudioMetaData(frames):

    jsonArray = []
    for i in range(len(frames)):
        data = np.frombuffer(frames[i], dtype=np.int16)
        crossings = numZeroCrossings(data)
        peak = np.amax(np.abs(data))
        bars = int(255*peak/2**16)
        #dispbars = '#'*int(255*peak/2**16)
        #print(dispbars)
        jsonStr = {"crossings": crossings, "peak": bars}
        jsonArray.append(jsonStr)

    jsonObject = {
            #"phrase": phrase, 
            "recLimitSecs": seconds,
            "framesLimit": maxFramesBeforeTrim,
            "numRecFrames": numActualRecordedFrames, "frameData": jsonArray }
    return jsonObject

##################################################################
def addFakeAudioMetaDataForFillerFrames(metaData):

    numRecFrames = metaData['numRecFrames']
    framesLimit  = metaData['framesLimit']
    numFillFrames = framesLimit - numRecFrames
    frameData = metaData['frameData']
    for i in range(numFillFrames):
        frameData.append({"crossings": 0, "peak": 0})
    #metaData['numRecFrames'] = framesLimit

##################################################################
def countVolumeValue(data, value):
    count = 0
    for i in range(len(data)):
        if data[i] == value:
            count += 1
    return count

##################################################################
def loadJsonDataFromFiles():

    global yesNoQuitArray
    global phrasesArray
    global conversationMap

    print('Load Existing Yes/No/Quit JSON meta data from file...')
    try:
        yesNoQuitFile = open(yesNoQuitJsonFile,'r')
        yesNoQuitString = yesNoQuitFile.read()
        yesNoQuitFile.close()
        yesNoQuitArray = json.loads(yesNoQuitString)
        print('Existing Yes/No/Quit JSON meta data loaded from file.')
    except json.decoder.JSONDecodeError:
        print('')
        print('bad Yes/No/Quit JSON file data..')
        print('')
        sys.exit(1)
    except FileNotFoundError:
        print('')
        print('No Yes/No/Quit JSON file Data..')
        print('')


    print('Load Existing phrases JSON meta data from file...')
    try:
        phrasesFile = open(phrasesJsonFile,'r')
        phrasesString = phrasesFile.read()
        phrasesFile.close()
        phrasesArray = json.loads(phrasesString)
        print('Existing phrases JSON meta data loaded from file.')
    except json.decoder.JSONDecodeError:
        print('')
        print('bad phrases JSON file data..')
        print('')
        sys.exit(1)
    except FileNotFoundError:
        print('')
        print('No phrases JSON file Data..')
        print('')


    print('Load Existing conversation JSON file...')
    try:
        conversationFile = open(conversationJsonFile,'r')
        conversationString = conversationFile.read()
        conversationFile.close()
        conversationMap = json.loads(conversationString)
        print('Existing conversation JSON file loaded.')
    except json.decoder.JSONDecodeError:
        print('')
        print('bad conversation JSON file data..')
        print('')
        cleanUp()
    except FileNotFoundError:
        print('')
        print('No conversation JSON file Data..')
        print('')
        cleanUp()


##################################################################
def findTheNoiseLevel(phraseFrames):
    print('we are in find-noise-level mode....')

    global maxBackgroundStartVolume
    global valueOfMaxBackgroundStartVolumeFound
    global foundMaxBackgroundStartVolumeLevel
    global foundMaxBackgroundStartCrossingsLevel
    global valueOfMaxBackgroundStartCrossingsFound
    global maxBackgroundStartCrossings

    if len(phraseFrames) > 0 and not foundMaxBackgroundStartVolumeLevel:
        valueOfMaxBackgroundStartVolumeFound = maxBackgroundStartVolume
        maxBackgroundStartVolume = sys.maxsize
        foundMaxBackgroundStartVolumeLevel = True
        input('Found Start Background Volume Noise Level: ' +  str(valueOfMaxBackgroundStartVolumeFound) + ' ; <ENTER>: ')
        #continue
        return False


    if len(phraseFrames) > 0 and foundMaxBackgroundStartVolumeLevel and not foundMaxBackgroundStartCrossingsLevel:
        valueOfMaxBackgroundStartCrossingsFound = maxBackgroundStartCrossings
        foundMaxBackgroundStartCrossingsLevel = True
        print('Found Start Background Crossings Noise Level: ', valueOfMaxBackgroundStartCrossingsFound)
        print('Found Start Background Volume Noise Level: ', valueOfMaxBackgroundStartVolumeFound)
        #break
        return True

    if len(phraseFrames) < 1:
        print('we are in find-noise-level mode and nothing was recorded so we might change some params....')
        if not foundMaxBackgroundStartVolumeLevel:

            if maxBackgroundStartVolume > 0:
                maxBackgroundStartVolume -= 1
                print('Lowered Start Background Volume Threshold: ', maxBackgroundStartVolume)
            else:
                valueOfMaxBackgroundStartVolumeFound = maxBackgroundStartVolume
                maxBackgroundStartVolume = sys.maxsize
                foundMaxBackgroundStartVolumeLevel = True
                input('Found Start Background Volume Noise Level: ' +  str(valueOfMaxBackgroundStartVolumeFound) + ' ; <ENTER>: ')

        if foundMaxBackgroundStartVolumeLevel and not foundMaxBackgroundStartCrossingsLevel:

            if maxBackgroundStartCrossings > 0:
                maxBackgroundStartCrossings -= 1
                print('Lowered Start Background Crossings Threshold: ', maxBackgroundStartCrossings)
            else:
                valueOfMaxBackgroundStartCrossingsFound = maxBackgroundStartCrossings
                foundMaxBackgroundStartCrossingsLevel = True
                input('Found Start Background Crossings Noise Level: ' + str(valueOfMaxBackgroundStartCrossingsFound) + '. Press <ENTER>:')
                #break
                return True


    return False

##################################################################
def doAction(action, successText = 'Success', successDelay = 1, failureText = 'Failure'):
    if action == 'doOfferHelp':
        offerHelp()
        return
    if action == 'doListPhrasesTrained':
        sayPhrases = False
        listPhrasesTrained(sayPhrases)
        return
    if action == 'doGoodBye':
        doGoodBye(successText)
        return
    if action == 'doCurrentTime':
        sayCurrentTime()
        return
    if action == 'doInitRobotDrive':
        global robotIsReadyToDrive
        if not robotIsReadyToDrive:
            robotIsReadyToDrive = initRobotDrive()
            if robotIsReadyToDrive:
                say(successText, 1.5)
            else:
                say('Robot Init Error', 1.5)
        return
    if action == 'doDoYouSeeMe':
        getUpdateLatestStatus = True
        status = getRobotStatus(getUpdateLatestStatus)
        print('')
        print(status)
        print('')
        if status == 'Refused':
            say('Refused', successDelay)

        elif status == None:
            say('Status None.', successDelay)

        elif status != None and 'visual' in status.keys():
            visual = status['visual']
            if 'faceDetected' in visual.keys() and visual['faceDetected'] == True:
                say(successText, successDelay)
            else:
                say(failureText, successDelay)
        return

    if action == 'doForward':
        sendRobotDriveCommand('forward', fwdBakSpeed)
        #time.sleep(1.2)
        #sendRobotDriveCommand('forward')
        #time.sleep(1.2)
        #sendRobotDriveCommand('forward')
        say('Did ' + successText + '.', 2)
        return
    if action == 'doBackward':
        sendRobotDriveCommand('backward', fwdBakSpeed)
        #time.sleep(1.2)
        #sendRobotDriveCommand('forward')
        #time.sleep(1.2)
        #sendRobotDriveCommand('forward')
        say('Did ' + successText + '.', 2)
        return
    if action == 'doLeft':
        sendRobotDriveCommand('left', leftSpeed)
        #time.sleep(1.2)
        #sendRobotDriveCommand('forward')
        #time.sleep(1.2)
        #sendRobotDriveCommand('forward')
        say('Did ' + successText + '.', 2)
        return
    if action == 'doRight':
        sendRobotDriveCommand('right', rightSpeed)
        #time.sleep(1.2)
        #sendRobotDriveCommand('forward')
        #time.sleep(1.2)
        #sendRobotDriveCommand('forward')
        say('Did ' + successText + '.', 2)
        return





    say('Do not know action ' + action + '.', 1.5)

##################################################################
def doGoodBye(phraseText):
    metaDataForLatestRecordedPhrase['phrase'] = phraseText
    print('')
    print('Saving : ', phraseText)
    print('')
    phrasesArray.append(metaDataForLatestRecordedPhrase)
    global newPhraseAddedThisTime
    newPhraseAddedThisTime = True
    saveJsonAndCleanUp()


##################################################################
def offerHelp():
    sayPhrases = True
    listPhrasesTrained(sayPhrases)

##################################################################
def sayCurrentTime():
    say(datetime.now().strftime('%H:%M'),1.5)

##################################################################
def wallaceIndicatesReadiness():

    #print('Wallace is ready.')

    say('Wallace is ready.  Do you need help?',0.5)
    justGetYesOrNoResponse = True

    doHelp, tryAgainForYesNo, gotClearYesOrNo = getIsThisCorrectUserInput(justGetYesOrNoResponse, False)

    if not tryAgainForYesNo and gotClearYesOrNo and not doHelp:
        say('Very well, good show. Ready.',2);
        return

    if not tryAgainForYesNo and doHelp:
        offerHelp()
        return

    if tryAgainForYesNo:

        doHelp, tryAgainForYesNo, gotClearYesOrNo = getIsThisCorrectUserInput(justGetYesOrNoResponse, True)

        if not tryAgainForYesNo and gotClearYesOrNo and not doHelp:
            say('Very well, good show. Ready.',2);
            return

        if not tryAgainForYesNo and doHelp:
            offerHelp()
            return

        if not tryAgainForYesNo:
            say('Sorry.',1)


    say('I am confused.', 1.5)


##################################################################
def sendGetMessage(completeUriString):

    global robotDriveServerConnectionRefusedNumberOfTimes

    try:
        print(robotMessagingUrl + completeUriString)
        response = requests.get(url=robotMessagingUrl + completeUriString, timeout=httpTimeout)
        robotDriveServerConnectionRefusedNumberOfTimes = 0;
        return response.text
    except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        return 'Timeout'
    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        time.sleep(0.20)
        robotDriveServerConnectionRefusedNumberOfTimes += 1;
        if robotDriveServerConnectionRefusedNumberOfTimes > 3:
            saveJsonAndCleanUp()
        return 'Refused'
    except:
        track = traceback.format_exc()
        print(track)
        say('Other Communication Error', 0)
        saveJsonAndCleanUp()


##################################################################
def waitForVisionRobotControlToBeReadyForNextCommand():

    isReady = False
    count = 0
    while not isReady and count < 20:
        count += 1
        isReady = checkIfVisionRobotControlIsReadyForNextCommand()
        if isReady:
            break
        print('')
        print('')
        print('sendPostMessage(): vision program not yet ready for this next command..')
        print('')
        print('')

        time.sleep(0.2)

    if not isReady:
        track = traceback.format_exc()
        print(track)
        say('Other Communication Error', 0)

    return isReady

##################################################################
def sendPostMessage(completeUriString):

    global robotDriveServerConnectionRefusedNumberOfTimes

    waitForVisionRobotControlToBeReadyForNextCommand()

    try:
        print(robotMessagingUrl + completeUriString)
        response = requests.post(url=robotMessagingUrl + completeUriString, timeout=httpTimeout)

        robotDriveServerConnectionRefusedNumberOfTimes = 0;
        return response.text
    except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        return 'Timeout'
    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        time.sleep(0.2)
        robotDriveServerConnectionRefusedNumberOfTimes += 1;
        if robotDriveServerConnectionRefusedNumberOfTimes > 3:
            saveJsonAndCleanUp()
        return 'Refused'
    except:
        track = traceback.format_exc()
        print(track)
        say('Other Communication Error', 0)
        saveJsonAndCleanUp()


##################################################################
def checkIfVisionRobotControlIsReadyForNextCommand():

    print('')
    print('checkIfVisionRobotControlIsReadyForNextCommand()...')
    print('')

    possibleJsonResp = sendGetMessage('/vision/ready?from=voice.control')
    try:
        response = json.loads(possibleJsonResp)
        print(response)
        if type(response) is dict:
            if 'ready' in response.keys()and response['ready'] == True:
                return True
            return False
        else:
            track = traceback.format_exc()
            print(track)
            print('')
            print(possibleJsonResp)
            print('')
            saveJsonAndCleanUp()
    except:
        track = traceback.format_exc()
        print(track)
        print('')
        print(possibleJsonResp)
        print('')
        saveJsonAndCleanUp()

##################################################################
def clearMessagingCommand():

    print('')
    print('clearMessagingCommand() : clear the previous messaging command...')
    print('')

    possibleJsonResp = sendDeleteMessage('/vision/command?from=voice.control')
    try:
        response = json.loads(possibleJsonResp)
        print(response)
        if 'msg' in response.keys() and response['msg'] == 'ok':
            return True
        return False
    except:
        track = traceback.format_exc()
        print(track)
        print('')
        print(possibleJsonResp)
        print('')
        saveJsonAndCleanUp()

##################################################################
def tellRobotVisionDriveControlToQuit():

    print('')
    print('')
    print('')
    print('tellRobotVisionDriveControlToQuit() : send post command requesting latest status...')
    print('')

    possibleJsonResp = sendPostMessage('/vision/command/quit?from=voice.control')
    if 'Refused' in possibleJsonResp:
        status = 'Refused'
        return status
    try:
        response = json.loads(possibleJsonResp)
        #print(response)
    except:
        track = traceback.format_exc()
        print(track)
        print('')
        print(possibleJsonResp)
        print('')
        print('NO STATUS')
        print('')
        status = None
        return status

    print('')
    print('tellRobotVisionDriveControlToQuit() : now waiting for vision to post status, to get latest status...')
    print('')

    time.sleep(2)

    possibleJsonResp = sendGetMessage('/vision/status?from=voice.control')
    if 'Refused' in possibleJsonResp:
        status = 'Refused'
        return status
    try:
        response = json.loads(possibleJsonResp)
        print(response)
    except:
        track = traceback.format_exc()
        print(track)
        print('')
        print(possibleJsonResp)
        print('')
        print('NO STATUS')
        print('')
        status = None
        return status


    if 'status' in response.keys() and response['status'] != '':
        status = response['status']
        if type(status) is dict and 'quit' in status.keys():
            status = 'quit'
    else:
        status = None

    return status


##################################################################
def getRobotStatus(getUpdatedStatus=False):

    if getUpdatedStatus:
        print('')
        print('')
        print('')
        print('getRobotStatus() : send post command requesting latest status...')
        print('')

        possibleJsonResp = sendPostMessage('/vision/command/status?from=voice.control')
        if 'Refused' in possibleJsonResp:
            status = 'Refused'
            return status
        try:
            response = json.loads(possibleJsonResp)
            #print(response)
        except:
            track = traceback.format_exc()
            print(track)
            print('')
            print(possibleJsonResp)
            print('')
            print('NO STATUS')
            print('')
            #saveJsonAndCleanUp()
            status = None
            return status

        print('')
        print('getRobotStatus() : now waiting for vision to post status, to get latest status...')
        print('')

        waitForVisionRobotControlToBeReadyForNextCommand()

    print('')
    print('getRobotStatus() : get status...')
    print('')

    possibleJsonResp = sendGetMessage('/vision/status?from=voice.control')
    if 'Refused' in possibleJsonResp:
        status = 'Refused'
        return status
    try:
        response = json.loads(possibleJsonResp)
        #print(response)
    except:
        track = traceback.format_exc()
        print(track)
        print('')
        print(possibleJsonResp)
        print('')
        print('NO STATUS')
        print('')
        #saveJsonAndCleanUp()
        status = None
        return status

    print('')
    print('getRobotStatus() : get status IS: ')
    print('')
    print(response)


    if 'status' in response.keys() and response['status'] != '':
        status = response['status']
    else:
        status = None

    return status


##################################################################
def initRobotDrive():


    possibleJsonResp = sendPostMessage('/vision/command/initialize')
    if possibleJsonResp == 'Refused':
        say('Refused',0)
        saveJsonAndCleanUp()
    try:
        response = json.loads(possibleJsonResp)
        print(response)
    except:
        track = traceback.format_exc()
        print(track)
        print('')
        print(possibleJsonResp)
        print('')
        saveJsonAndCleanUp()

    #time.sleep(3)
    waitForVisionRobotControlToBeReadyForNextCommand()

    getUpdateLatestStatus = True
    status = getRobotStatus(getUpdateLatestStatus)

    if status != None:
        #status = response['status']
        if type(status) is dict:
            if 'error' in status.keys() and status['error'] == '':
                #return clearMessagingCommand()
                return True
        else:
            track = traceback.format_exc()
            print(track)
            print('')
            print(status)
            print('')
            saveJsonAndCleanUp()

    return False

##################################################################
def sendRobotDriveCommand(direction, mySpeed):
    global robotIsReadyToDrive
    if not robotIsReadyToDrive:
        robotIsReadyToDrive = initRobotDrive()
    if robotIsReadyToDrive:
        respText = sendPostMessage('/arduino/api/' + direction + '/' + str(mySpeed))
        if not 'Cmd Sent To Arduino' in respText:
            print(respText)
            say(respText,2)

##################################################################
def sendRobotNodeJsCommand(command, resultExpected, sayOnGoodResult):
    global robotIsReadyToDrive
    if not robotIsReadyToDrive:
        robotIsReadyToDrive = initRobotDrive()
    if robotIsReadyToDrive:
        respText = sendGetMessage('/nodejs/api/' + command)
        if not 'volts\":12' in respText:
            print(respText)
            say(respText,2)
        else:
            say(sayOnGoodResult,1)




##################################################################
def actOnKnownPhrases(phraseText, metaDataForLatestRecordedPhrase):

    try:
        conversation = conversationMap[phraseText]
    except (KeyError):
        say('Do not know conversation for ' + phraseText, 2.5)
        return
    except:
        track = traceback.format_exc()
        print(track)
        return

    if phraseText == 'noise':
        return

    if conversation['firstresp'] != 'none' and conversation['firstresp'] != '':
        say(conversation['firstresp'], int(conversation['delay']))
        if conversation['action'] == 'none' or conversation['action'] == '':
            return

    if conversation['action'] != 'none' and conversation['action'] != '':
        if 'successresp' in conversation.keys() and 'successdelay' in conversation.keys() and 'failresp' in conversation.keys():
            doAction(conversation['action'], conversation['successresp'], conversation['successdelay'], conversation['failresp'])
        elif 'successresp' in conversation.keys() and 'successdelay' in conversation.keys():
            doAction(conversation['action'], conversation['successresp'], conversation['successdelay'])
        elif 'successresp' in conversation.keys():
            doAction(conversation['action'], conversation['successresp'])
        else:
            doAction(conversation['action'], phraseText)
        return


    say('Do not know what to do with ' + phraseText, 2)

##################################################################
if __name__ == '__main__':
    signal(SIGINT, signalHandler)



if not findNoiseLevel:
    loadJsonDataFromFiles()
    wallaceIndicatesReadiness()

while not quitProgram:

    # if a continuousPhrase was given, we dont need to ask for input.
    # we just keep listening, and assign that continuous phrase to everthing.
    # if we are in finding noise level mode, we also do not prompt for input.
    # there is also the option to be more conversational, where it acts on phrases,
    # AND does live training, so we dont want user to have to keep hitting <ENTER> here.
    if not handsFree and not semiHandsFree:
        if continuousPhrase == '' or (findNoiseLevel and not findNoiseLevelReadyToBegin):

            sayPhrases = False
            listPhrasesTrained(sayPhrases)

            if findNoiseLevel:
                findNoiseLevelReadyToBegin = True

            userInput = input('Press <ENTER> to record, or \'q\' to quit program: ')

            if userInput == 'q':
                break


    phraseFrames = recordAudio()

    print('phrase frames: ', len(phraseFrames), ' vol thre: ', maxBackgroundStartVolume, ', cros the:' , maxBackgroundStartCrossings)
    # we assume here that:
    #   we are not attempting to record particular phrase.
    #   we are merely establishing what is the level of background noise.
    #   we start with a very high value and just listen,
    #       expecting NO audio result, and we slowly lower the value
    #       until we DO get an audio result.
    #       That is our background level
    if continuousPhrase and findNoiseLevel:

        if findTheNoiseLevel(phraseFrames):
            break
        else:
            continue


    if len(phraseFrames) > 0:
 

        metaDataForLatestRecordedPhrase = getAudioMetaData(phraseFrames)
        addFakeAudioMetaDataForFillerFrames(metaDataForLatestRecordedPhrase)


        if continuousPhrase != '':
            metaDataForLatestRecordedPhrase['phrase'] = continuousPhrase
            phrasesArray.append(metaDataForLatestRecordedPhrase)
            newPhraseAddedThisTime = True
            continue

        if len(phrasesArray) > 0:


            difference, numMatches, bestPhraseMatch = findBestMatch(metaDataForLatestRecordedPhrase, phrasesArray)
            bestPhrase = bestPhraseMatch['phrase']
            try:
                conversation = conversationMap[bestPhrase]
                verify = conversation['verify']
            except:
                verify = None
            print('best Phrase Match: ', bestPhrase, '  numMatches: ', numMatches)
            if (verify == 'assume' and numMatches > 1) or (difference < 150 and numMatches > 6) or (difference < 250 and numMatches > 8):
                print(f.renderText(bestPhraseMatch['phrase']))
                needPhrase = bestPhraseMatch['phrase']
                actOnKnownPhrases(needPhrase, metaDataForLatestRecordedPhrase)
            else:
                print(f.renderText(bestPhraseMatch['phrase']))
                #say('Did you say ' + bestPhraseMatch['phrase'] + '?')
                if verify != None and verify != 'assume':
                    say(verify, 1.5)
                else:
                    say('Did you say ' + bestPhrase + '?"', 1.5)
                justGetYesOrNoResponse = False
                isThisCorrect, tryAgainForYesNo, gotClearYesOrNo = getIsThisCorrectUserInput(justGetYesOrNoResponse, False)
                if not tryAgainForYesNo and isThisCorrect:
                    needPhrase = bestPhraseMatch['phrase']
                    actOnKnownPhrases(needPhrase, metaDataForLatestRecordedPhrase)
                elif not tryAgainForYesNo and not isThisCorrect:
                    say('Enter phrase.', 1)
                    needPhrase = input('Need to assign new phrase to this latest recording:')
                elif tryAgainForYesNo:
                    isThisCorrect, tryAgainForYesNo, gotClearYesOrNo = getIsThisCorrectUserInput(justGetYesOrNoResponse, True)
                    if not tryAgainForYesNo and isThisCorrect:
                        needPhrase = bestPhrase
                        actOnKnownPhrases(needPhrase, metaDataForLatestRecordedPhrase)
                    elif not tryAgainForYesNo and gotClearYesOrNo and not isThisCorrect:
                        say('Enter phrase.', 1)
                        needPhrase = input('Need to assign new phrase to this latest recording:')
                    else:
                        say('Sorry.', 1)
                        continue
                else:
                    say('Sorry.', 1)
                    continue
        else:
            needPhrase = input('Need to assign new phrase to this latest recording:')

        if len(needPhrase) > 0:
            metaDataForLatestRecordedPhrase['phrase'] = needPhrase
            print('')
            print('Saving : ', metaDataForLatestRecordedPhrase['phrase'])
            print('')
            phrasesArray.append(metaDataForLatestRecordedPhrase)
            newPhraseAddedThisTime = True
        else:
            print('Throwing new recording away....')


    else:
        print('Nothing Recorded ....')
        print('Nothing Recorded ....')
        print('Nothing Recorded ....')



# Terminate the PortAudio interface
p.terminate()

saveJsonData()



