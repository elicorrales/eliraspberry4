'use strict';

const argv = require('yargs').argv;
const serial = require('serialport');
const readline = require('@serialport/parser-readline');

const thisServerPort = 8084;
const messagingServerPort = 8085;

//const raspberry2arduinoBaud = 9600;
//const raspberry2arduinoBaud = 19200;
const raspberry2arduinoBaud = 38400;
//const raspberry2arduinoBaud = 57600;
//const raspberry2arduinoBaud = 74880;
//const raspberry2arduinoBaud = 115200;
//const raspberry2arduinoBaud = 230400;
//const raspberry2arduinoBaud = 250000;
//const raspberry2arduinoBaud = 500000;
//const raspberry2arduinoBaud = 1000000;
//const raspberry2arduinoBaud = 2000000;

const raspberry2redboardBaud = 9600;
//const raspberry2redboardBaud = 115200;


//////////////////////////////////////////////////////////////////////////////////////////
// arduino backside serial port related stuff
//////////////////////////////////////////////////////////////////////////////////////////
 
const arduinoPort = new serial('/dev/ttyACM0',{baudRate:raspberry2arduinoBaud,autoOpen:false});
const arduinoParser = arduinoPort.pipe(new readline({ delimiter: '\n'}));
let   isConnectedToArduino = false;

arduinoPort.on('open', () => {
        console.log('serial arduinoPort open');
        isConnectedToArduino = true;
});

arduinoPort.on('close', () => {
        console.log('serial arduinoPort closed');
        reconnectToArduino();
});

arduinoPort.on('error', () => {
        console.log('serial arduinoPort error');
        reconnectToArduino();
});

const connectToArduino = () => {
    arduinoPort.open();
}

const reconnectToArduino = () => {
    isConnectedToArduino = false;
    clearAllStatusVariables();
    console.log('ATTEMPT RE-CONNECT TO ARDUINO');
    error = 'ATTEMPT RE-CONNECT TO ARDUINO';
    setTimeout(() => {
        connectToArduino();
    }, 2000);
}

connectToArduino();


//////////////////////////////////////////////////////////////////////////////////////////
// redboard backside serial port related stuff
//////////////////////////////////////////////////////////////////////////////////////////


/*
const redboardPort = new serial('/dev/ttyUSB0',{baudRate:raspberry2redboardBaud,autoOpen:false});
const redboardParser = redboardPort.pipe(new readline({ delimiter: '\n'}));

redboardPort.on('open', () => {
        console.log('serial redboardPort open');
});

redboardPort.on('close', () => {
        console.log('serial redboardPort closed');
        reconnectToRedboard();
});

redboardPort.on('error', () => {
        console.log('serial redboardPort error');
        reconnectToRedboard();
});

const connectToRedboard = () => {
    redboardPort.open();
}

const reconnectToRedboard = () => {
    console.log('ATTEMPT RE-CONNECT TO RED BOARD');
    setTimeout(() => {
        connectToRedboard();
    }, 2000);
}

connectToRedboard();
*/


//////////////////////////////////////////////////////////////////////////////////////////
// arduino - robot - driving functions
//////////////////////////////////////////////////////////////////////////////////////////

////////////these are the status values ///////////////////////////
let timestamp = 0;
let volts = '';
let amps1 = '';
let amps2 = '';
let temp = '';
let speed1 = '';
let speed2 = '';
let cmds = '';
let lastcmd = '';
let msg = '';
let error = '';
let spdcmd = '';
let version = '';
let cmdNum = '';
let dropped = '';
let thereIsError = false;
let commandWasSentToArduino = false;
let millisSinceLastCommandSentToArduino = new Date().getTime();
let millisSinceLastResponseFromArduino = new Date().getTime();
let showArduinoResponseInServerTerminal = true;

