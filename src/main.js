const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    show:false,
    icon: './assets/smt.ico',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
    },
  });
  var splash = new BrowserWindow({ 
    icon: './assets/smt.ico',
    width: 640, 
    height: 358, 
    transparent: true, 
    frame: false, 
    alwaysOnTop: false, 
    resizable: false
  });
  
  splash.loadFile('splash.html');
  splash.center();
  setTimeout(function () {
    splash.close();
    mainWindow.center();
    mainWindow.show();
    mainWindow.maximize();
  }, 9000);

  // and load the index.html of the app.
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`))
    
  }
  mainWindow.setMenuBarVisibility(false);
 
  // Open the DevTools.
  // mainWindow.webContents.openDevTools();
  
  
};




// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);


ipcMain.on('saveFiles', (event, files) => {
  console.log('saveFiles... running');
  const destinationPath = path.join(__dirname, 'saved_files');
  console.log(destinationPath);
  if (!fs.existsSync(destinationPath)) {
    fs.mkdirSync(destinationPath);
  }

  files.forEach(file => {
    const filePath = path.join(destinationPath, file.name);
    fs.copyFileSync(file.path, filePath);
  });

  event.sender.send('filesSaved');
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.
