
document.addEventListener("DOMContentLoaded", () => {
    const $ = (id) => document.getElementById(id);

    // Upload elements
    const fileInput = $("fileInput");
    const uploadArea = $("uploadArea");
    const uploadForm = $("uploadForm");
    const previewImage = $("previewImage");
    const resultPreviewImage = $("resultPreviewImage");
    const previewPlaceholder = $("previewPlaceholder");
    const filePreviewName = $("filePreviewName");

    // Status and buttons
    const statusMessage = $("statusMessage");
    const scanButton = $("scanButton");
    const clearButton = $("clearButton");
    const copyButton = $("copyButton");
    const textOutput = $("textOutput");

    // Information outputs
    const emailsOutput = $("emailsOutput");
    const phonesOutput = $("phonesOutput");
    const datesOutput = $("datesOutput");
    const formFieldsOutput = $("formFieldsOutput");

    // Classification outputs
    const documentTypeOutput = $("documentTypeOutput");
    const classificationConfidence = $("classificationConfidence");
    const classificationMessage = $("classificationMessage");

    // Result information
    const textStats = $("textStats");
    const resultBadge = $("resultBadge");
    const excelDownloadLink = $("excelDownloadLink");

    // Create CSV link if it does not already exist
    let csvDownloadLink = $("csvDownloadLink");

    if (excelDownloadLink && !csvDownloadLink) {
        csvDownloadLink = document.createElement("a");
        csvDownloadLink.id = "csvDownloadLink";
        csvDownloadLink.className = "button-link";
        csvDownloadLink.textContent = "Download CSV";
        csvDownloadLink.href = "#";
        csvDownloadLink.hidden = true;

        excelDownloadLink.insertAdjacentElement(
            "afterend",
            csvDownloadLink
        );
    }

    // Camera elements
    const startCameraButton = $("startCameraButton");
    const switchCameraButton = $("switchCameraButton");
    const capturePhotoButton = $("capturePhotoButton");
    const stopCameraButton = $("stopCameraButton");
    const cameraPanel = $("cameraPanel");
    const cameraVideo = $("cameraVideo");
    const cameraCanvas = $("cameraCanvas");

    const MAX_SIZE = 10 * 1024 * 1024;

    const allowedExtensions = [
        ".pdf",
        ".docx",
        ".xlsx",
        ".xls",
        ".csv",
        ".txt",
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
        ".bmp"
    ];

    let selectedFile = null;
    let previewUrl = null;
    let cameraStream = null;
    let cameraFacingMode = "environment";
    let isScanning = false;
    let latestScanId = null;

    // --------------------------------------------------
    // STATUS AND BUTTONS
    // --------------------------------------------------

    function showStatus(message, type = "info") {
        if (!statusMessage) return;

        statusMessage.textContent = message;
        statusMessage.className = `status show ${type}`;
    }

    function setScanButton(disabled, label = "Scan document →") {
        if (!scanButton) return;

        scanButton.disabled = disabled;
        scanButton.textContent = label;
    }

    function displayList(element, values) {
        if (!element) return;

        element.textContent =
            Array.isArray(values) && values.length
                ? values.map(String).join(", ")
                : "None found";
    }

    // --------------------------------------------------
    // EDITABLE FORM FIELDS AND CORRECTED CSV
    // --------------------------------------------------

    function displayFormFields(fields) {
        if (!formFieldsOutput) return;

        formFieldsOutput.replaceChildren();

        if (
            !fields ||
            typeof fields !== "object" ||
            Array.isArray(fields) ||
            Object.keys(fields).length === 0
        ) {
            formFieldsOutput.textContent = "No form fields found.";
            return;
        }

        const heading = document.createElement("h3");
        heading.textContent = "Review and Edit Form Fields";
        formFieldsOutput.appendChild(heading);

        const table = document.createElement("table");
        table.className = "form-fields-table";

        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");

        ["Field Name", "Extracted Value"].forEach((text) => {
            const th = document.createElement("th");
            th.textContent = text;
            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");

        Object.entries(fields).forEach(([key, value]) => {
            const row = document.createElement("tr");

            const nameCell = document.createElement("td");
            nameCell.textContent = key;

            const valueCell = document.createElement("td");
            const input = document.createElement("input");

            input.type = "text";
            input.value = String(value ?? "");
            input.dataset.field = key;
            input.className = "extracted-field-input";
            input.setAttribute("aria-label", key);

            valueCell.appendChild(input);
            row.append(nameCell, valueCell);
            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        formFieldsOutput.appendChild(table);

        const downloadButton = document.createElement("button");
        downloadButton.type = "button";
        downloadButton.textContent = "Download Corrected CSV";
        downloadButton.className = "download-corrected-csv";

        downloadButton.addEventListener("click", () => {
            const rows = [["Field Name", "Corrected Value"]];

            formFieldsOutput
                .querySelectorAll(".extracted-field-input")
                .forEach((input) => {
                    rows.push([
                        input.dataset.field || "",
                        input.value
                    ]);
                });

            const csv = rows
                .map((row) =>
                    row
                        .map((value) =>
                            '"' +
                            String(value).replace(/"/g, '""') +
                            '"'
                        )
                        .join(",")
                )
                .join("\r\n");

            const blob = new Blob(["\uFEFF" + csv], {
                type: "text/csv;charset=utf-8;"
            });

            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download = "corrected_form_fields.csv";

            document.body.appendChild(link);
            link.click();
            link.remove();

            URL.revokeObjectURL(url);

            showStatus(
                "Corrected form fields downloaded as CSV.",
                "success"
            );
        });

        formFieldsOutput.appendChild(downloadButton);
    }

    function resetClassification() {
        if (documentTypeOutput) {
            documentTypeOutput.textContent = "Not classified yet";
        }

        if (classificationConfidence) {
            classificationConfidence.textContent = "—";
        }

        if (classificationMessage) {
            classificationMessage.textContent =
                "Scan a document to classify it.";
        }
    }

    function resetDownloads() {
        latestScanId = null;

        if (excelDownloadLink) {
            excelDownloadLink.href = "#";
            excelDownloadLink.hidden = true;
        }

        if (csvDownloadLink) {
            csvDownloadLink.href = "#";
            csvDownloadLink.hidden = true;
        }
    }

    function resetResults() {
        if (textOutput) {
            textOutput.value = "";
        }

        if (emailsOutput) {
            emailsOutput.textContent = "None found";
        }

        if (phonesOutput) {
            phonesOutput.textContent = "None found";
        }

        if (datesOutput) {
            datesOutput.textContent = "None found";
        }

        displayFormFields({});

        if (textStats) {
            textStats.textContent = "0 characters";
        }

        if (resultBadge) {
            resultBadge.textContent = "NO RESULTS YET";
        }

        resetClassification();
        resetDownloads();
    }

    // --------------------------------------------------
    // FILE PREVIEW
    // --------------------------------------------------

    function resetPreview() {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
            previewUrl = null;
        }

        if (previewImage) {
            previewImage.removeAttribute("src");
            previewImage.classList.add("hidden");
        }

        if (resultPreviewImage) {
            resultPreviewImage.removeAttribute("src");
            resultPreviewImage.classList.add("hidden");
        }

        if (previewPlaceholder) {
            previewPlaceholder.hidden = false;
        }

        if (filePreviewName) {
            filePreviewName.textContent = "";
        }
    }

    function updatePreview(file) {
        resetPreview();

        if (!file) return;

        if (filePreviewName) {
            filePreviewName.textContent = `Selected: ${file.name}`;
        }

        if (!file.type.startsWith("image/")) {
            return;
        }

        // Browser support for TIFF previews varies.
        if (/\.tiff?$/i.test(file.name)) {
            showStatus(
                "TIFF selected. Preview may be unavailable, but scanning can continue.",
                "info"
            );
            return;
        }

        previewUrl = URL.createObjectURL(file);

        if (previewImage) {
            previewImage.src = previewUrl;
            previewImage.classList.remove("hidden");
        }

        if (resultPreviewImage) {
            resultPreviewImage.src = previewUrl;
            resultPreviewImage.classList.remove("hidden");
        }

        if (previewPlaceholder) {
            previewPlaceholder.hidden = true;
        }
    }

    // --------------------------------------------------
    // FILE VALIDATION
    // --------------------------------------------------

    function selectFile(file) {
        if (!file || isScanning) return;

        const dot = file.name.lastIndexOf(".");
        const extension =
            dot >= 0 ? file.name.slice(dot).toLowerCase() : "";

        if (!allowedExtensions.includes(extension)) {
            selectedFile = null;

            if (fileInput) fileInput.value = "";

            resetPreview();
            resetResults();
            setScanButton(true);

            showStatus(
                "Unsupported file. Choose PDF, DOCX, XLSX, XLS, CSV, TXT or a supported image.",
                "error"
            );
            return;
        }

        if (file.size === 0 || file.size > MAX_SIZE) {
            selectedFile = null;

            if (fileInput) fileInput.value = "";

            resetPreview();
            resetResults();
            setScanButton(true);

            showStatus(
                file.size === 0
                    ? "The selected file is empty."
                    : "The maximum file size is 10 MB.",
                "error"
            );
            return;
        }

        selectedFile = file;

        updatePreview(file);
        resetResults();
        setScanButton(false);

        showStatus(`Ready to scan: ${file.name}`, "success");
    }

    if (fileInput) {
        fileInput.addEventListener("change", () => {
            const file = fileInput.files?.[0];

            if (file) {
                selectFile(file);
            } else {
                selectedFile = null;
                setScanButton(true);
            }
        });
    }

    // --------------------------------------------------
    // DRAG AND DROP
    // --------------------------------------------------

    if (uploadArea) {
        uploadArea.addEventListener("dragover", (event) => {
            event.preventDefault();
            uploadArea.classList.add("dragover");
        });

        uploadArea.addEventListener("dragleave", (event) => {
            if (!uploadArea.contains(event.relatedTarget)) {
                uploadArea.classList.remove("dragover");
            }
        });

        uploadArea.addEventListener("drop", (event) => {
            event.preventDefault();
            uploadArea.classList.remove("dragover");

            const file = event.dataTransfer?.files?.[0];

            if (!file) return;

            selectFile(file);

            if (selectedFile === file && fileInput) {
                try {
                    const transfer = new DataTransfer();
                    transfer.items.add(file);
                    fileInput.files = transfer.files;
                } catch (error) {
                    // selectedFile still stores the chosen file.
                }
            }
        });
    }

    // --------------------------------------------------
    // CAMERA
    // --------------------------------------------------

    async function startCamera() {
        if (
            !navigator.mediaDevices?.getUserMedia ||
            !cameraVideo ||
            !cameraPanel
        ) {
            showStatus(
                "Camera unavailable. Use localhost or HTTPS in a supported browser.",
                "error"
            );
            return;
        }

        stopCamera();

        try {
            cameraStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: { ideal: cameraFacingMode },
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                },
                audio: false
            });

            cameraVideo.srcObject = cameraStream;
            cameraPanel.classList.remove("hidden");

            if (switchCameraButton) {
                switchCameraButton.disabled = false;
            }

            await cameraVideo.play();

            showStatus(
                "Camera ready. Position your document.",
                "success"
            );
        } catch (error) {
            stopCamera();

            showStatus(
                error.name === "NotAllowedError"
                    ? "Camera permission denied. Allow camera access in browser settings."
                    : "Could not open the camera. Check its connection and permissions.",
                "error"
            );
        }
    }

    function stopCamera() {
        if (cameraStream) {
            cameraStream.getTracks().forEach((track) => track.stop());
            cameraStream = null;
        }

        if (cameraVideo) {
            cameraVideo.srcObject = null;
        }

        if (cameraPanel) {
            cameraPanel.classList.add("hidden");
        }

        if (switchCameraButton) {
            switchCameraButton.disabled = true;
        }
    }

    if (startCameraButton) {
        startCameraButton.addEventListener("click", startCamera);
    }

    if (switchCameraButton) {
        switchCameraButton.addEventListener("click", async () => {
            cameraFacingMode =
                cameraFacingMode === "environment"
                    ? "user"
                    : "environment";

            await startCamera();
        });
    }

    if (stopCameraButton) {
        stopCameraButton.addEventListener("click", () => {
            stopCamera();
            showStatus("Camera closed.", "info");
        });
    }

    if (capturePhotoButton) {
        capturePhotoButton.addEventListener("click", () => {
            if (
                !cameraStream ||
                !cameraVideo ||
                !cameraVideo.videoWidth ||
                !cameraCanvas
            ) {
                showStatus("Wait for the camera to start.", "error");
                return;
            }

            cameraCanvas.width = cameraVideo.videoWidth;
            cameraCanvas.height = cameraVideo.videoHeight;

            const context = cameraCanvas.getContext("2d");

            if (!context) {
                showStatus(
                    "Could not access the camera canvas.",
                    "error"
                );
                return;
            }

            context.drawImage(
                cameraVideo,
                0,
                0,
                cameraCanvas.width,
                cameraCanvas.height
            );

            cameraCanvas.toBlob((blob) => {
                if (!blob) {
                    showStatus(
                        "Could not capture the image.",
                        "error"
                    );
                    return;
                }

                const photo = new File(
                    [blob],
                    `camera_scan_${Date.now()}.jpg`,
                    { type: "image/jpeg" }
                );

                selectFile(photo);

                if (selectedFile === photo) {
                    if (fileInput) {
                        try {
                            const transfer = new DataTransfer();
                            transfer.items.add(photo);
                            fileInput.files = transfer.files;
                        } catch (error) {
                            // selectedFile still stores the photo.
                        }
                    }

                    stopCamera();

                    showStatus(
                        "Photo captured. Click Scan document.",
                        "success"
                    );
                }
            }, "image/jpeg", 0.95);
        });
    }

    // --------------------------------------------------
    // RESULT TABS
    // --------------------------------------------------

    function activateTab(target) {
        document.querySelectorAll(".result-tab").forEach((tab) => {
            const active = tab.dataset.tab === target;

            tab.classList.toggle("active", active);
            tab.setAttribute("aria-selected", String(active));
        });

        document.querySelectorAll(".tab-content").forEach((panel) => {
            const active = panel.dataset.panel === target;

            panel.hidden = !active;
            panel.classList.toggle("active", active);
        });
    }

    document.querySelectorAll(".result-tab").forEach((tab) => {
        tab.addEventListener("click", () => {
            activateTab(tab.dataset.tab);
        });
    });

    // --------------------------------------------------
    // DISPLAY SCAN RESULTS
    // --------------------------------------------------

    function displayScanResults(result) {
        const extractedText = result.extracted_text || "";

        if (textOutput) {
            textOutput.value = extractedText;
        }

        if (textStats) {
            textStats.textContent =
                `${extractedText.length.toLocaleString()} characters`;
        }

        const information = result.information || {};

        displayList(emailsOutput, information.emails);

        displayList(
            phonesOutput,
            information.phone_numbers || information.phones
        );

        displayList(datesOutput, information.dates);

        // Display editable form fields from app.py.
        displayFormFields(result.form_fields || {});

        const classification = result.classification || {};

        if (documentTypeOutput) {
            documentTypeOutput.textContent =
                classification.document_type || "Unknown";
        }

        if (classificationConfidence) {
            const confidence = classification.confidence;

            classificationConfidence.textContent =
                confidence !== undefined && confidence !== null
                    ? String(confidence)
                    : "Not available";
        }

        if (classificationMessage) {
            classificationMessage.textContent =
                classification.message ||
                "No classification details available.";
        }

        latestScanId = result.scan_id ?? null;

        if (latestScanId !== null) {
            const excelUrl =
                result.excel_download ||
                `/download/excel/${encodeURIComponent(latestScanId)}`;

            if (excelDownloadLink) {
                excelDownloadLink.href = excelUrl;
                excelDownloadLink.hidden = false;
            }

            if (csvDownloadLink) {
                csvDownloadLink.href =
                    `/download/csv/${encodeURIComponent(latestScanId)}`;
                csvDownloadLink.hidden = false;
            }
        } else {
            resetDownloads();
        }

        if (resultBadge) {
            resultBadge.textContent =
                latestScanId !== null
                    ? `SCAN #${latestScanId}`
                    : "SCAN COMPLETE";
        }

        activateTab("text");

        if (result.warning) {
            showStatus(result.warning, "info");
        } else if (!extractedText.trim()) {
            showStatus(
                "No text detected. Try a clearer document.",
                "error"
            );
        } else {
            showStatus(
                `Scan completed successfully. Scan ID: ${latestScanId ?? "saved"}`,
                "success"
            );
        }
    }

    // --------------------------------------------------
    // SCAN DOCUMENT
    // --------------------------------------------------

    if (uploadForm) {
        uploadForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            if (isScanning) return;

            if (!selectedFile) {
                showStatus("Choose a document first.", "error");
                return;
            }

            const formData = new FormData();
            formData.append("file", selectedFile, selectedFile.name);

            isScanning = true;

            setScanButton(true, "Scanning...");
            showStatus(
                "Processing your document. Please wait...",
                "info"
            );

            if (resultBadge) {
                resultBadge.textContent = "PROCESSING";
            }

            try {
                const response = await fetch("/scan", {
                    method: "POST",
                    body: formData
                });

                let result;

                try {
                    result = await response.json();
                } catch {
                    throw new Error(
                        "Invalid server response. Check the VS Code terminal."
                    );
                }

                if (!response.ok) {
                    throw new Error(
                        result.detail || "Document scanning failed."
                    );
                }

                displayScanResults(result);
            } catch (error) {
                showStatus(
                    error.message || "Unable to scan the document.",
                    "error"
                );

                if (resultBadge) {
                    resultBadge.textContent = "SCAN FAILED";
                }
            } finally {
                isScanning = false;
                setScanButton(!selectedFile);
            }
        });
    }

    // --------------------------------------------------
    // COPY EXTRACTED TEXT
    // --------------------------------------------------

    if (copyButton) {
        copyButton.addEventListener("click", async () => {
            if (!textOutput || !textOutput.value.trim()) {
                showStatus(
                    "There is no extracted text to copy.",
                    "error"
                );
                return;
            }

            try {
                await navigator.clipboard.writeText(textOutput.value);

                showStatus("Text copied to clipboard.", "success");
            } catch {
                textOutput.focus();
                textOutput.select();

                const copied = document.execCommand("copy");

                showStatus(
                    copied
                        ? "Text copied to clipboard."
                        : "Select the text and copy it manually.",
                    copied ? "success" : "info"
                );
            }
        });
    }

    // --------------------------------------------------
    // CLEAR
    // --------------------------------------------------

    if (clearButton) {
        clearButton.addEventListener("click", () => {
            if (isScanning) {
                showStatus(
                    "Wait for the current scan to finish.",
                    "info"
                );
                return;
            }

            selectedFile = null;

            if (fileInput) {
                fileInput.value = "";
            }

            resetPreview();
            resetResults();
            setScanButton(true);

            showStatus(
                "Cleared. Choose another document.",
                "info"
            );
        });
    }

    // Stop camera when leaving the page.
    window.addEventListener("pagehide", stopCamera);

    // --------------------------------------------------
    // INITIAL STATE
    // --------------------------------------------------

    resetResults();
    setScanButton(true);
});
