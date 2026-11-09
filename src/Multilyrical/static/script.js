const songBtn = document.getElementById("song-identify");
const saveBtn = document.getElementById("save-song");
const savedContainer = document.getElementById("saved");
const playlistBtn = document.getElementById("save-to-playlist");
const playlistsContainer = document.getElementById("playlists-container");
const dialog = document.getElementById("app-dialog");
const dialogTitle = dialog?.querySelector("h3");
const dialogMessage = dialog?.querySelector("p");
const dialogInput = dialog?.querySelector("input");
const dialogConfirm = dialog?.querySelector(".dialog-confirm");
const dialogCancel = dialog?.querySelector(".dialog-cancel");

function showDialog(title, options = {}) {
    if (!dialog) return Promise.resolve(null);

    const { message, customContent, confirmText = "OK", cancelText = "Cancel", showInput = false, inputPlaceholder = "" } = options;

    return new Promise((resolve) => {
        let closed = false;
        dialogTitle.textContent = title;
        dialogMessage.textContent = message || "";
        dialogInput.style.display = showInput ? "block" : "none";
        dialogInput.placeholder = inputPlaceholder;
        dialogInput.value = "";
        dialogConfirm.textContent = confirmText;
        dialogCancel.textContent = cancelText;
        dialogCancel.style.display = cancelText ? "inline-flex" : "none";

        // clear previous content
        const oldCustom = dialog.querySelector(".dialog-custom");
        if (oldCustom) oldCustom.remove();

        if (customContent) {
            const wrapper = document.createElement("div");
            wrapper.className = "dialog-custom";
            wrapper.appendChild(customContent);
            dialogMessage.parentNode.insertBefore(wrapper, dialogMessage.nextSibling);
        }

        const cleanup = () => {
            if (closed) return;
            closed = true;
            dialog.close();
            dialogConfirm.onclick = null;
            dialogCancel.onclick = null;
            dialog.onclose = null;
            const c = dialog.querySelector(".dialog-custom");
            if (c) c.remove();
        };

        dialogConfirm.onclick = () => {
            cleanup();
            resolve(showInput ? dialogInput.value : true);
        };

        dialogCancel.onclick = () => {
            cleanup();
            resolve(null);
        };

        dialog.onclose = () => {
            cleanup();
            resolve(null);
        };

        dialog.showModal();
        if (showInput) setTimeout(() => dialogInput.focus(), 0);
    });
}

function showAlert(title, message) {
    return showDialog(title, { message, confirmText: "OK", cancelText: null });
}

