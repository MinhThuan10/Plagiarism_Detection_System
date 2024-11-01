document.addEventListener("DOMContentLoaded", function () {
  const submitDayField = document.getElementById("submitDay");
  const currentDate = new Date();
  const formattedDate = `${
    currentDate.getMonth() + 1
  }/${currentDate.getDate()}/${currentDate.getFullYear()}`;
  submitDayField.value = formattedDate;
});

function updateFileName() {
  const fileInput = document.getElementById("submissionFile");
  const fileNameField = document.getElementById("fileName");
  const removeFileBtn = document.getElementById("removeFileBtn");

  if (fileInput.files.length > 0) {
    fileNameField.value = fileInput.files[0].name;
    removeFileBtn.style.display = "inline";
  } else {
    fileNameField.value = "No file chosen";
    removeFileBtn.style.display = "none";
  }
}

function removeFile() {
  const fileInput = document.getElementById("submissionFile");
  const fileNameField = document.getElementById("fileName");
  const removeFileBtn = document.getElementById("removeFileBtn");

  fileInput.value = ""; // Clear the file input
  fileNameField.value = "No file chosen"; // Reset the file name display
  removeFileBtn.style.display = "none"; // Hide the "x" button
}

let school_id = "";
let class_id = "";
let assignment_id = "";

// Lấy URL hiện tại
const url = window.location.href;

// Sử dụng regex để tìm giá trị của 'class'
const match = url.match(/class=(\d+)/);

if (match) {
  class_id = match[1];
}
const assignment = url.match(/assignment=(\d+)/);

if (assignment) {
  assignment_id = assignment[1];
}

function convertDateFormat(dateString) {
  const [year, month, day] = dateString.split("-"); // Tách phần ngày tháng năm
  return `${month}/${day}/${year}`; // Trả về định dạng MM/DD/YYYY
}

// Hàm chuyển đổi định dạng ngày sang YYYY-MM-DD
function formatDate(dateString) {
  const [month, day, year] = dateString.split("/"); // Tách chuỗi
  return `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`; // Định dạng lại
}

document.addEventListener("DOMContentLoaded", function () {
  fetch(`/api/file@class=${class_id}-assignment=${assignment_id}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const assignment_name = data.assignment.assignment_name;
        school_id = data.assignment.school_id;
        document.getElementById("assignment_name").innerText = assignment_name;

        let student_submited = data.assignment.student_ids;

        const tbody = document.getElementById("file_table_body");

        data.list_students.forEach((studentInfo, index) => {
          let submissionID,
            title,
            submitDay,
            similarity,
            status,
            modal_upload,
            modal_download,
            link;
          if (student_submited.includes(studentInfo.user_id)) {
            submissionID = data.list_files[index].file_id;
            title = data.list_files[index].title;
            submitDay = data.list_files[index].submit_day;
            link = `/api/download_pdf@school=${school_id}-class=${class_id}-assignment=${assignment_id}-student=${studentInfo.user_id}`;
            similarity = data.list_files[index].plagiarism || 0;
            status = "bx-check text-success";
            modal_upload = "";
            modal_download = "modal";
          } else {
            submissionID = "--";
            title = "--";
            submitDay = "--";
            link = "#";
            similarity = "--";
            status = "bx-x text-danger";
            modal_upload = "modal";
            modal_download = "";
          }

          console.log(submissionID);
          const row = document.createElement("tr");
          // Thêm các ô vào hàng
          row.innerHTML = `
                    <td class="ps-4">${studentInfo.user_id}</td>
                    <td>${studentInfo.last_name} ${studentInfo.firs_tname}</td>
                    <td>${submissionID}</td>
                    <td class="wrap-text">
                        <a
                        href="#"
                        class="text-body"
                        style="color: #35509a !important"
                        title="${title}"
                        >${title}</a
                        >
                    </td>
                    <td style="text-align: center">${submitDay}</td>
                    <td style="text-align: center">${similarity}%</td>
                    <td style="text-align: center">
                        <i
                        class="bx ${status} font-size-18"
                        title="Pass"
                        ></i>
                    </td>


                    <td style="text-align: center">
                        <ul class="list-inline mb-0">
                            <li class="list-inline-item">
                                <a
                                href="javascript:void(0);"
                                data-bs-toggle="${modal_upload}"
                                data-bs-target="#uploadModal"
                                class="text-primary upload"
                                student_id = "${studentInfo.user_id}"
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
                                student_id = "${studentInfo.user_id}"
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
            let student_id = this.getAttribute("student_id");
            console.log("Đã nhấn upload cho học sinh có ID:", student_id);
            const submit_button = document.getElementById("submit_button");

            submit_button.addEventListener("click", function () {
              const messageDiv = document.getElementById("signupMessage");
              const submissionTitle =
                document.getElementById("submissionTitle");
              const submissionFile = document.getElementById("submissionFile");
              const storageOption = document.getElementById("storageOption");
              const submitDay = document.getElementById("submitDay");

              messageDiv.textContent = "";

              if (!submissionTitle.value) {
                messageDiv.textContent += "Please give Submission Title! ";
                allFilled = false;
              }
              if (!submissionFile.value) {
                messageDiv.textContent += "Please chose File! ";
                allFilled = false;
              }

              const file = submissionFile.files[0];
              const formData = new FormData();
              formData.append("file", file);
              formData.append("student_id", student_id);
              formData.append("submissionTitle", submissionTitle.value);
              formData.append("storageOption", storageOption.value);
              formData.append("submitDay", submitDay.value);

              fetch(
                `/api/upload_file@school=${school_id}-class=${class_id}-assignment=${assignment_id}`,
                {
                  method: "POST",
                  body: formData,
                }
              )
                .then((response) => response.json())
                .then((data) => {
                  console.log(data); // Kiểm tra phản hồi từ máy chủ
                  location.reload();
                })
                .catch((error) => {
                  console.error("Error:", error);
                });
            });
          });

          const deleteicon = row.querySelector(".delete");
          deleteicon.addEventListener("click", function () {
            const student_id = this.getAttribute("student_id");
            console.log("Đã nhấn xóa lớp có ID:", student_id);
            const deletebutton = document.getElementById("delete_file");
            deletebutton.addEventListener("click", function () {
              fetch(
                `/api/delete_file@school=${school_id}-class=${class_id}-assignment=${assignment_id}-student=${student_id}`,
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
        console.error("Không thể tải dữ liệu trường học");
      }
    })
    .catch((error) => console.error("Lỗi:", error));
});
