##################################################################
# this uses byte objects
# good values: 90 150
##################################################################
import sys
import os
import argparse
import pyaudio
import numpy as np
import wave
import statistics 
import json
import talkey
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
continuousPhrase=args.continuousPhrase
findNoiseLevel=args.findNoiseLevel
handsFree=args.handsFree

findNoiseLevelReadyToBegin = False
foundMaxBackgroundStartVolumeLevel = False
valueOfMaxBackgroundStartVolumeFound = sys.maxsize
foundMaxBackgroundStartCrossingsLevel = False
valueOfMaxBackgroundStartCrossingsFound = sys.maxsize

numActualRecordedFrames = 0
maxFramesBeforeTrim = int(RATE / CHUNK * seconds)
textToSpeech = talkey.Talkey(preferred_language=['en'])
p = pyaudio.PyAudio()  # Create an interface to PortAudio
f = Figlet()
yesNoQuitArray = []
phrasesArray = []

quitProgram = False
newPhraseAddedThisTime = False
newYesNoQuitAddedThisTime = False


robotDriveUrl = 'http://10.0.0.58:8084'
robotIsReadyToDrive = False

##################################################################
def listPhrasesTrained(sayPhrases):

    listedPhrases = []
    for phrase in phrasesArray:
        phrStr = phrase['phrase']
        if not phrStr in listedPhrases:
            listedPhrases.append(phrStr)
            print(phrStr)
            if sayPhrases and phrStr != 'noise':
                textToSpeech.say(phrStr)


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
def getIsThisCorrectUserInput(justGetYesOrNoResponse):

    global newYesNoQuitAddedThisTime

    previousPhrase = ''
    numYesNoQuitMatches = 0

    metaData = getUserVoiceInputMetaData()

    numMatches = 0
    isThisCorrect = False
    tryAgainForYesNo = False
    difference = sys.maxsize
    if metaData is not None:
        
        global yesNoQuitArray
        if len(yesNoQuitArray) > 0:
            difference, numMatches, bestMatch = findBestMatch(metaData, yesNoQuitArray)
            print('difference: ', difference, ', numMatches: ', numMatches)

        if (difference < 400 and numMatches > 3) or (difference < 650 and numMatches > 5) or (difference < 550 and numMatches > 4):
            newYesNoQuitAddedThisTime = True
            print('Found good match...')
            if bestMatch['phrase'] == 'yes':
                metaData['phrase'] = 'yes'
                isThisCorrect = True
            elif bestMatch['phrase'] == 'no':
                metaData['phrase'] = 'no'
                isThisCorrect = False
            yesNoQuitArray.append(metaData)
        elif handsFree:
            textToSpeech.say('Yes or No?')
            tryAgainForYesNo = True
        else:
            if justGetYesOrNoResponse:
                userResponse = input('Yes or No <y|n> :')
            else:
                userResponse = input('Correct ? <y|n> :')
            if userResponse == 'y':
                isThisCorrect = True
                metaData['phrase'] = 'yes'
                yesNoQuitArray.append(metaData)
                newYesNoQuitAddedThisTime = True
            elif userResponse == 'n':
                metaData['phrase'] = 'no'
                yesNoQuitArray.append(metaData)
                newYesNoQuitAddedThisTime = True


    return isThisCorrect, tryAgainForYesNo

##################################################################
def saveJsonData():

    global newPhraseAddedThisTime
    global phrasesArray

    if newPhraseAddedThisTime and len(phrasesArray) > 0:
        print('Saving meta data as JSON file...')
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
def signalHandler(signalReceived, frame):
    print('Got CTRL-C...')


    # Terminate the PortAudio interface
    global p
    p.terminate()

    saveJsonData()

    print('Done.')

    sys.exit(0)


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
    numConsecutiveInvalidSounds = 0
    while not isFirstValidSound:
        data = stream.read(CHUNK, exception_on_overflow=False)
        resultTrue, why, bars, crossings = isValidSound(data, maxBackgroundStartVolume, maxBackgroundStartCrossings)
        if resultTrue:
            print('')
            print('')
            print('')
            print('.......capturing..... reason:', why, ' vol:', bars, ' crossings:', crossings)
            isFirstValidSound = True
            frames.append(data)

    for i in range(0, int(RATE / CHUNK * seconds)):
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

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()

    return frames

