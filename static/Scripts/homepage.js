window.addEventListener("DOMContentLoaded", async function () {
    // load the profiles from the API
    loadProfiles();
});

async function loadProfiles() {
    const profilesURL = "/api/v1/profiles/";

    fetch(profilesURL)
        .then(validateJSON)
        .then(addProfiles)
        .catch(error => {
            console.log("Profile Fetch Failed: ", error)
        })
}

async function addProfiles(profiles) {
    const profilesDiv = document.getElementById("all-profiles");
    const container = document.createElement("div");
    container.classList.add("container");
    profilesDiv.appendChild(container);
    const row = document.createElement("div");
    row.classList.add("row");
    container.appendChild(row);

    var count = 0;

    for (const profile of profiles.profiles) {
        if (count !== 0 || count % 6 !== 0) {
            const prof = document.createElement("div");
            prof.classList.add("col-lg-2");
            const profPad = document.createElement("div");
            profPad.classList.add("profPad");
            profPad.innerText = profile.fname + " " + profile.lname + "\n"
                + profile.gender + "\n" + profile.bio;

            row.appendChild(prof);
            prof.appendChild(profPad);
        } else {
            const prof = document.createElement("div");
            prof.classList.add("col-lg-2");
            const profPad = document.createElement("div");
            profPad.classList.add("profPad");
            profPad.innerText = profile.fname + " " + profile.lname + "\n"
                + profile.gender + "\n" + profile.bio;
                
            row.appendChild(prof);
            prof.appendChild(profPad);
        }

        count++;
    }
}

/**
 * Validate a response to ensure the HTTP status code indcates success.
 * 
 * @param {Response} response HTTP response to be checked
 * @returns {object} object encoded by JSON in the response
 */
function validateJSON(response) {
    if (response.ok) {
        return response.json();
    } else {
        return Promise.reject(response);
    }
}