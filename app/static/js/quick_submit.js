
let school_id = "";

document.addEventListener("DOMContentLoaded", function () {
    const submitDayField = document.getElementById("submitDay");
    const currentDate = new Date();
    const formattedDate = `${
        currentDate.getMonth() + 1
    }/${currentDate.getDate()}/${currentDate.getFullYear()}`;
    submitDayField.value = formattedDate;


    fetch(`/api/quick_submit`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            document.getElementById("school_name").innerText = data.school_name;
            const tbody = document.getElementById("file_table_body");
            school_id = data.school_id;
            data.list_files.forEach((fileInfo, index) => {
              const row = document.createElement("tr");
              // Thêm các ô vào hàng
              row.innerHTML = `
                        <td>${fileInfo.author_name}</td>
                        <td class="ps-4">${fileInfo.file_id}</td>
                        <td class="wrap-text">
                            <a
                                href="#"
                                class="text-body"
                                style="color: #35509a !important"
                                title="${fileInfo.title}"
                                >${fileInfo.title}
                            </a>
                        </td>
                        <td>${fileInfo.submit_day}</td>
                        <td style="text-align: center">${fileInfo.plagiarism}%</td>

                        <td style="text-align: center">
                            <ul class="list-inline mb-0">
                                <li class="list-inline-item">
                                    <a
                                    href="/api/download_pdf@file_id=${fileInfo.file_id}-type=raw"
                                    >
                                    <i class="bx bx-download font-size-18"></i>
                                    </a>
                                </li>
                                <li class="list-inline-item">
                                    <a
                                    href="javascript:void(0);"
                                    data-mdb-toggle="modal"
                                    data-mdb-target="#deleteModal"
                                    class="text-danger delete"
                                    file_id = "${fileInfo.file_id}"
                                    title="Delete"
                                    >
                                    <i class="bx bx-trash-alt font-size-18"></i>
                                    </a>
                                </li>
                            </ul>
                        </td>
                        `;
    
              tbody.appendChild(row);
    

              const deleteicon = row.querySelector(".delete");
              deleteicon.addEventListener("click", function () {
                const file_id = this.getAttribute("file_id");
                console.log("Đã nhấn xóa file có ID:", file_id);
                const deletebutton = document.getElementById("submit_delete");
                deletebutton.addEventListener("click", function () {
                  fetch(
                    `/api/delete_file@file_id=${file_id}`,
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



function updateFileName() {
    const fileInput = document.getElementById("submissionFile");
    const fileNameField = document.getElementById("fileName");
    const removeFileBtn = document.getElementById("removeFileBtn");

    if (fileInput.files.length > 0) {
        fileNameField.value = fileInput.files[0].name;
        removeFileBtn.style.display = "inline"; // Show the "x" button
    } else {
        fileNameField.value = "No file chosen";
        removeFileBtn.style.display = "none"; // Hide the "x" button
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

const submit_button = document.getElementById("submit_button");
submit_button.addEventListener("click", function () {
    const messageDiv = document.getElementById("signupMessage");
    const authorName = document.getElementById("authorName");

    const submissionTitle = document.getElementById("submissionTitle");
    const submissionFile = document.getElementById("submissionFile");
    const storageOption = document.getElementById("storageOption");
    const submitDay = document.getElementById("submitDay");

    messageDiv.textContent = "";

    if (!authorName.value) {
        messageDiv.textContent += "Please give author Name! ";
        allFilled = false;
      }

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
    formData.append("author_name", authorName.value);
    formData.append("submissionTitle", submissionTitle.value);
    formData.append("storageOption", storageOption.value);
    formData.append("submitDay", submitDay.value);
    fetch(
      `/api/upload_file_quick_submit@school=${school_id}`,
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
