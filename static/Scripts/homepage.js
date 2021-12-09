window.addEventListener("DOMContentLoaded", async function () {
    // load the profiles from the API
    loadProfiles();
});

/**
 * Fetches a list of profiles and adds them to the page with addProfiles
 * @see {@link addProfiles}
 */
async function loadProfiles() {
    const profilesURL = "/api/v1/profiles/";

    fetch(profilesURL)
        .then(validateJSON)
        .then(addProfiles)
        .catch(error => {
            console.log("Profile Fetch Failed: ", error)
        })
}

/**
 * Inserts profile data into a Bootstrap grid 
 * @param {RaceAPIResouce} profiles 
 */
async function addProfiles(profiles) {
    // Get existing div and add a new div "container". Div "row" is added to that.
    const profilesDiv = document.getElementById("all-profiles");
    const container = document.createElement("div");
    container.classList.add("container");
    profilesDiv.appendChild(container);

    // Will be used to track when to create a new row. Can be modified
    var count = 0;

    for (const profile of profiles.profiles) {
        /* 
        * If the count is not 0 or is not divisible by 6, add a new profile to the
        * existing row. Otherwise refresh the memory location and value of row
        * and keep adding profiles.
        */
        if (profile.fname !== null || profile.lname !== null ||
            profile.gender !== null || profile.bio !== null || profile.picture !== null) {
            if (count !== 0 && count % 6 !== 0) {
                console.log("if"); // Debugging
                const prof = document.createElement("div");
                prof.classList.add("col");

                // Create an inner div for CSS styling
                const profPad = document.createElement("div");
                profPad.classList.add("profPad");
                profPad.classList.add("p-3");
                profPad.classList.add("border");
                profPad.classList.add("rounded");
                profPad.classList.add("bg-light");
                profPad.classList.add("row-eq-height");

                const profilePic = document.createElement("img");
                profilePic.src = profile.picture;
                profilePic.alt = "Profile Picture";
                profilePic.classList.add("preview");

                const imageDiv = document.createElement("div");
                imageDiv.classList.add("pfp");
                profPad.appendChild(imageDiv);
                imageDiv.appendChild(profilePic);

                const text = document.createElement("p");
                text.classList.add("blurb");
                text.innerText = profile.fname + " " + profile.lname + "\n"
                + profile.age + ", " + profile.gender;
                insertAfter(text, imageDiv);

                row.appendChild(prof);
                prof.appendChild(profPad);

                profPad.addEventListener("click", function() {viewProfile(profile.id);});
                
                // Increment and log count
                count++;
                console.log(count);
            } else {
                console.log("else"); // Debugging
                // New row
                row = document.createElement("div");
                row.classList.add("row");
                row.classList.add("row-cols-3");
                row.classList.add("row-cols-lg-6");
                row.classList.add("g-2");
                row.classList.add("g-lg-3");
                container.appendChild(row);

                const prof = document.createElement("div");
                prof.classList.add("col");

                // Create an inner div for CSS styling
                const profPad = document.createElement("div");
                profPad.classList.add("profPad");
                profPad.classList.add("p-3");
                profPad.classList.add("border");
                profPad.classList.add("rounded");
                profPad.classList.add("bg-light");
                profPad.classList.add("row-eq-height");

                const profilePic = document.createElement("img");
                profilePic.src = profile.picture;
                profilePic.alt = "Profile Picture";
                profilePic.classList.add("preview");

                const imageDiv = document.createElement("div");
                imageDiv.classList.add("pfp");
                profPad.appendChild(imageDiv);
                imageDiv.appendChild(profilePic);

                const text = document.createElement("p");
                text.classList.add("blurb");
                text.innerText = profile.fname + " " + profile.lname + "\n"
                + profile.age + ", " + profile.gender;
                insertAfter(text, imageDiv);

                row.appendChild(prof);
                prof.appendChild(profPad);

                profPad.addEventListener("click", function() {viewProfile(profile.id);});

                // const link = document.createElement("a");
                // link.href = ''

                // Increment and log count
                count++;
                console.log(count); // Debugging
            }
        } else if (count % 6 === 0) {
            console.log("else if");
            // New row
            row = document.createElement("div");
            row.classList.add("row");
            row.classList.add("row-cols-3");
            row.classList.add("row-cols-lg-6");
            row.classList.add("g-2");
            row.classList.add("g-lg-3");
            container.appendChild(row);
        }
    }
}

async function viewProfile(id) {
    const profileView = `/api/v1/profiles/${id}` // Make this optional
    
    fetch(profileView)
        .then(validateJSON)
        .then(data => {
            const profile = document.getElementById("current-profile");

            const profileContent = document.createElement("div");
            profileContent.id = "current-profile-content";
            profileContent.innerText = data.profile.fname;

            console.log(data);

            profile.appendChild(profileContent);

            profile.style.display = "block";

            window.onclick = function(event) {
                if (event.target.id === "current-profile") {
                    event.target.style.display = "none";
                    document.getElementById("current-profile").innerHTML = null;
                }
            }
        })
        .catch(error => {
            console.log("Profile Fetch Failed: ", error)
        })
}

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
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