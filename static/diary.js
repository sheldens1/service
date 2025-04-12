function toggleEntry(card) {
    const body = card.querySelector('.entry-body');
    const arrow = card.querySelector('.arrow');
    card.classList.toggle('open');
    if (card.classList.contains('open')) {
        body.style.maxHeight = body.scrollHeight + "px";
        arrow.style.transform = "rotate(180deg)";
    } else {
        body.style.maxHeight = null;
        arrow.style.transform = "rotate(0deg)";
    }
}

function toggleTheme() {
document.body.classList.toggle('dark-theme');
}

function toggleEntry(card) {
const body = card.querySelector('.entry-body');
const arrow = card.querySelector('.arrow');
card.classList.toggle('open');
if (card.classList.contains('open')) {
    body.style.maxHeight = body.scrollHeight + "px";
    arrow.style.transform = "rotate(180deg)";
} else {
    body.style.maxHeight = null;
    arrow.style.transform = "rotate(0deg)";
}
}
