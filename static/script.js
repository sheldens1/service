document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("toggleSettings");
    const panel = document.getElementById("settingsPanel");
    let isOpen = false;
    let sudahDitutup = false;

    toggleBtn.addEventListener("click", function () {
        if (sudahDitutup) return;

        if (!isOpen) {
            panel.classList.add("active");
            isOpen = true;
        } else {
            panel.classList.remove("active");
            sudahDitutup = true; // habis nutup ga bisa dibuka lagi
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("toggleSettings");
    const panel = document.getElementById("settingsPanel");

    toggleBtn.addEventListener("click", function () {
        panel.classList.toggle("active");
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById('toggleSettings');
    const panel = document.getElementById('settingsPanel');

    toggleBtn.addEventListener('click', () => {
        panel.classList.toggle('show');
    });
});