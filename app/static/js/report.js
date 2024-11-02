$(document).ready(function () {
    function toggleReport(modalId) {
        // Khi modal được hiển thị
        $(modalId).on("show.bs.modal", function () {
            $(".report").addClass("hidden"); // Ẩn phần báo cáo
        });

        // Khi modal được ẩn đi
        $(modalId).on("hidden.bs.modal", function () {
            $(".report").removeClass("hidden"); // Hiện lại phần báo cáo
        });
    }

    // Áp dụng cho cả hai modal
    toggleReport("#addFilter");
    toggleReport("#addExclusion");
});



        // khi nhấn loại trừ source
function toggleContainer() {
    const container = document.querySelector(".container-source");
    container.style.display =
        container.style.display === "none" ? "block" : "none";
    }
let fileId = document.getElementById('file-info').getAttribute('data-file-id');

// khi nhấn loại trừ text
function toggleContainer2() {
    const container = document.querySelector(".container-text");
    container.style.display =
      container.style.display === "none" ? "block" : "none";
  }

  async function loadPDF(pdfId) {
    try {
        const response = await fetch(`/api/load_file_checked@file_id=${pdfId}`);
        if (!response.ok) {
            throw new Error("Không thể tải file PDF");
        }
        
        const pdfBlob = await response.blob();
        const pdfURL = URL.createObjectURL(pdfBlob);

        const viewer = document.getElementById('pdf-viewer');
        viewer.innerHTML = `<iframe src="${pdfURL}" width="100%" height="600px" style="border: none;"></iframe>`;
    } catch (error) {
        console.error("Error loading PDF:", error);
    }
}

// Gọi hàm loadPDF với ID của PDF từ MongoDB
loadPDF(fileId)