##################################################################
def compareTwoPhraseMetaData(phrase1, phrase2):

    numFrames = phrase1['numRecFrames']

    crossingsDiff = 0
    peakDiff = 0
    for i in range(numFrames):
            data1 = phrase1['frameData'][i]
            data2 = phrase2['frameData'][i]
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
def isValidStartingSound(data, maxBackground):

    try:

        mode = statistics.mode(data)
        volCount = countVolumeValue(data, mode)

        print('mode:', mode, ', volCount:', volCount, ', maxBackground:', maxBackground)

        if mode > 250  and volCount>= maxBackground:
            return False
        if mode < 3    and volCount >= maxBackground:
            return False

        if mode >= 3 and mode <= 250 and volCount >= maxBackground:
            return True

        return False

    except:
        #print('exception')
        return False

##################################################################
def loadJsonDataFromFiles():

    global yesNoQuitArray
    global phrasesArray

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


    print('Load Existing JSON meta data from file...')
    try:
        phrasesFile = open(phrasesJsonFile,'r')
        phrasesString = phrasesFile.read()
        phrasesFile.close()
        phrasesArray = json.loads(phrasesString)
        print('Existing JSON meta data loaded from file.')
    except json.decoder.JSONDecodeError:
        print('')
        print('bad JSON file data..')
        print('')
        sys.exit(1)
    except FileNotFoundError:
        print('')
        print('No JSON file Data..')
        print('')


##################################################################
def findNoiseLevel(phraseFrames):
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
def offerHelp():

    textToSpeech.say('You may say, ')
    sayPhrases = True
    listPhrasesTrained(sayPhrases)

##################################################################
def wallaceIndicatesReadiness():

    textToSpeech.say('Wallace is ready.  Do you need help?')
    justGetYesOrNoResponse = True

    doHelp, tryAgainForYesNo = getIsThisCorrectUserInput(justGetYesOrNoResponse)

    if not tryAgainForYesNo and not doHelp:
        textToSpeech.say('Very well, good show. Ready.');
        return

    if not tryAgainForYesNo and doHelp:
        offerHelp()
        return

    if tryAgainForYesNo:

        doHelp, tryAgainForYesNo = getIsThisCorrectUserInput(justGetYesOrNoResponse)

        if not tryAgainForYesNo and not doHelp:
            textToSpeech.say('Very well, good show. Ready.');
            return

        if not tryAgainForYesNo and doHelp:
            offerHelp()
            return

        if tryAgainForYesNo:
            textToSpeech.say('Sorry.')


    textToSpeech.say('I am confused.')


##################################################################
def initRobotDrive():
    respText = sendRobotUrl('/arduino/api/clr.usb.err')

    if 'Cmd Sent To Arduino' in respText:
        respText = sendRobotUrl('/nodejs/api/stop.console.log.response')
        if 'Cmd Sent To Arduino' in respText:
            textToSpeech.say('Robot Is Ready.')
        return True
    else:
        print(respText)
        textToSpeech.say(respText)

    return False

