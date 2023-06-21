let {PythonShell} = require('python-shell')
const {shell} = require('electron') // deconstructing assignment
const fs = require('fs');
const path = require('path');
const { clipboard, nativeImage } = require('electron');
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
      var progressBarParent = document.getElementById("progress-bar-parent");
      progressBarParent.classList.remove("d-none");
      console.log(message);
      const [typeofmessage, messagecode] = message.split(":");


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
          outputMessage = document.getElementById('python-output');
          outputMessage.classList.remove("d-none");
          outputMessage.innerHTML = '<i class="bi bi-info-circle-fill"></i> ' + tn + ' : Images Selected for Stitching';
          
      }

      if (typeofmessage == 'cd') {
          cd=messagecode;
          let percentageDone = cd/tn*100;
          console.log(percentageDone);
          var progressBar = document.getElementById("progress-bar");
          progressBar.setAttribute("aria-valuenow", percentageDone);
          progressBar.style.width = percentageDone + "%";
          // progressBar.value = percentageDone;
          outputMessage = document.getElementById('python-output');
          // outputMessage.classList.replace("alert-info", "alert-success");
          outputMessage.innerHTML = '<i class="bi bi-info-circle-fill"></i>' + cd + ' of ' + tn + ' Images Processed';
      }

      if (typeofmessage == 'er') {
          if (messagecode==0) {
              console.log(messagecode)
              console.log('no stitching needed')
              // console.log(fd);
              var fileOpenButton = document.getElementById('file-open-button');
              var fileCopyButton = document.getElementById('copy-path-button');
              outputMessage = document.getElementById('python-output');
              outputMessage.classList.replace("alert-info", "alert-success");
              outputMessage.innerHTML = '<i class="bi bi-check-lg"></i> All Images Stitched Successfully!';
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

copyImageToClipBoard = () => {
  finalImagePath = localStorage.getItem('finalImagePath');
  const image = nativeImage.createFromPath(finalImagePath);
  clipboard.writeImage(image);
  var fileCopyButton = document.getElementById('copy-path-button');
  fileCopyButton.innerHTML = '<i class="bi bi-clipboard-check"></i> Copy Image to Clipboard';
  setTimeout(function(){
      fileCopyButton.innerHTML = '<i class="bi bi-clipboard"></i> Copy Image to Clipboard';
  },1000);
}

cancelProcess = () => {
    pyshell.kill();
    console.log('process cancelled');
}
// Tour
// Initialize the Shepherd.js Tour
const Shepherd = require('shepherd.js')
let tour = null;


function startTour() {
  if (tour) {
    var fileOpenButton = document.getElementById('file-open-button');
    var fileCopyButton = document.getElementById('copy-path-button');
    fileOpenButton.style.display = 'block';
    fileCopyButton.style.display = 'block';
    tour.start();
  }
}

  tour = new Shepherd.Tour({
    useModalOverlay: true,
  });

  tourCancelAction = () => {
    tour.cancel();
    console.log('tour cancelled');
    var fileOpenButton = document.getElementById('file-open-button');
    var fileCopyButton = document.getElementById('copy-path-button');
    fileOpenButton.style.display = 'none';
    fileCopyButton.style.display = 'none';
  }

  steps=[{
    id: 'step1',
   title: 'Upload Files',
    text: 'Click this button to upload your images to the automatic stitcher.',
    attachTo: {
      element: '#uploadtour',
      on: 'right',
    },
    classes: 'step-class',
    buttons: [
      {
        text: 'Next',
        action: tour.next,
      },
      {
        text: 'Exit Tour',
        action: tourCancelAction
      },
    ],
  },
  {
    id: 'step2',
    title: 'Copy Image',
    text: 'After the image is stitched, this button will be shown,Click this to Copy the saved image to your clipboard.',
    attachTo: {
      element: '#copy-path-button',
      on: 'right',
    },
    classes: 'step-class',
    buttons: [
      {
        text: 'Next',
        action: tour.next,
      },
      {
        text: 'Exit Tour',
        action: tourCancelAction
      },
    ],
  },
  {
    id: 'step3',
    title: 'Open Folder',
    text: 'After the image is stitched, this button will be shown,Click this to open the folder where the imaegs are saved.',
    attachTo: {
      element: '#file-open-button',
      on: 'right',
    },
    classes: 'step-class',
    buttons: [
      {
        text: 'Next',
        action: tour.next,
      },
      {
        text: 'Exit Tour',
        action: tourCancelAction,
      },
    ],
  },
  {
    id: 'step4',
    title: 'Go Back',
    text: 'Click this  button to Go back to Homepage.',
    attachTo: {
      element: '#backtour',
      on: 'right',
    },
    classes: 'step-class',
    buttons: [
      {
        text: 'Next',
        action: tour.next,
      },
      {
        text: 'Exit Tour',
        action: tourCancelAction
      },
    ],
  },
  {
    id: 'step5',
    title: 'Tour Button',
    text: 'In case you forget the button function, you can click this button again anytime and it will guide you through all the buttons.',
    attachTo: {
      element: '#tourtour',
      on: 'top',
    },
    classes: 'step-class',
    buttons: [
      {
        text: 'Exit Tour',
        action: tourCancelAction
      },
    ],
  }
];

  tour.addSteps(steps);

  tour.defaultStepOptions = {
    classes: 'shepherd-theme-arrows',
    scrollTo: true,
    buttons: [
      {
        text: 'Next',
        action: tour.next,
      },
      {
        text: 'Exit Tour',
        action: tourCancelAction
      },
    ],
  };
