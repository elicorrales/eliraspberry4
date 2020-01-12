#!/bin/bash


function  getMessagingStatus {
    echo http://10.0.0.58:8085/messaging/api/vision/ready?from=voice.control;
    curl http://10.0.0.58:8085/messaging/api/vision/ready?from=voice.control;
    echo;

    echo http://10.0.0.58:8085/messaging/api/vision/new?from=voice.control;
    curl http://10.0.0.58:8085/messaging/api/vision/new?from=voice.control;
    echo;

    echo http://10.0.0.58:8085/messaging/api/vision/status?from=voice.control;
    curl http://10.0.0.58:8085/messaging/api/vision/status?from=voice.control;
    echo;

    echo http://10.0.0.58:8085/messaging/api/vision/command?from=voice.control;
    curl http://10.0.0.58:8085/messaging/api/vision/command?from=voice.control;
    echo;

    echo "================================================="
}


function initialize {

    echo;
    command="/initialize?from=voice.control";
    echo "-X POST -H \"Content-Type:application/json\" http://10.0.0.58:8085/messaging/api/vision/command${command}";
    curl -X POST -H "Content-Type:application/json" http://10.0.0.58:8085/messaging/api/vision/command${command};
    echo;
    echo "================================================="
}


function quit {

    echo;
    command="/quit?from=voice.control";
    echo "-X POST -H \"Content-Type:application/json\" http://10.0.0.58:8085/messaging/api/vision/command${command}";
    curl -X POST -H "Content-Type:application/json" http://10.0.0.58:8085/messaging/api/vision/command${command};
    echo;
    echo "================================================="
}




function requestUpdatedStatus {

    echo;
    command="/status?from=voice.control";
    echo "-X POST -H \"Content-Type:application/json\" http://10.0.0.58:8085/messaging/api/vision/command${command}";
    curl -X POST -H "Content-Type:application/json" http://10.0.0.58:8085/messaging/api/vision/command${command};
    echo;
    echo "================================================="

    sleep 1
}

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

read -p "continue - request to quit"
quit

read -p "continue - get current message broker values"
getMessagingStatus
