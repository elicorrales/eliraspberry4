'use strict';

const minRequiredActualMotorSpeed = 20;
const maxDiffActualSpeedM1vsM2 = 20;
const startingSpeedCommandValue = 0.2;
let doRotationTest = false;
let currentRotateDirection = 'left';
let currentlyRotating = false;
let didNewRotationCycle = false;
let haveCompletedCurrentLeftAndRightRotationCycle = false;


const maxNumRotationCommandsToSendInOneStream = 80; // aprox 2secs worth of drive commands
let currentNumRotationCommandsSentInStream = 0;


let delayStarted = false;
let delayMillis = 0;

let currentLeftSpeedCommandValue = startingSpeedCommandValue;
let currentRightSpeedCommandValue = startingSpeedCommandValue;
let currentMillisRotating = 0;
let maxAttainedLeftM1Speed = 0;
let maxAttainedLeftM2Speed = 0;
let maxAttainedRightM1Speed = 0;
let maxAttainedRightM2Speed = 0;
let numTimesToggleBetweenLeftVsRight = 0;
let LeftSpeedsWereFasterThanRightSpeeds = false;
let LeftSpeedsAreFasterThanRightSpeeds = false;

const doSwitchToFollowRedShirtDrive = () => {
    location.href = "followredshirt.html";
    clearTouchEvents();
}

const doSwitchToTouchDrive = () => {
    location.href = "touchdrive.html";
}



const doStartRotationTest = () => {
    doRotationTest = true;
}

const doStopRotationTest = () => {
    doRotationTest = false
}


const delay = (millis) => {
    console.log('..............doing delay.....');
    delayStarted = true;

    setTimeout(()=> {
        console.log('..............delay ENDED');
        delayStarted = false;
    },millis);
}

const rotate = (x,directionString) => {

    console.log('Rotating.....' + directionString + ' --------------');

    warnings.innerHTML = 'Rotating ' + directionString + ' ....';
    let now = new Date().getTime();
    if (now - currentMillisRotating > 1000) {
        warnings.innerHTML = 'Done Rotating ' + directionString;

        switch (directionString) {
            case 'Left':
                if (maxAttainedLeftM1Speed < Math.abs(dataReceivedFromNodeJsServer.speed1)) {
                    maxAttainedLeftM1Speed = Math.abs(dataReceivedFromNodeJsServer.speed1);
                }

                if (maxAttainedLeftM2Speed < Math.abs(dataReceivedFromNodeJsServer.speed2)) {
                    maxAttainedLeftM2Speed = Math.abs(dataReceivedFromNodeJsServer.speed2);
                }
                break;
            case 'Right':
                if (maxAttainedRightM1Speed < Math.abs(dataReceivedFromNodeJsServer.speed1)) {
                    maxAttainedRightM1Speed = Math.abs(dataReceivedFromNodeJsServer.speed1);
                }

                if (maxAttainedRightM2Speed < Math.abs(dataReceivedFromNodeJsServer.speed2)) {
                    maxAttainedRightM2Speed = Math.abs(dataReceivedFromNodeJsServer.speed2);
                }
                break;
        }

        if (directionString === 'Right') {
            haveCompletedCurrentLeftAndRightRotationCycle = true;
        }
        currentlyRotating = false;
        return;
    }
    setTimeout(() => {
        if (!doRotationTest) { return; }
        console.log(dataReceivedFromNodeJsServer);
        if (currentNumRotationCommandsSentInStream < maxNumRotationCommandsToSendInOneStream) {
            currentNumRotationCommandsSentInStream++;
            delayMillis = 50;
        } else {
            delayMillis = 500;
            currentNumRotationCommandsSentInStream = 0;
        }
        processXandY(x,0,0); 
        rotate(x,directionString);
    },delayMillis);
}



const rotateLeft = (x) => {
    rotate(-x,'Left');
}

const rotateRight = (x) => {
    rotate(x,'Right');
}




