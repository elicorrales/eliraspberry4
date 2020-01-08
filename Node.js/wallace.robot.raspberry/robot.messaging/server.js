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
        response.status(200).send('{\"command\":\"' + latestCommandToRobotDrive + '\"}');
        return;
    }

    if (request.path === '/messaging/api/status') {
        response.status(200).send('{\"status\":\"' + latestStatusFromRobotDrive + '\"}');
        return;
    }



    console.log(request.method);
    console.log(request.params);
    response.status(500).send('{\"error\":\"Error: You requested ' + request.path + '. Unknown.\"}');
}
app.get('/messaging/api/*', mainGetHandler);

const mainPostHandler = (request, response) => {

    console.log('client request: mainPostHandler: ' + request.path);


    if (request.path === '/messaging/api/command') {
        console.log('query.uri:' + request.query.uri);
        console.log('query.params:' + JSON.stringify(request.params));
        latestCommandToRobotDrive = request.query.uri;
        response.status(201).send('{\"msg\":\"ok\"}');
        return;
    }


    console.log(request.method);
    console.log(request.params);
    response.status(500).send('{\"error\":\"Error: You requested ' + request.path + '. Unknown.\"}');
}
app.post('/messaging/api/*', mainPostHandler);



const messagingApiBad = (request, response) => {
    console.log('client request: messagingApiBad : ' + request.path);
    console.log(request.method);
    console.log(request.params);
    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /api/blah.blah after that.\"}');
}
app.get('/messaging/api', messagingApiBad);
app.post('/messaging/api', messagingApiBad);


const messagingBad = (request, response) => {
    console.log('client request: messagingBad : ' + request.path);
    console.log(request.method);
    console.log(request.params);
    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /api/blah blah after that.\"}');
}
app.get('/messaging', messagingBad);
app.post('/messaging', messagingBad);


const badRoot = (request, response) => {
    console.log('client request: badRoot : ' + request.path);
    console.log(request.method);
    console.log(request.params);
    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /messaging/api/blah blah after that.\"}');
}
app.get('/', badRoot);
app.post('/', badRoot);


app.listen(thisServerPort, () => {
    console.log('HTTP Raspberry Pi Server is Up at ', thisServerPort);
});

