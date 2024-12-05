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

function deleteSource(source_id) {
  fetch(`/api/remove_source_school@file_id=${fileId}-school_id=${source_id}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        location.reload();
      } else {
        console.error("Không thể tải dữ liệu trường học");
      }
    })
    .catch((error) => console.error("Lỗi:", error));
}

const closeButtons = document.querySelectorAll(".btn-close");

closeButtons.forEach((button) => {
  button.addEventListener("click", function () {
    location.reload();
  });
});


function toggleContainer() {
  const container = document.querySelector(".container-source");
  container.style.display =
    container.style.display === "none" ? "block" : "none";
}
let fileId = document.getElementById("file-info").getAttribute("data-file-id");


function toggleContainer2(school_id) {
  schoolSource = ".container-text-school_id-" + school_id;
  const container = document.querySelector(schoolSource);
  // Kiểm tra trạng thái hiển thị ban đầu
  const isHidden = container.style.display === "none";

  // Chuyển trạng thái hiển thị
  container.style.display = isHidden ? "block" : "none";

  if (flexSwitchCheckDefault.checked) {
    if (isHidden) {
      console.log("highlight theo trương")
      fetch(`/api/highlight_school@file_id=${fileId}-school_id=${school_id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            loadPDF(fileId, "view_all");
          } else {
            console.error("Không thể tải dữ liệu trường học");
          }
        })
        .catch((error) => console.error("Lỗi:", error));
    }
  }
  

}

async function loadPDF(pdfId, type) {
  try {
    const response = await fetch(
      `/api/load_file@file_id=${pdfId}-type=${type}`
    );
    if (!response.ok) {
      throw new Error("Unable to download PDF file");
    }

    const pdfBlob = await response.blob();
    const pdfURL = URL.createObjectURL(pdfBlob);

    console.log(pdfURL);

    const viewer = document.getElementById("pdf-viewer");
    viewer.innerHTML = `<iframe src="${pdfURL}" width="100%" height="600px" style="border: none;"></iframe>`;
  } catch (error) {
    console.error("Error loading PDF:", error);
  }
}

loadPDF(fileId, "checked");

loadFileInfo("school_source_off");

// Lấy đối tượng toggle switch
const toggleSwitch = document.getElementById("flexSwitchCheckDefault");

toggleSwitch.addEventListener("change", (event) => {
  if (event.target.checked) {
    loadPDF(fileId, "raw");
    loadFileInfo("school_source_on");
  } else {
    loadPDF(fileId, "checked");
    loadFileInfo("school_source_off");
  }
});

