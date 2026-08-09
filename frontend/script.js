/* =============== Notes List =============== */

let notes = [];
let currentPage = 1;

const notesPerPage = 3;

let totalNotes = 0;
let currentSort = "";
let currentKeyword = "";

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
const sortBy = document.getElementById("sortBy");
/* smart search */
const smartSearchInput =
document.getElementById("smartSearchInput");

const smartSearchBtn =
document.getElementById("smartSearchBtn");

const smartSearchResults =
document.getElementById("smartSearchResults");

/* =========== Message ================== */

const messageBox = document.getElementById("messageBox");

let messageTimeout;

function showMessage(message, type = "success") {

    // Clear previous timer
    clearTimeout(messageTimeout);

    // Set message
    messageBox.textContent = message;

    // Remove hidden class and apply type
    messageBox.className = `message ${type}`;

    // Hide after 3 seconds
    messageTimeout = setTimeout(() => {

        messageBox.classList.add("hidden");

    }, 3000);

}

/* ================ normal search ================ */
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

    if (!response.ok) {

        alert("Search failed.");

        return;

    }

    const result = await response.json();

    // Update global variables
    notes = result.notes;

    totalNotes = result.total;

    currentPage = 1;

    // Display notes
    displayNotes();

    updatePagination();

    clearSearchBtn.style.display = "flex";

    // Update count
    noteCount.textContent =
        `Showing ${notes.length} of ${totalNotes} Notes`;

    // Show clear button
    clearSearchBtn.style.display = "flex";

    // Message
    showMessage(
        `${totalNotes} note(s) found.`,
        "info"
    );

}


/* ========== show and hide clear filter =================== */
async function clearSearch() {

    // Clear normal search
    searchInput.value = "";

    // clear smart search
    smartSearchInput.value = "";

    // Clear binary search
    lookupTitle.value = "";

    // Reset binary search algorithm
    lookupAlgo.value = "iterative";

    // Reset sorting
    sortBy.selectedIndex = 0;
    currentSort = "";

    // Remove active quick tag
    document
        .querySelectorAll(".tag-btn")
        .forEach(button => {

            button.classList.remove("active");

        });

    // Reset pagination
    currentPage = 1;

    // Hide clear filter button
    clearSearchBtn.style.display = "none";

    // Load original notes
    await loadNotes();

    showMessage(
        "All filters cleared.",
        "success"
    );

}

const clearSearchBtn = document.getElementById("clearSearchBtn");

clearSearchBtn.addEventListener("click", clearSearch);


/* smart search */
async function smartSearch() {

    const query = smartSearchInput.value.trim();

    if (!query) {

        showMessage("Enter search text.", "warning");

        return;

    }

    try {

        const response = await fetch(
            `http://127.0.0.1:8000/notes/smart-search?q=${encodeURIComponent(query)}`
        );

        if (!response.ok) {

            throw new Error("Smart Search failed.");

        }

        const results = await response.json();

        notes = results;

        totalNotes = results.length;

        currentPage = 1;

        displayNotes(results);

        updatePagination();

        clearSearchBtn.style.display = "flex";

        showMessage("Smart Search completed.");

    }

    catch (error) {

        console.error(error);

        showMessage("Unable to perform Smart Search.", "error");

    }

}
smartSearchBtn.addEventListener(
    "click",
    smartSearch
);
smartSearchInput.addEventListener(
    "keypress",
    function (event) {

        if (event.key === "Enter") {

            smartSearch();

        }

    }
);


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
    noteCount.textContent = `${totalNotes} Notes`;
    
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
            
            ${note.ai_suggestion ? (() => {

                const currentTag = (note.tags || "").trim().toLowerCase();

                const suggestedTag = note.ai_suggestion.tags.find(
                    tag => tag.toLowerCase() !== currentTag
                );

                return `

                    <div class="ai-panel">

                        <h4>🤖 AI Suggests</h4>

                        <p>

                            <strong>Summary:</strong>

                            ${note.ai_suggestion.summary}

                        </p>

                        <div class="ai-tags">

                            ${note.ai_suggestion.tags.map(tag => `

                                <span class="ai-tag">

                                    ${tag}

                                </span>

                            `).join("")}

                        </div>

                        ${
                            suggestedTag

                            ?

                            `
                                <div class="ai-action-buttons">

                                    <button
                                        class="apply-tag-btn"
                                        data-id="${note.id}"
                                        data-tag="${suggestedTag}">

                                        Apply "${suggestedTag}" as Tag

                                    </button>

                                    <button
                                        class="close-ai-btn"
                                        data-id="${note.id}">

                                        Close

                                    </button>

                                </div>
                            `

                            :

                            `
                                <div class="ai-action-buttons">

                                    <button
                                        class="apply-tag-btn"
                                        disabled>

                                        ✓ Already Applied

                                    </button>

                                    <button
                                        class="close-ai-btn"
                                        data-id="${note.id}">

                                        Close

                                    </button>

                                </div>
                            `
                        }

                    </div>

                `;

            })() : ""}





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

        const applyBtn = card.querySelector(".apply-tag-btn");

        if (applyBtn && !applyBtn.disabled) {

            applyBtn.addEventListener("click", () => {

                applySuggestedTag(

                    note.id,

                    applyBtn.dataset.tag

                );

             });

        }

        const closeBtn = card.querySelector(".close-ai-btn");
        if(closeBtn){
            console.log("close button")
            closeBtn.addEventListener("click", () => {
                loadNotes()
            })
        }
        
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

