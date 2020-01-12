'use strict';

const argv = require('yargs').argv;

const express = require('express');
const app = express();
app.use(express.json());
app.use((request, response, next) => {
  response.header("Access-Control-Allow-Origin", "*");
  response.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});


const thisServerPort = 8085;

// the robot vision control program will set to 'true' when it is ready
let visionReadyForNextCommand = true;

// the voice control program will set to 'true' when there is a new command set inside this server
let visionHasNewCommandWaiting = false;

let latestStatusFromVision = '';

let latestCommandToVision = '';

const setNewCommandWaiting = () => {
    visionReadyForNextCommand = false;
    visionHasNewCommandWaiting = true;
}

const setVisionReadyForNewCommand = () => {
    visionHasNewCommandWaiting = false;
    visionReadyForNextCommand = true;
}

const mainGetHandler = (request, response) => {

    console.log('');
    //console.log('client request: mainGetHandler: ' + request.path);
    //if (request.query !== undefined) console.log('request.query:' + JSON.stringify(request.query));
    //if (request.params !== undefined) console.log('request.params:' + JSON.stringify(request.params));
    //if (request.body !== undefined) console.log('request.body:' + JSON.stringify(request.body));


    if (request.path === '/messaging/api/vision/ready') {
        console.log(visionReadyForNextCommand);
        let ready = {}
        ready.ready = visionReadyForNextCommand;
        console.log(ready);
        response.status(200).send(JSON.stringify(ready));
        return;
    }

    if (request.path === '/messaging/api/vision/new') {
        console.log(visionHasNewCommandWaiting);
        let newcmd = {}
        newcmd.newcmdavail = visionHasNewCommandWaiting;
        console.log(newcmd);
        response.status(200).send(JSON.stringify(newcmd));
        return;
    }


    if (request.path === '/messaging/api/vision/command') {
        console.log('client request: mainGetHandler: ' + request.path);
        if (request.query !== undefined) console.log('request.query:' + JSON.stringify(request.query));
        if (request.params !== undefined) console.log('request.params:' + JSON.stringify(request.params));
        if (request.body !== undefined) console.log('request.body:' + JSON.stringify(request.body));
        console.log(latestCommandToVision);
        let command = {}
        command.command = latestCommandToVision;
        console.log(command);
        response.status(200).send(JSON.stringify(command));
        return;
    }

    if (request.path === '/messaging/api/vision/status') {
        let theStatus = {}
        theStatus.status = latestStatusFromVision;
        console.log(theStatus);
        response.status(200).send(JSON.stringify(theStatus));
        return;
    }


    if (request.path === '/messaging/api/vision/command') {
        console.log('client request: mainGetHandler: ' + request.path);
        if (request.query !== undefined) console.log('request.query:' + JSON.stringify(request.query));
        if (request.params !== undefined) console.log('request.params:' + JSON.stringify(request.params));
        if (request.body !== undefined) console.log('request.body:' + JSON.stringify(request.body));
        let command = {}
        command.command = latestCommandToVision;
        console.log(command);
        response.status(200).send(JSON.stringify(command));
        return;
    }




    console.log(request.method);
    console.log(request.params);
    let error = {}
    error.error = 'Error: You requested ' + request.path + '. Unknown.';
    //response.status(500).send('{\"error\":\"Error: You requested ' + request.path + '. Unknown.\"}');
    response.status(500).send(error);
    server.close()
    process.exit();

}
app.get('/messaging/api/*', mainGetHandler);


const postCommandHandler = (request, response) => {

    console.log('');
    console.log('client request: postCommandHandler: ' + request.path);
    if (request.query !== undefined) console.log('request.query:' + JSON.stringify(request.query));
    if (request.params !== undefined) console.log('request.params:' + JSON.stringify(request.params));
    if (request.body !== undefined) console.log('request.body:' + JSON.stringify(request.body));


    latestCommandToVision = request.params['0'];
    let msg = {}
    msg.msg = 'ok';
    response.status(201).send(msg);
    setNewCommandWaiting();

}
app.post('/messaging/api/vision/command/*', postCommandHandler);