// Hàm loadFileInfo để tải dữ liệu từ API
function loadFileInfo(sourceType) {
  // Xóa nội dung cũ trong source-container
  const container = document.getElementById("source-container");
  container.innerHTML = ""; // Xóa các phần tử cũ

  fetch(`/api/load_fileInfo_checked@file_id=${fileId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const page_count = data.list_files[0].page_count;
        document.getElementById("page_count").innerText =
          "Page count: " + page_count;

        const word_count = data.list_files[0].word_count;
        document.getElementById("word_count").innerText =
          "Word count: " + word_count;

        const similarity = data.list_files[0].plagiarism;
        document.getElementById("similarity").innerText =
          similarity + "% Standard Similarity";
        document.getElementById("similarity2").innerText =
          similarity + "% Standard Similarity";

        const container = document.getElementById("source-container");

        data[sourceType].forEach((item, index) => {
          const [school_id, details] = item;

          const sectionDiv = document.createElement("div");
          sectionDiv.className = "section";

          const sourceInfoDiv = document.createElement("div");
          sourceInfoDiv.className = "source-info";

          const iconDiv = document.createElement("div");
          iconDiv.className = "icon";
          iconDiv.innerHTML = `
                    <i class="fas fa-ban" onclick="deleteSource(${school_id})"></i>
                    <i class="fas fa-angle-down" onclick="toggleContainer2(${school_id})"></i>
                `;

          const sourceTitleDiv = document.createElement("div");
          sourceTitleDiv.className = "source-title";
          sourceTitleDiv.innerHTML = `
                    <span class="number" style="background-color: ${
                      details.color
                    };">${index + 1}</span>
                    <span class="tag" style="background-color: ${
                      details.color
                    };">${details.type_source}</span>
                `;

          const sourceNameSpan = document.createElement("span");
          sourceNameSpan.className = "source-name";
          sourceNameSpan.textContent = details.school_name;

          const matchedDiv = document.createElement("div");
          matchedDiv.className = "matched";

          const matched1Div = document.createElement("div");
          matched1Div.className = "matched1";
          matched1Div.innerHTML = `
                    <span class="number-matched">${details.word_count}</span>
                    <span class="matched-words">matched words</span>
                `;

          const percentageDiv = document.createElement("div");
          percentageDiv.className = "percentage";
          percentageDiv.textContent = `${Math.round(
            (details.word_count / word_count) * 100
          )}%`;

          const containerText = document.createElement("div");
          containerText.className = "container-text-school_id-" + school_id;
          containerText.style.display = "none";

          if (
            typeof details.sentences === "object" &&
            details.sentences !== null
          ) {
            for (const page in details.sentences) {
              for (const key in details.sentences[page]) {

                if (details.sentences[page].hasOwnProperty(key)) {
                  const sentence = details.sentences[page][key];

                  const sectionSource = document.createElement("div");
                  sectionSource.className = "section-source";
                  sectionSource.id = `text-${key}`; // Sử dụng khóa làm ID

                  const sectionText = document.createElement("div");
                  sectionText.className = "section-text";

                  const textSection = document.createElement("div");
                  textSection.className = "text-section";
                  textSection.innerHTML = sentence.best_match;

                  const sectionLink = document.createElement("div");
                  sectionLink.className = "section-link2";
                  sectionLink.textContent = sentence.file_id;

                  const icon = document.createElement("i");
                  icon.className = "fas fa-xmark";
                  // Gán sự kiện click cho icon
                  icon.addEventListener("click", function () {
                    fetch(
                      `/api/remove_text_school@file_id=${fileId}-school_id=${school_id}-page=${page}-sentence=${key}`,
                      {
                        method: "POST",
                        headers: {
                          "Content-Type": "application/json",
                        },
                      }
                    )
                      .then((response) => response.json())
                      .then((data) => {
                        if (data.success) {
                          console.log("Thành công");
                          location.reload();
                        } else {
                          console.error("Không thể tải dữ liệu trường học");
                        }
                      })
                      .catch((error) => console.error("Error", error));
                  });

                  sectionText.appendChild(textSection);
                  sectionText.appendChild(sectionLink);
                  sectionSource.appendChild(sectionText);
                  sectionSource.appendChild(icon);
                  containerText.appendChild(sectionSource);
                }
              }
            }
          } else {
            console.log(
              "details.sentences is not an object or array:",
              details.sentences
            );
          }

          matchedDiv.appendChild(matched1Div);
          matchedDiv.appendChild(percentageDiv);

          sourceInfoDiv.appendChild(iconDiv);
          sourceInfoDiv.appendChild(sourceTitleDiv);
          sourceInfoDiv.appendChild(sourceNameSpan);
          sourceInfoDiv.appendChild(matchedDiv);
          sourceInfoDiv.appendChild(containerText);

          sectionDiv.appendChild(sourceInfoDiv);
          container.appendChild(sectionDiv);
        });

        const downloadIcon = document.getElementById("dowload_file");
        downloadIcon.href = `/api/download_pdf@file_id=${fileId}-type=checked`;

        const containerSourceExclude =
          document.getElementById("sourceContainer");
        Object.entries(data.school_exclusion_source).forEach(
          ([index, source]) => {
            const sectionSourceDiv = document.createElement("div");
            sectionSourceDiv.className = "section-source";
            sectionSourceDiv.id = `source-${index}`; // Sử dụng index làm ID

            const sectionLinkDiv = document.createElement("div");
            sectionLinkDiv.className = "section-link";
            sectionLinkDiv.textContent = source.school_name;

            const icon = document.createElement("i");
            icon.className = "fas fa-xmark";

            // Gán sự kiện click cho icon
            icon.addEventListener("click", function () {
              // Lấy phần tử theo ID và xóa nó
              const sectionToRemove = document.getElementById(
                sectionSourceDiv.id
              );
              if (sectionToRemove) {
                sectionToRemove.remove();
                console.log(`Đã loại bỏ trường học: ${index}`);
              }
              fetch(
                `/api/add_source_school@file_id=${fileId}-school_id=${index}`,
                {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
                }
              )
                .then((response) => response.json())
                .then((data) => {
                  if (data.success) {
                    console.log("Thành công");
                    loadPDF(fileId, "checked");
                  } else {
                    console.error("Không thể tải dữ liệu trường học");
                  }
                })
                .catch((error) => console.error("Lỗi:", error));
            });

            sectionSourceDiv.appendChild(sectionLinkDiv);
            sectionSourceDiv.appendChild(icon);

            containerSourceExclude.appendChild(sectionSourceDiv);
          }
        );

        const containerTextExclude = document.getElementById("textContainer");
        Object.entries(data.school_exclusion_text).forEach(
          ([page, sources]) => {
            // Lặp qua từng nguồn trong khóa chính
            Object.entries(sources).forEach(([sentence_id, source_page]) => {
              Object.entries(source_page).forEach(([index, source]) => {
                console.log(index)
                const sectionSource = document.createElement("div");
                sectionSource.className = "section-source";
                sectionSource.id = `text-exclude-${page}-${sentence_id}-${index}`; // Sử dụng khóa chính và phụ làm ID

                const sectionText = document.createElement("div");
                sectionText.className = "section-text";

                const textSection = document.createElement("div");
                textSection.className = "text-section";
                textSection.innerHTML = source.best_match;

                const sectionLink = document.createElement("div");
                sectionLink.className = "section-link2";
                sectionLink.textContent = source.school_name; // Sửa thành school_name

                const icon = document.createElement("i");
                icon.className = "fas fa-xmark";

                // Gán sự kiện click cho icon
                icon.addEventListener("click", function () {
                  const sectionToRemove = document.getElementById(
                    sectionSource.id
                  );
                  if (sectionToRemove) {
                    sectionToRemove.remove();
                  }
                  fetch(
                    `/api/add_text_school@file_id=${fileId}-page=${page}-sentence=${sentence_id}-${index}`,
                    {
                      method: "POST",
                      headers: {
                        "Content-Type": "application/json",
                      },
                    }
                  )
                    .then((response) => response.json())
                    .then((data) => {
                      if (data.success) {
                        console.log("Thành công");
                        location.reload();
                      } else {
                        console.error("Không thể tải dữ liệu trường học");
                      }
                    })
                    .catch((error) => console.error("Lỗi:", error));
                });

                sectionText.appendChild(textSection);
                sectionText.appendChild(sectionLink);
                sectionSource.appendChild(sectionText);
                sectionSource.appendChild(icon);
                containerTextExclude.appendChild(sectionSource);
              });
            })
          }
        );

        const student = data.list_files[0].source.student_data;
        document.getElementById("flexCheckDefault_student").checked = student;

        const internet = data.list_files[0].source.internet;
        document.getElementById("flexCheckDefault_internet").checked = internet;

        const paper = data.list_files[0].source.paper;
        document.getElementById("flexCheckDefault_paper").checked = paper;

        const reference = data.list_files[0].fillter.references;
        document.getElementById("flexCheckDefault_reference").checked =
          reference;

        const quoted = data.list_files[0].fillter.quotation_marks;
        document.getElementById("flexCheckDefault_quoted").checked = quoted;

        const small = data.list_files[0].fillter.min_word.min_word;
        document.getElementById("flexCheckDefault_small").checked = small;

        const small_text = data.list_files[0].fillter.min_word.minWordValue;
        document.getElementById("input_small_text").value = small_text;
      } else {
        console.error("Không thể tải dữ liệu trường học");
      }
    })
    .catch((error) => console.error("Lỗi:", error));
}

function addAllSource() {
  fetch(`/api/add_all_source_school@file_id=${fileId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        console.log("Thành công");
        location.reload();
      } else {
        console.error("Không thể tải dữ liệu trường học");
      }
    })
    .catch((error) => console.error("Lỗi:", error));
}

