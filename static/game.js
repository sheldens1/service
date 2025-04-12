function cekJawaban() {
    var jawaban = document.getElementById("jawaban").value.toLowerCase();
    var hasil = document.getElementById("hasil");

    if (jawaban === "lucky") { // Ganti dengan jawaban yang sesuai
        hasil.innerHTML = "✅ Benar! Kamu masih inget ya?";
        hasil.style.color = "lightgreen";

        // Efek transisi sebelum pindah halaman
        setTimeout(() => {
            document.body.style.opacity = "0";
            setTimeout(() => {
                window.location.href = "secret.html"; // Ganti dengan halaman tujuan
            }, 1000);
        }, 2000); // Tunggu 2 detik sebelum pindah
    } else {
        hasil.innerHTML = "❌ Salah! Coba lagi!";
        hasil.style.color = "red";
    }
}

// Animasi Daun Jatuh
document.addEventListener("DOMContentLoaded", function() {
    let daunContainer = document.getElementById("daun-container");
    
    function createLeaf() {
        let leaf = document.createElement("div");
        leaf.classList.add("daun");
        leaf.style.left = Math.random() * 100 + "vw";
        leaf.style.animationDuration = (Math.random() * 3 + 2) + "s";
        daunContainer.appendChild(leaf);

        setTimeout(() => {
            leaf.remove();
        }, 5000);
    }

    setInterval(createLeaf, 500);
});