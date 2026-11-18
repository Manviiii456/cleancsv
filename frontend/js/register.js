
const registerForm = document.getElementById("registerForm");

registerForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword =
        document.getElementById("confirmPassword").value;

    const message = document.getElementById("registerMessage");

    if (password !== confirmPassword) {
        message.textContent = "Passwords do not match!";
        message.style.color = "red";
        return;
    }

    message.textContent = "Creating your account...";
    message.style.color = "blue";

    try {

        const response = await fetch(
            "http://localhost:8000/auth/register",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            const errorMessage =
                typeof data.detail === "string"
                    ? data.detail
                    : JSON.stringify(data.detail || "Registration failed");

            throw new Error(errorMessage);
        }

        message.textContent =
            data.message || "Registration successful! Please login.";

        message.style.color = "green";

        alert("Account created successfully! Please login.");

        window.location.href = "login.html";

    } catch (error) {

        message.textContent = error.message;
        message.style.color = "red";

        console.error("Registration Error:", error);

    }

});
