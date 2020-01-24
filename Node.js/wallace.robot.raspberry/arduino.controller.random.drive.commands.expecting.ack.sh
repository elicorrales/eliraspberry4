#!/bin/bash

baseurl="http://localhost:8084";
arduino="${baseurl}/arduino";
api="${arduino}/api";
data="${arduino}/data";
clrusberr=${api}/clr.usb.err;
clrcmds=${api}/clr.num.usb.cmds;

echo;echo "STOP RC auto send status indication";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl --silent "${api}/status/start/50";
echo; echo;

speed=50;

curl --silent $clrusberr;
echo; echo;
sleep 1;
curl --silent $clrcmds;
echo; echo;

numCycles=400;
#numCycles=4;
while [ $numCycles -gt 0 ];
do
    random=$RANDOM;
    if [ $random -ge 0 ] && [ $random -lt 8192 ];
    then
        echo;echo "Move forward at $speed..";
        curl --silent "${api}/forward/${speed}";
        echo; echo;
    elif [ $random -ge 8192 ] && [ $random -lt 16384 ];
    then
        echo;echo "Move backward at $speed..";
        curl --silent "${api}/backward/${speed}";
        echo; echo;
    elif [ $random -ge 16384 ] && [ $random -lt 24576 ];
    then
        echo;echo "Move left at $speed..";
        curl --silent "${api}/left/${speed}";
        echo; echo;
    else
        echo;echo "Move right at $speed..";
        curl --silent "${api}/right/${speed}";
        echo; echo;
    fi;
        #sleep 0.001;
        numCycles=$((numCycles-1));
        dataResults=$(curl --silent $data 2>&1);
        cmdNotSent=$(echo $dataResults | grep "CMD NOT SENT");
        unkCmd=$(echo $dataResults | grep "UNKCMD");
        if [ "$unkCmd" != "" ];
        then
            echo $unkCmd;
            break;
        elif [ "$cmdNotSent" != "" ];
        then
            echo $cmdNotSent;
            #break;
        fi;
done;


curl --silent "${api}/status/stop";
echo; echo;
echo;echo "Stop motors";
curl --silent "${api}/stop";
echo; echo;
