let {PythonShell} = require('python-shell')
const {shell} = require('electron') // deconstructing assignment
const fs = require('fs');
const path = require('path');
// const path = require('path');
// currentPath = path.join(__dirname, 'result-images');


let options_exe = {
    mode : 'text',
    pythonPath: 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
    // scriptPath: 'src/',
};

let options_py = {
    mode : 'text',
    pythonOptions: ['-u'], // get print results in real-time
    // scriptPath: 'engine/',
};

// possible type of messages passed by python code to javascript
// tn = total number of images sent to python
// cd = current number of images currently processed
// er = error message to see if manual stitching is required
// fd = file directory of the stitched image
let pyshell = new PythonShell("./src/engine/upload_multiple.py", options_py);  // for when py is converted to exe

// let pyshell = new PythonShell("./resources/app/src/upload_multiple.exe", options_exe);  // for when py is converted to exe
// let pyshell = new PythonShell('upload_multiple.py', options_py);
fileNames = [];
var imageUpload = document.getElementById('image-upload');
imageUpload.addEventListener('change', function(event) {
    var files = event.target.files;
    for (var i = 0; i < files.length; i++) {
        fileNames.push(files[i].path);
    }
    pyshell.send(fileNames);
    console.log(fileNames);
    
    pythonRunner();

});


  
pythonRunner = () => {
    // console.log(pyPaths);

    pyshell.on('message', function (message) {
        var progressBar = document.getElementById('myProgress');
        progressBar.style.display = 'block';

        console.log(message);
        const [typeofmessage, messagecode] = message.split(":");

        let fd=""

        if (typeofmessage == 'fd') {
            console.log(message);
            console.log('stitched image saved');
            let strippedPath = message.replace(/^fd:/, '');
            // let outputMessage = document.getElementById('file-directory');
            // outputMessage.innerHTML = "Stitched image will be saved at: " + strippedPath;
            // fd = path.join(strippedPath, 'image1.png');
            localStorage.setItem('finalImageFolder', strippedPath);
        }
        
        if (typeofmessage == 'tn') {
            tn=messagecode;
            document.getElementById('python-output').innerHTML = tn + ': Images Uploaded';
            
        }

        if (typeofmessage == 'cd') {
            let cd=messagecode;
            let percentageDone = cd/tn*100;
            console.log(percentageDone);
            var progressBar = document.getElementById("myProgress");
            progressBar.value = percentageDone;
            document.getElementById('python-output').innerHTML = cd + ' of ' + tn + ' Images Processed';
        }

        if (typeofmessage == 'er') {
            if (messagecode==0) {
                console.log(messagecode)
                console.log('no stitching needed')
                console.log(fd);
                var fileOpenButton = document.getElementById('file-open-button');
                var fileCopyButton = document.getElementById('copy-path-button');
                fileOpenButton.style.display = 'block';
                fileCopyButton.style.display = 'block';
                finalImagePath = localStorage.getItem('finalImagePath');
                shell.openPath(finalImagePath);
            }
            if (messagecode==1) {
                console.log(messagecode)
                console.log('needs stitching')
                window.location.href = 'autostitch-manualstitcher.html';                 // Redirect to autostitcher-maualstitcher HTML file
            }
        }
        if (typeofmessage == 'finished') {
            let strippedPath = message.replace(/^finished:/, '');
            // shell.openPath(strippedPath);
            localStorage.setItem('finalImagePath', strippedPath);
        }
    });
    
    // end the input stream and allow the process to exit
    pyshell.end(function (err,code,signal) {
    if (err) throw err;
    console.log('The exit code was: ' + code);
    console.log('The exit signal was: ' + signal);
    console.log('finished');
    });
}

showInFolder = () => {
    let finalImageFolder = localStorage.getItem('finalImageFolder');
    shell.openPath(finalImageFolder);
}

copyFilePath = () => {
    let finalImageFolder = localStorage.getItem('finalImageFolder');
    console.log(finalImageFolder);
    navigator.clipboard.writeText(finalImageFolder);
}


// Tour
  // Initialize the Shepherd.js Tour
  document.addEventListener('DOMContentLoaded', function() {
    const tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: {
        classes: 'shepherd-theme-arrows',
        // scrollTo: true,
        // buttons: [
        //   {
        //     text: 'Next',
        //     action: tour.next,
        //   },
        // ],
      },
      
      steps: [
        {
          id: 'step1',
          attachTo: {
            element: '.boxy .box:nth-child(1) bottom',
            
          },
          title: 'Step 1',
          text: 'This is the first box. It contains a button to clear images.',
        },
        {
          id: 'step2',
          attachTo: {
            element: '.boxy .box:nth-child(2)',
            on: 'bottom',
          },
          title: 'Step 2',
          text: 'This is the second box. It contains a label and an input for uploading files.',
        },
        {
          id: 'step3',
          attachTo: {
            element: '.boxy .box:nth-child(3)',
            on: 'bottom',
          },
          title: 'Step 3',
          text: 'This is the third box. It contains a button to save the image.',
        },
        {
          id: 'step4',
          attachTo: {
            element: '.boxy .box:nth-child(4)',
            on: 'bottom',
          },
          title: 'Step 4',
          text: 'This is the fourth box. It contains a button to go back to the index page.',
        },
        {
          id: 'step5',
          attachTo: {
            element: '#opacityRange',
            on: 'top',
          },
          title: 'Step 5',
          text: 'This is the opacity range slider.',
        },
      ],
    });

    // Start the tour
    tour.start();
  });
