//HTML handling

function goToSimulation(){
    document.getElementById('simulationPage').style.display = 'block';
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('educationPage').style.display = 'none';
    document.getElementById('summaryPage').style.display = 'none';
}

function goToHomepage(){
    document.getElementById('simulationPage').style.display = 'none';
    document.getElementById('educationPage').style.display = 'none';
    document.getElementById('homePage').style.display = 'block';
    document.getElementById('summaryPage').style.display = 'none';
}

function goToEducational(){
    document.getElementById('simulationPage').style.display = 'none';
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('educationPage').style.display = 'block';
    document.getElementById('summaryPage').style.display = 'none';
}

function goToSummary(){
    document.getElementById('simulationPage').style.display = 'none';
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('educationPage').style.display = 'none';
    document.getElementById('summaryPage').style.display = 'block';
}









const apiUrl = "https://musical-space-trout-wrj67r7r4j59h9p9r-5000.app.github.dev/projection";


class golfBall{
    constructor(speed, angle, spin) {
        this.speed = speed;
        this.angle = angle;
        this.spin = spin;
    }
}


const statusBox = document.getElementById('statusBox')
const speedInput = document.getElementById('speedInput')
const angleInput = document.getElementById('angleInput')
const spinInput = document.getElementById('spinInput')
const sendBallButton = document.getElementById('sendBall')
const trajectoryImageContainer = document.getElementById('trajectoryImageContainer')

function updateStatus(message) {
    statusBox.innerText = message;
}

function sendData(){
    const speed = parseFloat(speedInput.value)
    const angle = parseFloat(angleInput.value)
    const spin = parseFloat(spinInput.value)

    const datapacket= new golfBall(speed,angle,spin)


    // Send the request
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Telling the server to expect JSON
        },
        body: JSON.stringify(datapacket)
    })

    
    .then(response => response.json()) // Parse the JSON response from Python

    .catch((error) => {
        
        updateStatus('Error calculating data.',error);
    })
    .then(data => {
        if (!data || !data.trajectory_png) {
        updateStatus('No trajectory data received from server.');
        return;
        }

        updateStatus('Data calculated successfully!');
        const xData = data.x_result
        const yData = data.y_result

        const pngData = data.trajectory_png;

        trajectoryImageContainer.innerHTML = '';
        const img = document.createElement('img');
        img.alt = 'Golf ball trajectory';
        img.src = `data:image/png;base64,${pngData}`;
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        trajectoryImageContainer.appendChild(img);
        updateStatus('Trajectory plotted successfully!');



        /*
        updateStatus('Data calculated successfully!');
        const xData = data.x_result
        const yData = data.y_result
        const pngData = data.trajectory_png;

        trajectoryImageContainer.innerHTML = '';
        const img = document.createElement('img');
        img.alt = 'Golf ball trajectory';
        img.src = `data:image/png;base64,${pngData}`;
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        trajectoryImageContainer.appendChild(img);
        updateStatus('Trajectory plotted successfully!');
        */
    })
    
}

sendBallButton.addEventListener('click', sendData);