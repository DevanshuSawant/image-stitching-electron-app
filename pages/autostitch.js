let {PythonShell} = require('python-shell')
const { ipcRenderer } = require('electron');
let pyshell = new PythonShell('engine/upload_multiple.py');
console.log('hellos');
pythonRunner = () => {
    // sends a message to the Python script via stdin
    pyshell.send('hello');
    // console.log('hello');
    pyshell.on('message', function (message) {
        // received a message sent from the Python script (a simple "print" statement)
        console.log(message);
        if (message==0) {
            console.log(message)
            console.log('no stitching needed')
        }
        
        if (message==1) {
            console.log(message)
            console.log('needs stitching')

            // Redirect to autostitcher-maualstitcher HTML file
            window.location.href = 'autostitch-manualstitcher.html';
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

    // document.getElementById('python-output').innerHTML = code;
    });
    // return {message}
}
pythonRunner()
// if (message==0) {
//     console.log(message)
//     console.log('no stitching needed')
// }

// if (message==1) {
//     console.log(message)
//     console.log('needs stitching')
//     // Redirect to autostitcher-maualstitcher HTML file
//     window.location.href = 'autostitcher-manualstitcher.html';
// }

