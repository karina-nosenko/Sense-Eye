const { app, BrowserWindow } = require('electron')
const fs = require('fs');
const { contextBridge, ipcRenderer } = require('electron');

const folderPath = `${__dirname}/../../output_videos/`;

contextBridge.exposeInMainWorld('myAPI', {
  getOutputVideos: () => {
    const output_videos = []
    fs.readdir(folderPath, (err, files) => {
      if (err) {
        console.log('Error reading folder:', err);
        return;
      }

      files.forEach(file => {
        output_videos.push(file);
      });
    })
    .then(() => {
      ipcRenderer.send('getOutputVideos', output_videos);
    }); 
  }
});


function createWindow () {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true
    }
  })

  win.loadFile('index.html')
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
