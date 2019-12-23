##################################################################
# this uses byte objects
# good values: 90 150
##################################################################
import sys
import argparse
import pyaudio
import numpy as np
import wave
import statistics 
import json
import talkey
from signal import signal, SIGINT
from pyfiglet import Figlet

CHUNK = 512
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
#RATE = 16000
RATE = 32000

##################################################################
# set up command-line arguments
##################################################################
parser = argparse.ArgumentParser(prog=sys.argv[0], description='Train Yes, No, Quit', allow_abbrev=False)
parser.add_argument('-s', '--max-bg-start', type=int, dest='maxBackgroundStart')
parser.add_argument('--max-bg-start-volume', type=int, dest='maxBackgroundStartVolume')
parser.add_argument('--max-bg-start-crossings', type=int, dest='maxBackgroundStartCrossings')
parser.add_argument('-l', '--length', type=int, dest='seconds')
parser.add_argument('-j', '--json-file', type=str, dest='jsonFile')
parser.set_defaults(
        maxBackgroundStartVolume=9, 
        maxBackgroundStartCrossings=24, 
        seconds=5, 
        jsonFile='yes.no.quit.json')

args = parser.parse_args()



##################################################################
#init program global variables
##################################################################
phrase=''
maxBackgroundStartVolume=args.maxBackgroundStartVolume
maxBackgroundStartCrossings=args.maxBackgroundStartCrossings
seconds=args.seconds
jsonFile=args.jsonFile
#frames = []
numActualRecordedFrames = 0
maxFramesBeforeTrim = int(RATE / CHUNK * seconds)

#textToSpeech = talkey.Talkey()
textToSpeech = talkey.Talkey(preferred_language=['en'])

p = pyaudio.PyAudio()  # Create an interface to PortAudio
f = Figlet()

phrasesArray = []

quitProgram = False
newPhraseAddedThisTime = False

##################################################################
def listPhrasesTrained():

    listedPhrases = []
    for phrase in phrasesArray:
        print(phrase.keys())
        if not phrase['phrase'] in listedPhrases:
            listedPhrases.append(phrase['phrase'])
            print(phrase['phrase'])


##################################################################
def signalHandler(signalReceived, frame):
    print('Got CTRL-C...')


    # Terminate the PortAudio interface
    global p
    p.terminate()

    global newPhraseAddedThisTime
    global phrasesArray

    if newPhraseAddedThisTime and len(phrasesArray) > 0:
        print('Saving meta data as JSON file...')
        phrasesFile = open(jsonFile,'w')
        phrasesFile.write(json.dumps(phrasesArray, indent=4, sort_keys=True))
        phrasesFile.close()

    print('Done.')

    sys.exit(0)


