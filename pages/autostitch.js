let {PythonShell} = require('python-shell')
const { ipcRenderer } = require('electron');

let pyshell = new PythonShell('engine/upload_multiple.py');

pythonRunner = () => {
    // sends a message to the Python script via stdin
    pyshell.send('hello');
    console.log('hello');
    pyshell.on('message', function (message) {
    // received a message sent from the Python script (a simple "print" statement)
    console.log(message);
    });

    // end the input stream and allow the process to exit
    pyshell.end(function (err,code,signal) {
    if (err) throw err;
    console.log('The exit code was: ' + code);
    console.log('The exit signal was: ' + signal);
    console.log('finished');
    // document.getElementById('python-output').innerHTML = code;
    });
    
}