let secondIntervalId = null
let minuteIntervalId = null

async function oneSecondPoll() {
    try {
        const response = await fetch("/apiv1/system_one_second");
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }
        const status = await response.json();
        document.getElementById("td_system_time").textContent = status.data.time;
        document.getElementById("td_system_cpu").textContent = status.data.cpu;
        document.getElementById("td_system_disk").textContent = status.data.disk;
        document.getElementById("td_system_mem").textContent = status.data.mem;

    } catch (error) {
        clearInterval(secondIntervalId);
        //console.error("Error fetching service status:", error);
    }
}



async function oneMinutePoll() {
    try {
        const response = await fetch("/apiv1/system_one_minute");
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }
        const status = await response.json();
        document.getElementById("td_system_ntpqp").textContent = status.data.ntpq;
        
    } catch (error) {
        clearInterval(minuteIntervalId);
        //console.error("Error fetching service status:", error);
    }
}




window.onload = function() {
    secondIntervalId = setInterval(oneSecondPoll, 1000);
    minuteIntervalId = setInterval(oneMinutePoll, 60000);
    oneMinutePoll()
  };