'use strict';


/////////////////////////////////////////////////////////////////////////////////////////////////
// related to establishing initial conncection between browser client and node.js server.
/////////////////////////////////////////////////////////////////////////////////////////////////
let currIpAddress = '';
let haveReachedRaspberryNodeJsServerAtLeastOneTime = false;
let haveTriedToReachRaspberryNodeJsServerAtLeastThisManyTimes = 0;
let haveInformedUserThatRaspberryNodeJsServerIsAvailable = false;
let maxTriesToReachRaspberryNodeJsServerBeforeSwitchingIpAddresses = 3;
let lastTimeResponseFromRaspberryPiServer = new Date().getTime();


let p5jsSetupHasRun = false;


let maxspeed = document.getElementById('maxspeed').value;
document.getElementById('maxspeedvalue').innerHTML = maxspeed;
let maxrotspeed = document.getElementById('maxrotspeed').value;
document.getElementById('maxrotspeedvalue').innerHTML = maxrotspeed;

let speedcmdthreshold = document.getElementById('speedcmdthreshold').value;
document.getElementById('speedcmdthresholdvalue').innerHTML = speedcmdthreshold;
let minactualspeed    = document.getElementById('minactualspeed').value;
document.getElementById('minactualspeedvalue').innerHTML = minactualspeed;
let millislowspeed    = document.getElementById('millislowspeed').value;
document.getElementById('millislowspeedvalue').innerHTML = millislowspeed;
let startTrackingMillisLowSpeed = false;
let currMillisLowSpeed;
let robotMovementIsDisabled = true;
let movementIsDisabledDetailsMessage = '';
let millisLastTimeXandY = new Date().getTime();
let isXandYMovement = false;


let dataReceivedFromNodeJsServer;


const doUseThisIp = (ipAddr) => {
    currIpAddress = ipAddr;
    connectingplswait.innerHTML = 'Connecting with Raspberry Pi Node.js Server.... pls wait';
}


const doArduinoSetSpeedCmdThreshold = (slider) => {
    speedcmdthreshold = slider.value;
    speedcmdthresholdvalue.innerHTML = slider.value;
}

const doArduinoSetMinActualSpeed = (slider) => {
    minactualspeed = slider.value;
    minactualspeedvalue.innerHTML = slider.value;
}

const doArduinoSetMillisLowSpeed = (slider) => {
    millislowspeed = slider.value;
    millislowspeedvalue.innerHTML = slider.value;
}


const doArduinoCommand = (command) => {


    if (command === 'arduino/api/clr.usb.err') {
        robotMovementIsDisabled = false;
        movementIsDisabledDetailsMessage = '';
        robotMovementIsDisabled = false;
        startTrackingMillisLowSpeed = false;
    }

    fetch('http://'+currIpAddress+':8084/' + command, { method: 'GET' })
    .then(result => {
        //console.log(result);
    })
    .catch(error => {
        console.log(error);
    });
}

const doArduinoSetMaxSpeed = (slider) => {
    maxspeed = slider.value;
    maxspeedvalue.innerHTML = maxspeed;
}
const doArduinoSetMaxRotationSpeed = (slider) => {
    maxrotspeed = slider.value;
    maxrotspeedvalue.innerHTML = maxrotspeed;
}



/*
// this fires as long as slider is moving
// (speed changing)
let mouseSliderPressed = false
const doArduinoStartMovement = (slider, event) => {
    if (!mouseSliderPressed) {
        mouseSliderPressed = true;
        const command = slider.id;
        const speed = slider.value;
        //console.log(command,' ',speed,' ',event);
        sendArduinoMovementCommand(command);
    }
}

// this fires when slider button goes up 
// we need to keep sending movement even if slider does not move,
// as long as it's held down - (same speed)
const doArduinoEndMovement = (slider, event) => {
    mouseSliderPressed = false;
    slider.value = 0;
}

const sendArduinoMovementCommand = (command) => {

    if (!mouseSliderPressed) return;

    setTimeout(() => {
        const speed = document.getElementById(command).value;
        fetch('http://'+currIpAddress+':8084/arduino/api/' + command + '/' + speed, { method: 'GET' })
        .then(result => {
            //console.log(result);
        })
        .catch(error => {
            console.log(error);
            mouseSliderPressed = false;
        });
        sendArduinoMovementCommand(command);
    }, 10);
}
*/

