
const API_URL = "http://127.0.0.1:8000";


// =====================================
// 0. JWT AUTHENTICATION
// =====================================

async function authenticatedFetch(url, options = {}) {

    const token = sessionStorage.getItem("cleancsv_token");

    if (!token) {
        sessionStorage.removeItem("cleancsv_logged_in");
        window.location.href = "login.html";
        throw new Error("Please login first.");
    }

    const headers = {
        ...options.headers,
        "Authorization": `Bearer ${token}`
    };

    const response = await fetch(url, {
        ...options,
        headers: headers
    });

    if (response.status === 401) {

        sessionStorage.removeItem("cleancsv_token");
        sessionStorage.removeItem("cleancsv_logged_in");

        alert("Your session has expired. Please login again.");

        window.location.href = "login.html";

        throw new Error("Session expired. Please login again.");
    }

    return response;
}


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

        const response = await authenticatedFetch(
            `${API_URL}/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : JSON.stringify(data.detail || "Upload failed")
            );
        }

        sessionStorage.setItem("cleancsv_file_id", data.file_id);

        // Clear previous cleaned file information
        sessionStorage.removeItem("cleancsv_cleaned_file_id");

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

        console.error("Upload Error:", error);

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

        const response = await authenticatedFetch(
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

    if (!status || !cleanButton) {
        console.error("Cleaning page elements not found.");
        return;
    }

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

    if (handleMissing) {
        params.append("missing_method", "mean");
    }

    params.append("text_case", standardizeText ? "title" : "none");

    // Clear previous cleaned file ID before starting a new cleaning
    sessionStorage.removeItem("cleancsv_cleaned_file_id");

    cleanButton.disabled = true;

    status.textContent = "Cleaning your CSV file...";
    status.style.color = "blue";

    try {

        const response = await authenticatedFetch(
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

        // Save the cleaned file ID after successful cleaning
        sessionStorage.setItem(
            "cleancsv_cleaned_file_id",
            fileId
        );

        status.textContent =
            "CSV cleaned successfully! " +
            `Original rows: ${data.original_rows}, ` +
            `Cleaned rows: ${data.cleaned_rows}`;

        status.style.color = "green";

        console.log("CSV cleaning successful.");
        console.log("Cleaned File ID:", fileId);

    } catch (error) {

        status.textContent = "Error: " + error.message;
        status.style.color = "red";

        console.error("Cleaning Error:", error);

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

    if (!status) {
        console.error("Cleaning status element not found.");
        return;
    }

    // Check whether cleaning was completed
    if (!fileId) {

        status.textContent =
            "Please clean your CSV file first.";

        status.style.color = "red";

        return;
    }

    status.textContent = "Preparing download...";
    status.style.color = "blue";

    try {

        const response = await authenticatedFetch(
            `${API_URL}/download/${encodeURIComponent(fileId)}`
        );

        if (!response.ok) {

            let errorMessage = "Download failed.";

            try {
                const errorData = await response.json();
                errorMessage =
                    typeof errorData.detail === "string"
                        ? errorData.detail
                        : JSON.stringify(errorData.detail || errorMessage);
            } catch (parseError) {
                console.error("Could not read download error response.");
            }

            throw new Error(errorMessage);
        }

        const blob = await response.blob();

        if (blob.size === 0) {
            throw new Error("The downloaded file is empty.");
        }

        const downloadUrl = window.URL.createObjectURL(blob);

        const link = document.createElement("a");

        link.href = downloadUrl;
        link.download = "cleaned_" + fileId + ".csv";

        document.body.appendChild(link);

        link.click();

        link.remove();

        // Release the temporary download URL
        setTimeout(() => {
            window.URL.revokeObjectURL(downloadUrl);
        }, 1000);

        status.textContent =
            "Your cleaned CSV has been downloaded!";

        status.style.color = "green";

        console.log("CSV download started successfully.");

    } catch (error) {

        status.textContent =
            "Download error: " + error.message;

        status.style.color = "red";

        console.error("Download Error:", error);

    }

}