##################################################################
def isValidSound(frame, maxBackgroundVolume, maxBackgroundCrossings):
    jsonArray = []
    data = np.frombuffer(frame, dtype=np.int16)
    peak = np.amax(np.abs(data))
    bars = int(255*peak/2**16)
    #print('#'*bars)
    crossings = numZeroCrossings(data)
    #print('vol:', bars,' freq:', crossings)
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
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        if not isFirstValidSound:
            resultTrue, why, bars, crossings = isValidSound(data, maxBackgroundStartVolume, maxBackgroundStartCrossings)
            if resultTrue:
                print('.......capturing..... reason:', why, ' vol:', bars, ' crossings:', crossings)
                print('.......capturing..... reason:', why, ' vol:', bars, ' crossings:', crossings)
                print('.......capturing..... reason:', why, ' vol:', bars, ' crossings:', crossings)
                isFirstValidSound = True
        if isFirstValidSound:
            isValid, why, bars, crossings = isValidSound(data, maxBackgroundStartVolume, maxBackgroundStartCrossings)
            if lastSoundWasInvalid and not isValid:
                numConsecutiveInvalidSounds += 1
            elif not isValid:
                numConsecutiveInvalidSounds = 1
                lastSoundWasInvalid = True
            else:
                lastSoundWasInvalid = False

            if numConsecutiveInvalidSounds > 15:
                print('...Aborting capture..... reason:', why, ' vol:', bars, ' crossings:', crossings)
                print('...Aborting capture..... reason:', why, ' vol:', bars, ' crossings:', crossings)
                print('...Aborting capture..... reason:', why, ' vol:', bars, ' crossings:', crossings)
                break

        if isFirstValidSound:
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
def findBestMatch(latestPhrase, phrasesArray):

    numPhrases = len(phrasesArray)

    leastDiff = sys.maxsize
    bestMatchIndex = -1
    previousPhrase = ''
    numMatches = 0
    print('findBestMatch(): numPhrases to compare against: ', numPhrases)
    for i in range(numPhrases):
        phrase = phrasesArray[i]
        #print('comparing ' + latestPhrase['phrase'] +', ' + str(latestPhrase['numRecFrames']) + 
                #' against ' + phrase['phrase'] + ', ' + str(phrase['numRecFrames']))
        crDiff, pkDiff, numFramesDiff = compareTwoPhraseMetaData(latestPhrase, phrase)
        difference = crDiff + pkDiff + numFramesDiff
        if leastDiff > difference:
            leastDiff = difference
            bestMatchIndex = i
            print('findBestMatch():' + phrase['phrase'], ' leastDiff: ', leastDiff)

            if phrase['phrase'] == previousPhrase:
                numMatches += 1
                #print('currPhrase EQUALS previousPhrase', numMatches)
            else:
                numMatches = 0
                previousPhrase = phrase['phrase']
                #print('currPhrase NOT previousPhrase', numMatches)


    print('findBestMatch(): leastDiff ', leastDiff)
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
            "phrase": phrase, 
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

        if mode > 250  and volCount>= maxBackground:
            return False
        if mode < 3    and volCount >= maxBackground:
            return False

        return True

    except:
        #print('exception')
        return False

##################################################################


if __name__ == '__main__':
    signal(SIGINT, signalHandler)




print('Load Existing JSON meta data from file...')
try:
    phrasesFile = open(jsonFile,'r')
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


while not quitProgram:

    listPhrasesTrained()

    userInput = input('Press <ENTER> to record, or \'q\' to quit program: ')

    if userInput == 'q':
        break


    phraseFrames = recordAudio()

    print('phrase frames: ', len(phraseFrames), ' vol thre: ', maxBackgroundStartVolume, ', cros the:' , maxBackgroundStartCrossings)


    if len(phraseFrames) > 0:
        

        metaDataForLatestRecordedPhrase = getAudioMetaData(phraseFrames)
        addFakeAudioMetaDataForFillerFrames(metaDataForLatestRecordedPhrase)

        if len(phrasesArray) > 0:
            difference, numMatches, bestMatch = findBestMatch(metaDataForLatestRecordedPhrase, phrasesArray)
            print('best Yes No Quit Match: ', bestMatch['phrase'], ' numMatches: ', numMatches)
            if difference < 200 and numMatches > 6:
                print(f.renderText(bestMatch['phrase']))
                textToSpeech.say('You said, ' + bestMatch['phrase'])
                needPhrase = bestMatch['phrase']
            else:
                print(f.renderText(bestMatch['phrase']))
                textToSpeech.say(bestMatch['phrase'] + '?')
                isThisCorrect = input('Correct ? <y|n> :')
                if isThisCorrect == 'y':
                    needPhrase = bestMatch['phrase']
                else:
                    needPhrase = input('Need to assign new phrase to this latest recording:')
        else:
            needPhrase = input('Need to assign new phrase to this latest recording:')

        if len(needPhrase) > 0:
            metaDataForLatestRecordedPhrase['phrase'] = needPhrase
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

if newPhraseAddedThisTime:
    print('Saving meta data as JSON file...')
    phrasesFile = open(jsonFile,'w')
    phrasesFile.write(json.dumps(phrasesArray, indent=4, sort_keys=True))
    phrasesFile.close()
    print('Done.')


