let secondIntervalId = null
// let minuteIntervalId = null

async function tenSecondPoll() {
    try {
        const response = await fetch("/apiv1/system_ten_second");
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



async function servicesPoll() {
    try {
        const response = await fetch("/apiv1/system_services_poll");
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }
        const status = await response.json();
        document.getElementById("td_www_service").textContent = status.data.wwwrf;
        document.getElementById("td_gps_service").textContent = status.data.gpsd;
        document.getElementById("td_ntp_service").textContent = status.data.ntpsec;
        document.getElementById("td_gps_lat").textContent = status.data.lat;
        document.getElementById("td_gps_lon").textContent = status.data.lon;
        document.getElementById("td_gps_sats").textContent = status.data.sats;
        document.getElementById("td_ntp_refs").innerHTML =  status.data.ntp.join("<br />");;
    } catch (error) {
        clearInterval(servicesIntervalId);
        //console.error("Error fetching service status:", error);
    }
}



window.onload = function() {
    tenSecondPoll()
    servicesPoll()
    secondIntervalId = setInterval(tenSecondPoll, 10000);
    servicesIntervalId = setInterval(servicesPoll, 30000);
};


  window.addEventListener("beforeunload", () => {
    clearInterval(secondIntervalId);
    clearInterval(servicesIntervalId);
});