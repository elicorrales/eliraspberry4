import sys
import argparse
import json
from signal import signal, SIGINT


##################################################################
# set up command-line arguments
##################################################################
parser = argparse.ArgumentParser(prog=sys.argv[0], description='remove a select phrase(all instances) and save to an new file.', allow_abbrev=False)
parser.add_argument('--phrase-to-remove', type=str, dest='phraseToRemove', required=True)
parser.add_argument('--input-json-file', type=str, dest='inputJsonFileName', required=True)
parser.add_argument('--output-json-file', type=str, dest='outputJsonFileName', required=True)
parser.set_defaults()

args = parser.parse_args()



##################################################################
#init program global variables
##################################################################
phraseToRemove=args.phraseToRemove
inputJsonFileName=args.inputJsonFileName
outputJsonFileName=args.outputJsonFileName

phrasesArray = []
resultPhrasesArray = []


##################################################################
def cleanUp():

    print('Done.')
    sys.exit(0)

##################################################################
def signalHandler(signalReceived, frame):
    print('Got CTRL-C...')
    cleanUp()

##################################################################
def loadJsonDataFromFile():

    global phrasesArray

    print('Load Existing phrases JSON meta data from file...')
    try:
        phrasesFile = open(inputJsonFileName,'r')
        phrasesString = phrasesFile.read()
        phrasesFile.close()
        phrasesArray = json.loads(phrasesString)
        print('Existing phrases JSON meta data loaded from file.')
    except json.decoder.JSONDecodeError:
        print('')
        print('bad phrases JSON file data..')
        print('')
        cleanUp()
    except FileNotFoundError:
        print('')
        print('No phrases JSON file Data..')
        print('')
        cleanUp()

##################################################################
def removePhraseFromJsonData():

    global phrasesArray

    for phrase in phrasesArray:
        if phrase['phrase'] != phraseToRemove:
            resultPhrasesArray.append(phrase)


##################################################################
def saveJsonDataToFile():

    global resultPhrasesArray

    if len(resultPhrasesArray) > 0:
        print('Saving phrase meta data as JSON file...')
        phrasesFile = open(outputJsonFileName,'w')
        phrasesFile.write(json.dumps(resultPhrasesArray, indent=4))
        phrasesFile.close()



##################################################################
if __name__ == '__main__':
    signal(SIGINT, signalHandler)


if inputJsonFileName == outputJsonFileName:
    print('')
    print('')
    print('')
    print('')
    print('Input file Name (' + inputJsonFileName + ') can not be same as output file name(' + outputJsonFileName + ')')
    cleanUp()


loadJsonDataFromFile()

removePhraseFromJsonData()

saveJsonDataToFile()
