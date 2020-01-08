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


let latestCommandToRobotDrive = '';
let latestStatusFromRobotDrive = '';

const respondeWithCollectedDataHandler = (request, response) => {
        response.status(200).send('{\"status\":\"' + latestStatusFromRobotDrive + '\"}');
}

const mainGetHandler = (request, response) => {

    console.log('client request: mainGetHandler: ' + request.path);

    if (request.path === '/messaging/api/command') {
        let command = {}
        command.command = latestCommandToRobotDrive;
        console.log(command);
        //console.log('{\"command\":\"' + latestCommandToRobotDrive + '\"}');
        //response.status(200).send('{\"command\":\"' + latestCommandToRobotDrive + '\"}');
        response.status(200).send(JSON.stringify(command));
        return;
    }

    if (request.path === '/messaging/api/status') {
        let status = {}
        status.status = latestStatusFromRobotDrive;
        //console.log('{\"status\":\"' + latestStatusFromRobotDrive + '\"}');
        //response.status(200).send('{\"status\":\"' + latestStatusFromRobotDrive + '\"}');
        console.log(status);
        response.status(200).send(JSON.stringify(status));
        return;
    }



    console.log(request.method);
    console.log(request.params);
    let error = {}
    error.error = 'Error: You requested ' + request.path + '. Unknown.';
    //response.status(500).send('{\"error\":\"Error: You requested ' + request.path + '. Unknown.\"}');
    response.status(500).send(error);
}
app.get('/messaging/api/*', mainGetHandler);

const mainPostHandler = (request, response) => {

    console.log('client request: mainPostHandler: ' + request.path);


    if (request.path === '/messaging/api/command') {
        console.log('query.query.uri:' + request.query.uri);
        if (request.params !== undefined) console.log('request.params:' + JSON.stringify(request.params));
        if (request.body !== undefined) console.log('request.body:' + JSON.stringify(request.body));
        latestCommandToRobotDrive = request.query.uri;
        let msg = {}
        msg.msg = 'ok';
        //response.status(201).send('{\"msg\":\"ok\"}');
        response.status(201).send(msg);
        return;
    }


    if (request.path === '/messaging/api/status') {
        //console.log('');
        //console.log('');
        //console.log(request.body);
        if (request.body !== undefined) console.log(request.body);
        //console.log('');
        //console.log('request.query.uri:' + request.query.uri);
        //console.log('request.params:' + JSON.stringify(request.params));
        latestStatusFromRobotDrive = request.body;
        let msg = {}
        msg.msg = 'ok';
        //response.status(201).send('{\"msg\":\"ok\"}');
        response.status(201).send(msg);
        return;
    }


    console.log(request.method);
    console.log(request.params);
    let error = {}
    error.error = 'Error: You requested ' + request.path + '. Unknown.';
    //response.status(500).send('{\"error\":\"Error: You requested ' + request.path + '. Unknown.\"}');
    response.status(500).send(error);
}
app.post('/messaging/api/*', mainPostHandler);



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


app.listen(thisServerPort, () => {
    console.log('HTTP Raspberry Pi Server is Up at ', thisServerPort);
});

