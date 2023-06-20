let {PythonShell} = require('python-shell')
const {ipcRenderer} = require('electron')


// ipcRenderer.send('get-path', 'ping')

path = require('path');
const fs = require('fs');
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
// let pyshell = new PythonShell("./resources/app/engine/upload_multiple.py", options_py);  // for when py is converted to exe

let pyshell = new PythonShell("./resources/app/src/upload_multiple.exe", options_exe);  // for when py is converted to exe
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

        if (typeofmessage == 'fd') {
            console.log(message);
            console.log('stitched image saved');
            const strippedPath = message.replace(/^fd:/, '');
            let outputMessage = document.getElementById('file-directory');
            outputMessage.innerHTML = "Stitched image will be saved at: " + strippedPath;
        }
        
        if (typeofmessage == 'tn') {
            tn=messagecode;
        }

        if (typeofmessage == 'cd') {
            let cd=messagecode;
            let percentageDone = cd/tn*100;
            console.log(percentageDone);
            var progressBar = document.getElementById("myProgress");
            progressBar.value = percentageDone;
            document.getElementById('python-output').innerHTML = cd + ' of ' + tn + ' images processed';
        }

        if (typeofmessage == 'er') {
            if (messagecode==0) {
                console.log(messagecode)
                console.log('no stitching needed')
                // let outputMessage = document.getElementById('python-output');
                // outputMessage.innerHTML = 'No stitching needed'; 
                // console.log(currentPath);
            }
            if (messagecode==1) {
                console.log(messagecode)
                console.log('needs stitching')
                window.location.href = 'autostitch-manualstitcher.html';                 // Redirect to autostitcher-maualstitcher HTML file
            }
        }
    });
    
    // end the input stream and allow the process to exit
    pyshell.end(function (err,code,signal) {
    if (err) throw err;
    console.log('The exit code was: ' + code);
    console.log('The exit signal was: ' + signal);
    console.log('finished');
    // Make the button visible
    // var button = document.getElementById('myButton');
    // button.style.display = 'block';
    });
}