const sendCommandToServer = (command) => {

    if (robotMovementIsDisabled) {
        messages.innerHTML = 'ROBOT IS DISABLED : ' + movementIsDisabledDetailsMessage + '<br/> Press "Clear USB Error"';
        console.log(movementIsDisabledDetailsMessage);
        return;
    }

    isXandYMovement = true;
    millisLastTimeXandY = new Date().getTime();

    //console.log(X,' ',Y);
    fetch('http://'+currIpAddress+':8084/arduino/api/' + command)
    .then(result => {
        //console.log(result);
    })
    .catch(error => {
        console.log(error);
    });

}

const processXandY = (X,Y, minDiffBetweenThem) => {
        const absX = Math.abs(X);
        const absY = Math.abs(Y);
        const now = new Date().getTime();

        // since joystick not guaranteed to be centered..
        if (absX < 0.18 && absY < 0.18) {
            return;
        }

        // insure maxspeed and maxrotspeed do NOT exceed 100. that is what arduino is expecting.
        if (maxrotspeed > 100) maxrotspeed = 100;
        if (maxspeed > 100) maxspeed = 100;

        // make sure the joystick movement is clearly vertical, or clearly horizontal
        if ((absX + minDiffBetweenThem > absY) || (absY + minDiffBetweenThem > absX)) {

            let x = X>=0 ? map(X,0.2,1,0,maxrotspeed,true) : map(X,-0.2,-1,0,-maxrotspeed,true);

            let y = Y>=0 ? map(Y,0.2,1,0,maxspeed,true) : map(Y,-0.2,-1,0,-maxspeed,true);

            let intx = Math.floor(x);
            let inty = Math.floor(y);

            //console.log(intx,'  ',inty);
            convertXandYtoMovementUrl(intx, inty);
        }
}


const convertXandYtoMovementUrl = (intx, inty) => {
    const X = intx;
    const Y = inty;

    //console.log(X,' ',Y);
  
    let command = '';
    if (Math.abs(Y) > Math.abs(X)) {
        if (Y < 0) {
            //command = 'forwardresp/' + (-Y);
            command += 'forward/' + (-Y);
        } else if (Y > 0) {
            //command = 'backwardresp/' + Y + '/' + Y;
            command += 'backward/' + Y;
        }
    } else if (Math.abs(Y) < Math.abs(X)) {
        if (X > 0) {
            //command = 'rightresp/' + X;
            command += 'right/' + X;
        } else if (X < 0) {
            //command = 'leftresp/' + (-X);
            command += 'left/' + (-X);
        }
    }

    if (command !== '') {
        sendCommandToServer(command);
    } else {
        warnings.innerHTML = 'No Speed Command Sent - Too Low';
    }

}


const handleNotReachingRaspberryPi = () => {
            if (!haveReachedRaspberryNodeJsServerAtLeastOneTime) {
                console.log('Not Reaching Raspberry Node Js Server at address ' + currIpAddress + ' for try #'+
                haveTriedToReachRaspberryNodeJsServerAtLeastThisManyTimes);
                warnings.innerHTML = 'Not Reaching Raspberry Node Js Server at address ' + currIpAddress + ' for try #' +
                haveTriedToReachRaspberryNodeJsServerAtLeastThisManyTimes;
                if (haveTriedToReachRaspberryNodeJsServerAtLeastThisManyTimes <=
                maxTriesToReachRaspberryNodeJsServerBeforeSwitchingIpAddresses) {
                    haveTriedToReachRaspberryNodeJsServerAtLeastThisManyTimes++;
                } else { 
                    console.log('Not Reaching Raspberry Node Js Server.');
                    errors.innerHTML = 'Not Reaching Raspberry Node Js Server';
                }

            } else {
                console.log(error);
            }
}



