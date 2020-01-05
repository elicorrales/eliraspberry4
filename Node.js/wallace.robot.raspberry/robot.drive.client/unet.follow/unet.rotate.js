'use strict';

const url0="http://10.0.0.34:8082/?action=stream";
let cameraWorks = false;
camera0.crossOrigin = "Anonymous";

let mainWidth = camera0.width;
let mainHeight = camera0.height;

let isCameraImageLoaded = false;
let isModelLoading = false;
let isModelReady = false;
let processingImage = false;

let img;
let segImg;
let canvas;
let uNet;
let segmented = false;


debugger;

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
            console.log(error);
            errors.innerHTML = 'No Camera Feed';
            if (messages.innerHTML === 'Checked Camera Feed Ok') {
                messages.innerHTML = '';
            }
            cameraWorks = false;
            tryCamera(url);
        });
    },1000);
}

/*
const processSegImg = () => {

    segImg.loadPixels();

    for (let i=0; i<segImg.pixels.length; i+=4) {
        let red = segImg.pixels[i];
        let grn = segImg.pixels[i+1];
        let blu = segImg.pixels[i+2];
        let sum = red + grn + blu;
        if (sum == 0) { segImg.pixels[i+3] = 0; }
        else {
            segImg.pixels[i]   = 255;
            segImg.pixels[i+1] = 0;
            segImg.pixels[i+2] = 0;
        }

    } 

    segImg.updatePixels();

}
*/

const handleModelSegmentedResult = (error, result) => {
    if (error) {
        console.log(error);
        errors.innerHTML = 'handleModelSegmentedResult error: ' + error;
        return;
    }

    if (result === undefined) {
        errors.innerHTML = 'handleModelSegmentedResult error: model result is undefined';
        return;
    }

    let canv = result.image.canvas;
    let imageData = result.image.canvas.getContext('2d').getImageData(0,0,mainWidth,mainHeight);
    segCanv.getContext('2d').putImageData(imageData,0,0);
    //processSegImg();

    segmented = true;

    uNet.segment(camera0,handleModelSegmentedResult);
}


const modelReady = () => {
    isModelReady = true;
    uNet.segment(camera0,handleModelSegmentedResult);
}

const loadModel = () => {
        uNet = ml5.uNet('face',modelReady);
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
            //rotateTowardWhichAreasMatch();

            //clearWhichAreasMatch();

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

    if (!isModelLoading && isCameraImageLoaded) {
        isModelLoading = true;
        loadModel();
    }

    if (cameraWorks && isModelReady && isCameraImageLoaded) {

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


camera0.onload = () => {
    isCameraImageLoaded = true;
};



startMainLoop();