function addTextSource() {
  fetch(`/api/add_all_text_school@file_id=${fileId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        console.log("Thành công");
        location.reload();
      } else {
        console.error("Không thể tải dữ liệu trường học");
      }
    })
    .catch((error) => console.error("Lỗi:", error));
}

function toggleFillterApply() {
  // Lấy giá trị của các checkbox
  const studentData = document.getElementById(
    "flexCheckDefault_student"
  ).checked;
  const internet = document.getElementById("flexCheckDefault_internet").checked;
  const paper = document.getElementById("flexCheckDefault_paper").checked;
  const references = document.getElementById(
    "flexCheckDefault_reference"
  ).checked;
  const curlybracket = document.getElementById(
    "flexCheckDefault_quoted"
  ).checked;
  const minWord = document.getElementById("flexCheckDefault_small").checked;

  var minWordValue = document.getElementById("input_small_text").value;

  var feedbackElement = document.getElementById("input_feedback");

  // Kiểm tra nếu giá trị là số nguyên và nằm trong khoảng từ 3 đến 100
  if (
    minWordValue &&
    !isNaN(minWordValue) &&
    Number.isInteger(Number(minWordValue))
  ) {
    minWordValue = Number(minWordValue); // Chuyển thành số nguyên

    if (minWordValue >= 3 && minWordValue < 100) {
      feedbackElement.textContent = ""; // Không hiển thị thông báo nếu giá trị hợp lệ
      const pdfPath = `/api/fillter@file_id=${fileId}`;

      fetch(pdfPath, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          studentData: studentData,
          internet: internet,
          paper: paper,
          references: references,
          curlybracket: curlybracket,
          minWord: minWord,
          minWordValue: minWordValue,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            console.log("Thành công");
            location.reload();
          } else {
            console.error("Không thể tải dữ liệu trường học");
          }
        })
        .catch((error) => console.error("Lỗi:", error));
    } else {
      feedbackElement.textContent =
        "Giá trị phải là số nguyên lớn hơn hoặc bằng 3 và nhỏ hơn 100.";
    }
  } else {
    feedbackElement.textContent = "Giá trị phải là số nguyên.";
  }
}
