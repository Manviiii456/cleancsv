
const resetForm = document.getElementById("resetPasswordForm");

resetForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();

    const newPassword =
        document.getElementById("newPassword").value;

    const confirmPassword =
        document.getElementById("confirmPassword").value;

    const message = document.getElementById("resetMessage");

    // Check whether passwords match
    if (newPassword !== confirmPassword) {

        message.textContent = "Passwords do not match!";
        message.style.color = "red";

        return;
    }

    // Check minimum password length
    if (newPassword.length < 8) {

        message.textContent =
            "Password must contain at least 8 characters.";

        message.style.color = "red";

        return;
    }

    message.textContent = "Resetting your password...";
    message.style.color = "blue";

    try {

        const response = await fetch(
            "http://localhost:8000/auth/reset-password",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    new_password: newPassword
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Password reset failed"
            );

        }

        message.textContent =
            "Password reset successful! Redirecting to login...";

        message.style.color = "green";

        alert("Password reset successful! Please login with your new password.");

        window.location.href = "login.html";

    } catch (error) {

        message.textContent = error.message;
        message.style.color = "red";

        console.error("Password Reset Error:", error);

    }

});
