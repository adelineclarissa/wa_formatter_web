async function uploadFile() {
  const input = document.getElementById("fileInput");
  if (!input.files.length) {
    alert("Please select a file.");
    return;
  }

  const file = input.files[0];
  const formData = new FormData();
  formData.append("file", file);

  document.getElementById("status").textContent = "Uploading...";

  const response = await fetch("/upload", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  if (data.filename) {
    const link = `/static/${data.filename}`;
    document.getElementById(
      "status"
    ).innerHTML = `Download: <a href="${link}" target="_blank">${data.filename}</a>`;
  } else {
    document.getElementById("status").textContent = "Failed to upload.";
  }
}