let statusInterval = 1000;
setInterval(() => {

    if (currIpAddress === '') {
        return;
    }

         if (haveReachedRaspberryNodeJsServerAtLeastOneTime) {
            if (!haveInformedUserThatRaspberryNodeJsServerIsAvailable) {
                haveInformedUserThatRaspberryNodeJsServerIsAvailable = true;
                let mainappcontainer = document.getElementById('mainappcontainer');
                if (mainappcontainer !== null) mainappcontainer.style.display = 'block';
                let touchdrivecontainer = document.getElementById('touchdrivecontainer');
                if (touchdrivecontainer !== null) touchdrivecontainer.style.display = 'block';
                let switchcontainer = document.getElementById('switchcontainer');
                if (switchcontainer !== null) switchcontainer.style.display = 'block';
                let connectingcontainer = document.getElementById('connectingcontainer');
                if (connectingcontainer !== null) connectingcontainer.style.display = 'none';
                console.log('Have Reached Raspberry Pi Node.js server at ' + currIpAddress);
                messages.innerHTML = 'Have Reached Raspberry Pi Node.js server at ' + currIpAddress;
                statusInterval = 5000;
            } else if (!robotMovementIsDisabled) {
                statusInterval = 50;
            }
         }

        lastTimeResponseFromRaspberryPiServer = new Date().getTime();
    
        fetch('http://'+currIpAddress+':8084/nodejs/api/data', { method: 'GET' })
        .then(response => {
            haveReachedRaspberryNodeJsServerAtLeastOneTime = true;
            if (response.status !== 200) {
                console.log('Bad data retrieval response from server:',response.status);
                return;
            }
            response.json().then(data => {

                dataReceivedFromNodeJsServer = data;

                arduinodata.innerHTML = ''
                        + 'Volts:' + (data.volts/10).toFixed(1) + '<br/>'
                        + 'Amps1:' + (data.amps1/100).toFixed(1) + '<br/>'
                        + 'Amps2:' + (data.amps2/100).toFixed(1)  + '<br/>'
                        + 'M1 Spd:' + data.speed1 + '<br/>'
                        + 'M2 Spd:' + data.speed2 + '<br/>'
                        + 'Spd Cmd:'+ data.spdcmd + '<br/>'
                        + 'Temp: ' + ((data.temp/10)*1.8+32).toFixed(1) + '<br/>'
                        + 'Cmds: ' + data.cmds + '&nbsp;&nbsp;'
                        + 'Dropped: ' + data.dropped + '&nbsp;&nbsp;'
                        + 'Err: ' + ((data.dropped / data.cmds) * 100).toFixed(1) + '%&nbsp;&nbsp;'
                        + 'Last: ' + data.lastcmd + '&nbsp;&nbsp;<br/>';

                if (data.version!==undefined && data.version !== '') {
                    console.log('version:'+data.version);
                }
                messages.innerHTML = (data.msg!==undefined?data.msg:'') + (data.version!==undefined?'<br/>'+data.version:'');
                errors.innerHTML   = data.error;

                if (!robotMovementIsDisabled && data.spdcmd !== undefined && data.spdcmd !== '' 
                    && data.spdcmd > speedcmdthreshold 
                    && (Math.abs(data.speed1) < minactualspeed || Math.abs(data.speed2) < minactualspeed)
                ) {
                    let now = new Date().getTime();

                    if (now - millisLastTimeXandY > 200) {
                        isXandYMovement = false;
                        millisLastTimeXandY = new Date().getTime();
                        startTrackingMillisLowSpeed = false;
                    }

                    if (!startTrackingMillisLowSpeed) {
                        currMillisLowSpeed = new Date().getTime();
                        startTrackingMillisLowSpeed = true;
                    }

                    if (now - currMillisLowSpeed > millislowspeed) {
                        movementIsDisabledDetailsMessage = 'WARNING! ROBOT IS STUCK!!'
                                            + ' thres:' + data.spdcmd
                                            + ', actual1:' + data.speed1
                                            + ', actual2:' + data.speed2
                                            + ', millis:' + (now - currMillisLowSpeed);
                        warnings.innerHTML = movementIsDisabledDetailsMessage;
                        robotMovementIsDisabled = true;
                        console.log(movementIsDisabledDetailsMessage);
                    }
                } else {
                    warnings.innerHTML = '';
                }


            });
        })
        .catch(error => {
            handleNotReachingRaspberryPi();
        });
}, statusInterval);

//p5.js functions - i believe required to be able to use the
//map() function - not sure - haven't double-checked in some time.
function setup() {
    p5jsSetupHasRun = true;
    console.log('p5.js setup() ....');
}
//function draw() {} <--- this should go only in the camera-related files

