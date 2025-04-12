document.addEventListener("DOMContentLoaded", function() {
    // Musik tetap lanjut tanpa restart saat pindah halaman
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

  
});