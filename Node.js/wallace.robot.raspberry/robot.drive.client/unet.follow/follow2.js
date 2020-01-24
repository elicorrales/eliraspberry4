'use strict';

const url0="http://10.0.0.34:8081/?action=stream";
let cameraWorks = false;
camera0.crossOrigin = "Anonymous";


let chosenColor = 'red';
let colorDiff = parseInt(document.getElementById('colorDiffElem').value);
let minChosenColorCount = parseInt(document.getElementById('minChosenColorCountElem').value);
let processingImage = false;

// the reason for multiple 'Left's or 'Right's is because originally,
// the 'isC' was split into 'isL' and 'isR'.  but having a dividing line
// down the center was bad - robot would oscillate
// so i joined the center Left and center Right into a single area.
let isLLL = false;// is Left Left Left
let isLL  = false;// is Left Left
let isC   = false;// is Center
let isRR  = false;// is Right Right
let isRRR = false;// is Right Right Right

const maxNumRotationCommandsToSendInOneStream = 80; // aprox 2secs worth of drive commands
let currentNumRotationCommandsSentInStream = 0;


const doSwitchToGamepadDrive = () => {
    location.href = "gamepaddrive.html";
    clearTouchEvents();
}

const doSwitchToTouchDrive = () => {
    location.href = "touchdrive.html";
}



const tryCamera = (url) => {
    setTimeout(() => {
        fetch(url)
        .then(result => {
            if (!cameraWorks) {
                camera0.src = url;
                messages.innerHTML = 'Checked Camera Feed Ok';
            }
            if (errors.innerHTML === 'No Camera Feed') {
                errors.innerHTML = '';
            }
            cameraWorks = true;
        })
        .catch(error => {
            errors.innerHTML = 'No Camera Feed';
            if (messages.innerHTML === 'Checked Camera Feed Ok') {
                messages.innerHTML = '';
            }
            cameraWorks = false;
            tryCamera(url);
        });
    },1000);
}




const doChooseColor = (color) => {
    chosenColor = color;
}

const doSetColorDiff = (slider) => {
    colorDiff = parseInt(slider.value);
}

const doSetMinChosenColorCount = (slider) => {
    minChosenColorCount = parseInt(slider.value);
}


const rotate = (x,directionString) => {

    console.log('Rotating.....' + directionString + ' --------------');

    warnings.innerHTML = 'Rotating ' + directionString + ' ....';

    if (dataReceivedFromNodeJsServer !== undefined && (dataReceivedFromNodeJsServer.speed1 < 1 && dataReceivedFromNodeJsServer.speed2 < 1)) {
        processXandY(x,0,0); 
    }
}



const rotateLeft = (x) => {
    rotate(-x,'Left');
}

const rotateRight = (x) => {
    rotate(x,'Right');
}


const rotateTowardWhichAreasMatch = () => {

    //printWhichAreasMatch();

    if (isC) {
        return;
    }

    //////////////////////////////////////////////////
    // since we are handling the center condition first
    // (code immediately above here), we do not have to
    // consider it anymore.
    //////////////////////////////////////////////////
 
    //extreme left side, spans 1 area, almost out of view, time to rotate very fast
    if (isLLL && !isLL && !isRR && !isRRR) {
        rotateLeft(0.55);
    }

    //very left side, spans 2 areas, rotate fast
    if (isLLL && isLL && !isRR && !isRRR) {
        rotateLeft(0.5);
    }

    //left side, spans 1 area, rotate medium
    if (!isLLL && isLL && !isRR && !isRRR) {
        rotateLeft(0.45);
    }


    //right side, spans 1 area, rotate medium
    if (!isLLL && !isLL && isRR && !isRRR) {
        rotateRight(0.45);
    }

    //very right side, spans 2 areas, rotate fast
    if (!isLLL && !isLL && isRR && isRRR) {
        rotateRight(0.5);
    }

    //extreme right side, spans 1 area, almost out of view, time to rotate very fast
    if (!isLLL && !isLL && !isRR && isRRR) {
        rotateRight(0.55);
    }

}


const printWhichAreasMatch = () => {
    console.log(isLLL, isLL, isC, isRR, isRRR);
}

const clearWhichAreasMatch = () => {
    isLLL = false;
    isLL  = false;
    isC   = false;
    isRR  = false;
    isRRR = false;
}


const setWhichAreasMatch = (area) => {
    switch (area) {
        case 'LLL': isLLL = true; break;
        case 'LL' : isLL  = true; break;
        case 'C'  : isC   = true; break;
        case 'RR' : isRR  = true; break;
        case 'RRR': isRRR = true; break;
    }
}

