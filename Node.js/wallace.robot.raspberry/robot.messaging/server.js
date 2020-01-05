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




const mainHandler = (request, response) => {

    console.log('client request: mainHandler: ' + request.path);


    if (request.path === '/messaging/api/status') {
        respondWithCollectedDataHandler(request, response);
        return;
    }

    response.status(500).send('{\"error\":\"Error: ' + e + ' : You requested ' + request.path + '. Unknown.\"}');
}
app.get('/messaging/api/*', mainHandler);



const messagingApiBad = (request, response) => {
    console.log('client request: messagingApiBad : ' + request.path);
    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /api/blah.blah after that.\"}');
}
app.get('/messaging/api', messagingApiBad);
app.post('/messaging/api', messagingApiBad);


const messagingBad = (request, response) => {
    console.log('client request: messagingBad : ' + request.path);
    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /api/blah blah after that.\"}');
}
app.get('/messaging', messagingBad);
app.post('/messaging', messagingBad);


const badRoot = (request, response) => {
    console.log('client request: badRoot : ' + request.path);
    response.status(404).send('{\"error\":\"You requested ' + request.path + '. You need /messaging/api/blah blah after that.\"}');
}
app.get('/', rootHandler);
app.post('/', rootHandler);


app.listen(thiServerPort, () => {
    console.log('HTTP Raspberry Pi Server is Up at ', thisServerPort);
});

