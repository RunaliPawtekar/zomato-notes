/* =============== Notes List =============== */

let notes = [];
let currentPage = 1;

const notesPerPage = 3;

let totalNotes = 0;

const notesContainer = document.getElementById("notesContainer");
const notesList = document.getElementById("notesList");
const noteCount = document.getElementById("noteCount");
const noteForm = document.getElementById("noteForm");

const titleInput = document.getElementById("title");
const descriptionInput = document.getElementById("description");
const userInput = document.getElementById("user");

const saveBtn = document.getElementById("saveBtn");

const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");

searchBtn.addEventListener("click", searchNotes);

searchInput.addEventListener("keyup", function (e) {

    if (e.key === "Enter") {

        searchNotes();

    }

});

async function searchNotes() {

    const keyword = searchInput.value.trim();

    if (keyword === "") {

        currentPage = 1;

        loadNotes();

        return;

    }

    const response = await fetch(
        `http://127.0.0.1:8000/notes/search?keyword=${encodeURIComponent(keyword)}`
    );

    const result = await response.json();

    displayNotes(result);

    noteCount.textContent = `${result.length} Notes`;

    pageInfo.textContent = "Search Results";

    prevBtn.disabled = true;

    nextBtn.disabled = true;

}


async function loadUsers() {

    try {

        const response = await fetch("http://127.0.0.1:8000/users");

        if (!response.ok) {
            throw new Error("Failed to load users");
        }

        const users = await response.json();

        userInput.innerHTML = `
            <option value="">Select Engineer</option>
        `;

        if (users.length === 0) {

            userInput.innerHTML = `
                <option value="">No Engineers Available</option>
            `;

            return;

        }

        users.forEach(user => {

            const option = document.createElement("option");

            option.value = user.id;
            option.textContent = user.name;

            userInput.appendChild(option);

        });

    }

    catch (error) {

        console.error(error);

        userInput.innerHTML = `
            <option value="">Unable to Load Engineers</option>
        `;

    }

}

loadUsers();


function displayNotes(noteArray = notes)  {

    // Clear previous notes
    notesList.replaceChildren();

    // Update total notes count
    noteCount.textContent = `${notes.length} Notes`;
    
    // Show message if there are no notes
    if (noteArray.length === 0)  {

        notesList.innerHTML = `
            <div class="empty-notes">
                <i class="fa-solid fa-note-sticky"></i>
                <h2>No Notes Found</h2>
                <p>Create a new note or import a TXT file.</p>
            </div>
        `;

        return;
    }

    // Display all notes
    noteArray.forEach((note) => {

        const card = document.createElement("div");

        card.className = "note-card";

        card.innerHTML = `

            <div class="card-header">

                <h3>${note.title}</h3>

                <div class="card-actions">

                    <button
                        class="edit-btn"
                        data-id="${note.id}">

                        <i class="fa-solid fa-pen"></i>

                    </button>

                    <button
                        class="delete-btn">

                        <i class="fa-solid fa-trash"></i>

                    </button>

                </div>

            </div>

            <p class="description">

                ${note.content}

            </p>

            <div class="tags">

                ${(note.tags || "")
                    .split(",")
                    .filter(tag => tag.trim() !== "")
                    .map(tag => `<span class="tag">${tag.trim()}</span>`)
                    .join("")}

            </div>

            <div class="card-footer">

                <span>

                    <i class="fa-solid fa-user"></i>

                    ${note.user_name}

                </span>

                <span>

                    <i class="fa-solid fa-calendar"></i>

                    ${new Date(note.created_at).toLocaleDateString(
                        "en-IN",
                        {
                            day: "2-digit",
                            month: "short",
                            year: "numeric",
                            timeZone: "Asia/Kolkata"
                        }
                    )}

                </span>

            </div>

        `;

        notesList.append(card);

        // Edit button
        card.querySelector(".edit-btn").addEventListener("click", () => {
            editNote(note);
        });

        // Delete button
        card.querySelector(".delete-btn").addEventListener("click", () => {
            deleteNote(note.id);
        });

    });

}

/* ============== Edit note function ================ */
let editingNoteId = null;

function editNote(note) {

    editingNoteId = note.id;

    titleInput.value = note.title;
    descriptionInput.value = note.content;
    userInput.value = note.user_id;

    saveBtn.innerHTML = `
        <i class="fa-solid fa-pen"></i>
        Update Note
    `;

    noteForm.scrollIntoView({
        behavior: "smooth"
    });

}