const processImageColorOnOffScreenCanvas = (whichArea,canv,x,y) => {
    let chosenColorCount = 0;
    let offScrnCtx = canv.offscreenCanvas.getContext('2d');
    let imgWidth  = (whichArea === 'C' ? 320 : 160);
    let canvWidth = (whichArea === 'C' ? 160 : 80); 
    offScrnCtx.drawImage(camera0,x,y,imgWidth,240,0,0,canvWidth,120);

    let imgData = offScrnCtx.getImageData(0,0,canvWidth,120);
    let data = imgData.data;
    for (let i=0; i<data.length; i+=4) {
        let r = data[i];
        let g = data[i+1];
        let b = data[i+2];

        switch (chosenColor) {
            case 'red':
                if (r>g+colorDiff && r>b+colorDiff) {
                    data[i]   = 255;
                    data[i+1] = 0;
                    data[i+2] = 0;
                    chosenColorCount++;
                }
                break;
            case 'green':
                if (g>r+colorDiff && g>b+colorDiff) {
                    data[i]   = 0;
                    data[i+1] = 255;
                    data[i+2] = 0;
                    chosenColorCount++;
                }
                break;
            case 'blue':
                if (b>r+colorDiff && b>g+colorDiff) {
                    data[i]   = 0;
                    data[i+1] = 0;
                    data[i+2] = 255;
                    chosenColorCount++;
                }
                break;
        }
    }

    let areaCountMultiplier = whichArea==='C'?2:1; // since the center areas are bigger, we need to adjust what is the minimum
    if (chosenColorCount>minChosenColorCount * areaCountMultiplier) {
        switch (chosenColor) {
            case 'red':
                offScrnCtx.rect(0,0,canvWidth,120);
                offScrnCtx.fillStyle = 'red';
                offScrnCtx.fill();
                setWhichAreasMatch(whichArea);
                break;
            case 'green':
                offScrnCtx.rect(0,0,canvWidth,120);
                offScrnCtx.fillStyle = 'green';
                offScrnCtx.fill();
                setWhichAreasMatch(whichArea);
                break;
            case 'blue':
                offScrnCtx.rect(0,0,canvWidth,120);
                offScrnCtx.fillStyle = 'blue';
                offScrnCtx.fill();
                setWhichAreasMatch(whichArea);
                break;
        }
    } else {
        offScrnCtx.putImageData(imgData,0,0);
    }
 
}

const processPartOfImage = (whichArea, canv,x,y) => {
    processImageColorOnOffScreenCanvas(whichArea, canv,x,y);
    canv.getContext('2d').drawImage(canv.offscreenCanvas,0,0);
}


const mainLoop = () => {

    setInterval(() => {

        if (!processingImage) {

            processingImage = true;
/*
            processPartOfImage('LLL',canvTLLL,0,0);
            processPartOfImage('LL', canvTLL,160,0);
            processPartOfImage('C',  canvTC,2*160,0);
            processPartOfImage('RR', canvTRR,4*160,0);
            processPartOfImage('RRR',canvTRRR,5*160,0);

            processPartOfImage('LLL',canvLLL,0,240);
            processPartOfImage('LL', canvLL,160,240);
            processPartOfImage('C',  canvC,2*160,240);
            processPartOfImage('RR', canvRR,4*160,240);
            processPartOfImage('RRR',canvRRR,5*160,240);

            processPartOfImage('LLL',canvBLLL,0,2*240);
            processPartOfImage('LL', canvBLL,160,2*240);
            processPartOfImage('C',  canvBC,2*160,2*240);
            processPartOfImage('RR', canvBRR,4*160,2*240);
            processPartOfImage('RRR',canvBRRR,5*160,2*240);
*/
            rotateTowardWhichAreasMatch();

            clearWhichAreasMatch();

            processingImage = false;
        }

    },20);
}


const createOffScreenCanvas = (mainCanvas, center) => {
        mainCanvas.offscreenCanvas = document.createElement('canvas');
        mainCanvas.offscreenCanvas.width = (center==='C'?160:80);
        mainCanvas.offscreenCanvas.height = 120;
}

const startMainLoop = () => {

    if (cameraWorks) {
        console.log('starting main loop');

        createOffScreenCanvas(canvTLLL); 
        createOffScreenCanvas(canvTLL); 
        createOffScreenCanvas(canvTC,'C'); 
        createOffScreenCanvas(canvTRR); 
        createOffScreenCanvas(canvTRRR); 
        createOffScreenCanvas(canvLLL); 
        createOffScreenCanvas(canvLL); 
        createOffScreenCanvas(canvC,'C'); 
        createOffScreenCanvas(canvRR); 
        createOffScreenCanvas(canvRRR); 
        createOffScreenCanvas(canvBLLL); 
        createOffScreenCanvas(canvBLL); 
        createOffScreenCanvas(canvBC,'C'); 
        createOffScreenCanvas(canvBRR); 
        createOffScreenCanvas(canvBRRR); 
        mainLoop();
        return;
    }

    setTimeout(() => {
        console.log('waiting to start main loop');
        startMainLoop();
    },50);

}



tryCamera(url0);
startMainLoop();
