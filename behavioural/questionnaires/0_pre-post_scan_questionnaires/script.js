const panasItems = [
            "Interested", "Distressed", "Excited", "Upset", "Strong", 
            "Guilty", "Scared", "Hostile", "Enthusiastic", "Proud", 
            "Irritable", "Alert", "Ashamed", "Inspired", "Nervous", 
            "Determined", "Attentive", "Jittery", "Active", "Afraid"
        ];



const pomsItems = [
    "Tense", "Angry", "Worn Out", "Unhappy", "Proud", 
    "Lively", "Confused", "Sad", "Active", "On-edge", 
    "Grouchy", "Ashamed", "Energetic", "Hopeless", "Uneasy", 
    "Restless", "Unable to concentrate", "Fatigued", "Competent", "Annoyed",
    "Discouraged", "Resentful", "Nervous", "Miserable", "Confident", 
    "Bitter", "Exhausted", "Anxious", "Helpless", "Weary", 
    "Satisfied", "Bewildered", "Furious", "Full of Pep", "Worthless", 
    "Forgetful", "Vigorous", "Uncertain about things", "Bushed", "Embarrassed"
];


const tbody = document.querySelector("tbody");
var subjectID = ''
var sessionNumber = ''
var sessionDescription = ''
var panasRatings = [];

// Enable Submit Button Only When All Fields are Valid on th first page
const form = document.querySelector('.page');
const submitButton = document.getElementById('submitInfo');

form.addEventListener('input', () => {
    subjectID = document.getElementById('subjectID').value.trim();
    sessionNumber = document.getElementById('sessionNumber').value;
    sessionDescription = document.getElementById('sessionDescription').value;
    
    // Check if all fields have valid input
    if (subjectID && sessionNumber >= 1 && sessionNumber <= 5 && sessionDescription) {
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
});

// Prevent the default submission of the form and navigate to PANAS
document.getElementById('info').addEventListener('submit', function(event) {
    event.preventDefault(); // Stop the page from refreshing
    goToPage('PANAS'); // Navigate to the PANAS page
});

// Prevent propagation navigate to POMS
document.getElementById('submitPANAS').addEventListener('click', function(event) {
    event.preventDefault(); // Stop the page from refreshing
    submitRatings('PANAS',panasItems);
    goToPage('POMS'); // Navigate to the POMS page
});

// Prevent propagation navigate to PANAS
document.getElementById('submitPOMS').addEventListener('click', function(event) {
    event.preventDefault(); // Stop the page from refreshing
    submitRatings('POMS', pomsItems);
    goToPage('END'); // Navigate to the POMS page
});


function goToPage(pageId) {

  // Show the target page
  var targetPage = document.getElementById(pageId);

  if (targetPage !== null) { 

    // Hide all pages
    var pages = document.querySelectorAll('.page');
    pages.forEach(function(page) {
      page.classList.remove('visible');
    });

    targetPage.classList.add('visible');

    if (pageId==='PANAS'){

        createPANASScale();
    }; 

    if (pageId==='POMS'){

        createPOMSScale();
    }; 
    }
}

function enableSubmitButton(type) {

    const form = document.getElementById(`${type}Form`);
    const submitButton = document.getElementById(`submit${type}`);

    // Select all radio buttons with the name corresponding to the current scale
    const radioButtons = form.querySelectorAll(`input[type="radio"][name^="${type}"]`);

    const totalItems = radioButtons.length/5;

    console.log(radioButtons)

    // Check if all radio buttons have been rated (i.e., selected)
    const allRated = Array.from(radioButtons).filter(input => input.checked).length === totalItems;
    console.log(allRated)

    // Enable the submit button if all radio buttons are checked, otherwise disable it
    submitButton.disabled = !allRated;
}

function createPANASScale(){

    panasItems.forEach((item, index) => {
        const row = document.createElement("tr");

        // Item column
        const itemCell = document.createElement("td");
        itemCell.textContent = item;
        itemCell.className = "item-column";
        row.appendChild(itemCell);

        // Scale columns (1-5 radio buttons)
        for (let i = 1; i <= 5; i++) {
            const scaleCell = document.createElement("td");
            scaleCell.className = "scale-column";

            const radioInput = document.createElement("input");
            radioInput.type = "radio";
            radioInput.name = `PANAS${index + 1}`;
            radioInput.value = i;
            radioInput.required = true;

            // Attach event listener to each radio button
            radioInput.addEventListener("change", function() {
                enableSubmitButton('PANAS'); // Call enableSubmitButton when a radio button is changed
            });

            scaleCell.appendChild(radioInput);
            row.appendChild(scaleCell);
        }

        tbody.appendChild(row);
    });
}

function createTable(sideItems, tableId, initial_idx) {
    const tbody = document.getElementById(tableId).querySelector("tbody");
    sideItems.forEach((item, index) => {
        const row = document.createElement("tr");

        // Item column
        const itemCell = document.createElement("td");
        itemCell.textContent = item;
        itemCell.className = "item-column";
        row.appendChild(itemCell);

        // Scale columns (1-5 radio buttons)
        for (let i = 1; i <= 5; i++) {
            const scaleCell = document.createElement("td");
            scaleCell.className = "scale-column";

            const radioInput = document.createElement("input");
            radioInput.type = "radio";
            radioInput.name = `POMS${index + initial_idx + 1}`;
            radioInput.value = i;
            radioInput.required = true;

            // Attach event listener to each radio button
            radioInput.addEventListener("change", function() {
                enableSubmitButton('POMS'); // Call enableSubmitButton when a radio button is changed
            });


            scaleCell.appendChild(radioInput);
            row.appendChild(scaleCell);
        }

        tbody.appendChild(row);
    });
}

function createPOMSScale() {
    createTable(pomsItems.slice(0, 20), 'upperTable', initial_idx=0);
    createTable(pomsItems.slice(-20), 'lowerTable', initial_idx=20);
}

function submitRatings(type, ItemIDs) {
    const form = document.getElementById(`${type}Form`);
    const formData = new FormData(form);

    // Create a Blob and a downloadable link
    let csvContent =  `${type} Item,Score\n`;

   ItemIDs.forEach((item, index) => {
        const response = formData.get(`${type}${index + 1}`);
        csvContent += `${item},${response}\n`;
    });
        
        // Generate timestamp for filename
    const now = new Date();
    const timestamp = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}_${now.getHours()}-${now.getMinutes()}-${now.getSeconds()}`;


    var order = ''
    if (sessionDescription==='before'){
        order='pre';
    }
    else{
        order='post';
    }

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    // Create filename with timestamp
    const filename = `${type}ratings-${order}_${subjectID}_ses-0${sessionNumber}_${timestamp}.csv`;

    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = filename;
    downloadLink.click();

    URL.revokeObjectURL(url);
    
}

