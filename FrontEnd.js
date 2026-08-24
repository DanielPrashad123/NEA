

//HTML handling
/* 
these functions are used to switch between the different pages of the dispplay 
they work by changing the display property of the different divs which seperate the pages.
*/
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








//this is the url of the api that will be used to send the data to the backend for processing. 
const apiUrl = "https://musical-space-trout-wrj67r7r4j59h9p9r-5000.app.github.dev/projection";


//define the display elements that will be interacting with teh user as variables to be used later in functions.
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
    // this function is called when the user clicks the send button on the simulation page
    const speed = parseFloat(speedInput.value)
    const angle = parseFloat(angleInput.value)
    const spin = parseFloat(spinInput.value)
    
    //assemble the data into a golf ball data packed to be easily sent to the backend.
    const datapacket= {
        speed: speed,
        angle: angle,
        spin: spin
    }


    // this sends the data to the backend using a POST request.
    // it also updates the status box with the responce from the backend. 
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Telling the server to expect JSON
        },
        body: JSON.stringify(datapacket)
    })

    
    .then(response => response.json()) // Parse the JSON response



    
    .then(data => {
        //this block handles the data that is returned from the backend
        //this error messsage validation is the check if the backend has returned an error mesasge back to this file 
        //this adds another layer of error handling to the api link between the 2 files and also help give the user feedback on any issues,and again will also help in debugging of developers if there is an issue.
        const errorMessage = data.error; 
        if (errorMessage) {
            updateStatus(`Error from server: ${errorMessage}`);
            return;
        }
        //this check for the presence of the trajectory data in the json provides a final layer of error handling to ensure that the data is present and valid before being displayed.
        
        if (!data || !data.trajectory_png) {
        updateStatus('No trajectory data received from server.');
        return;
        }
       

        // extract data from json response and store them in variables.
        const pngData = data.trajectory_png;
        const apexData = data.apex;
        const distData = data.distance;
        const angleFeedback = data.angleFeedback; 
        const spinFeedback = data.spinFeedback;   
        
        

        
        // Setup the image for the simulation Page
        
        trajectoryImageContainer.innerHTML = '';
        const img = document.createElement('img');
        img.alt = 'Golf ball trajectory';
        img.src = `data:image/png;base64,${pngData}`;
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        trajectoryImageContainer.appendChild(img);
        
        // setup image for the summary Page using cloneNode
        const summaryImageContainer = document.getElementById('summaryImageContainer');
        summaryImageContainer.innerHTML = '';
        const imgClone = img.cloneNode(true); // copies image element
        summaryImageContainer.appendChild(imgClone);

        // update the text boxes in summary page 
        document.getElementById('outDistance').innerText = distData;
        document.getElementById('outApex').innerText = apexData;
        document.getElementById('angleOutFeedback').innerText = angleFeedback;
        document.getElementById('spinOutFeedback').innerText = spinFeedback;
        //final update of the status box to let the user know that the data has been successfully processed and returned to the display. 
        updateStatus('Data calculated successfully and summary data generated successfully');
        })
    .catch((error) => {
        //this catch block will grab any errrors that occur during the fetch requenst and display them in the status box 
        //this is to give the user feedback as to what the problem might be and helps any developers to debug the code if there is an issue. 
        //this is important as it ensures that the user is not presented with the wrong data if there is an issue with the backend or the data ebign sent/received.
        //it is located after the .then blocks specifically to catch any errors that occur during the fetch request and not during the processing of data in the .then blocks.
        updateStatus('Error calculating data.',error);
    })
}

sendBallButton.addEventListener('click', sendData);


