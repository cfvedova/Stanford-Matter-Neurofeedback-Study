// Declare a global variable to hold the list of images
var imageList = [
"animals/Bear 3.jpg",
"animals/Bird 2.jpg",
"animals/Bird 3.jpg",
"animals/Bird 4.jpg",
"animals/Cat 1.jpg",
"animals/Cat 3.jpg",
"animals/Cat 4.jpg",
"animals/Cat 5.jpg",
"animals/Chipmunk 2.jpg",
"animals/Chipmunk 3.jpg",
"animals/Couple 5.jpg",
"animals/Dog 12.jpg",
"animals/Dog 14.jpg",
"animals/Dog 28.jpg",
"animals/Dog 4.jpg",
"animals/Dog 6.jpg",
"animals/Elephant 1.jpg",
"animals/Horse 1.jpg",
"animals/Lamb 1.jpg",
"animals/Penguins 2.jpg",
"animals/Stingray 3.jpg",
"animals/Zebra 1.jpg",
"neutral/Bark 1.jpg",
"neutral/Bricks 1.jpg",
"neutral/Cardboard 1.jpg",
"neutral/Cardboard 2.jpg",
"neutral/Cardboard 3.jpg",
"neutral/Dirt 1.jpg",
"neutral/Dirt 4.jpg",
"neutral/Rocks 2.jpg",
"neutral/Rocks 3.jpg",
"neutral/Rocks 4.jpg",
"neutral/Rocks 5.jpg",
"neutral/Rocks 6.jpg",
"neutral/Rocks 7.jpg",
"neutral/Roofing 1.jpg",
"neutral/Roofing 3.jpg",
"neutral/Roofing 5.jpg",
"neutral/Sidewalk 3.jpg",
"neutral/Sidewalk 5.jpg",
"neutral/Sidewalk 6.jpg",
"neutral/Wall 1.jpg",
"neutral/Wall 2.jpg",
"neutral/Wall 3.jpg",
"neutral/Wall 4.jpg",
"neutral/Wall 5.jpg",
"objects/Alcohol 8.jpg",
"objects/Birthday 1.jpg",
"objects/Birthday 3.jpg",
"objects/Bubble 2.jpg",
"objects/Car 1.jpg",
"objects/Coffee 1.jpg",
"objects/Cold 8.jpg",
"objects/Dessert 2.jpg",
"objects/Dessert 3.jpg",
"objects/Dessert 5.jpg",
"objects/Dessert 6.jpg",
"objects/Flowers 2.jpg",
"objects/Food 2.jpg",
"objects/Food 3.jpg",
"objects/Food 4.jpg",
"objects/Food 5.jpg",
"objects/Food 6.jpg",
"objects/Ornament 1.jpg",
"objects/Present 2.jpg",
"objects/Rubber duck 1.jpg",
"objects/Wedding 4.jpg",
"objects/Wedding ring 1.jpg",
"people/Baby 8.jpg",
"people/Beach 6.jpg",
"people/Biking 1.jpg",
"people/Celebration 2.jpg",
"people/Collaboration 1.jpg",
"people/Dancing 1.jpg",
"people/Father 1.jpg",
"people/Frisbee 1.jpg",
"people/Guitar 1.jpg",
"people/Massage 1.jpg",
"people/Mother 4.jpg",
"people/Parachuting 2.jpg",
"people/Performance 2.jpg",
"people/Picnic 2.jpg",
"people/Rafting 4.jpg",
"people/Rollercoaster 1.jpg",
"people/Siblings 1.jpg",
"people/Skier 1.jpg",
"people/Skydiving 4.jpg",
"people/Swimming 1.jpg",
"people/Toast 1.jpg",
"people/Yoga 1.jpg",
"scenes/Beach 1.jpg",
"scenes/Beach 2.jpg",
"scenes/Beach 3.jpg",
"scenes/Beach 8.jpg",
"scenes/Bridge 1.jpg",
"scenes/Cold 7.jpg",
"scenes/Dirt 2.jpg",
"scenes/Fireworks 2.jpg",
"scenes/Fireworks 3.jpg",
"scenes/Galaxy 8.jpg",
"scenes/Happy pose 3.jpg",
"scenes/Lake 11.jpg",
"scenes/Lake 12.jpg",
"scenes/Lake 3.jpg",
"scenes/Lake 9.jpg",
"scenes/Moon 1.jpg",
"scenes/Nature 1.jpg",
"scenes/Rainbow 2.jpg",
"scenes/Sidewalk 4.jpg",
"scenes/Sunflower 1.jpg",
"scenes/Sunset 1.jpg",
"scenes/Sunset 3.jpg"
  // Add more image names as needed
];

