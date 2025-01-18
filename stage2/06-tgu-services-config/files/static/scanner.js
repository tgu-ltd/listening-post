let statusIntervalId;
let start_button = document.getElementById("scannerStart");
let status_area = document.getElementById("scanStatus");
let previous_area = document.getElementById("previousScansFiles");
let live_scan_area = document.getElementById("liveScanDataArea"); 





function convertToIntegerList(input) {
    return input
      .split(",")                 // Split by commas
      .map(item => parseInt(item.trim(), 10)) // Trim whitespace and convert to integer
      .filter(Number.isInteger);  // Filter out any non-integer values (optional)
  }



async function pollServiceStatus() {
    try {
        const response = await fetch("/apiv1/scanner_status");
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }
        const status = await response.json();
        if (status.data.running) {
            start_button.classList.add("green");
            start_button.disabled = true
            status_area.value = `Current: ${status.data.name} | ${status.data.size}\n`;
            status_area.value += `Last Entry: ${status.data.fifo}\n`;   
        }
    } catch (error) {
        clearInterval(statusIntervalId);  // Stop polling
        console.error("Error fetching service status:", error);
    }
}


document.getElementById("scannerStart").addEventListener("click", () => {
    const checkbox = document.getElementById("useTrigger");
    const formData = {
        scan_ids: convertToIntegerList(document.getElementById('scan_ids').value),
        use_trigger: checkbox.checked
      };
    const apiEndpoint = "/apiv1/scanner_start";  // Replace with your API endpoint
    fetch(apiEndpoint, {
        method: "POST", 
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(formData),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok " + response.statusText);
        }
        statusIntervalId = setInterval(pollServiceStatus, 1000);
        previous_area.value = ''
        document.getElementById("showScansFiles").click()
        return response.json();
    })
    .catch(error => {
        console.error("There was a problem with the fetch operation:", error);
    });
});



document.getElementById("scannerStop").addEventListener("click", () => {
    const apiEndpoint = "/apiv1/scanner_stop";
    fetch(apiEndpoint, {
        method: "GET",
        headers: {"Content-Type": "application/json"}
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok " + response.statusText);
        }
        clearInterval(statusIntervalId);  // Stop polling
        start_button.classList.remove("green");
        start_button.disabled = false
        status_area.value = ``;
        return response.json();
    })
    .catch(error => {
        console.error("There was a problem with the fetch operation:", error);
    });
});




async function getScanFiles() {
    try {
        const response = await fetch('/apiv1/scanner_get_scan_files'); // Example API endpoint
        if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
        }
        previous_area.value = ``;
        const status = await response.json();
        for (const value of status.data.files) {
            previous_area.value += `${value}\n`;
        }
    } catch (error) {
      console.error("Fetch error:", error);
    }
}
document.getElementById("showScansFiles").addEventListener("click", getScanFiles);




document.getElementById("removeScanFiles").addEventListener("click", () => {
    const apiEndpoint = "/apiv1/scanner_remove_scan_files";
    fetch(apiEndpoint, {
        method: "GET",
        headers: {"Content-Type": "application/json"}
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok " + response.statusText);
        }
        previous_area.value = ``;
        document.getElementById("showScansFiles").click();
        return response.json();
    })
    .catch(error => {
        console.error("There was a problem with the fetch operation:", error);
    });
});


async function getLiveData() {
    try {
        const response = await fetch('/apiv1//apiv1/scanner_get_live_data');
        if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
        }
        const data = await response.json();
        live_scan_area.value = `Entries: ${data.data.length}\n` 
        data.data.forEach(entry => {
            live_scan_area.value += entry
        });
        
    } catch (error) {
      console.error("Fetch error:", error);
    }
}
document.getElementById("getLiveScanData").addEventListener("click", getLiveData);



document.getElementById("downLoadLiveFile").addEventListener("click", () => {
    fetch('/apiv1/scanner_download_live_file')
        .then(response => response.json())
        .then(data => {
            const jsonString = JSON.stringify(data.data, null, 2);
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'scanner_data.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error fetching JSON data:', error));
});




async function getScanFiles() {
    try {
        const response = await fetch('/apiv1/scanner_get_scan_files'); // Example API endpoint
        if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
        }
        previous_area.value = ``;
        const status = await response.json();
        for (const value of status.data.files) {
            previous_area.value += `${value}\n`;
        }
    } catch (error) {
      console.error("Fetch error:", error);
    }
}
document.getElementById("showScansFiles").addEventListener("click", getScanFiles);


async function showScanPlot() {
    try {
        fetch('/apiv1/scanner_download_live_file')
        .then(response => response.json())
        .then(data => {

            const dbs = data.data["Power(db)"];
            const secs = data.data["Timestamp(ns)"];
            const freqs = data.data["Frequency(Hz)"];
            
            const plt = [{
                    z: dbs,
                    x: secs,
                    y: freqs,
                    type: 'heatmap',
                    colorbar: { title: 'dB' },
                    colorscale: 'plasma',
                    zmin: -30,
                    zmax: 10
            }];

            const layout = {
                title: 'Time Frequency Decibel Plot',
                xaxis: { title: 'Frequency (Hz)' },
                yaxis: { title: 'Time (ms)' },
            };
            Plotly.newPlot('plot_div', plt, layout);
        })
        .catch(error => console.error('Error fetching JSON data:', error));

        
    } catch (error) {
        console.error("Error fetching service status:", error);
    }
}
document.getElementById("showCurrentAnalysis").addEventListener("click", showScanPlot);





window.onload = function() {
    status_area.value = ''
    previous_area.value = ''
    live_scan_area.value = ''
    //document.getElementById("scannerStart").click();
    document.getElementById("showScansFiles").click();
  };