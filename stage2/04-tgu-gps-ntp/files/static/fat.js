async function updateFATText() {
    const response = await fetch('/fat_map/tgu_fat_map.json');
    const data = await response.json();
    document.getElementById("fatMapping").value = JSON.stringify(data, null, 2);
}

async function restoreDefault() {
    try {
        const response = await fetch('/apiv1/scanner_restore_default_fat');
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        updateFATText()
    } catch (error) {
      console.error("Fetch error:", error);
    }
}
document.getElementById("restoreDefaultFAT").addEventListener("click", restoreDefault);


async function downLoadFAT() {
    fetch('/apiv1/scanner_download_fat')
    .then(response => response.json())
    .then(data => {
        const jsonString = JSON.stringify(data.data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'fat.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    })
    .catch(error => console.error('Error fetching JSON data:', error));
}
document.getElementById("downloadDefaultFAT").addEventListener("click", downLoadFAT);



const fileInput = document.getElementById('newFatMapping');
const uploadButton = document.getElementById('uploadNewFAT');


// Event listener for when a file is selected
fileInput.addEventListener('change', function(event) {
    const file = event.target.files[0];  // Get the selected file

    if (file) {
        const reader = new FileReader();

        // When the file is read, store its content
        reader.onload = function(e) {
            fileContent = e.target.result;  // Store the file content
            // console.log('File content loaded:', fileContent);
        };

        // Read the file as text (for JSON or other text-based files)
        reader.readAsText(file);
    }
});





// Event listener for the "Upload and Post File" button
uploadButton.addEventListener('click', function() {
    if (!fileContent) {
        alert('Please select a file first!');
        return;
    }
    fetch('/apiv1/scanner_upload_fat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',  // Set appropriate content type for JSON
        },
        body: fileContent,
    })
    .then(response => response.text())
    .then(data => {
        //console.log('Server response:', data);
        updateFATText()
    })
    .catch(error => {
        console.error('Error posting file content:', error);
    });
});


document.addEventListener("DOMContentLoaded", async function() {
    try {
        updateFATText()
    } catch (error) {
        console.error('Error:', error);
    }
});








