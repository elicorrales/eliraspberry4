'use strict';

const url0="http://10.0.0.34:8082/?action=stream";
let cameraWorks = false;
camera0.crossOrigin = "Anonymous";


let chosenColor = 'red';
let colorDiff = parseInt(document.getElementById('colorDiffElem').value);
let minChosenColorCount = parseInt(document.getElementById('minChosenColorCountElem').value);
let processingImage = false;

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


const doSwitchToGamepadDrive = () => {
    location.href = "gamepaddrive.html";
    clearTouchEvents();
}

const doSwitchToTouchDrive = () => {
    location.href = "touchdrive.html";
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



const processImageColorOnOffScreenCanvas = (canv,x,y) => {
    let chosenColorCount = 0;
    let offScrnCtx = canv.offscreenCanvas.getContext('2d');
    offScrnCtx.drawImage(camera0,x,y,160,240,0,0,80,120);

    let imgData = offScrnCtx.getImageData(0,0,80,120);
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

    if (chosenColorCount>minChosenColorCount) {
        switch (chosenColor) {
            case 'red':
                offScrnCtx.rect(0,0,80,120);
                offScrnCtx.fillStyle = 'red';
                offScrnCtx.fill();
                break;
            case 'green':
                offScrnCtx.rect(0,0,80,120);
                offScrnCtx.fillStyle = 'green';
                offScrnCtx.fill();
                break;
            case 'blue':
                offScrnCtx.rect(0,0,80,120);
                offScrnCtx.fillStyle = 'blue';
                offScrnCtx.fill();
                break;
        }
    } else {
        offScrnCtx.putImageData(imgData,0,0);
    }
 
}

const processPartOfImage = (canv,x,y) => {
    processImageColorOnOffScreenCanvas(canv,x,y);
    canv.getContext('2d').drawImage(canv.offscreenCanvas,0,0);
}


const mainLoop = () => {
    setInterval(() => {
        if (!processingImage) {

            processingImage = true;

            processPartOfImage(canvTLLL,0,0);
            processPartOfImage(canvTLL,160,0);
            processPartOfImage(canvTL,2*160,0);
            processPartOfImage(canvTR,3*160,0);
            processPartOfImage(canvTRR,4*160,0);
            processPartOfImage(canvTRRR,5*160,0);

            processPartOfImage(canvLLL,0,240);
            processPartOfImage(canvLL,160,240);
            processPartOfImage(canvL,2*160,240);
            processPartOfImage(canvR,3*160,240);
            processPartOfImage(canvRR,4*160,240);
            processPartOfImage(canvRRR,5*160,240);

            processPartOfImage(canvBLLL,0,2*240);
            processPartOfImage(canvBLL,160,2*240);
            processPartOfImage(canvBL,2*160,2*240);
            processPartOfImage(canvBR,3*160,2*240);
            processPartOfImage(canvBRR,4*160,2*240);
            processPartOfImage(canvBRRR,5*160,2*240);

            processingImage = false;
        }
    },20);
}


const createOffScreenCanvas = (mainCanvas) => {
        mainCanvas.offscreenCanvas = document.createElement('canvas');
        mainCanvas.offscreenCanvas.width = 80;
        mainCanvas.offscreenCanvas.height = 120;
}

const startMainLoop = () => {

    if (cameraWorks) {
        console.log('starting main loop');

        createOffScreenCanvas(canvTLLL); 
        createOffScreenCanvas(canvTLL); 
        createOffScreenCanvas(canvTL); 
        createOffScreenCanvas(canvTR); 
        createOffScreenCanvas(canvTRR); 
        createOffScreenCanvas(canvTRRR); 
        createOffScreenCanvas(canvLLL); 
        createOffScreenCanvas(canvLL); 
        createOffScreenCanvas(canvL); 
        createOffScreenCanvas(canvR); 
        createOffScreenCanvas(canvRR); 
        createOffScreenCanvas(canvRRR); 
        createOffScreenCanvas(canvBLLL); 
        createOffScreenCanvas(canvBLL); 
        createOffScreenCanvas(canvBL); 
        createOffScreenCanvas(canvBR); 
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
