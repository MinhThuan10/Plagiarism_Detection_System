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

let school_id = "";
let class_id = "";

// Lấy URL hiện tại
const url = window.location.href;

// Sử dụng regex để tìm giá trị của 'class'
const match = url.match(/class=([\w_]+)/);

if (match) {
  class_id = match[1];
}


let userId = document.getElementById("user-info").getAttribute("data-user-id");

document.addEventListener("DOMContentLoaded", function () {
  fetch(`/api/assignments@class=${class_id}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const className = data.classs.class_name;
        school_id = data.classs.school_id;
        document.getElementById("class_name").innerText = className;
        const tbody = document.getElementById("assignment_table_body");
        data.assignments.forEach((assignmentInfo) => {
          let student_submited = assignmentInfo.student_ids;
          let title,
            submitDay,
            similarity,
            modal_upload,
            modal_download,
            link,
            file_id;
          if (student_submited.includes(userId)) {
            file_id = assignmentInfo.file_id;
            title = assignmentInfo.title;
            submitDay = assignmentInfo.submit_day;
            link = `/api/download_pdf@school=${school_id}-class=${class_id}-assignment=${assignmentInfo.assignment_id}-student=${userId}`;
            similarity = assignmentInfo.plagiarism
              ? assignmentInfo.plagiarism + "%"
              : "--";
            modal_upload = "";
            modal_download = "modal";
          } else {
            file_id = "0";
            title = "--";
            submitDay = "--";
            link = "#";
            similarity = "--";
            modal_upload = "modal";
            modal_download = "";
          }

          const row = document.createElement("tr");
          // Thêm các ô vào hàng
          row.innerHTML = `
                    <td class="ps-4">${assignmentInfo.assignment_name}</td>
                    <td>${assignmentInfo.start_day}</td>
                    <td>${assignmentInfo.end_day}</td>
                    <td>
                        <a href="/report/file_id=${file_id}" class="text-body" style="color: #35509a !important">${title}</a>
                    </td>
                    <td>${submitDay}</td>
                    <td style="text-align: center;">${similarity}</td>
                    <td>
                        <ul class="list-inline mb-0">
                            <li class="list-inline-item">
                                <a
                                href="javascript:void(0);"
                                data-bs-toggle="${modal_upload}"
                                data-bs-target="#uploadModal"
                                class="text-primary upload"
                                assignment_id = "${assignmentInfo.assignment_id}"
                                title="Upload"
                                >
                                <i class="bx bx-upload font-size-18"></i>
                                </a>
                            </li>

                            <li class="list-inline-item">
                                <a
                                href="${link}"
                                >
                                <i class="bx bx-download font-size-18"></i>
                                </a>
                            </li>
                            <li class="list-inline-item">
                                <a
                                href="javascript:void(0);"
                                data-mdb-toggle="${modal_download}"
                                data-mdb-target="#deleteModal"
                                class="text-danger delete"
                                assignment_id = "${assignmentInfo.assignment_id}"
                                title="Delete"
                                >
                                <i class="bx bx-trash-alt font-size-18"></i>
                                </a>
                            </li>
                        </ul>
                    </td>
                `;

          tbody.appendChild(row);

          const uploadIcon = row.querySelector(".upload");
          uploadIcon.addEventListener("click", function () {
            let assignment_id = this.getAttribute("assignment_id");
            console.log("Đã nhấn upload cho bài tập có ID:", assignment_id);
            const submit_button = document.getElementById("submit_button");

            submit_button.addEventListener("click", function () {
              const messageDiv = document.getElementById("signupMessage");
              const submissionFile = document.getElementById("submissionFile");
              const storageOption = document.getElementById("storageOption");
              const submitDay = document.getElementById("submitDay");

              messageDiv.textContent = "";

              if (!submissionFile.value) {
                messageDiv.textContent += "Please chose File! ";
                messageDiv.style.color = "red";

                allFilled = false;
              }

              const file = submissionFile.files[0];
              const formData = new FormData();
              formData.append("file", file);
              formData.append("storageOption", storageOption.value);
              formData.append("submitDay", submitDay.value);

              document.getElementById("loadingSpinner").style.display ="block";
              fetch(
                `/api/upload_file@school=${school_id}-class=${class_id}-assignment=${assignment_id}`,
                {
                  method: "POST",
                  body: formData,
                }
              )
                .then((response) => response.json())
                .then((data) => {
                  if (data.success) {
                    messageDiv.textContent = data.message;
                    messageDiv.style.color = "#0369C3";
                    location.reload();
                  } else {
                    messageDiv.textContent = data.message;
                    messageDiv.style.color = "red";
                  }
                })
                .catch((error) => {
                  console.error("Error:", error);
                })
                .finally(() => {
                  // Hide the loading spinner
                  document.getElementById("loadingSpinner").style.display =
                    "none";
                });;
            });
          });

          const deleteicon = row.querySelector(".delete");
          deleteicon.addEventListener("click", function () {
            const assignment_id = this.getAttribute("assignment_id");
            console.log("Đã nhấn xóa bài tập có ID:", assignment_id);
            const deletebutton = document.getElementById("delete_file");
            deletebutton.addEventListener("click", function () {
              fetch(
                `/api/delete_file@school=${school_id}-class=${class_id}-assignment=${assignment_id}-student=${userId}`,
                {
                  method: "DELETE",
                  headers: {
                    "Content-Type": "application/json",
                  },
                }
              )
                .then((response) => response.json())
                .then((data) => {
                  if (data.success) {
                    console.log(data.message);
                    location.reload();
                  } else {
                    console.log(data.message);
                  }
                })
                .catch((error) => {
                  console.error("Error:", error);
                });
            });
          });
        });
      } else {
        console.error("Unable to load school data");
      }
    })
    .catch((error) => console.error("Lỗi:", error));
});
