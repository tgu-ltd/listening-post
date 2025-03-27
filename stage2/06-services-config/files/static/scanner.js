let statusIntervalId;
let updateIntervalId;
let start_button = document.getElementById("scannerStart");
let status_area = document.getElementById("scanStatus");
let graph_update = document.getElementById("");





function convertToIntegerList(input) {
    return input
      .split(",")                               // Split by commas
      .map(item => parseInt(item.trim(), 10))   // Trim whitespace and convert to integer
      .filter(Number.isInteger);                // Filter out any non-integer values (optional)
  }



async function pollServiceStatus() {
    try {
        const response = await fetch("/apiv1/scanner_status");
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }
        const status = await response.json();
        status_area.value = `Running: ${status.data.running}\n`;
        status_area.value += `FAT: ${status.data.fat}\n`;
        status_area.value += `CSV File: ${status.data.name} | ${status.data.size}\n`;
        status_area.value += `Scanning: ${status.data.scan_name}\n`;
        status_area.value += `Last CSV Entry: ${status.data.fifo}\n`;
        status_area.value += `SDR:\n`;
        status_area.value += `    Gain: ${status.data.sdr_gain}\n`;
        status_area.value += `    Rate: ${status.data.sdr_rate}\n`;
        status_area.value += `    Min Hz: ${status.data.sdr_min_hz}\n`;
        status_area.value += `    Max Hz: ${status.data.sdr_max_hz}\n`;
        status_area.value += `    Read Samples: ${status.data.read_samples}\n`;
        

        if (status.data.running) {
            start_button.disabled = true
            start_button.classList.add("green");   
        }
        else {
            start_button.disabled = false
            start_button.classList.remove("green");
        }
    } catch (error) {
        clearInterval(statusIntervalId);  // Stop polling
        console.error("Error fetching service status:", error);
    }
}



document.getElementById("scannerStart").addEventListener("click", () => {

    const checkbox = document.getElementById("useTrigger");
    const formData = { use_trigger: checkbox.checked };

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
        start_button.classList.remove("green");
        start_button.disabled = false
        status_area.value = ``;
        return response.json();
    })
    .catch(error => {
        console.error("There was a problem with the fetch operation:", error);
    });
});



document.getElementById("scannerClear").addEventListener("click", () => {
    document.getElementById("scannerStop").click()
    const apiEndpoint = "/apiv1/scanner_clear";
    fetch(apiEndpoint, {
        method: "GET",
        headers: {"Content-Type": "application/json"}
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok " + response.statusText);
        }
    })
    .catch(error => {
        console.error("There was a problem with the fetch operation:", error);
    });
});




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





async function showScanPlot() {

    const freqbox = document.getElementById("useBandName");
    use_band_name = freqbox.checked;

    function formatTime(seconds) {
        let date = new Date(seconds * 1000); // Convert to milliseconds
        return date.toISOString()
        //return date.toISOString().substring(11, 8); // Extract HH:MM:SS
    }

    try {
        fetch('/apiv1/scanner_download_live_file')
        .then(response => response.json())
        .then(data => {
            const seconds = data.data["Seconds"];
            const formattedTime = seconds.map(formatTime);
            let dbs = data.data["Power(db)"];
            let swap_data = data.data["Name"]
            let swap_data_title = "Band Name"
            if (!use_band_name) {
                swap_data_title = "Frequency(Hz)"
                swap_data = data.data["Frequency(Hz)"];
            }

            const plt = [{
                x: formattedTime,
                y: swap_data,
                mode: 'markers',
                type: 'scatter',
                marker: {
                    size: 11,
                    symbol: 'square',
                    color: dbs,
                    colorbar: { title: 'Power(dB)'},
                    colorscale: [[0, 'blue'], [0.25, 'cyan'], [0.5, 'green'], [0.75, 'yellow'], [1, 'red']],
                    cmin: -10,
                    cmax: 3
                },
                hovertemplate: swap_data_title + ':%{y}, %{x}<extra></extra>'
            }];

            const layout = {
                title: 'Time Frequency Decibel Plot',
                dragmode: "pan",
                showlegend: false,
                xaxis: {title: 'Time'},
                yaxis: {title: {text: swap_data_title}},
                zaxis: {title: {text: 'dB'}}
            };
            Plotly.newPlot('plot_div', plt, layout);
        })
        .catch(error => console.error('Error fetching JSON data:', error));

        
    } catch (error) {
        console.error("Error fetching service status:", error);
    }
}
document.getElementById("showCurrentAnalysis").addEventListener("click", showScanPlot);




document.getElementById("autoUpdate").addEventListener("change", function() {
    if (this.checked) {
        updateIntervalId = setInterval(showScanPlot, 1000);
    } else {
        clearInterval(updateIntervalId);
    }
});



window.onload = function() {
    status_area.value = ''
    statusIntervalId = setInterval(pollServiceStatus, 1000);
    //document.getElementById("scannerStart").click()
  };