/* sorting */
async function loadSortedNotes() {

    try {

        const skip = (currentPage - 1) * notesPerPage;

        const response = await fetch(
            `http://127.0.0.1:8000/notes/search` +
            `?sort_by=${encodeURIComponent(currentSort)}` +
            `&skip=${skip}` +
            `&limit=${notesPerPage}`
        );

        if (!response.ok) {
            throw new Error("Failed to load sorted notes");
        }

        const data = await response.json();

        notes = data.notes;
        totalNotes = data.total;

        displayNotes();
        updatePagination();
        clearSearchBtn.style.display = "flex";

    }
    catch (error) {

        console.error(error);
        alert("Unable to sort notes.");

    }
}


sortBy.addEventListener("change", async () => {

    currentSort = sortBy.value;

    currentPage = 1;

    if (currentSort === "") {
        await loadNotes();
    } else {
        await loadSortedNotes();
    }

});

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

    showMessage("Edit mode enabled. Update the note and click 'Update Note'.", "info");

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
                method: "DELETE",
                headers: {
                    "x-token": "zomato123"
                }
            }
        );

        if (!response.ok) {
            throw new Error("Failed to delete note");
        }
        // If last note on current page is deleted,
        // go to previous page (except Page 1)
        if (notes.length === 1 && currentPage > 1) {

            currentPage--;

        }

        await loadNotes();
        // Reload reports
        await loadReports();
        showMessage("Note deleted successfully.");

    }

    catch (error) {

        console.error(error);

        showMessage("Unable to delete note.", "error");

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

        if (currentSort) {
            await loadSortedNotes();
        } else {
            await loadNotes();
        }

        this.blur();

    }

});

