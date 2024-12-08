
// List of questions
const questions = [
    "Rate your positive Engagement when looking at positive images",
    "Rate your positive Engagement when looking at scrambled images",
    "How much could you control the thermometer level?",
    "Was the thermometer level reflecting your positive emotional engagement?"
];

// List of questions
const strategy_questions = [
    "Did you use mental imagery?",
    "Did you focus only on positive feelings?"
];

// Enable Submit Button Only When All Fields are Valid on th first page
const form = document.querySelector('.page');
const submitButton1 = document.getElementById('submitInfo');

form.addEventListener('input', () => {
    subjectID = document.getElementById('subjectID').value.trim();
    sessionNumber = document.getElementById('sessionNumber').value;
    nrNFRuns = document.getElementById('NrNFRuns').value;
    
    // Check if all fields have valid input
    if (subjectID && sessionNumber >= 1 && sessionNumber <= 5 && nrNFRuns >= 1 && nrNFRuns <= 4) {
        submitButton1.disabled = false;
    } else {
        submitButton1.disabled = true;
    }
});

const submitButton2 = document.getElementById('submitRatings');
const form2 = document.querySelector('#run-questions');

form2.addEventListener('input', () => {

    // Select all radio buttons with the name corresponding to the current scale
    const radioButtons = form2.querySelectorAll(`input[type="radio"][name^="NFrun"]`);

    // const filteredRadios = Array.from(radioButtons).filter(radio => !radio.name.includes('strategy'));

    const totalItems = radioButtons.length/10; // the ratings scale is from 1 to 10

    console.log(radioButtons)

    // Check if all radio buttons have been rated (i.e., selected)
    const allRated = Array.from(radioButtons).filter(input => input.checked).length === totalItems;
    console.log(allRated)

    // Enable the submit button if all radio buttons are checked, otherwise disable it
    submitButton2.disabled = !allRated;

});


// Get references to the text areas and submit button
const answer1 = document.getElementById('answer1');
const answer2 = document.getElementById('answer2');
const submitButton3 = document.getElementById('submitStrategyInfo');
const form3 = document.querySelector('#strategy-evaluation');

// Function to check if both answers are not empty
form3.addEventListener('input', () => {

    // Select all radio buttons with the name corresponding to the current scale
    const radioButtons = form3.querySelectorAll(`input[type="radio"][name^="Strategy"]`);

    // const filteredRadios = Array.from(radioButtons).filter(radio => !radio.name.includes('strategy'));

    const totalItems = radioButtons.length/10; // the ratings scale is from 1 to 10

    console.log(radioButtons)

    // Check if all radio buttons have been rated (i.e., selected)
    const allRated = Array.from(radioButtons).filter(input => input.checked).length === totalItems;
    console.log(allRated)

    // Enable the submit button if also all radio buttons are checked, otherwise disable it

    if (answer1.value.trim() !== '' && answer2.value.trim() !== '' && allRated) {
        submitButton3.disabled = false; // Enable the submit button
    } else {
        submitButton3.disabled = true; // Disable the submit button
    }
});



// Prevent the default submission of the form and navigate to PANAS
document.getElementById('info').addEventListener('submit', function(event) {
    event.preventDefault(); // Stop the page from refreshing
    goToPage('run-questions'); // Navigate to the RUN questions Page
});
document.getElementById('submitRatings').addEventListener('click', function(event) {
    event.preventDefault(); // Stop the page from refreshing
    saveRatings();
    goToPage('strategy-evaluation'); // Navigate to the Strategy evaluation Page
});
document.getElementById('submitStrategyInfo').addEventListener('click', function(event) {
    event.preventDefault(); // Stop the page from refreshing
    saveStrategyInfo();
    goToPage('END'); // Navigate to the end page
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

    if (pageId==='run-questions'){

        generateRunQuestionnaires();
    }; 

    if (pageId==='strategy-evaluation'){

        generateStragegyQuestionnaires();
    }; 

    }
}

// Function to create a single questionnaire
function createQuestionnaire(instanceId) {
    const questionnaireDiv = document.createElement('div');
    questionnaireDiv.classList.add('questionnaire');
    questionnaireDiv.setAttribute('id', `questionnaire-${instanceId}`);

    // Add a heading for the instance number
    const heading = document.createElement('h2');
    heading.textContent = `NF run ${instanceId}`;
    questionnaireDiv.appendChild(heading);

    questions.forEach((question, questionIndex) => {
        const questionDiv = document.createElement('div');
        questionDiv.classList.add('question');

        const questionLabel = document.createElement('span');
        questionLabel.classList.add('question-label');
        questionLabel.textContent = `${questionIndex + 1}. ${question}`;
        questionDiv.appendChild(questionLabel);

        const ratingScaleDiv = document.createElement('div');
        ratingScaleDiv.classList.add('rating-scale');

        for (let i = 1; i <= 10; i++) {
            const radio = document.createElement('input');
            radio.type = 'radio';
            radio.id = `NFrun${instanceId}-q${questionIndex+1}-${i}`;
            radio.name = `NFrun${instanceId}-q${questionIndex+1}`;
            radio.value = i;

            const label = document.createElement('label');
            label.htmlFor = `NFrun${instanceId}-q${questionIndex+1}-${i}`;
            label.textContent = i;

            ratingScaleDiv.appendChild(radio);
            ratingScaleDiv.appendChild(label);
        }

        questionDiv.appendChild(ratingScaleDiv);
        questionnaireDiv.appendChild(questionDiv);
    });

    return questionnaireDiv;
}

