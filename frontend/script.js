/* =============== Notes List =============== */

const notes = [

    {

        id:1,

        title:"Payment Gateway Timeout",

        description:"Database connection timed out while processing orders.",

        user:"Rahul",

        tags:["Database","Payment"],

        date:"29 Jul 2026"

    }

];

const notesContainer = document.getElementById("notesContainer");
const noteCount = document.getElementById("noteCount");

function displayNotes() {

    notesContainer.innerHTML = "";

    noteCount.textContent = `${notes.length} Notes`;

    notes.forEach((note) => {

        const card = document.createElement("div");

        card.className = "note-card";

        card.innerHTML = `

            <div class="card-header">

                <h3>${note.title}</h3>

                <div class="card-actions">

                    <button class="edit-btn">

                        <i class="fa-solid fa-pen"></i>

                    </button>

                    <button class="delete-btn">

                        <i class="fa-solid fa-trash"></i>

                    </button>

                </div>

            </div>

            <p class="description">

                ${note.description}

            </p>

            <div class="tags">

                ${note.tags.map(tag =>
                    `<span class="tag">${tag}</span>`
                ).join("")}
            </div>

            <div class="card-footer">

                <span>

                    <i class="fa-solid fa-user"></i>

                    ${note.user}

                </span>

                <span>

                    <i class="fa-solid fa-calendar"></i>

                    ${note.date}

                </span>

            </div>

        `;

        notesContainer.append(card);

    });

}

displayNotes();

/* ========== loading ========== */

const loadingState = document.getElementById("loadingState")

loadingState.classList.add("hidden");
loadingState.classList.remove("hidden");


/*
use after implemantation of fast api backend

async function loadNotes(){

    const response = await fetch("http://127.0.0.1:8000/notes");

    const notes = await response.json();

    displayNotes(notes);

}

*/

/* =============== Report =============== */

/* Temporary data */

document.getElementById("totalNotes").textContent = notes.length;

document.getElementById("totalUsers").textContent = 3;

document.getElementById("popularTag").textContent = "Database";

document.getElementById("todayNotes").textContent = 2;

/*

async function loadReports() {

    try {

        const response = await fetch("http://127.0.0.1:8000/reports");

        const data = await response.json();

        document.getElementById("totalNotes").textContent = data.total_notes;

        document.getElementById("totalUsers").textContent = data.total_users;

        document.getElementById("popularTag").textContent = data.popular_tag;

        document.getElementById("todayNotes").textContent = data.today_notes;

    }

    catch(error){

        console.log(error);

    }

}

loadReports();

*/


/* =============== Bulk file and import status =============== */

const bulkFile = document.getElementById("bulkFile");

const importStatus = document.getElementById("importStatus");

bulkFile.addEventListener("change", () => {

    if(bulkFile.files.length > 0){

        importStatus.innerHTML = `
            <i class="fa-solid fa-file-lines"></i>
            Selected File :
            <strong>${bulkFile.files[0].name}</strong>
        `;

    }

    else{

        importStatus.textContent = "No file selected.";

    }

});
