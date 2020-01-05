#!/bin/bash

baseurl="http://localhost:8084";
arduino="${baseurl}/arduino";
api="${arduino}/api";
data="${arduino}/data";
clrusberr=${api}/clr.usb.err;
clrcmds=${api}/clr.num.usb.cmds;
onestatus=${api}/status;
statusstop=${api}/status.stop;
timeout500=${api}/move.timeout/500;
timeout200=${api}/move.timeout/200;
timeout100=${api}/move.timeout/100;
forward=${api}/forward/50;

function arduinoReceivedCommand {
    curl --silent $onestatus 2>&1;
    echo;echo;
    dataResults=$(curl --silent $data 2>&1);
    echo $dataResults #| sed -e 's/^.*lastcmd.://g' -e 's/,.*$//g');
    lastCmd=$(echo $dataResults | sed -e 's/^.*lastcmd.://g' -e 's/,.*$//g');
    if [ "$1" = "$lastCmd" ];
    then
        return 1;
    else
        return 0;
    fi;
}

function sendArduinoCommandUntilResponse {
    cmdUri=$1;
    cmdNum=$2;
    curl --silent $cmdUri;
    echo; echo;
    arduinoReceivedCommand $cmdNum; 
    rtn=$?;
    while [ "$rtn" != "1" ];
    do
        arduinoReceivedCommand $cmdNum; 
        rtn=$?;
        sleep 1;
    done;
    sleep 1;
}

read -p "press <ENTER> to clear usb error flag and initiate arduino.";
sendArduinoCommandUntilResponse $clrusberr 4;
sendArduinoCommandUntilResponse $clrcmds 5;

read -p "press <ENTER> to send stop auto status.";
sendArduinoCommandUntilResponse $statusstop 2;


read -p "press <ENTER> to set movement timeout at 500ms.";
sendArduinoCommandUntilResponse $timeout500 6;

read -p "press <ENTER> to clear all errors.";
sendArduinoCommandUntilResponse $clrusberr 4;

read -p "press <ENTER> to move forward.";
sendArduinoCommandUntilResponse $forward 29;

read -p "press <ENTER> to clear all errors.";
sendArduinoCommandUntilResponse $clrusberr 4;

read -p "press <ENTER> to set movement timeout at 200ms.";
sendArduinoCommandUntilResponse $timeout200 6;

read -p "press <ENTER> to clear all errors.";
sendArduinoCommandUntilResponse $clrusberr 4;

read -p "press <ENTER> to move forward.";
sendArduinoCommandUntilResponse $forward 29;

read -p "press <ENTER> to clear all errors.";
sendArduinoCommandUntilResponse $clrusberr 4;

read -p "press <ENTER> to set movement timeout at 100ms.";
sendArduinoCommandUntilResponse $timeout100 6;

read -p "press <ENTER> to clear all errors.";
sendArduinoCommandUntilResponse $clrusberr 4;

read -p "press <ENTER> to move forward.";
sendArduinoCommandUntilResponse $forward 29;

read -p "press <ENTER> to clear all errors.";
sendArduinoCommandUntilResponse $clrusberr 4;