// Function to generate multiple questionnaires
function generateRunQuestionnaires() {
    const numInstances = document.getElementById('NrNFRuns').value;
    const container = document.getElementById('questionnaire-container1');

    // Clear previous questionnaires
    container.innerHTML = '';

    // Create and append each questionnaire
    for (let i = 1; i <= numInstances; i++) {
        const questionnaire = createQuestionnaire(i);
        container.appendChild(questionnaire);
    }
}


// Function to generate multiple questionnaires
function generateStragegyQuestionnaires() {

    const container = document.getElementById('questionnaire-container2');

    // Clear previous questionnaires
    container.innerHTML = '';

    const questionnaireDiv = document.createElement('div');
    questionnaireDiv.classList.add('questionnaire');
    questionnaireDiv.setAttribute('id', `questionnaire-strategy`);

    strategy_questions.forEach((question, questionIndex) => {
        const questionDiv = document.createElement('div');
        questionDiv.classList.add('question');

        const questionLabel = document.createElement('span');
        questionLabel.classList.add('question-label');
        questionLabel.textContent = `${questionIndex + 1}. ${question}`;
        questionDiv.appendChild(questionLabel);

        const ratingScaleDiv = document.createElement('div');
        ratingScaleDiv.classList.add('rating-scale');

        for (let i = 1; i <= 10; i++) {
            const radio = document.createElement('input');
            radio.type = 'radio';
            radio.id = `Strategy-q${questionIndex+1}-${i}`;
            radio.name = `Strategy-q${questionIndex+1}`;
            radio.value = i;

            const label = document.createElement('label');
            label.htmlFor = `Strategy-q${questionIndex+1}-${i}`;
            label.textContent = i;

            ratingScaleDiv.appendChild(radio);
            ratingScaleDiv.appendChild(label);
        }

        questionDiv.appendChild(ratingScaleDiv);
        questionnaireDiv.appendChild(questionDiv);
    });

    container.appendChild(questionnaireDiv);
}


function saveRatings() { // finishing saving downloading the data

    // Create a Blob and a downloadable link
    let csvContent =  'NFRun,Question,Score\n';

    const nrNFRuns = document.getElementById('NrNFRuns').value;

    for (let i = 1; i <= nrNFRuns; i++) {
        for (let q_idx = 1; q_idx <= 4; q_idx++) {

            const radios = document.getElementsByName(`NFrun${i}-q${q_idx}`);
            let selectedRating = null;

            radios.forEach(radio => {
                if (radio.checked) {
                    selectedRating = radio.value;
                }
            });

            csvContent += `NFrun${i},q${q_idx},${selectedRating}\n`;
        };    
    };
        
    // Generate timestamp for filename
    const now = new Date();
    const timestamp = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}_${now.getHours()}-${now.getMinutes()}-${now.getSeconds()}`;


    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    // Create filename with timestamp
    const filename = `interscan-NF-ratings_${subjectID}_ses-0${sessionNumber}_${timestamp}.csv`;

    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = filename;
    downloadLink.click();

    URL.revokeObjectURL(url);
    
}

function saveStrategyInfo() {

    // Get the values of the question and textarea
    const answer1 = document.getElementById('answer1').value;
    const answer2 = document.getElementById('answer2').value;


    const data = {};
    data['Question 1: Which strategies did you use to engage in a positive emotional state?'] = answer1;
    data['Question 2: Which strategy proved most effective?'] = answer2;

    // Save last 2 ratings
    for (let i = 1; i <= 2; i++) {
        const radios = document.getElementsByName(`Strategy-q${i}`);
                let selectedRating = null;

                radios.forEach(radio => {
                    if (radio.checked) {
                        data[`Strategy-q${i}`] = radio.value;
                    }
                });
    }


    // Convert the object to a JSON string
    const jsonData = JSON.stringify(data, null, 2);

    // Create a Blob object
    const blob = new Blob([jsonData], { type: 'application/json' });

    // Create a link to download the file
    const url = URL.createObjectURL(blob);

    // Generate timestamp for filename
    const now = new Date();
    const timestamp = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}_${now.getHours()}-${now.getMinutes()}-${now.getSeconds()}`;

    // Create filename with timestamp
    const filename = `postscan-questions_${subjectID}_ses-0${sessionNumber}_${timestamp}.json`;

    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = filename;
    downloadLink.click();

    URL.revokeObjectURL(url);    


}