//Global variables
const emo_labels = ['EXCITEMENT', 'SEXUAL DESIRE', 'RECOGNITION', 'FAMILY LOVE', 'CONTENTMENT', 'FRIENDSHIP', 'AMUSEMENT', 'PLEASURE', 'GRATITUDE'];
var nr_selected_images = 0;
const MAX_SELECTED_IMAGES = 12;
var selected_images_list = [];

var scores = Array.from({ length: MAX_SELECTED_IMAGES * 2 }, () => // valence and emotions scores for both positive and neutral images
    new Array(emo_labels.length + 1).fill(0)
);


var ratingIndex = 0
var ratingLoopIndex = '1' // index to handle rating loop elements 1-> positive, 2 -> neutral

// Disable the Submit buttons at the beginning
const submit_botton = document.getElementById("Submit");
submit_botton.disabled = true;
const submit_botton2 = document.getElementById("Submit2");
submit_botton2.disabled = true;

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

    // check whether images have to been shown in the current page

    // Load image dynamically
    var imageContainer = document.getElementById('imageContainer' + pageId.charAt(pageId.length - 1));


    if (imageContainer !== null) {  

      // Get the class of the container which specifies the image category
      var containerClass = imageContainer.classList.value;

      loadImagesFromList(imageContainer, containerClass);

      // check the status of the selection while switching image blocks
      if (pageId === 'page7') { // this is the page showing neutral images
        nr_selected_images = 0; // restore the image counter to 0
        ratingIndex = MAX_SELECTED_IMAGES; // to index the valence_score array correctly (neutral images are appended to the positive image list)
        submit_botton2.disabled = true;
        ratingLoopIndex = '2'; // handle second rating loop
      }
     
      checkSelection();
      
      
      displaySelectionInfo();


      selectImages();

    };
  }

  // Prepare rating loop pages
  if (pageId === 'page6' || pageId === 'page9') {
    initRatingProcess();
  }

}


function displaySelectionInfo() {

   // Get all elements with the id "selection-info"
  var selectionInfoElements = document.querySelectorAll("#selection-info");

  // Update the text content of each element
  selectionInfoElements.forEach(function(element) {
    element.innerHTML = `Selected images ${nr_selected_images}/${MAX_SELECTED_IMAGES}`;
  });

}


function loadImagesFromList(container, containerClass) {

  // Create an image element for each image and append it to the container
  container.innerHTML = '';
  imageList.forEach(image => {
    var imgElement = document.createElement('img');
    if (image.includes(containerClass)) {
      imgElement.src = 'images/' + image; // Assuming images are in a subfolder named "images"
      imgElement.classList.add("image");
      imgElement.id = image;
      imgElement.selected = false; // object property to indicate wheter the user selected that image or not
      //console.log(image)
      container.appendChild(imgElement);

    };
  });
}


function selectImages() {

  // Get all images with the class 'image'
  var images = document.querySelectorAll('.image');

  // Add a click event listener to each image
  images.forEach(function(image) {
    image.addEventListener('click', function() {

      if (image.selected) {
        // deselect the image
        image.selected = false;
        image.style.borderColor = 'black';
        image.style.borderWidth = '1px';

        // Remove the image's ID from the selected list
        const index = selected_images_list.indexOf(image.id);
        if (index !== -1) {
          selected_images_list.splice(index, 1);
        }        

        console.log('deselect')
        console.log(selected_images_list)
        nr_selected_images -= 1;

      }
      else {
        // select the image only if the maximum has not been reached yet

        if (nr_selected_images < MAX_SELECTED_IMAGES) {
          image.selected = true;
          image.style.borderColor = 'red';
          image.style.borderWidth = '4px';
          selected_images_list.push(image.id)
          console.log(selected_images_list)
          nr_selected_images += 1;
        };

      };

      // Update the image selection count on the screen
      displaySelectionInfo();

      // enable the submit button if the user finished the selection
      if (nr_selected_images === MAX_SELECTED_IMAGES) {
        submit_botton.disabled = false;
        submit_botton2.disabled = false;
      }
      else {
        submit_botton.disabled = true;
        submit_botton2.disabled = true;

      };

    });
  });

}

