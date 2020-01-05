'use strict';

const MY_CAM_URL ="http://10.0.0.34:8082/?action=stream";
const MY_WIDTH = 240;
const MY_HEIGHT = 180;
const MY_THIRD  = MY_WIDTH/3;
const MY_2THIRD = 2*(MY_WIDTH/3);

let cameraWorks = false;
let camera0 = new Image(MY_WIDTH, MY_HEIGHT);

camera0.crossOrigin = "Anonymous";

let mainWidth = camera0.width;
let mainHeight = camera0.height;

let isCameraImageLoaded = false;
let isModelLoading = false;
let isModelReady = false;

let bodyPix;

let minColorCount = parseInt(document.getElementById('minColorCountElem').value);

const doSetMinColorCount = (slider) => {
    minColorCount = parseInt(slider.value);
}

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


const isWhiteEnough = (data) => {
    let whiteCount = 0;
    for (let i=0; i<data.length; i+=4) {
        //if (data[i] > 0 || data[i+1] > 0 || data[i+2] > 0) {
        if (data[i+3] > 0) {
            whiteCount++;
        }
    }
    if (whiteCount > minColorCount) {
        return true;
    } else {
        return false;
    }
}

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

    result.maskBackground.loadPixels();
    let ctx = result.maskBackground.canvas.getContext('2d');
    //let ctx = result.maskBackground.drawingContext;
//    let full = ctx.getImageData(0, 0, MY_WIDTH, MY_HEIGHT);
    let left = ctx.getImageData(0, 0, MY_THIRD, MY_HEIGHT);
    let right= ctx.getImageData(MY_2THIRD, 0, MY_THIRD, MY_HEIGHT);

    leftCanv.getContext('2d').putImageData(left,0,0);
//    fullCanv.getContext('2d').putImageData(full,0,0);
    rightCanv.getContext('2d').putImageData(right,0,0);

/*
    if (isWhiteEnough(full.data)) {
        messages.innerHTML = 'FULL';
    }
*/
    if (isWhiteEnough(left.data)) {
        messages.innerHTML = 'LEFT';
    } else {
        messages.innerHTML = '';
    }

    if (isWhiteEnough(right.data)) {
        messages.innerHTML = 'RIGHT';
    } else {
        messages.innerHTML = '';
    }

/*
    try {
        segCanvParent.removeChild(segCanvParent.lastChild);
    } catch (e) {}
    segCanvParent.appendChild(result.maskBackground.canvas);
*/

    bodyPix.segment(camera0,handleModelSegmentedResult);
}


const modelReady = () => {
    isModelReady = true;
    console.log('Model Loaded... starting to segment...');
    bodyPix.segment(camera0,handleModelSegmentedResult);
}

const loadModel = () => {
    console.log('Loading Model...');
    bodyPix = ml5.bodyPix(modelReady);
}



const startMainLoop = () => {

    // this happens once, after camera image is loaded/streaming
    if (!isModelLoading && isCameraImageLoaded) {
        isModelLoading = true;
        loadModel();
    }

    // this happens once, after all init is complete - we're outta here
    if (cameraWorks && isModelReady && isCameraImageLoaded) {

        console.log('starting main program...');

        return;
    }

    // this keeps happening until the above exits this function
    setTimeout(() => {
        console.log('waiting to start main program');
        startMainLoop();
    },50);

}



tryCamera(MY_CAM_URL );


camera0.onload = () => {
    isCameraImageLoaded = true;
};



startMainLoop();


