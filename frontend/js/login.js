
const password = document.getElementById("password");
const monkey = document.getElementById("monkey");
const loginForm = document.getElementById("loginForm");


// =====================================
// 1. MONKEY HAND ANIMATION
// =====================================

// When password field is clicked
password.addEventListener("focus", function () {
    monkey.classList.add("hide");
});

// When password field loses focus
password.addEventListener("blur", function () {
    monkey.classList.remove("hide");
});


// =====================================
// 2. REAL BACKEND LOGIN
// =====================================

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const userPassword = password.value;

    try {

        const response = await fetch("http://localhost:8000/auth/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: userPassword
            })

        });

        const data = await response.json();

        if (response.ok) {

            sessionStorage.setItem(
                "cleancsv_token",
                data.access_token
            );

            sessionStorage.setItem(
                "cleancsv_logged_in",
                "true"
            );

            alert("Login successful!");

            window.location.href = "index.html";

        } else {

            alert(data.detail || "Invalid email or password");

        }

    } catch (error) {

        alert("Cannot connect to the server. Please try again.");

        console.error("Login Error:", error);

    }

});
