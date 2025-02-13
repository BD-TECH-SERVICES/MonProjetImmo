
document.addEventListener("DOMContentLoaded", function() {
    let loadingDiv = document.querySelector(".loading");
    if (loadingDiv) {
        loadingDiv.style.display = "none"; // ✅ Cache le llsff oader après chargement
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.querySelector(".theme-toggle");
    const body = document.body;

    // Vérifier si le mode sombre est activé dans localStorage
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
        themeToggle.checked = true; // Coche le switch si le mode sombre est activé
    }

    // Ajouter un écouteur d'événement pour détecter les changements d'état du switch
    themeToggle.addEventListener("change", function () {
        if (this.checked) {
            body.classList.add("dark-mode");
            localStorage.setItem("theme", "dark");
        } else {
            body.classList.remove("dark-mode");
            localStorage.setItem("theme", "light");
        }
    });
});
