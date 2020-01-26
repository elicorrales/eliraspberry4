#!/bin/bash


function  getMessagingStatus {

    echo http://localhost:8085/messaging/api/status;
    curl http://localhost:8085/messaging/api/status;
    echo;

    echo "================================================="
}


function basicPostCommand {
    command=$1;
    echo "-X POST -H \"Content-Type:application/json\" http://localhost:8085/messaging/api/vision/command${command}";
    curl -X POST -H "Content-Type:application/json" http://localhost:8085/messaging/api/vision/command${command};
    echo;
    echo "================================================="
}

function initialize {

    echo;
    command="/initialize?from=voice.control";
    basicPostCommand ${command};
}


function quit {

    echo;
    command="/quit?from=voice.control";
    basicPostCommand ${command};
}




function requestUpdatedStatus {

    echo;
    command="/robotstatus?from=voice.control";
    basicPostCommand ${command};

    sleep 1
}

function moveForward {
    echo;
    command="/forward?from=voice.control";
    basicPostCommand ${command};
}

function comeHere {
    echo;
    command="/come.here?from=voice.control";
    basicPostCommand ${command};
}

read -p "continue - request to initialize"
initialize

read -p "continue - request to initialize"
initialize

read -p "continue - request to come here"
comeHere


read -p "continue - get initial message broker values"
getMessagingStatus

read -p "continue - request updated status"
requestUpdatedStatus

read -p "continue - get current message broker values"
getMessagingStatus

read -p "continue - request to initialize"
initialize

read -p "continue - get current message broker values"
getMessagingStatus

read -p "continue - request updated status"
requestUpdatedStatus

read -p "continue - get current message broker values"
getMessagingStatus

read -p "continue - request to move forward"
moveForward

read -p "continue - get current message broker values"
getMessagingStatus

read -p "continue - request updated status"
requestUpdatedStatus

read -p "continue - get current message broker values"
getMessagingStatus

read -p "continue - request to quit"
quit

read -p "continue - get current message broker values"
getMessagingStatus
