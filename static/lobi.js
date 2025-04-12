document.addEventListener("DOMContentLoaded", function() {
    let audio = document.getElementById("bg-music");
    if (audio) {
        let savedTime = sessionStorage.getItem("musicTime");
        if (savedTime) {
            audio.currentTime = savedTime;
        }
        if (!sessionStorage.getItem("musicPlaying")) {
            sessionStorage.setItem("musicPlaying", "true");
            audio.play();
        }
        window.addEventListener("beforeunload", function() {
            sessionStorage.setItem("musicTime", audio.currentTime);
        });
    }

    document.querySelector(".dropdown-header").addEventListener("click", function() {
        let content = document.querySelector(".dropdown-content");
        let icon = document.querySelector(".dropdown-icon");
        content.classList.toggle("show");
        icon.classList.toggle("rotate");
    });
});
