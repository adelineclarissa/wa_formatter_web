let downloadUrl = "";

console.log("Script loaded");
window.addEventListener("DOMContentLoaded", () => {
  console.log("DOM fully loaded");
});

async function uploadFile() {
  const input = document.getElementById("fileInput");
  const status = document.getElementById("status");
  const downloadBtn = document.getElementById("downloadBtn");

  if (!input.files.length) {
    alert("Please select a file.");
    return;
  }

  const file = input.files[0];
  const formData = new FormData();
  formData.append("file", file);

  status.textContent = "Uploading...";
  downloadBtn.disabled = true;

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    console.log(data.filename);
    if (data.filename) {
      downloadUrl = `/static/${data.filename}`;
      status.textContent = "File ready. Click download.";
      downloadBtn.disabled = false;
    } else {
      status.textContent = "Failed to process file.";
    }
  } catch (error) {
    status.textContent = "Error: " + error.message;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const downloadBtn = document.getElementById("downloadBtn");
  downloadBtn.addEventListener("click", () => {
    if (downloadUrl) {
      window.open(downloadUrl, "_blank");
    }
  });
});
