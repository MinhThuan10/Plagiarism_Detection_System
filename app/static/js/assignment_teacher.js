document.addEventListener("DOMContentLoaded", () => {
  const addNewModal = document.getElementById("addNewModal");

  addNewModal.addEventListener("show.bs.modal", () => {
    const createDayInput = document.getElementById("createDay");
    const today = new Date();
    const formattedDate = `${String(today.getMonth() + 1).padStart(
      2,
      "0"
    )}/${String(today.getDate()).padStart(2, "0")}/${today.getFullYear()}`;
    createDayInput.value = formattedDate;
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
  console.log("class_id:", class_id);
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
        console.log(className);
        const tbody = document.getElementById("assignment_table_body");

        data.assignments.forEach((assignmentInfo) => {
          const row = document.createElement("tr");
          // Thêm các ô vào hàng
          row.innerHTML = `
                    <td class="ps-4">${assignmentInfo.assignment_id}</td>
                    <td>
                        <a href="class=${class_id}/assignment=${assignmentInfo.assignment_id}" class="text-body" style="color: #35509a !important">${assignmentInfo.assignment_name}</a>
                    </td>
                    <td>${assignmentInfo.create_day}</td>
                    <td>${assignmentInfo.start_day}</td>
                    <td>${assignmentInfo.end_day}</td>
                    <td style="text-align: center">${assignmentInfo.student_ids.length}/${data.classs.student_ids.length}</td>

                    <td>
                        <ul class="list-inline mb-0">
                            <li class="list-inline-item">
                                <a href="#" data-mdb-toggle="modal" data-mdb-target="#editModal" title="Edit" assignment_id="${assignmentInfo.assignment_id}" class="px-2 text-primary edit">
                                    <i class="bx bx-pencil font-size-18"></i>
                                </a>
                            </li>
                            <li class="list-inline-item">
                                <a href="#" data-mdb-toggle="modal" data-mdb-target="#deleteModal" title="Delete" assignment_id="${assignmentInfo.assignment_id}" class="px-2 text-danger delete">
                                    <i class="bx bx-trash-alt font-size-18"></i>
                                </a>
                            </li>
                        </ul>
                    </td>
                `;

          tbody.appendChild(row);

          const deleteicon = row.querySelector(".delete");
          deleteicon.addEventListener("click", function () {
            const assignment_id = this.getAttribute("assignment_id");
            console.log("Đã nhấn xóa lớp có ID:", assignment_id);
            const deletebutton = document.getElementById("submit_delete");
            deletebutton.addEventListener("click", function () {
              fetch(
                `/api/delete_assignment@school=${school_id}-class=${class_id}-assignment=${assignment_id}`,
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

          const editicon = row.querySelector(".edit");
          editicon.addEventListener("click", function () {
            const assignment_id = this.getAttribute("assignment_id");
            console.log("Đã nhấn chỉnh sửa lớp có ID:", assignment_id);
            document.getElementById("assignmentName_replace").value =
              assignmentInfo.assignment_name;

            document.getElementById("startDay_replace").value = formatDate(
              assignmentInfo.start_day
            );
            document.getElementById("dueDay_replace").value = formatDate(
              assignmentInfo.end_day
            );

            const updatebutton = document.getElementById("update_btn");
            updatebutton.addEventListener("click", function () {
              const assignment_name_replace = document.getElementById(
                "assignmentName_replace"
              );
              const start_day_replace =
                document.getElementById("startDay_replace");
              const end_day_replace = document.getElementById("dueDay_replace");

              const convertedStartDay = convertDateFormat(
                start_day_replace.value
              );
              const convertedEndDay = convertDateFormat(end_day_replace.value);

              fetch(
                `/api/update_assignment@school=${school_id}-class=${class_id}}-assignment=${assignment_id}`,
                {
                  method: "PUT",
                  headers: {
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify({
                    class_name: assignment_name_replace.value,
                    start_day: convertedStartDay,
                    end_day: convertedEndDay,
                  }),
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

        const student_body = document.getElementById("students_table_body");
        data.list_students.forEach((studentInfo, index) => {
          const row = document.createElement("tr");
          // Thêm các ô vào hàng
          row.innerHTML = `
                    <td class="ps-4">${data.classs.student_ids[index][1]}</td>
                    <td>${studentInfo.last_name} ${studentInfo.first_name}</td>
                    <td>${studentInfo.user_id}</td>
                    <td>${studentInfo.email}</td>
                  
                    <td>
                        <ul class="list-inline mb-0" style="margin-left: -3px">
                            <li class="list-inline-item">
                                <a href="#" data-mdb-toggle="modal" data-mdb-target="#deleteStudentModal" title="Delete" user_id="${studentInfo.user_id}" class="px-2 text-danger delete_student">
                                    <i class="bx bx-trash-alt font-size-18"></i>
                                </a>
                            </li>
                        </ul>
                    </td>
                `;

          student_body.appendChild(row);

          const deleteicon = row.querySelector(".delete_student");
          deleteicon.addEventListener("click", function () {
            const user_id = this.getAttribute("user_id");
            console.log("Đã nhấn xóa lớp có ID:", user_id);
            const deletebutton = document.getElementById("delete_student");
            deletebutton.addEventListener("click", function () {
              fetch(`/api/delete_user_to_class`, {
                method: "PUT",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  class_id: class_id,
                  student_id: user_id,
                }),
              })
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

document
  .getElementById("button_create_asignment")
  .addEventListener("click", function (event) {
    event.preventDefault();

    const assignmentName = document.getElementById("assignmentName");
    const createDay = document.getElementById("createDay");
    const startDay = document.getElementById("startDay");
    const dueDay = document.getElementById("dueDay");
    const messageDiv = document.getElementById("signupMessage");

    messageDiv.textContent = "";

    let allFilled = true;

    if (!assignmentName.value) {
      messageDiv.textContent += "Please give assignment name! ";
      messageDiv.style.color = "red";
      allFilled = false;
    }
    if (!startDay.value) {
      messageDiv.textContent += "Please give start day name! ";
      messageDiv.style.color = "red";
      allFilled = false;
    }
    if (!dueDay.value) {
      messageDiv.textContent += "Please chose due day! ";
      messageDiv.style.color = "red";
      allFilled = false;
    }

    const convertedstartDay = convertDateFormat(startDay.value);
    const converteddueDay = convertDateFormat(dueDay.value);

    console.log(convertedstartDay);

    if (allFilled) {
      fetch(`/api/create_assignment@school=${school_id}-class=${class_id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          assignmentName: assignmentName.value,
          createDay: createDay.value,
          startDay: convertedstartDay,
          dueDay: converteddueDay,
        }),
      })
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
          messageDiv.textContent = "An error occurred. Please try again.";
          messageDiv.style.color = "red";
        });
    }
  });