const rotationTest = () => {

    setInterval(()=> {

        console.log('Rotation Test ------------------------------------------------------------------------');

        if (doRotationTest && !currentlyRotating && !haveCompletedCurrentLeftAndRightRotationCycle) {

            didNewRotationCycle = true;

            currentlyRotating = true;

            switch (currentRotateDirection) {
                case 'left':
                    currentRotateDirection = 'right';
                    currentMillisRotating = new Date().getTime();
                    rotateLeft(currentLeftSpeedCommandValue);
                    break;
                case 'right':
                    currentRotateDirection = 'left';
                    currentMillisRotating = new Date().getTime();
                    rotateRight(currentRightSpeedCommandValue);
                    break;
            }

        } 

        maxSpeedValueElem.innerHTML = '<font size="+3">'
            + 'M1 Left: ' + maxAttainedLeftM1Speed + ', M2 Left: ' + maxAttainedLeftM2Speed + ' Left Spd Cmd: ' + currentLeftSpeedCommandValue + '<br/>'
            + 'M1 Right: ' + maxAttainedRightM1Speed + ', M2 Right: ' + maxAttainedRightM2Speed + ' Right Spd Cmd: ' + currentRightSpeedCommandValue
            + '</font>';

        if (didNewRotationCycle && haveCompletedCurrentLeftAndRightRotationCycle && !currentlyRotating && (maxAttainedLeftM1Speed < minRequiredActualMotorSpeed || maxAttainedLeftM2Speed < minRequiredActualMotorSpeed)) {
            currentLeftSpeedCommandValue += 0.01;
            currentLeftSpeedCommandValue = parseFloat(currentLeftSpeedCommandValue.toFixed(2));
        }

        if (didNewRotationCycle && haveCompletedCurrentLeftAndRightRotationCycle && !currentlyRotating && (maxAttainedRightM1Speed < minRequiredActualMotorSpeed || maxAttainedRightM2Speed < minRequiredActualMotorSpeed)) {
            currentRightSpeedCommandValue += 0.01;
            currentRightSpeedCommandValue = parseFloat(currentRightSpeedCommandValue.toFixed(2));
        }

        // if right is more powerful move than left, increase left
        if (didNewRotationCycle && haveCompletedCurrentLeftAndRightRotationCycle && !currentlyRotating 
            && (
                (Math.abs(maxAttainedRightM1Speed) - Math.abs(maxAttainedLeftM1Speed) > maxDiffActualSpeedM1vsM2)
                || 
                (Math.abs(maxAttainedRightM2Speed) - Math.abs(maxAttainedLeftM2Speed) > maxDiffActualSpeedM1vsM2)
                ) 
        ) {
            currentLeftSpeedCommandValue += 0.01;
            currentLeftSpeedCommandValue = parseFloat(currentLeftSpeedCommandValue.toFixed(2));
            LeftSpeedsWereFasterThanRightSpeeds = LeftSpeedsAreFasterThanRightSpeeds;
            LeftSpeedsAreFasterThanRightSpeeds = false;
        }

        // if left is more powerful move than right, increase right
        if (didNewRotationCycle && haveCompletedCurrentLeftAndRightRotationCycle && !currentlyRotating 
            && (
                (Math.abs(maxAttainedLeftM1Speed) - Math.abs(maxAttainedRightM1Speed) > maxDiffActualSpeedM1vsM2)
                || 
                (Math.abs(maxAttainedLeftM2Speed) - Math.abs(maxAttainedRightM2Speed) > maxDiffActualSpeedM1vsM2)
                ) 
        ) {
            currentRightSpeedCommandValue += 0.01;
            currentRightSpeedCommandValue = parseFloat(currentRightSpeedCommandValue.toFixed(2));
            LeftSpeedsWereFasterThanRightSpeeds = LeftSpeedsAreFasterThanRightSpeeds;
            LeftSpeedsWereFasterThanRightSpeeds = true;
        }


        if (didNewRotationCycle && haveCompletedCurrentLeftAndRightRotationCycle && !currentlyRotating) {
            haveCompletedCurrentLeftAndRightRotationCycle = false;
            didNewRotationCycle = false;
        }

        if (currentLeftSpeedCommandValue > 0.99 || currentRightSpeedCommandValue > 0.99) {
            doRotationTest = false;
            errors.innerHTML = 'Rotation Speed Value has hit ONE';
        }


        if (doRotationTest && LeftSpeedsWereFasterThanRightSpeeds != LeftSpeedsAreFasterThanRightSpeeds) {
            numTimesToggleBetweenLeftVsRight++;
        }

        if (numTimesToggleBetweenLeftVsRight > 5) {
            doRotationTest = false;
            messages.innerHTML = 'Left vs Right Rotation Speeds Have Toggled ' + numTimesToggleBetweenLeftVsRight;
        }
    },2000);
}

const initializeMinRotationValuesTest = () => {
    if (p5jsSetupHasRun) {
        rotationTest();
        return;
    }
    setTimeout(()=>{
        initializeMinRotationValuesTest(); 
    },50);
}


initializeMinRotationValuesTest();