function checkSelection() {

   // Get all images with the class 'image'
  var images = document.querySelectorAll('.image');

  // Add a click event listener to each image
  images.forEach(function(image) {
   
      if (selected_images_list.includes(image.id)) {
        // mark the image with the red border if it was selected before
        image.selected = true;
        image.style.borderColor = 'red';
        image.style.borderWidth = '4px';
      };
  });

    // enable the submit button if the user finished the selection
  if (nr_selected_images === MAX_SELECTED_IMAGES) {
    submit_botton.disabled = false;
  }
  else {
    submit_botton.disabled = true;

  };
}


function createImageRatingElement(imageId) {

  var imageElement = document.getElementById(imageId).cloneNode(true);
  imageElement.classList.remove("image")
  imageElement.classList.add('rating-image');
  imageElement.removeAttribute('id');

  const imageContainer = document.createElement('div');
  imageContainer.classList.add('image-container');

  const instructions = document.createElement('rating-instruction');
  instructions.textContent = "Please rate this image.";
  instructions.classList.add('rating-instructions')
  imageContainer.appendChild(imageElement)
  imageContainer.appendChild(instructions);

  const ratingScales = createRatingField(imageId);

  const container = document.createElement('div');
  container.classList.add('image-rating-container');
  container.appendChild(imageContainer);
  container.appendChild(ratingScales);
  //container.appendChild(nextButton); // to avoid overlaps

  return container;
}


function createLikertScale(imageId, scaleLabel, instructions, firstScore=0) {

  const container = document.createElement('div');
  container.classList.add('likert-scale-container');

  // Main Likert scale label 
  const label = document.createElement('instructions');
  label.textContent = scaleLabel + ' ' + instructions ;
  container.appendChild(label);
 
  // Wrapper for labels and radio buttons
  const labelRadioWrapper = document.createElement('div');
  labelRadioWrapper.classList.add('likert-scale-wrapper'); // Apply styling as needed

  // Use flexbox to arrange items horizontally
  labelRadioWrapper.style.display = 'flex';

  for (let i = firstScore; i <= 10; i++) {
    const label = document.createElement('label');
    label.textContent = i;

    const radio = document.createElement('input');
    radio.type = 'radio';
    radio.name = `rating-${scaleLabel}-${imageId}`;
    radio.value = i;

    // Associate the label with the radio button for accessibility
    label.setAttribute('for', radio.id); // Assign unique IDs to each radio first

    // Wrap label and radio in a container (optional)
    const item = document.createElement('div');
    item.classList.add('likert-scale-item'); // Apply styling as needed

    item.appendChild(label);
    item.appendChild(radio);
    labelRadioWrapper.appendChild(item);
  }

  container.appendChild(labelRadioWrapper);

  return container;
}


function createRatingField(imageId) {


  const container = document.createElement('div');
  container.classList.add('ratings-container');


  ratingField = createLikertScale(imageId, 'VALENCE', '(1 = Neutral, 10 = Very Positive)', 1); // last element refers to the first score, default=0s
  container.appendChild(ratingField);


  emo_labels.forEach(function(emo) {

    ratingField = createLikertScale(imageId, emo, '(0 = No Emotion)');
    container.appendChild(ratingField);

  });

  return container;
}


