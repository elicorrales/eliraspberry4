#!/bin/bash

for loop in 1 2 3 4 5 6;
do
    figlet 'Abre Que Voy'
    read -p "<ENTER>"
    python train.phrases.py --phrase='Abre Que Voy' --json-file=music.json --length=2


    figlet 'Asi Son'
    read -p "<ENTER>"
    python train.phrases.py --phrase='Asi Son' --json-file=music.json --length=2


    figlet 'Abandonada Fue'
    read -p "<ENTER>"
    python train.phrases.py --phrase='Abandonada Fue' --json-file=music.json --length=2

    figlet 'A que saben tus besos'
    read -p "<ENTER>"
     python train.phrases.py --phrase='A que saben tus besos' --json-file=music.json --length=2
done;