/* ============= Delete note function ============== */
async function deleteNote(noteId) {

    const confirmDelete = confirm("Are you sure you want to delete this note?");

    if (!confirmDelete) {
        return;
    }

    try {

        const response = await fetch(
            `http://127.0.0.1:8000/notes/${noteId}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            throw new Error("Failed to delete note");
        }

        await loadNotes();

    }

    catch (error) {

        console.error(error);

        alert("Unable to delete note.");

    }

}

/* ========== loading ========== */

const loadingState = document.getElementById("loadingState")
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const pageInfo = document.getElementById("pageInfo");

function updatePagination() {

    const totalPages = Math.ceil(totalNotes / notesPerPage);

    pageInfo.textContent = `Page ${currentPage} of ${totalPages || 1}`;

    prevBtn.disabled = currentPage === 1;

    nextBtn.disabled = currentPage >= totalPages;

}

prevBtn.addEventListener("click", async function (e) {

    e.preventDefault();

    if (currentPage > 1) {

        currentPage--;

        await loadNotes();

        this.blur();

    }

});

nextBtn.addEventListener("click", async function (e) {

    e.preventDefault();

    const totalPages = Math.ceil(totalNotes / notesPerPage);

    if (currentPage < totalPages) {

        currentPage++;

        await loadNotes();

        this.blur();

    }

});

async function loadNotes() {

    try {

        const skip = (currentPage - 1) * notesPerPage;

        const response = await fetch(
            `http://127.0.0.1:8000/notes?skip=${skip}&limit=${notesPerPage}`
        );

        if (!response.ok) {
            throw new Error("Failed to load notes");
        }

        const data = await response.json();

        notes = data.notes;
        totalNotes = data.total;

        displayNotes();
        updatePagination();

    }
    catch (error) {

        console.error(error);
        alert("Unable to load notes.");

    }

}
document.addEventListener("DOMContentLoaded", () => {

    loadNotes();

    loadReports();

});

async function createNote(event) {

    event.preventDefault();

    const newNote = {
        title: titleInput.value.trim(),
        content: descriptionInput.value.trim(),
        user_id: Number(userInput.value)
    };

    if (
        !newNote.title ||
        !newNote.content ||
        !newNote.user_id
    ) {
        alert("Please fill all fields.");
        return;
    }

    // Default: Create Note
    let url = "http://127.0.0.1:8000/notes";
    let method = "POST";

    // If editing, change to Update
    if (editingNoteId !== null) {

        url = `http://127.0.0.1:8000/notes/${editingNoteId}`;
        method = "PUT";

    }

    try {

        const response = await fetch(url, {

            method: method,

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(newNote)

        });

        if (!response.ok) {

            throw new Error("Failed to save note");

        }

        // Reset form
        noteForm.reset();

        // Back to Create mode
        editingNoteId = null;

        saveBtn.innerHTML = `
            <i class="fa-solid fa-plus"></i>
            Save Note
        `;

        // Reload notes
        await loadNotes();

    }

    catch (error) {

        console.error(error);

        alert("Unable to save note.");

    }

}

noteForm.addEventListener("submit", createNote);




/* =============== Report =============== */

async function loadReports() {

    try {

        const response = await fetch("http://127.0.0.1:8000/reports");

        const data = await response.json();

        document.getElementById("totalNotes").textContent =
            data.total_notes;

        document.getElementById("totalUsers").textContent =
            data.total_users;

        document.getElementById("popularTag").textContent =
            data.most_used_tag;

        document.getElementById("importedNotes").textContent =
            data.imported_notes;

    }
    catch (error) {

        console.error(error);

    }

}

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
/*upload file */
const importBtn = document.getElementById("importBtn");

importBtn.addEventListener("click", importNotes);

async function importNotes() {

    if (bulkFile.files.length === 0) {
        alert("Please select a TXT file.");
        return;
    }

    const formData = new FormData();

    formData.append("file", bulkFile.files[0]);

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/notes/import",
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {
            throw new Error("Import failed");
        }

        const result = await response.json();

        alert(result.message);

        bulkFile.value = "";

        importStatus.textContent = "No file selected.";

        await loadNotes();

    }
    catch (error) {

        console.error(error);

        alert("Unable to import notes.");

    }

}