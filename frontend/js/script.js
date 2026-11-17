
const API_URL = "http://127.0.0.1:8000";


// =====================================
// 1. CSV UPLOAD
// =====================================

const fileInput = document.getElementById("csvFile");

if (fileInput) {
    fileInput.addEventListener("change", function () {
        const file = this.files[0];
        const fileName = document.getElementById("fileName");

        if (fileName) {
            fileName.textContent = file
                ? file.name
                : "No file selected";
        }
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
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : JSON.stringify(data.detail || "Upload failed")
            );
        }

        sessionStorage.setItem("cleancsv_file_id", data.file_id);

        message.style.color = "green";

        message.textContent =
            `${data.message}\n` +
            `File: ${data.filename}\n` +
            `Rows: ${data.rows}\n` +
            `Columns: ${data.columns}\n` +
            `File ID: ${data.file_id}`;

    } catch (error) {

        message.textContent = "Error: " + error.message;
        message.style.color = "red";

    }
}


// =====================================
// 2. CLEANING OPTION PREVIEW
// =====================================

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

    if (!message || !preview) {
        return;
    }

    if (operations.length === 0) {

        message.textContent = "Please select at least one operation.";
        preview.textContent = "No operations selected.";

        return;
    }

    message.textContent = "Selected operations: " + operations.length;

    preview.textContent = operations
        .map(operation => "✓ " + operation)
        .join("\n");

}


// =====================================
// 3. DASHBOARD - LOAD REAL CSV ANALYSIS
// =====================================

