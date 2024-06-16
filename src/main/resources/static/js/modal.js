const modal = document.getElementById("networkModal");
const span = document.getElementsByClassName("close")[0];


span.onclick = function() {
    modal.style.display = "none";
    document.getElementById('Network').style.display = 'none';
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
        document.getElementById('Network').style.display = 'none';
    }
}