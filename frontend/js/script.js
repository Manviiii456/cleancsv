
function previewCleaning() {

    const operations = [];

    if (document.getElementById("duplicates").checked)
        operations.push("Remove Duplicate Rows");

    if (document.getElementById("missing").checked)
        operations.push("Handle Missing Values");

    if (document.getElementById("spaces").checked)
        operations.push("Remove Extra Spaces");

    if (document.getElementById("format").checked)
        operations.push("Standardize Text Formatting");

    if (document.getElementById("types").checked)
        operations.push("Convert Data Types");

    const message = document.getElementById("cleanMessage");
    const preview = document.getElementById("previewMessage");

    if (operations.length === 0) {
        message.textContent = "Please select at least one operation.";
        preview.textContent = "No cleaning operations selected.";
        return;
    }

    message.textContent = "Selected operations: " + operations.length;

    preview.innerHTML = operations
        .map(operation => "✓ " + operation)
        .join("<br>");
}

const fileInput = document.getElementById("csvFile");

if (fileInput) {
    fileInput.addEventListener("change", function () {
        const file = this.files[0];

        document.getElementById("fileName").textContent =
            file ? file.name : "No file selected";
    });
}

function uploadCSV() {
    const file = fileInput.files[0];
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

    message.textContent = "CSV file selected successfully!";
    message.style.color = "green";
}