async function loadDashboard() {

    const message = document.getElementById("dashboardMessage");

    if (!message) {
        return;
    }

    const fileId = sessionStorage.getItem("cleancsv_file_id");

    const datasetName = document.getElementById("datasetName");
    const tableBody = document.getElementById("issuesTableBody");
    const columnList = document.getElementById("columnList");

    if (!fileId) {

        message.textContent =
            "No dataset found. Please upload a CSV file first.";

        message.style.color = "red";

        datasetName.textContent = "No dataset uploaded";

        document.getElementById("totalRows").textContent = "--";
        document.getElementById("totalColumns").textContent = "--";
        document.getElementById("missingValues").textContent = "--";
        document.getElementById("duplicateRows").textContent = "--";

        tableBody.textContent = "";

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 3;
        cell.textContent = "Please upload a CSV file first.";

        row.appendChild(cell);
        tableBody.appendChild(row);

        return;
    }

    message.textContent = "Fetching analysis results...";
    message.style.color = "blue";

    try {

        const response = await fetch(
            `${API_URL}/analysis/${encodeURIComponent(fileId)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : JSON.stringify(data.detail || "Analysis failed")
            );
        }

        if (!data.analysis || !data.missing_values || !data.duplicates) {
            throw new Error("Unexpected analysis response from backend.");
        }

        datasetName.textContent =
            data.filename || "Uploaded Dataset";

        document.getElementById("totalRows").textContent =
            data.analysis.total_rows ?? "--";

        document.getElementById("totalColumns").textContent =
            data.analysis.total_columns ?? "--";

        document.getElementById("missingValues").textContent =
            data.missing_values.total_missing_values ?? "--";

        document.getElementById("duplicateRows").textContent =
            data.duplicates.total_duplicates ?? "--";

        tableBody.textContent = "";

        let issueFound = false;

        const missingDetails =
            data.missing_values.missing_details || {};

        Object.entries(missingDetails).forEach(
            ([column, details]) => {

                const count = Number(details.missing_count || 0);

                if (count > 0) {

                    issueFound = true;

                    const row = document.createElement("tr");

                    const columnCell = document.createElement("td");
                    columnCell.textContent = column;

                    const issueCell = document.createElement("td");
                    issueCell.textContent = "Missing Values";

                    const countCell = document.createElement("td");
                    countCell.textContent = count;

                    row.appendChild(columnCell);
                    row.appendChild(issueCell);
                    row.appendChild(countCell);

                    tableBody.appendChild(row);

                }

            }
        );

        const duplicateCount =
            Number(data.duplicates.total_duplicates || 0);

        if (duplicateCount > 0) {

            issueFound = true;

            const row = document.createElement("tr");

            const columnCell = document.createElement("td");
            columnCell.textContent = "Entire Dataset";

            const issueCell = document.createElement("td");
            issueCell.textContent = "Duplicate Rows";

            const countCell = document.createElement("td");
            countCell.textContent = duplicateCount;

            row.appendChild(columnCell);
            row.appendChild(issueCell);
            row.appendChild(countCell);

            tableBody.appendChild(row);

        }

        if (!issueFound) {

            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 3;
            cell.textContent =
                "No missing values or duplicate rows found.";

            row.appendChild(cell);
            tableBody.appendChild(row);

        }

        columnList.textContent = "";

        const columns = data.analysis.column_names || [];

        columns.forEach(column => {

            const item = document.createElement("li");
            item.textContent = column;
            columnList.appendChild(item);

        });

        message.textContent = "Analysis loaded successfully!";
        message.style.color = "green";

    } catch (error) {

        message.textContent =
            "Error loading analysis: " + error.message;

        message.style.color = "red";

        console.error("Dashboard Error:", error);

    }

}


// =====================================
// 4. RUN DASHBOARD WHEN PAGE LOADS
// =====================================

document.addEventListener("DOMContentLoaded", function () {

    if (document.getElementById("dashboardMessage")) {
        loadDashboard();
    }

});


// =====================================
// 5. CLEAN CSV FILE
// =====================================

async function cleanCSV() {

    const fileId = sessionStorage.getItem("cleancsv_file_id");

    const status = document.getElementById("cleanStatus");
    const cleanButton = document.getElementById("cleanButton");
    const downloadButton = document.getElementById("downloadButton");

    if (!fileId) {
        status.textContent = "Please upload a CSV file first.";
        status.style.color = "red";
        return;
    }

    const removeDuplicates =
        document.getElementById("duplicates").checked;

    const handleMissing =
        document.getElementById("missing").checked;

    const standardizeText =
        document.getElementById("format").checked;

    const removeSpaces =
        document.getElementById("spaces").checked;

    if (
        !removeDuplicates &&
        !handleMissing &&
        !standardizeText &&
        !removeSpaces
    ) {
        status.textContent =
            "Please select at least one supported cleaning operation.";

        status.style.color = "red";
        return;
    }

    const params = new URLSearchParams();

    params.append("remove_dups", removeDuplicates);

    // Send missing_method only when missing-value handling is selected.
    if (handleMissing) {
        params.append("missing_method", "mean");
    }

    params.append("text_case", standardizeText ? "title" : "none");

    cleanButton.disabled = true;
    downloadButton.disabled = true;

    status.textContent = "Cleaning your CSV file...";
    status.style.color = "blue";

    try {

        const response = await fetch(
            `${API_URL}/clean/${encodeURIComponent(fileId)}?${params.toString()}`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : JSON.stringify(data.detail || "Cleaning failed")
            );
        }

        sessionStorage.setItem(
            "cleancsv_cleaned_file_id",
            fileId
        );

        status.textContent =
            "CSV cleaned successfully! " +
            `Original rows: ${data.original_rows}, ` +
            `Cleaned rows: ${data.cleaned_rows}`;

        status.style.color = "green";

        downloadButton.disabled = false;

    } catch (error) {

        status.textContent = "Error: " + error.message;
        status.style.color = "red";

    } finally {

        cleanButton.disabled = false;

    }

}


// =====================================
// 6. DOWNLOAD CLEANED CSV
// =====================================

async function downloadCSV() {

    const fileId = sessionStorage.getItem("cleancsv_cleaned_file_id");

    const status = document.getElementById("cleanStatus");

    if (!fileId) {
        status.textContent = "Please clean your CSV file first.";
        status.style.color = "red";
        return;
    }

    status.textContent = "Preparing download...";
    status.style.color = "blue";

    try {

        const response = await fetch(
            `${API_URL}/download/${encodeURIComponent(fileId)}`
        );

        if (!response.ok) {
            const errorData = await response.json();

            throw new Error(
                typeof errorData.detail === "string"
                    ? errorData.detail
                    : "Download failed"
            );
        }

        const blob = await response.blob();

        const downloadUrl = window.URL.createObjectURL(blob);

        const link = document.createElement("a");

        link.href = downloadUrl;
        link.download = "cleaned_" + fileId + ".csv";

        document.body.appendChild(link);
        link.click();

        link.remove();

        window.URL.revokeObjectURL(downloadUrl);

        status.textContent = "Your cleaned CSV has been downloaded!";
        status.style.color = "green";

    } catch (error) {

        status.textContent = "Download error: " + error.message;
        status.style.color = "red";

    }

}
