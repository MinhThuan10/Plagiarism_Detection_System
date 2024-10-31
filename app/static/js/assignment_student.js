document.addEventListener("DOMContentLoaded", function () {
  const submitDayField = document.getElementById("submitDay");
  const currentDate = new Date();
  const formattedDate = `${
    currentDate.getMonth() + 1
  }/${currentDate.getDate()}/${currentDate.getFullYear()}`;
  submitDayField.value = formattedDate;
});

document.addEventListener("DOMContentLoaded", function () {
  const submissionFileInput = document.getElementById("submissionFile");
  const fileNameInput = document.getElementById("fileName");
  const removeFileBtn = document.getElementById("removeFileBtn");

  // Hàm cập nhật tên file và hiển thị dấu 'x'
  submissionFileInput.addEventListener("change", function () {
    if (submissionFileInput.files.length > 0) {
      fileNameInput.value = submissionFileInput.files[0].name;
      removeFileBtn.style.display = "inline"; // Hiện nút 'x'
    }
  });

  // Hàm xóa file đã chọn
  removeFileBtn.addEventListener("click", function () {
    submissionFileInput.value = ""; // Xóa giá trị file
    fileNameInput.value = "No file chosen"; // Đặt lại placeholder
    removeFileBtn.style.display = "none"; // Ẩn nút 'x'
  });
});
