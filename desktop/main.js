const { app, BrowserWindow } = require('electron')
const exec = require('child_process').exec;
const { spawn } = require('child_process');

function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    })
    console.log("hello")
    const scriptPath = 'C:/Sense-Eye/main.py';
    const directoryPath = 'C:/Sense-Eye';

    const pythonProcess = spawn('python', [scriptPath], { cwd: directoryPath });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
    ////////////////////////////////////////////////////////////
    exec('npm run dev', { cwd: 'C:/Sense-Eye/RecommendationsUnit/' }, (error, stdout, stderr) => {
        if (error) {
          console.error(`Error: ${error.message}`);
          return;
        }
        if (stderr) {
          console.error(`stderr: ${stderr}`);
          return;
        }
        console.log(`stdout: ${stdout}`);
      });

    ////////////////////////////////////////////////////////////
    const scriptPath2 = 'C:/Sense-Eye/ImageProcessingUnit/main.py';
    const directoryPath2 = 'C:/Sense-Eye/ImageProcessingUnit';

    const pythonProcess2 = spawn('python', [scriptPath2], { cwd: directoryPath2 });

    pythonProcess2.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    pythonProcess2.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess2.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
    /////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////
    win.loadFile('index.html')
    console.log("biii")

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