function showImageAndRating() {


  const ratingContainer = document.getElementById('ratingLoop' + ratingLoopIndex);
  ratingContainer.innerHTML = '';

  const nextButton = document.getElementById('nextRating' + ratingLoopIndex);
  nextButton.disabled = true; // Disable next button initially
  nextButton.removeEventListener('click', handleNextButtonClick);


  const imageId = selected_images_list[ratingIndex];
  const imageRatingElement = createImageRatingElement(imageId);

  ratingContainer.appendChild(imageRatingElement);
  console.log(ratingIndex);

  // Clear the selection of radio buttons
  const radioGroup = ratingContainer.querySelectorAll('input[type="radio"]');
  radioGroup.forEach(radio => {
    radio.checked = false;
  }); 

}


function handleNextButtonClick(pageName) {


  // Check if ratingIndex is within bounds
  let upperBound = MAX_SELECTED_IMAGES;

  // duplicate the upper bound in case of neutral images
  // since the positive image loop was completed
  if (ratingIndex >= 12) {
    upperBound = MAX_SELECTED_IMAGES*2;
  }

  if (ratingIndex >= 0 && ratingIndex < upperBound-1) {
    ratingIndex += 1; 
    showImageAndRating();   
  } 
  else {

    // Handle reaching the end of the list
    console.log(pageName)
    goToPage(pageName);

    if (pageName === "end") {
      // End of the experiment: download ratings
      downloadRatings();
    }
  }
}


function handleRatingContainerChange(event) {

  const nextButton = document.getElementById('nextRating' + ratingLoopIndex);
  console.log(nextButton.disabled);
  let ratingContainer = document.getElementById('ratingLoop' + ratingLoopIndex);
  const radioGroup = ratingContainer.querySelectorAll('input[type="radio"]');
  const selectedRadio = [...radioGroup].filter(radio => radio.checked);

  debugger
  if (selectedRadio.length === 10) { // all the emotions and valence have been rated

    console.log('Checked buttons:')
    selectedRadio.forEach(function(radioButton) {

      buttonLabel = radioButton.name;
      const index = emo_labels.findIndex(str => buttonLabel.includes(str));

      if (index === -1) { // no match in the emotion labels array. It's the valence rating
        scores[ratingIndex][0] = radioButton.value;
      }
      else {
        scores[ratingIndex][index+1] = radioButton.value;

      }

      console.log(buttonLabel+ ' ' + String(radioButton.value));
    });

    console.log(scores);
    nextButton.addEventListener('click', handleNextButtonClick);

  }

  const isSelected = selectedRadio.length === 10; //[...radioGroup].some(radio => radio.checked);
  nextButton.disabled = !isSelected;

  // Prevent event propagation to the ratingContainer
  event.stopPropagation();
  
}


function initRatingProcess() {

  // change the border back to black for all the selected images
  selected_images_list.forEach(function(image) {

    imageElement = document.getElementById(image)  
    imageElement.style.borderColor = 'black';
    imageElement.style.borderWidth = '1px';

  });
    
  // initialise the object and add listners here
  let ratingContainer = document.getElementById('ratingLoop' + ratingLoopIndex); // Assuming ratingContainer is available outside the function

  const imageId = selected_images_list[ratingIndex];
  const imageRatingElement = createImageRatingElement(imageId); 

  ratingContainer.appendChild(imageRatingElement);

  
  const nextButton = document.getElementById('nextRating' + ratingLoopIndex);

 // Remove existing event listeners to avoid duplicates
  ratingContainer.removeEventListener('change', handleRatingContainerChange);
  nextButton.removeEventListener('click', handleNextButtonClick);

  // Add new event listeners
  ratingContainer.addEventListener('change', handleRatingContainerChange);

}


function downloadRatings() {

  let csvContent = "Image ID,VALENCE," + emo_labels.join(',') + "\n";

  for (let i = 0; i < selected_images_list.length; i++) {
    const imageId = selected_images_list[i];
    const score = scores[i];
    csvContent += `${imageId},${scores[i].join(',')}\n`;
  }

  console.log(csvContent);

  // Generate timestamp for filename
  const now = new Date();
  const timestamp = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}_${now.getHours()}-${now.getMinutes()}-${now.getSeconds()}`;

  // Create filename with timestamp
  const filename = `ratings_${timestamp}.csv`;

  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);

  const downloadLink = document.createElement('a');
  downloadLink.href = url;
  downloadLink.download = filename;
  downloadLink.click();

  URL.revokeObjectURL(url);

}







