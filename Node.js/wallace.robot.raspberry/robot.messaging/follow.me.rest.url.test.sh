#!/bin/bash


function  getMessagingStatus {
    echo http://10.0.0.58:8085/messaging/api/vision/ready;
    curl http://10.0.0.58:8085/messaging/api/vision/ready;
    echo;

    echo http://10.0.0.58:8085/messaging/api/vision/new;
    curl http://10.0.0.58:8085/messaging/api/vision/new;
    echo;

    echo http://10.0.0.58:8085/messaging/api/robot/command;
    curl http://10.0.0.58:8085/messaging/api/robot/command;
    echo;

    echo http://10.0.0.58:8085/messaging/api/vision/status;
    curl http://10.0.0.58:8085/messaging/api/vision/status;
    echo;

    echo http://10.0.0.58:8085/messaging/api/vision/command;
    curl http://10.0.0.58:8085/messaging/api/vision/command;
    echo;

}


getMessagingStatus


    #######################################################################
    # should cause vision controller to fail because messaging broker expects command url and params, not body
    #echo;
    #body='{"command":"test"}';
    #echo "-X POST -H \"Content-Type:application/json\" -d '${body}' http://10.0.0.58:8085/messaging/api/robot/command";
    #curl -X POST -H "Content-Type:application/json" -d ${body} http://10.0.0.58:8085/messaging/api/robot/command;
    #echo;

    #######################################################################
    # should cause vision controller to fail because command url is empty
    #echo;
    #command="?uri=";
    #echo "-X POST -H \"Content-Type:application/json\" http://10.0.0.58:8085/messaging/api/robot/command${command}";
    #curl -X POST -H "Content-Type:application/json" http://10.0.0.58:8085/messaging/api/robot/command${command};
    #echo;

    #######################################################################
    # should cause vision controller to fail because command sent to Node.js driver controller fails
    #echo;
    #command="?uri=/";
    #echo "-X POST -H \"Content-Type:application/json\" http://10.0.0.58:8085/messaging/api/robot/command${command}";
    #curl -X POST -H "Content-Type:application/json" http://10.0.0.58:8085/messaging/api/robot/command${command};
    #echo;

    #######################################################################
    # should cause vision controller to fail because command sent to Node.js driver controller fails
    #echo;
    #command="?uri=/arduino";
    #echo "-X POST -H \"Content-Type:application/json\" http://10.0.0.58:8085/messaging/api/robot/command${command}";
    #curl -X POST -H "Content-Type:application/json" http://10.0.0.58:8085/messaging/api/robot/command${command};
    #echo;

    #######################################################################
    # should cause vision controller to fail because command sent to Node.js driver controller fails
    #echo;
    #command="?uri=/arduino/api";
    #echo "-X POST -H \"Content-Type:application/json\" http://10.0.0.58:8085/messaging/api/robot/command${command}";
    #curl -X POST -H "Content-Type:application/json" http://10.0.0.58:8085/messaging/api/robot/command${command};
    #echo;

    #######################################################################
    # should cause vision controller to fail because command sent to Node.js driver controller fails
    echo;
    command="?uri=/arduino/api/clr.usb.err";
    echo "-X POST -H \"Content-Type:application/json\" http://10.0.0.58:8085/messaging/api/robot/command${command}";
    curl -X POST -H "Content-Type:application/json" http://10.0.0.58:8085/messaging/api/robot/command${command};
    echo;


getMessagingStatus
