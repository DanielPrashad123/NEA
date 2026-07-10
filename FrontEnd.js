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
    .then(data => {
        // Output the final result to the console
        console.log('Success! The server calculated:', data.result);
    })
    .catch((error) => {
        console.error('Error communicating with the server:', error);
    })
}



// Send the request
fetch(apiUrl, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json' // Telling the server to expect JSON
    },
    body: JSON.stringify(dataPacket)
})
.then(response => response.json()) // Parse the JSON response from Python
.then(data => {
    // Output the final result to the console
    console.log('Success! The server calculated:', data.result);
})
.catch((error) => {
    console.error('Error communicating with the server:', error);
})

sendBallButton.addEventListener('click', sendData);