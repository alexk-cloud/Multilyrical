const songBtn = document.getElementById("song-identify");
const searchBar = document.getElementById("song-search");
const searchBtn = document.getElementById("search-button");

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
        songBtn.textContent = "Identify song";
    }
}

/*
async function searchSong() {
    let input = searchBar.value.trim();

    if (!input) {
        alert("Please enter a song to search for.");
        return;
    }
    
    try {
        const response = await fetch("/search", 
            {method: "POST", 
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: input })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Search attempt failed.")
        }

        console.log(data);
    }
    catch (error) {
        console.error(error)
        alert(error.message);
    }
}
*/

songBtn.addEventListener("click", idSong);
//searchBtn.addEventListener("click", searchSong);