// ======================================================
// DISPLAY HOTSPOT START OUTPUT
// ======================================================

window.addEventListener("DOMContentLoaded", function () {

    console.log("NetCore index.html loaded.");

    const hotspotOutput =
        sessionStorage.getItem("hotspotOutput");


    // Check if setup.html saved hotspot output
    if (hotspotOutput) {

        console.log(
            "Hotspot output received from setup.html:"
        );

        console.log(hotspotOutput);


        const output =
            document.getElementById("output");

        const outputStatus =
            document.getElementById("output-status");


        // Display the output
        if (output) {

            output.innerHTML =
                `<pre>${hotspotOutput}</pre>`;

            console.log(
                "Hotspot output displayed."
            );

        } else {

            console.error(
                "ERROR: #output was not found."
            );

        }


        // Update status
        if (outputStatus) {

            outputStatus.textContent =
                "Hotspot started";

        }


        // Remove stored result
        sessionStorage.removeItem(
            "hotspotOutput"
        );


        // ==================================================
        // AUTOMATICALLY SCROLL TO TERMINAL OUTPUT
        // ==================================================

        setTimeout(function () {

            const outputSection =
                document.querySelector(".output-section");

            if (outputSection) {

                outputSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

                console.log(
                    "Scrolled to terminal output."
                );

            } else {

                console.error(
                    "ERROR: .output-section was not found."
                );

            }

        }, 100);


    } else {

        console.log(
            "No hotspot output found."
        );

    }

});



// ======================================================
// STOP HOTSPOT
// ======================================================

async function stopHotspot() {

    console.log("stopHotspot() was called");

    const output =
        document.getElementById("output");

    const outputStatus =
        document.getElementById("output-status");


    outputStatus.textContent =
        "Stopping...";

    output.innerHTML =
        "<p>Stopping Windows hotspot...</p>";


    try {

        console.log(
            "Trying to connect to Flask..."
        );


        const response = await fetch(
            "http://127.0.0.1:5000/Stop-Hotspot"
        );


        console.log(
            "Response received:",
            response
        );


        const result =
            await response.json();


        console.log(
            "Python result:",
            result
        );


        output.innerHTML =
            `<pre>${result.data}</pre>`;

        outputStatus.textContent =
            "Hotspot stopped";


    } catch (error) {

        console.error(
            "ERROR:",
            error
        );


        output.innerHTML = `
            <p>
                Unable to connect to Server.
            </p>
        `;


        outputStatus.textContent =
            "Connection failed";

    }

}



// ======================================================
// DRIVER INFORMATION
// ======================================================

async function driverInfo() {

    console.log("driverInfo() was called");

    const output =
        document.getElementById("output");

    const outputStatus =
        document.getElementById("output-status");


    outputStatus.textContent =
        "Loading...";

    output.innerHTML =
        "<p>Connecting to server...</p>";


    try {

        console.log(
            "Trying to connect to Flask..."
        );


        const response = await fetch(
            "http://127.0.0.1:5000/driver-details"
        );


        console.log(
            "Response received:",
            response
        );


        const result =
            await response.json();


        console.log(
            "Python result:",
            result
        );


        output.innerHTML =
            `<pre>${result.data}</pre>`;

        outputStatus.textContent =
            "Driver information loaded";


    } catch (error) {

        console.error(
            "ERROR:",
            error
        );


        output.innerHTML = `
            <p>
                Unable to connect to Server.
            </p>
        `;


        outputStatus.textContent =
            "Connection failed";

    }

}



// ======================================================
// SYSTEM INFORMATION
// ======================================================

async function systeminfo() {

    console.log("systeminfo() was called");

    const output =
        document.getElementById("output");

    const outputStatus =
        document.getElementById("output-status");


    outputStatus.textContent =
        "Loading...";

    output.innerHTML =
        "<p>Connecting to Server...</p>";


    try {

        console.log(
            "Trying to connect to Flask..."
        );


        const response = await fetch(
            "http://127.0.0.1:5000/System-info"
        );


        console.log(
            "Response received:",
            response
        );


        const result =
            await response.json();


        console.log(
            "Python result:",
            result
        );


        output.innerHTML =
            `<pre>${result.data}</pre>`;

        outputStatus.textContent =
            "System information loaded";


    } catch (error) {

        console.error(
            "ERROR:",
            error
        );


        output.innerHTML = `
            <p>
                Unable to connect to Server.
            </p>
        `;


        outputStatus.textContent =
            "Connection failed";

    }

}



// ======================================================
// IP CONFIGURATION
// ======================================================

async function ipConfigurations() {

    console.log("ipConfigurations() was called");

    const output =
        document.getElementById("output");

    const outputStatus =
        document.getElementById("output-status");


    outputStatus.textContent =
        "Loading...";

    output.innerHTML =
        "<p>Getting IP configuration...</p>";


    try {

        const response = await fetch(
            "http://127.0.0.1:5000/ipconfig"
        );


        const result =
            await response.json();


        output.innerHTML =
            `<pre>${result.data}</pre>`;

        outputStatus.textContent =
            "IP configuration loaded";


    } catch (error) {

        console.error(
            "ERROR:",
            error
        );


        output.innerHTML =
            "<p>Unable to connect to Server.</p>";

        outputStatus.textContent =
            "Connection failed";

    }

}



// ======================================================
// SAVED NETWORKS
// ======================================================

async function saved_networks() {

    console.log("saved_networks() was called");

    const output =
        document.getElementById("output");

    const outputStatus =
        document.getElementById("output-status");


    outputStatus.textContent =
        "Loading...";

    output.innerHTML =
        "<p>Getting Saved Networks...</p>";


    try {

        const response = await fetch(
            "http://127.0.0.1:5000/saved-networks"
        );


        const result =
            await response.json();


        output.innerHTML =
            `<pre>${result.data}</pre>`;

        outputStatus.textContent =
            "Saved Networks loaded";


    } catch (error) {

        console.error(
            "ERROR:",
            error
        );


        output.innerHTML =
            "<p>Unable to connect to Server.</p>";

        outputStatus.textContent =
            "Connection failed";

    }

}



// ======================================================
// SCROLL TO OUTPUT
// ======================================================

function scrollToOutput() {

    const outputSection =
        document.querySelector(".output-section");


    if (outputSection) {

        outputSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

}

// ======================================================
// DOWNLOAD LAUNCHER
// ======================================================

function downloadLauncher() {
    const link = document.createElement("a");

    link.href = "https://github.com/rahuladhk/NetCore/raw/c1a75aeae0f68e5df857979b3c8b6202280b1ec4/NetCore-Launcher.zip";
    link.download = "NetCore-Launcher.zip";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}