// EcoQuest — small progressive-enhancement helpers (no framework needed)

document.addEventListener("DOMContentLoaded", function () {
    // Mobile nav toggle
    var toggle = document.getElementById("navToggle");
    var links = document.getElementById("navLinks");
    if (toggle && links) {
        toggle.addEventListener("click", function () {
            links.classList.toggle("open");
        });
    }

    // Auto-dismiss flash messages after a few seconds
    document.querySelectorAll(".flash").forEach(function (el) {
        setTimeout(function () {
            el.style.transition = "opacity 0.4s ease";
            el.style.opacity = "0";
            setTimeout(function () { el.remove(); }, 400);
        }, 4000);
    });

    // Quiz: highlight selected option and auto-submit on choice
    document.querySelectorAll(".quiz-option").forEach(function (label) {
        var input = label.querySelector("input[type=radio]");
        if (!input) return;
        input.addEventListener("change", function () {
            document.querySelectorAll(".quiz-option").forEach(function (l) {
                l.style.borderColor = "";
                l.style.background = "";
            });
            label.style.borderColor = "#2fb872";
            label.style.background = "#e5f7ec";
        });
    });

    // Confirm before destructive actions
    document.querySelectorAll("[data-confirm]").forEach(function (el) {
        el.addEventListener("submit", function (e) {
            if (!confirm(el.getAttribute("data-confirm"))) {
                e.preventDefault();
            }
        });
    });
});
