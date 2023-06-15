let {PythonShell} = require('python-shell')
const { ipcRenderer } = require('electron');

let options_exe = {
    mode : 'text',
    pythonPath: 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
    // pythonOptions: ['-u'], // get print results in real-time
    scriptPath: 'engine/dist/upload_multiple/',
    // args: ['value1', 'value2', 'value3']
};

let options_py = {
    mode : 'text',
    // pythonPath: 'C:\\Users\\james\\AppData\\Local\\Programs\\Python\\Python39\\python.exe',
    pythonOptions: ['-u'], // get print results in real-time
    scriptPath: 'engine/',
};

// possible type of messages passed by python code to javascript
// tn = total number of images sent to python
// cd = current number of images currently processed
// er = error message to see if manual stitching is required

// let pyshell = new PythonShell('upload_multiple.exe', options_exe);  // for when py is converted to exe
let pyshell = new PythonShell('upload_multiple.py', options_py);

  
pythonRunner = () => {
    // sends a message to the Python script via stdin
    pyshell.send('hello');
    // console.log('hello');
    pyshell.on('message', function (message) {
        var fsLoadingMessage = document.getElementById("fs-loading-message");
        fsLoadingMessage.style.display = "none";
        var progressBar = document.getElementById('myProgress');
        progressBar.style.display = 'block';

        console.log(message);
        const [typeofmessage, messagecode] = message.split(":");
        
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
    var button = document.getElementById('myButton');
    button.style.display = 'block';
    });
}
pythonRunner()