////////////// these are the drive command ack values ///////////////////
//console.log(argv.maxTimeout);
//process.exit(0);
if (argv.maxTimeout === undefined) { console.log('Need --maxTimeout'); process.exit(1); }
const maxTimeToWaitForAck = argv.maxTimeout;
let waitForDriveCmdAck = false;
let driveCmdAckRcvd = false;
let lastDriveCmd = '';
let lastAckNum = '';
let dir = '';
let ackNum = '';

let lastCommandSentToArduino = '';
let lastCommandSentTimestamp = 0;

const arduinoHistory = [];

const clearAllStatusVariables = () => {
    timestamp = 0;
    volts = '';
    amps1 = '';
    amps2 = '';
    temp = '';
    speed1 = '';
    speed2 = '';
    cmds = '';
    lastcmd = '';
    msg = '';
    error = '';
    spdcmd = '';
    cmdNum = '';
    dropped = '';
    version = '';
    thereIsError = false;
    commandWasSentToArduino = false;
}

arduinoParser.on('data', data => {

    //console.log(data);

    millisSinceLastResponseFromArduino = new Date().getTime();

    clearAllStatusVariables();


    timestamp = new Date().getTime();

/*
    arduinoHistory.push(data);

    if (arduinoHistory.length > 50) {
        arduinoHistory.shift();
    }
*/

    if (showArduinoResponseInServerTerminal) {
        console.log(data);
    }

    try {

        const result = JSON.parse(data);

        if (result.v !== undefined) {
            volts = result.v;
        }
        if (result.a1 !== undefined) {
            amps1 = result.a1;
        }
        if (result.a2 !== undefined) {
            amps2 = result.a2;
        }
        if (result.t !== undefined) {
            temp = result.t;
        }
        if (result.s1 !== undefined) {
            speed1 = result.s1;
        }
        if (result.s2 !== undefined) {
            speed2 = result.s2;
        }
        if (result.c !== undefined) {
            cmds = result.c;
        }
        if (result.d !== undefined) {
            dropped = result.d;
        } 
        if (result.l !== undefined) {
            lastcmd = result.l;
        }
        if (result.p1 !== undefined) {
            spdcmd = result.p1;
        }
        if (result.msg !== undefined) {
            msg = result.msg;
        }
        if (result.e !== undefined) {
            error = result.e;
            //thereIsError = true;
        } 
        if (result.version !== undefined) {
            version = result.version;
            console.log('VERSION VERSION'+version);
        }

        if (result.dir !== undefined) {
            dir = result.dir;
            ackNum = result.ackNum;
            driveCmdAckRcvd = true;
        } 

        if (thereIsError) { console.log(result); }

    } catch (e) {
        //console.log(e);
        console.log('corrupted JSON response from Arduino' + data); 
        error = 'corrupted JSON response from Arduino:'+data;
    }

});
//////////////////////////////////////////////////////////////////////