const mainPostHandler = (request, response) => {

    console.log('');
    console.log('client request: mainPostHandler: ' + request.path);
    if (request.query !== undefined) console.log('request.query:' + JSON.stringify(request.query));
    if (request.params !== undefined) console.log('request.params:' + JSON.stringify(request.params));



    //vision control posts this to upload the complete status info
    if (request.path === '/messaging/api/vision/status') {
        if (request.body !== undefined) console.log('request.body:' + JSON.stringify(request.body));
        latestStatusFromVision = request.body;
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        return;
    }


    //vision control sends this to tell voice control that it IS quitting.
    if (request.path === '/messaging/api/vision/status/quit') {
        latestStatusFromVision = {};
        latestStatusFromVision['quit'] = '';
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        return;
    }



    if (request.path === '/messaging/api/vision/ready') {
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        setVisionReadyForNewCommand();
        return;
    }

    console.log(request.method);
    console.log(request.params);
    let error = {}
    error.error = 'Error: You requested ' + request.path + '. Unknown.';
    response.status(500).send(error);
    server.close()
    process.exit();
}
app.post('/messaging/api/*', mainPostHandler);





const mainDeleteHandler = (request, response) => {

    console.log('');
    console.log('client request: mainDeleteHandler: ' + request.path);
    if (request.query !== undefined) console.log('request.query:' + JSON.stringify(request.query));
    if (request.params !== undefined) console.log('request.params:' + JSON.stringify(request.params));
    if (request.body !== undefined) console.log('request.body:' + JSON.stringify(request.body));


    if (request.path === '/messaging/api/vision/command') {
        latestCommandToVision = '';
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        return;
    }


    if (request.path === '/messaging/api/vision/new') {
        visionHasNewCommandWaiting = false;
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        return;
    }

    if (request.path === '/messaging/api/vision/status') {
        latestStatusFromVision = request.body;
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        return;
    }


    if (request.path === '/messaging/api/vision/status/quit') {
        latestStatusFromVision = {};
        latestStatusFromVision['quit'] = '';
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        return;
    }


    if (request.path === '/messaging/api/vision/command/status') {
        latestStatusFromVision = '';
        latestCommandToVision = 'status'
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        return;
    }


    if (request.path === '/messaging/api/vision/command/quit') {
        latestStatusFromVision = '';
        latestCommandToVision = 'quit'
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        return;
    }


    console.log(request.method);
    console.log(request.params);
    let error = {}
    error.error = 'Error: You requested ' + request.path + '. Unknown.';
    response.status(500).send(error);
    server.close()
    process.exit();
}
app.delete('/messaging/api/*', mainDeleteHandler);


const messagingApiBad = (request, response) => {
    console.log('client request: messagingApiBad : ' + request.path);
    let error = {}
    error.error = 'You requested ' + request.path + '. You need /api/blah.blah after that.';
    //response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /api/blah.blah after that.\"}');
    response.status(404).send(error);
}
app.get('/messaging/api', messagingApiBad);
app.post('/messaging/api', messagingApiBad);


const messagingBad = (request, response) => {
    console.log('client request: messagingBad : ' + request.path);
    let error = {}
    error.error = 'You requested ' + request.path + '. You need /api/blah blah after that.';
    //response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /api/blah blah after that.\"}');
    response.status(404).send(error);
}
app.get('/messaging', messagingBad);
app.post('/messaging', messagingBad);


const badRoot = (request, response) => {
    console.log('client request: badRoot : ' + request.path);
    let error = {}
    error.error = 'You requested ' + request.path + '. You need /messaging/api/blah blah after that.';
    //response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /messaging/api/blah blah after that.\"}');
    response.status(404).send(error);
}
app.get('/', badRoot);
app.post('/', badRoot);


const server = app.listen(thisServerPort, () => {
    console.log('HTTP Raspberry Pi Server is Up at ', thisServerPort);
});