##################################################################
def sendRobotUrl(command):
    try:
        response = requests.get(robotDriveUrl + command, timeout=1.5)
        return response.text
    except (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        #track = traceback.format_exc()
        #print(track)
        textToSpeech.say('The request timed out.')
        return ''

##################################################################
def sendRobotDriveCommand(direction):
    global robotIsReadyToDrive
    if not robotIsReadyToDrive:
        robotIsReadyToDrive = initRobotDrive()
    if robotIsReadyToDrive:
        respText = sendRobotUrl('/arduino/api/' + direction + '/100')
        if not 'Cmd Sent To Arduino' in respText:
            print(respText)
            textToSpeech.say(respText)

##################################################################
def sendRobotNodeJsCommand(command, resultExpected, sayOnGoodResult):
    global robotIsReadyToDrive
    if not robotIsReadyToDrive:
        robotIsReadyToDrive = initRobotDrive()
    if robotIsReadyToDrive:
        respText = sendRobotUrl('/nodejs/api/' + command)
        if not 'volts\":12' in respText:
            print(respText)
            textToSpeech.say(respText)
        else:
            textToSpeech.say(sayOnGoodResult)




##################################################################
def actOnKnownPhrases(phrase, metaDataForLatestRecordedPhrase):

    global robotIsReadyToDrive

    if phrase == 'noise':
        return
    if phrase == 'help please':
        offerHelp()
        return
    if phrase == 'hello wallace':
        textToSpeech.say('Hello, how are you today?')
        return
    if phrase == 'thank you wallace':
        textToSpeech.say('You are welcome.')
        return
    if phrase == 'fine thank you':
        textToSpeech.say('Good show.')
        return
    if phrase == 'what time is it':
        textToSpeech.say(datetime.now().strftime('%H:%M'))
        return

    if phrase == 'list please':
        sayPhrases = False
        listPhrasesTrained(sayPhrases)
        return

    if phrase == 'quit' or phrase == 'good-bye wallace' or phrase == 'that is all':
        textToSpeech.say('Good-bye.')
        metaDataForLatestRecordedPhrase['phrase'] = phrase
        print('')
        print('Saving : ', phrase)
        print('')
        phrasesArray.append(metaDataForLatestRecordedPhrase)
        global newPhraseAddedThisTime
        newPhraseAddedThisTime = True
        saveJsonData()
        sys.exit(0)

    if phrase == 'init robot drive':
        robotIsReadyToDrive = initRobotDrive()
        return


    if phrase == 'forward':
        sendRobotDriveCommand('forward')
        time.sleep(1.2)
        sendRobotDriveCommand('forward')
        time.sleep(1.2)
        sendRobotDriveCommand('forward')
        textToSpeech.say('Executed ' + phrase)
        return

    if phrase == 'back':
        sendRobotDriveCommand('backward')
        time.sleep(1.2)
        sendRobotDriveCommand('backward')
        time.sleep(1.2)
        sendRobotDriveCommand('backward')
        textToSpeech.say('Executed ' + phrase)
        return

    if phrase == 'left':
        sendRobotDriveCommand('left')
        time.sleep(1.2)
        sendRobotDriveCommand('left')
        time.sleep(1.2)
        sendRobotDriveCommand('left')
        textToSpeech.say('Executed ' + phrase)
        return

    if phrase == 'right':
        sendRobotDriveCommand('right')
        time.sleep(1.2)
        sendRobotDriveCommand('right')
        time.sleep(1.2)
        sendRobotDriveCommand('right')
        textToSpeech.say('Executed ' + phrase)
        return

    if phrase == 'status please':
        expected = 'volts\":12'
        sayOnGoodResult = 'Robot motors are good.'
        sendRobotNodeJsCommand('data', expected, sayOnGoodResult)

    textToSpeech.say('Do not know what to do with ' + phrase)

##################################################################
if __name__ == '__main__':
    signal(SIGINT, signalHandler)


loadJsonDataFromFiles()

wallaceIndicatesReadiness()

while not quitProgram:

    # if a continuousPhrase was given, we dont need to ask for input.
    # we just keep listening, and assign that continuous phrase to everthing.
    # if we are in finding noise level mode, we also do not prompt for input.
    # there is also the option to be more conversational, where it acts on phrases,
    # AND does live training, so we dont want user to have to keep hitting <ENTER> here.
    if not handsFree:
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

        if findNoiseLevel(phraseFrames):
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
            print('best Phrase Match: ', bestPhraseMatch['phrase'], '  numMatches: ', numMatches)
            if (difference < 230 and numMatches > 5) or (difference < 300 and numMatches > 6):
                print(f.renderText(bestPhraseMatch['phrase']))
                needPhrase = bestPhraseMatch['phrase']
                actOnKnownPhrases(needPhrase, metaDataForLatestRecordedPhrase)
            else:
                print(f.renderText(bestPhraseMatch['phrase']))
                #textToSpeech.say('Did you say ' + bestPhraseMatch['phrase'] + '?')
                os.system('espeak -s 140 "Did you say ' + bestPhraseMatch['phrase'] + '?"')
                justGetYesOrNoResponse = False
                isThisCorrect, tryAgainForYesNo = getIsThisCorrectUserInput(justGetYesOrNoResponse)
                if not tryAgainForYesNo and isThisCorrect:
                    needPhrase = bestPhraseMatch['phrase']
                    actOnKnownPhrases(needPhrase, metaDataForLatestRecordedPhrase)
                elif tryAgainForYesNo:
                    isThisCorrect, tryAgainForYesNo = getIsThisCorrectUserInput(justGetYesOrNoResponse)
                    if not tryAgainForYesNo and isThisCorrect:
                        needPhrase = bestPhraseMatch['phrase']
                        actOnKnownPhrases(needPhrase, metaDataForLatestRecordedPhrase)
                    elif tryAgainForYesNo:
                        textToSpeech.say('Sorry.')
                else:
                    textToSpeech.say('Enter phrase.')
                    needPhrase = input('Need to assign new phrase to this latest recording:')
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



