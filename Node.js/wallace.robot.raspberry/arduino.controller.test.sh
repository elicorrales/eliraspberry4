#!/bin/bash

baseurl="http://localhost:8084";
arduino="${baseurl}/arduino";
api="${arduino}/api";

echo "This next test should at least flash LED on Arduino.";
read -p "press <ENTER> to move on.";
curl $arduino;

echo;echo "This next test should show menu on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl $api;

echo;echo "This next test should show menu on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/help";

echo;echo "This next test should show numcmds on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/numcmds";

echo;echo "This next test should show RC status on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/status";

echo;echo "This next test should show RC version on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/version";

echo;echo "This next test should stop RC auto send status indication on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/status/stop";

echo;echo "This next test should start RC auto send status indication";
echo "at 500 ms on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/status/start/500";

echo;echo "This next test should start RC auto send status indication";
echo "at 250 ms on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/status/start/250";

echo;echo "This next test should STOP RC auto send status indication";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/status/stop";

echo;echo "This next test should should stop RC";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/stop";

echo;echo "This next test should should send clr.usb.err to arduino";
read -p "press <ENTER> to move on.";
curl "${api}/clr.usb.err";

echo;echo "This next test should should forward RC at 30 30";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/forward/30/0";

echo;echo "This next test should should forward RC at 50 50";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/forward/50/1";

echo;echo "This next test should should backward RC at 80 80";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/backward/80/2";

echo;echo "This next test should should rotate left RC at 100 100";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/left/100/3";

echo;echo "This next test should should rotate right RC at 100 100";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/right/100/4";

echo;echo "This next test should should stop RC";
echo "on server side console (node server.js)";
read -p "press <ENTER> to move on.";
curl "${api}/stop";

