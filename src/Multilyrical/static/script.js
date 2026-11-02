const songBtn = document.getElementById("song-identify");
const saveBtn = document.getElementById("save-song");
const savedContainer = document.getElementById("saved");

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
        })

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
        card.className = "song-card";

        if (song.art) {
            const img = document.createElement("img");
            img.src = song.art;
            img.alt = `Album artwork for ${song.title}`;
            img.width = 150;
            card.appendChild(img);
        }

        const title = document.createElement("h3");
        const link = document.createElement("a");

        link.href = `/song/${encodeURIComponent(song.id)}`;
        link.textContent = song.title;

        title.appendChild(link);
        card.appendChild(title);

        const artist = document.createElement("p");
        artist.textContent = song.artist;
        card.appendChild(artist);

        const album = document.createElement("p");
        album.textContent = song.album || "";
        card.appendChild(album);

        const removeBtn = document.createElement("button");
        removeBtn.textContent = "Remove";

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

if (songBtn) songBtn.addEventListener("click", idSong);
if (saveBtn) saveBtn.addEventListener("click", saveSong);
if (savedContainer) {
    showSaved();
}