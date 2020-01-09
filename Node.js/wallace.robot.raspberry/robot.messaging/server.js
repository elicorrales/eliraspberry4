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

let latestCommandToVision = '';

const respondeWithCollectedDataHandler = (request, response) => {
        response.status(200).send('{\"status\":\"' + latestStatusFromRobotDrive + '\"}');
}

const mainGetHandler = (request, response) => {

    console.log('client request: mainGetHandler: ' + request.path);
    if (request.query !== undefined) console.log('request.query:' + JSON.stringify(request.query));
    if (request.params !== undefined) console.log('request.params:' + JSON.stringify(request.params));
    if (request.body !== undefined) console.log('request.body:' + JSON.stringify(request.body));

    if (request.path === '/messaging/api/robot.command') {
        console.log(latestCommandToRobotDrive);
        //let command = {}
        //command.command = latestCommandToRobotDrive;
        //console.log(command);
        console.log('{\"command\":\"' + latestCommandToRobotDrive + '\"}');
        response.status(200).send('{\"command\":\"' + latestCommandToRobotDrive + '\"}');
        //response.status(200).send(JSON.stringify(command));
        return;
    }

    if (request.path === '/messaging/api/robot.status') {
        let theStatus = {}
        theStatus.status = latestStatusFromRobotDrive;
        //console.log('{\"status\":\"' + latestStatusFromRobotDrive + '\"}');
        //response.status(200).send('{\"status\":\"' + latestStatusFromRobotDrive + '\"}');
        console.log(theStatus);
        response.status(200).send(JSON.stringify(theStatus));
        return;
    }


    if (request.path === '/messaging/api/vision.command') {
        let command = {}
        command.command = latestCommandToVision;
        //console.log('{\"status\":\"' + latestStatusFromRobotDrive + '\"}');
        //response.status(200).send('{\"status\":\"' + latestStatusFromRobotDrive + '\"}');
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

const mainPostHandler = (request, response) => {

    console.log('client request: mainPostHandler: ' + request.path);
    if (request.query !== undefined) console.log('request.query:' + JSON.stringify(request.query));
    if (request.params !== undefined) console.log('request.params:' + JSON.stringify(request.params));
    if (request.body !== undefined) console.log('request.body:' + JSON.stringify(request.body));


    if (request.path === '/messaging/api/robot.command') {
        latestCommandToRobotDrive = request.query.uri;
        //let msg = {}
        //msg.msg = 'ok';
        response.status(201).send('{\"msg\":\"ok\"}');
        //response.status(201).send(msg);
        return;
    }


    if (request.path === '/messaging/api/robot.status') {
        latestStatusFromRobotDrive = request.body;
        //let msg = {}
        //msg.msg = 'ok';
        response.status(201).send('{\"msg\":\"ok\"}');
        //response.status(201).send(msg);
        return;
    }


    if (request.path === '/messaging/api/vision.command') {
        let msg = {}
        msg.msg = 'ok';
        response.status(201).send(msg);
        //response.status(201).send('{\"msg\":\"ok\"}');
        return;
    }


    console.log(request.method);
    console.log(request.params);
    //let error = {}
    ////error.error = 'Error: You requested ' + request.path + '. Unknown.';
    response.status(500).send('{\"error\":\"Error: You requested ' + request.path + '. Unknown.\"}');
    //response.status(500).send(error);
    server.close()
    process.exit();
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


const server = app.listen(thisServerPort, () => {
    console.log('HTTP Raspberry Pi Server is Up at ', thisServerPort);
});


