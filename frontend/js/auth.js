
// =====================================
// CLEANCSV PAGE AUTHENTICATION
// =====================================

// Check whether the user is logged in
(function () {

    const token = sessionStorage.getItem("cleancsv_token");

    if (!token) {
        window.location.replace("login.html");
        return;
    }

    // Logout functionality
    const logoutButton = document.getElementById("logoutButton");

    if (logoutButton) {

        logoutButton.addEventListener("click", function (event) {

            event.preventDefault();

            // Clear login and temporary session data
            sessionStorage.clear();

            alert("You have logged out successfully!");

            // Return to login page
            window.location.replace("login.html");

        });

    }

})();
