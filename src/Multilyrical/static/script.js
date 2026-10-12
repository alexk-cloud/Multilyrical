const songBtn = document.getElementById("song-identify");
const searchBar = document.getElementById("song-search");

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

        result.textContent = `${data.artist} - ${data.title}`;
        
    } catch (error) {
        document.getElementById("song-result").textContent = 
            `Error: ${error.message}`;
    } finally {
        songBtn.disabled = false;
        songBtn.textContent = "Identify song";
    }
}

function searchSong() {
    //TODO: write code for song search
}

songBtn.addEventListener("click", idSong);
searchBar.addEventListener("input", searchSong);