nextBtn.addEventListener("click", async function (e) {

    e.preventDefault();

    const totalPages = Math.ceil(totalNotes / notesPerPage);

    if (currentPage < totalPages) {

        currentPage++;

        if (currentSort) {
            await loadSortedNotes();
        } else {
            await loadNotes();
        }

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
document.addEventListener("DOMContentLoaded", async () => {

    await loadNotes();

    await loadReports();

    await loadQuickTags();

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

        const savedNote = await response.json();

        // Reset form
        noteForm.reset();

        // Back to Create mode
        editingNoteId = null;

        saveBtn.innerHTML = `
            <i class="fa-solid fa-plus"></i>
            Save Note
        `;

        // Show the newly created note immediately
        if (method === "POST") {

            notes.unshift(savedNote);

            totalNotes++;

            currentPage = 1;

            displayNotes();

            updatePagination();

        }
        else {

            await loadNotes();

        }
        // Reload reports
        await loadReports();

        // Success message
        if (method === "POST") {

            showMessage("Note created successfully.");

        }
        else {

            showMessage("Note updated successfully.");

        }

    }

    catch (error) {

        console.error(error);

        showMessage("Unable to save note.", "error");

    }

}

noteForm.addEventListener("submit", createNote);


async function applySuggestedTag(noteId, newTag) {

    console.log("Note ID:", noteId);
    console.log("New Tag:", newTag);

    const payload = {
        tags: newTag
    };

    console.log("Payload:", payload);

    try {

        const response = await fetch(
            `http://127.0.0.1:8000/notes/${noteId}`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            }
        );

        const result = await response.json();

        console.log("Response:", result);

        if (!response.ok) {
            throw new Error("Unable to apply AI tag.");
        }

        showMessage(`Tag changed to "${newTag}" successfully.`);

        await loadNotes();
        await loadReports();

    }
    catch (error) {

        console.error(error);

    }

}

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
            "http://127.0.0.1:8000/notes/import?owner_id=1",
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {
            throw new Error("Import failed");
        }

        const result = await response.json();

        // Success message
        showMessage(result.message);
        bulkFile.value = "";

        importStatus.textContent = "No file selected.";

        await loadNotes();
        // Reload reports
        await loadReports();

    }
    catch (error) {

        console.error(error);

        showMessage("Unable to import notes.", "error");

    }

}

async function lookupNote(){

    const title = document
        .getElementById("lookupTitle")
        .value
        .trim();

    const algo = document
        .getElementById("lookupAlgo")
        .value;

    if(title === ""){

        alert("Enter title");

        return;

    }

    try{

        const response = await fetch(

            `http://127.0.0.1:8000/notes/lookup` +

            `?title=${encodeURIComponent(title)}` +

            `&algo=${algo}`

        );

        if(!response.ok){

            throw new Error();

        }

        const note = await response.json();

        displayLookupResult(note);

    }

    catch{

        alert("Note not found.");

    }

}

function displayLookupResult(note){

    notes = [note];

    totalNotes = 1;

    displayNotes();

    updatePagination();
    clearSearchBtn.style.display = "flex";

}
document
.getElementById("lookupBtn")
.addEventListener(

    "click",

    lookupNote

);

/* quick tag jump */

async function loadQuickTags() {
    
    try {

        const response = await fetch(
            "http://127.0.0.1:8000/reports/tags"
        );
        
        if (!response.ok) {
            throw new Error("Unable to load tags");
        }

        const tags = await response.json();
        
        const container = document.getElementById("quickTagButtons");
        
        container.innerHTML = "";

        tags.forEach(tag => {

            const tagbtn = document.createElement("button");

            tagbtn.className = "tag-btn";

            tagbtn.textContent = tag.tag;

            tagbtn.addEventListener("click", async () => {

                document
                    .querySelectorAll(".tag-btn")
                    .forEach(button => {

                    button.classList.remove("active");

                    });

                tagbtn.classList.add("active");

                await quickFind(tag.tag);

            });

            container.appendChild(tagbtn);

            tagbtn.addEventListener("click", async () => {

                document
                    .querySelectorAll(".tag-btn")
                    .forEach(button => {

                        button.classList.remove("active");

                    });

                // Add active only to the clicked button
                tagbtn.classList.add("active");

                await quickFind(tag.tag);

            });

        });

    }
    catch (error) {

        console.error(error);

    }

}

/* Quick Tag Jump */

async function quickFind(tag) {

    try {

        const response = await fetch(

            `http://127.0.0.1:8000/notes/quick-find?tag=${encodeURIComponent(tag)}`

        );

        if (!response.ok) {

            throw new Error("No matching note found");

        }

        const note = await response.json();

        // Show only the matched note
        notes = [note];

        totalNotes = 1;

        currentPage = 1;

        displayNotes();

        updatePagination();
        clearSearchBtn.style.display = "flex";

        noteCount.textContent = "Showing 1 Matching Note";

        pageInfo.textContent = "Quick Tag Result";

        prevBtn.disabled = true;

        nextBtn.disabled = true;

        clearSearchBtn.style.display = "flex";

        showMessage(

            `Showing first "${tag}" note.`,

            "info"

        );

    }

    catch (error) {

        console.error(error);

        alert("No matching note found.");

    }

}