const express = require('express');
const app = express();
app.use(express.json());
app.use((request, response, next) => {
  response.header("Access-Control-Allow-Origin", "*");
  response.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

const axios = require('axios');



//default handler
const rootHandler = (request, response) => {
    response.send('Requested /');
}
app.get('/', rootHandler);



///////handler to respond with any arduino status data///////////////////////////////////
const respondWithCollectedDataHandler = (request, response) => {
    let dataToSend = {
        timestamp,
        volts,
        amps1,
        amps2,
        temp,
        speed1,
        speed2,
        msg,
        cmds,
        spdcmd,
        dropped,
        lastcmd,
        error,
        version
    };
    if (isConnectedToArduino) { 
        console.log('client requrested data: ', JSON.stringify(dataToSend));
    }
    response.send(dataToSend);
}
app.get('/nodejs/data', respondWithCollectedDataHandler);


///////handler to respond with history ///////////////////////////////////
const respondWithHistoryHandler = (request, response) => {
    response.send(arduinoHistory);
}



const processDriveCommand = (ackWaitTime,cmdNum, commandStr, myRand, p1, p2) => {
    //console.log('ELIELI: drCmdAckRcvd:',driveCmdAckRcvd,' dir:',dir,' lastDrivCmd:',lastDriveCmd,' ackNum:',ackNum,' lastAck:',lastAckNum,' time:',ackWaitTime);
    if ((driveCmdAckRcvd && dir === lastDriveCmd && ackNum == lastAckNum) || ackWaitTime > maxTimeToWaitForAck) {
        //console.log('ELIELI clear wait');
        waitForDriveCmdAck = false;
    }
    if (waitForDriveCmdAck) {
        //console.log('ELIELI waiting for ack...');
        return '';
    }
    if (thereIsError) {
        //console.log('ELIELI there is error');
        return '';
    }
    millisSinceLastCommandSentToArduino = new Date().getTime();

    ////////// we increment the drive command number if it is part of a stream of drive commands,
    ////////// other wise if some time elapsed, and it is a new stream, we reset the drive command number.
    let p3 = 0;
    if (ackWaitTime < 1000 && ackNum !== '') {
        p3 = parseInt(ackNum) + 1;    
    }
    lastDriveCmd = commandStr;
    waitForDriveCmdAck = true;
    driveCmdAckRcvd = false;
    let commandStringToSend = '7 ' + cmdNum + ' ' + myRand + ' ' 
                        + (parseInt(cmdNum) + parseInt(myRand) + parseInt(p1) + parseInt(p2) + parseInt(p3) + 7) 
                        + ' ' + p1 + ' ' + p2 + ' ' + p3;
    return commandStringToSend;
}

///////arduino command handler command code with gamepad/joystick handler//////////
const parseAndSendCommandToArduino = (path) => {


    commandWasSentToArduino = false;

    const tokens = path.split('/',10);
    console.log(tokens);
    let baseUri = '';
    let gotBaseUri = false;
    let apiStr = '';
    let gotApiStr = false;
    let cmd = '';
    let gotCmd = false;
    let gotParm1 = false;
    let parm1 =  '';
    let gotParm2 = false;
    let parm2 =  '';
    let gotParm3 = false;
    let parm3 =  '';
    for (let i=0;i<tokens.length;i++) {
        if (!gotBaseUri && tokens[i] != '' && tokens[i] === 'nodejs' || tokens[i] === 'arduino' || tokens[i] === 'gamepad') {
            baseUri = tokens[i]; gotBaseUri = true; continue;
        }
        if (!gotApiStr && tokens[i] != '' && tokens[i] === 'api' || tokens[i] === 'axes') {
            apiStr = tokens[i]; gotApiStr = true; continue;
        }
        if (!gotCmd && tokens[i] != '' && tokens[i] !== 'nodejs' && tokens[i] != 'arduino' && tokens[i] != 'api') {
            cmd = tokens[i]; gotCmd = true; continue;
        }
        if (!gotParm1 && tokens[i] != '' && tokens[i] !== 'nodejs' && tokens[i] != 'arduino' && tokens[i] != 'api') {
            parm1 = tokens[i]; gotParm1 = true; continue;
       }
        if (!gotParm2 && tokens[i] != '' && tokens[i] !== 'nodejs' && tokens[i] != 'arduino' && tokens[i] != 'api') {
            parm2 = tokens[i]; gotParm2 = true; continue;
        }
        if (!gotParm3 && tokens[i] != '' && tokens[i] !== 'nodejs' && tokens[i] != 'arduino' && tokens[i] != 'api') {
            parm3 = tokens[i]; gotParm3 = true; continue;
        }
    }


    let commandStringToSend = '';
    let myRandom = Math.floor(Math.random()*100);


    const now = new Date().getTime();
    let ackWaitTime = now - millisSinceLastCommandSentToArduino;

    let cmdUri = baseUri + '.' + apiStr + '.' + cmd;
    switch (cmdUri) {
        case 'nodejs.api.start.console.log.response' :
                showArduinoResponseInServerTerminal = true;
                console.log('Show Arduino response');
                return;
                break;
        case 'nodejs.api.stop.console.log.response' :
                showArduinoResponseInServerTerminal = false;
                return;
                break;
        case 'arduino.api.status.stop':
                cmdNum = 2;
                commandStringToSend = '4 ' + cmdNum + ' ' + myRandom + ' ' + (parseInt(cmdNum) + parseInt(myRandom) + 4);
                break;
        case 'arduino.api.status.start':
                cmdNum = 3;
                commandStringToSend = '5 ' + cmdNum + ' ' + myRandom + ' ' + ( parseInt(cmdNum) + parseInt(myRandom) + parseInt(parm1) + 5) + ' ' + parm1;
                break;
        case 'arduino.api.move.timeout':
                cmdNum = 6;
                commandStringToSend = '5 ' + cmdNum + ' ' + myRandom + ' ' + ( parseInt(cmdNum) + parseInt(myRandom) + parseInt(parm1) + 5) + ' ' + parm1;
                break;
        case 'arduino.api.clr.usb.err':
                cmdNum = 4;
                commandStringToSend = '4 ' + cmdNum + ' ' + myRandom + ' ' + (parseInt(cmdNum) + parseInt(myRandom) + 4);
                break;
        case 'arduino.api.clr.num.usb.cmds':
                cmdNum = 5;
                commandStringToSend = '4 ' + cmdNum + ' ' + myRandom + ' ' + (parseInt(cmdNum) + parseInt(myRandom) + 4);
                break;
        case 'arduino.api.version':
                cmdNum = 20;
                commandStringToSend = '4 ' + cmdNum + ' ' + myRandom + ' ' + (parseInt(cmdNum) + parseInt(myRandom) + 4);
                break;
        case 'arduino.api.status':
                cmdNum = 24;
                commandStringToSend = '4 ' + cmdNum + ' ' + myRandom + ' ' + (parseInt(cmdNum) + parseInt(myRandom) + 4);
                break;
        case 'arduino.api.stop':
                cmdNum = 28;
                commandStringToSend = '4 ' + cmdNum + ' ' + myRandom + ' ' + (parseInt(cmdNum) + parseInt(myRandom) + 4);
                break;

        case 'arduino.api.forward':
                commandStringToSend = processDriveCommand(ackWaitTime,29, cmd, myRandom, parm1, parm2);
                if (commandStringToSend === '') { return; }
                break;
        case 'arduino.api.backward':
                commandStringToSend = processDriveCommand(ackWaitTime,32, cmd, myRandom, parm1, parm2);
                if (commandStringToSend === '') { return; }
                break;
        case 'arduino.api.left':
                commandStringToSend = processDriveCommand(ackWaitTime,33, cmd, myRandom, parm1, parm2);
                if (commandStringToSend === '') { return; }
                break;
        case 'arduino.api.right':
                commandStringToSend = processDriveCommand(ackWaitTime,34, cmd, myRandom, parm1, parm2);
                if (commandStringToSend === '') { return; }
                break;

        default:
                throw 'Unknown command :' + cmdUri;
                break;
    }


    console.log('=========================================');
    console.log('COMMAND TO SEND : ' + commandStringToSend);
    console.log('=========================================');
    //return;
    commandWasSentToArduino = true;

    lastCommandSentToArduino = commandStringToSend;
    lastCommandSentTimestamp = new Date().getTime();

    //arduinoHistory.push({lastCommandSentToArduino,lastCommandSentTimestamp});
    //console.log(arduinoHistory);

    arduinoPort.write(commandStringToSend + '\n', e => {
        if (e) {
            error = 'Error sending data to arduino: ', e.message;
            console.log('Error sending data to arduino: ', e.message);
        } else {
            console.log(cmd + ': command \'',commandStringToSend,'\' sent to arduino');
        }
    });
}



///////arduino command handler/////////////////////////////////////////////////////
const arduinoApiCommandHandler = (request, response) => {

    console.log('client request: commandHandler : ' + request.path);

    try {
        parseAndSendCommandToArduino(request.path);
        if (commandWasSentToArduino) {
            response.status(200).send('Cmd Sent To Arduino. You requested ' + request.path);
        } else {
            response.status(500).send('{\"error\":\"CMD NOT SENT TO ARDUINO: You requested ' + request.path + '\"}');
        }
    } catch (e) {
        response.status(500).send('{\"error\":\"Error: ' + e + ' : You requested ' + request.path + '\"}');
        error = 'Error: ' + e + ' requesting ' + request.path;
    }
}
app.get('/arduino/api/*', arduinoApiCommandHandler);


///////arduino api NO command handler/////////////////////////////////////////////////////
const arduinoApiNoCommandHandler = (request, response) => {
    console.log('client request: commandHandler : ' + request.path);
    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need something after that.\"}');
}
app.get('/arduino/api', arduinoApiNoCommandHandler);


///////arduino NO command handler/////////////////////////////////////////////////////
const arduinoNoCommandHandler = (request, response) => {
    console.log('client request: commandHandler : ' + request.path);
    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /api/blah.blah after that.\"}');
}
app.get('/arduino', arduinoNoCommandHandler);

///////node.js server command handler/////////////////////////////////////////////////////
const nodeJsCommandHandler = (request, response) => {

    console.log('client request: nodeJsCommandHandler: ' + request.path);


    if (request.path === '/nodejs/api/data') {
        respondWithCollectedDataHandler(request, response);
        return;
    }

    if (request.path === '/nodejs/api/history') {
        respondWithHistoryHandler(request, response);
        return;
    }

    try {
        parseAndSendCommandToArduino(request.path);
    } catch (e) {
        response.status(500).send('{\"error\":\"Error: ' + e + ' : You requested ' + request.path + '\"}');
        error = 'Error: ' + e + ' requesting ' + request.path;
    }
}
app.get('/nodejs/api/*', nodeJsCommandHandler);


///////node.js api NO command handler/////////////////////////////////////////////////////
const nodeJsApiNoCommandHandler = (request, response) => {
    console.log('client request: commandHandler : ' + request.path);
    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need something after that.\"}');
}
app.get('/nodejs/api', nodeJsApiNoCommandHandler);


///////node.js api SHUTDOWN command handler/////////////////////////////////////////////////////
const nodeJsApiShutdownCommandHandler = (request, response) => {
    console.log('client request: SHUTDOWN handler : ' + request.path);
    let msg = {}
    msg.msg = "ok";
    response.status(201).send(msg);

    axios.delete('http://localhost:'+ messagingServerPort + '/messaging/api/robot.drive/quit')
    .then(response => {
        console.log('registered with messaging that this program is shutting down.');
        server.close()
        process.exit();
    })
    .catch(error => {
        axios.delete('http://localhost:'+ messagingServerPort + '/messaging/api/robot.drive/quit')
        .then(response => {
            console.log('registered with messaging that this program is shutting down.');
            server.close()
            process.exit();
        })
        .catch(error => {
            console.log('gave up trying to register with messaging that this program is shutting down.');
            server.close()
            process.exit();
        });
    });
 
}
app.post('/nodejs/api/shutdown', nodeJsApiShutdownCommandHandler);


///////node.js NO command handler/////////////////////////////////////////////////////
const nodeJsNoCommandHandler = (request, response) => {

    console.log('client request: nodeJsCommandHandler : ' + request.path);

    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /api/blah.blah after that.\"}');
}
app.get('/nodejs', nodeJsNoCommandHandler);


///////node.js bad/////////////////////////////////////////////////////
const nodeJsBad = (request, response) => {

    console.log('client request: nodeJsCommandHandler : ' + request.path);

    response.status(404).send('{\"error\":\"You requested ' + request.path + '. Did you mean /nodejs?\"}');
}
app.get('/node.js', nodeJsBad);





const server = app.listen(thisServerPort, () => {
    console.log('HTTP Raspberry Pi Server is Up at ', thisServerPort);
});