async function idSong() {
    try {
        songBtn.disabled = true;
        songBtn.textContent = "Listening...";

        const result = document.getElementById("song-result");
        result.textContent = "Listening for 5 seconds...";

        const response = await fetch("/identify", { 
            method: "POST" 
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Song identification failed.");
        }
        const params = new URLSearchParams({ 
            artist: data.artist, 
            title: data.title 
        });
        window.location.href = `/results?${params.toString()}`;
    } catch (error) {
        document.getElementById("song-result").textContent = 
        `Error: ${error.message}`;
    } finally {
        songBtn.disabled = false;
        songBtn.textContent = "Identify Song";
    }
}

function saveSong() {
    let saved = JSON.parse(
        localStorage.getItem("saved") || "[]"
    );

    const song = {
        id: saveBtn.dataset.id,
        title: saveBtn.dataset.title,
        artist: saveBtn.dataset.artist,
        album: saveBtn.dataset.album,
        art: saveBtn.dataset.art
    };

    if (!saved.some(item => item.id === song.id)) {
        saved.push(song);
        localStorage.setItem(
            "saved", 
            JSON.stringify(saved)
        );
        saveBtn.textContent = "Added to Favorites!";
    } 
    else {
        saveBtn.textContent = "Song is already in Favorites!";
    }
}

// TODO: refactor to show favorites in rows
function showSaved() {
    let saved = JSON.parse(
        localStorage.getItem("saved") || "[]"
    );
    savedContainer.innerHTML = "";

    if (saved.length === 0) {
        savedContainer.textContent = "Your Favorites collection is empty.";
        return;
    }

    saved.forEach(song => {
        const card = document.createElement("div");
        const title = document.createElement("h3");
        const link = document.createElement("a");

        card.className = "song-card";
        link.className = "song-link";
        
        link.href = `/song/${encodeURIComponent(song.id)}`;
        
        if (song.art) {
            const img = document.createElement("img");
            img.src = song.art;
            img.alt = `Album artwork for ${song.title}`;
            img.className = "album-art";

            link.appendChild(img);
        }

        link.appendChild(document.createTextNode(song.title));
        card.appendChild(title);
    
        const artist = document.createElement("p");
        artist.className = "artist-name"
        artist.textContent = `by ${song.artist}`;

        title.appendChild(link);
        title.appendChild(artist);
        card.appendChild(title);

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "Remove";
        removeBtn.className = "btn btn-sm btn-danger";
        removeBtn.addEventListener("click", () => {
            saved = saved.filter(item => item.id !== song.id);
            localStorage.setItem(
                "saved", 
                JSON.stringify(saved)
            );
            showSaved();
        });
        card.appendChild(removeBtn);
        savedContainer.appendChild(card);
    });
}

async function selectPlaylist() {
    const playlists = JSON.parse(localStorage.getItem("playlists") || "{}");
    let playlistNames = Object.keys(playlists);

    function buildPlaylistList() {
        const container = document.createElement("div");
        container.className = "playlist-select-list";
        container.dataset.selected = "";

        if (playlistNames.length === 0) {
            const msg = document.createElement("p");
            msg.className = "playlist-select-empty";
            msg.textContent = "No playlists yet.";
            container.appendChild(msg);
        } 
        else {
            playlistNames.forEach(name => {
                const label = document.createElement("label");
                label.className = "playlist-select-item";

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.value = name;
                checkbox.onchange = () => updateSelection(container);

                const span = document.createElement("span");
                span.textContent = `${name} (${playlists[name].length} song${playlists[name].length !== 1 ? "s" : ""})`;

                label.appendChild(checkbox);
                label.appendChild(span);
                container.appendChild(label);
            });
        }

        const createBtn = document.createElement("button");
        createBtn.className = "btn btn-lg btn-primary playlist-select-create";
        createBtn.textContent = "+ Create New Playlist";
        createBtn.onclick = () => showCreateForm(container);
        container.appendChild(createBtn);

        return container;
    }

    function updateSelection(container) {
        const checkboxes = container.querySelectorAll('input[type="checkbox"]:checked');
        const selected = Array.from(checkboxes).map(cb => cb.value);
        container.dataset.selected = selected.join(",");
    }

    function showCreateForm(listContainer) {
        const formContainer = document.createElement("div");
        formContainer.className = "playlist-select-list";

        const input = document.createElement("input");
        input.type = "text";
        input.placeholder = "Playlist name...";
        input.style.cssText = "width: 100%; padding: 12px; border: 2px solid black; border-radius: 8px; background: #1c1350; color: white; font-family: inherit; font-size: 14px; box-sizing: border-box; margin-bottom: 16px;";
        formContainer.appendChild(input);

        const btnRow = document.createElement("div");
        btnRow.style.cssText = "display: flex; gap: 12px; justify-content: center;";

        const createBtn = document.createElement("button");
        createBtn.className = "btn btn-md btn-primary";
        createBtn.textContent = "Create";
        createBtn.onclick = () => {
            const name = input.value.trim();

            if (!name) return;

            if (playlists[name]) {
                dialogMessage.textContent = "A playlist with that name already exists!";
                return;
            }

            playlists[name] = [];

            localStorage.setItem(
                "playlists",
                JSON.stringify(playlists)
            );

            dialogMessage.textContent = "Playlist created successfully!";
            dialogMessage.style.color = "#b9ffa5";

            playlistNames = Object.keys(playlists);

            dialogConfirm.style.display = "inline-flex";
            dialogCancel.style.display = "inline-flex";

            dialogConfirm.textContent = "Add to Selected";
            dialogCancel.textContent = "Cancel";

            dialogTitle.textContent = "Save to Playlist";
            dialogMessage.textContent = "Playlist created successfully!";

            showDialogContent(buildPlaylistList());
        };

        const cancelBtn = document.createElement("button");
        cancelBtn.className = "btn btn-md btn-danger";
        cancelBtn.textContent = "Cancel";
        cancelBtn.onclick = () => {
            dialogConfirm.style.display = "inline-flex";
            dialogCancel.style.display = "inline-flex";
            dialogConfirm.textContent = "Add to Selected";
            dialogCancel.textContent = "Cancel";
            dialogTitle.textContent = "Save to Playlist";
            showDialogContent(listContainer);
        };

        btnRow.appendChild(cancelBtn);
        btnRow.appendChild(createBtn);
        formContainer.appendChild(btnRow);

        dialogTitle.textContent = "Create Playlist";
        dialogMessage.textContent = "";
        dialogConfirm.style.display = "none";
        dialogCancel.style.display = "none";

        showDialogContent(formContainer);
        input.focus();
    }

    function showDialogContent(content) {
        const oldCustom = dialog.querySelector(".dialog-custom");
        if (oldCustom) oldCustom.remove();

        const wrapper = document.createElement("div");
        wrapper.className = "dialog-custom";
        wrapper.appendChild(content);
        dialogMessage.parentNode.insertBefore(wrapper, dialogMessage.nextSibling);
    }

    const initialContainer = buildPlaylistList();

    return new Promise((resolve) => {
        let closed = false;

        const cleanup = () => {
            if (closed) return;
            closed = true;
            dialog.close();
            dialogConfirm.onclick = null;
            dialogCancel.onclick = null;
            dialog.onclose = null;
            const c = dialog.querySelector(".dialog-custom");
            if (c) c.remove();
        };

        dialogConfirm.onclick = () => {
            cleanup();
            resolve(initialContainer.dataset.selected || null);
        };

        dialogCancel.onclick = () => {
            cleanup();
            resolve(null);
        };

        dialog.onclose = () => {
            cleanup();
            resolve(null);
        };

        dialogTitle.textContent = "Save to Playlist";
        dialogMessage.textContent = "";
        dialogInput.style.display = "none";
        dialogConfirm.textContent = "Add to Selected";
        dialogCancel.textContent = "Cancel";
        dialogCancel.style.display = "inline-flex";

        showDialogContent(initialContainer);
        dialog.showModal();
    });
}

function saveToPlaylist(playlistNames) {
    const playlists = JSON.parse(localStorage.getItem("playlists") || "{}");
    const names = playlistNames.split(",").filter(n => n.trim());

    if (names.length === 0) return;

    const song = {
        id: playlistBtn.dataset.id,
        title: playlistBtn.dataset.title,
        artist: playlistBtn.dataset.artist,
        album: playlistBtn.dataset.album,
        art: playlistBtn.dataset.art
    };

    let added = 0;
    let alreadyExists = 0;

    names.forEach(name => {
        if (!playlists[name.trim()]) return;
        const playlist = playlists[name.trim()];
        if (!playlist.some(item => item.id === song.id)) {
            playlist.push(song);
            added++;
        } 
        else {
            alreadyExists++;
        }
    });

    localStorage.setItem("playlists", JSON.stringify(playlists));

    if (added > 0 && alreadyExists === 0) {
        playlistBtn.textContent = `Saved to ${added} playlist${added !== 1 ? "s" : ""}!`;
    } 
    else if (added > 0 && alreadyExists > 0) {
        playlistBtn.textContent = `Saved to ${added} playlist${added !== 1 ? "s" : ""}! (${alreadyExists} already ${alreadyExists !== 1 ? "have" : "has"} this song!)`;
    }
    else {
        playlistBtn.textContent = "Song already in selected playlist(s)";
    }
}

function showPlaylists() {
    const playlists = JSON.parse(localStorage.getItem("playlists") || "{}");
    const message = document.createElement("p");
    message.className = "std-msg"
    message.textContent = ""
    playlistsContainer.innerHTML = "";

    let playlistNames = Object.keys(playlists);

    if (playlistNames.length === 0) {
        //playlistsContainer.textContent = "No playlists yet. Create one from a song page!";
        message.textContent = "No playlists yet. Create one from a song page!";
        playlistsContainer.appendChild(message);

        return;
    }

    playlistNames.forEach(name => {
        const playlist = playlists[name];
        const card = document.createElement("div");
        card.className = "playlist-card";

        const header = document.createElement("div");
        header.className = "playlist-header";

        const title = document.createElement("h3");
        title.textContent = name;

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn btn-md btn-danger";
        deleteBtn.textContent = "Delete Playlist";
        deleteBtn.onclick = async () => {
            const confirm = await showDialog("Delete Playlist", `Delete "${name}" and all its songs?`, false, "Delete");
            if (confirm) {
                delete playlists[name];
                localStorage.setItem("playlists", JSON.stringify(playlists));
                showPlaylists();
            }
        };

        header.appendChild(title);
        header.appendChild(deleteBtn);
        card.appendChild(header);

        const count = document.createElement("p");
        count.className = "playlist-count";
        count.textContent = `${playlist.length} song${playlist.length !== 1 ? "s" : ""}`;
        card.appendChild(count);

        if (playlist.length > 0) {
            const songsList = document.createElement("div");
            songsList.className = "playlist-songs";

            playlist.forEach(song => {
                const songRow = document.createElement("div");
                songRow.className = "playlist-song";

                if (song.art) {
                    const img = document.createElement("img");
                    img.src = song.art;
                    img.alt = song.title;
                    songRow.appendChild(img);
                }

                const songLink = document.createElement("a");
                songLink.href = `/song/${encodeURIComponent(song.id)}`;
                songLink.className = "playlist-song-link";

                const songInfo = document.createElement("div");
                songInfo.className = "playlist-song-info";

                const songTitle = document.createElement("div");
                songTitle.className = "playlist-song-title";
                songTitle.textContent = song.title;

                const songArtist = document.createElement("div");
                songArtist.className = "playlist-song-artist";
                songArtist.textContent = song.artist;

                songLink.appendChild(songTitle);
                songLink.appendChild(songArtist);
                songInfo.appendChild(songLink);
                songRow.appendChild(songInfo);

                const removeSongBtn = document.createElement("button");
                removeSongBtn.className = "btn btn-sm btn-danger";
                removeSongBtn.textContent = "Remove";
                removeSongBtn.onclick = () => {
                    const idx = playlist.findIndex(s => s.id === song.id);
                    if (idx !== -1) {
                        playlist.splice(idx, 1);
                        localStorage.setItem("playlists", JSON.stringify(playlists));
                        showPlaylists();
                    }
                };
                songRow.appendChild(removeSongBtn);
                songsList.appendChild(songRow);
            });

            card.appendChild(songsList);
        } 
        else {
            const empty = document.createElement("p");
            empty.className = "playlist-empty";
            empty.textContent = "Empty playlist";
            card.appendChild(empty);
        }

        playlistsContainer.appendChild(card);
    });
}

async function loadArtwork() {
    const images = document.querySelectorAll(".results-container img");

    const artworkRequests = Array.from(images).map(async (img) => {
        const artist = img.dataset.artist;
        const title = img.dataset.title;

        try {
            const response = await fetch(
                `/artwork?artist=${encodeURIComponent(artist)}&title=${encodeURIComponent(title)}`
            );

            if (!response.ok) return;

            const data = await response.json();

            if (data.art) {
                img.src = data.art;
            }
            
        } catch (error) {
            console.error(`Could not load artwork for ${title}:`, error);
        }
    });

    await Promise.all(artworkRequests);
}

if (songBtn) songBtn.addEventListener("click", idSong);
if (saveBtn) saveBtn.addEventListener("click", saveSong);
if (savedContainer) showSaved();
if (playlistsContainer) showPlaylists();
if (playlistBtn) playlistBtn.addEventListener("click", async () => {
    const playlistName = await selectPlaylist();
    if (playlistName) saveToPlaylist(playlistName);
});

if (document.querySelector(".results-container")) {
    loadArtwork();
}