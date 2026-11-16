
const API_URL = "http://127.0.0.1:8000";

// CSV Upload
const fileInput = document.getElementById("csvFile");

if (fileInput) {
    fileInput.addEventListener("change", function () {
        const file = this.files[0];

        document.getElementById("fileName").textContent =
            file ? file.name : "No file selected";
    });
}

async function uploadCSV() {
    const file = fileInput?.files[0];
    const message = document.getElementById("message");

    if (!file) {
        message.textContent = "Please select a CSV file!";
        message.style.color = "red";
        return;
    }

    if (!file.name.toLowerCase().endsWith(".csv")) {
        message.textContent = "Only CSV files are allowed!";
        message.style.color = "red";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    message.textContent = "Uploading your CSV...";
    message.style.color = "blue";

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Upload failed");
        }

        sessionStorage.setItem("cleancsv_file_id", data.file_id);

        message.style.color = "green";
        message.innerHTML = `
            <strong>${data.message}</strong><br>
            File: ${data.filename}<br>
            Rows: ${data.rows}<br>
            Columns: ${data.columns}<br>
            File ID: ${data.file_id}
        `;

    } catch (error) {
        message.textContent = "Error: " + error.message;
        message.style.color = "red";
    }
}


// Cleaning option selection preview
function previewCleaning() {
    const operations = [];

    const options = [
        ["duplicates", "Remove Duplicate Rows"],
        ["missing", "Handle Missing Values"],
        ["spaces", "Remove Extra Spaces"],
        ["format", "Standardize Text Formatting"],
        ["types", "Convert Data Types"]
    ];

    options.forEach(([id, name]) => {
        const checkbox = document.getElementById(id);

        if (checkbox && checkbox.checked) {
            operations.push(name);
        }
    });

    const message = document.getElementById("cleanMessage");
    const preview = document.getElementById("previewMessage");

    if (operations.length === 0) {
        message.textContent = "Please select at least one operation.";
        preview.textContent = "No operations selected.";
        return;
    }

    message.textContent =
        "Selected operations: " + operations.length;

    preview.innerHTML = operations
        .map(operation => "✓ " + operation)
        .join("<br>");
}
