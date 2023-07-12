const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require("electron-squirrel-startup")) {
  app.quit();
}

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    show: false,
    icon: "./resources/app/src/assets/square-smt-logo.ico",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
    },
  });
  var splash = new BrowserWindow({
    icon: "./resources/app/src/assets/square-smt-logo.ico",
    width: 650,
    height: 450,
    transparent: true,
    frame: false,
    alwaysOnTop: false,
    resizable: false,
    
  });

  splash.loadFile("./src/splash.html");
  splash.center();
  setTimeout(function () {
    splash.close();
    mainWindow.center();
    mainWindow.show();
    mainWindow.maximize();
  }, 11045);

  // and load the index.html of the app.
  mainWindow.loadFile(path.join(__dirname, "index.html"));
  mainWindow.setMenuBarVisibility(false);
  // Open the DevTools.
  // mainWindow.webContents.openDevTools();
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on("ready", createWindow);

app.on('ready', () => {
  updateApp = require('update-electron-app');

  updateApp({
      updateInterval: '1 hour',
      notifyUser: true
  });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

ipcMain.on("getImages", (event) => {
  const imagePaths = fs
    .readdirSync(path.join("result-images"))
    .filter((file) => file.endsWith(".jpg") || file.endsWith(".png"))
    .map((file) => path.join("result-images", file));

  event.reply("imagePaths", imagePaths);
});

ipcMain.on("get-path", (event) => {
  const path = require("path");
  const fs = require("fs");
  const imagePaths = fs.readdirSync(path.join("result-images"));
  ipcMain.send("get-path-reply", imagePaths);
});

app.on("activate", () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.
