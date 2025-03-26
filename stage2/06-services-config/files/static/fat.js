const fileInput = document.getElementById('newFatMapping');
const uploadButton = document.getElementById('uploadNewFAT');


async function updateFATText() {
    const response = await fetch('/fat_map/active_fat.json');
    const data = await response.json();
    document.getElementById("fatMapping").value = JSON.stringify(data, null, 2);
}


async function restoreFAT(fat) {
    try {
        const response = await fetch('/apiv1/' + fat);
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        updateFATText()
    } catch (error) {
      console.error("Fetch error:", error);
    }
}

restoreFullFAT = () => restoreFAT('scanner_restore_full_fat')
restoreProtoFAT = () => restoreFAT('scanner_restore_proto_fat')
restoreCustomFAT = () => restoreFAT('scanner_restore_custom_fat')

document.getElementById("restoreFullFAT").addEventListener("click", restoreFullFAT);
document.getElementById("restoreCustomFAT").addEventListener("click", restoreCustomFAT);
document.getElementById("restoreProtoFAT").addEventListener("click", restoreProtoFAT);



async function downLoadFAT(fat) {
    fetch('/apiv1/' + fat)
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

async function downLoadFullFAT() { downLoadFAT('scanner_download_full_fat') }
async function downLoadProtoFAT() { downLoadFAT('scanner_download_proto_fat')}

document.getElementById("downloadFullFAT").addEventListener("click", downLoadFullFAT);
document.getElementById("downloadProtoFAT").addEventListener("click", downLoadProtoFAT);



// Event listener for when a file is selected
fileInput.addEventListener('change', function(event) {
    const file = event.target.files[0];  // Get the selected file
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            fileContent = e.target.result;  // Store the file content
        };
        reader.readAsText(file);
        uploadButton.disabled = false;
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
        updateFATText()
        uploadButton.disabled = true;
    })
    .catch(error => {
        console.error('Error posting file content:', error);
    });
});


document.addEventListener("DOMContentLoaded", async function() {
    try {
        updateFATText()
        uploadButton.disabled = true;
    } catch (error) {
        console.error('Error:', error);
    }
});








