

function createVideoWindow(videoUrl) {
    const newWindow = window.open("", "", "width=600,height=400");
    newWindow.document.body.innerHTML = `
        <video width="100%" height="100%" controls autoplay>
            <source src="${videoUrl}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    `;
}


function getCurrentDirAbsolutePath() {
    let pathArray = window.location.pathname.split('/');
    pathArray.pop();
    let dirPath = window.location.origin + pathArray.join('/');
    return dirPath;
}



createVideoWindow(`/home/karina/FinalProject/SenseEye/output_videos/2023-03-19 22:21:39.mp4`)