const school_id = ""
document.addEventListener("DOMContentLoaded", function() {
    fetch(`/api/school`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const schoolName = data.school_data[0].school_name;
            school_id = data.school_data[0].school_id
            document.getElementById('school_name').innerText = schoolName;

            const tbody = document.getElementById('class_table_body');
            data.list_classs.forEach(classInfo => {
                const row = document.createElement('tr');
        
                // Thêm các ô vào hàng
                row.innerHTML = `
                    <td class="ps-4">${classInfo.class_id}</td>
                    <td>
                        <a href="#" class="text-body" style="color: #35509a !important">${classInfo.class_name}</a>
                    </td>
                    <td>${classInfo.start_day}</td>
                    <td>${classInfo.end_day}</td>
                    <td>
                        <ul class="list-inline mb-0">
                            <li class="list-inline-item">
                                <a href="javascript:void(0);" data-bs-toggle="tooltip" data-bs-placement="top" title="Edit" class="px-2 text-primary">
                                    <i class="bx bx-pencil font-size-18"></i>
                                </a>
                            </li>
                            <li class="list-inline-item">
                                <a href="javascript:void(0);" data-bs-toggle="tooltip" data-bs-placement="top" title="Delete" class="px-2 text-danger">
                                    <i class="bx bx-trash-alt font-size-18"></i>
                                </a>
                            </li>
                        </ul>
                    </td>
                `;
                                // Thêm hàng vào tbody
                tbody.appendChild(row);
            });
        } else {
            console.error("Không thể tải dữ liệu trường học");
        }
    })
    .catch(error => console.error('Lỗi:', error));
});



document.addEventListener("DOMContentLoaded", function () {
const startDayInput = document.getElementById("startDay");
const today = new Date();

// Lấy ngày hiện tại và định dạng theo mm/dd/yyyy
const formattedDate =
    ("0" + (today.getMonth() + 1)).slice(-2) +
    "/" +
    ("0" + today.getDate()).slice(-2) +
    "/" +
    today.getFullYear();

startDayInput.value = formattedDate; // Tự động điền ngày đã định dạng
});

function convertDateFormat(dateString) {
    const [year, month, day] = dateString.split('-'); // Tách phần ngày tháng năm
    return `${month}/${day}/${year}`; // Trả về định dạng MM/DD/YYYY
}



document.getElementById("button_create_class").addEventListener("click", function(event) {
    event.preventDefault();

    const className = document.getElementById("className");
    const enrollmentKey = document.getElementById("enrollmentKey");
    const startDay = document.getElementById("startDay");
    const endDay = document.getElementById("endDay");
    const messageDiv = document.getElementById("signupMessage");
   
    messageDiv.textContent = '';

    let allFilled = true;

    if (!className.value) {
        messageDiv.textContent += "Please give class name! ";
        allFilled = false;
    }
    if (!enrollmentKey.value) {
        messageDiv.textContent += "Please give class key! ";
        allFilled = false;
    } else if (enrollmentKey.value.length < 6) {
        messageDiv.textContent += "Class key must be at least 6 characters! ";
        allFilled = false;
    }

    if (!endDay.value) {
        messageDiv.textContent += "Please chose end day! ";
        allFilled = false;
    }

    
    const convertedEndDay = convertDateFormat(endDay.value  );


    if (allFilled) {
        fetch(`/api/create_class@school=${school_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ class_name: className.value,
                class_key: enrollmentKey.value,
                start_day: startDay,
                end_day:convertedEndDay
             })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                
            } else {
                messageDiv.textContent = data.message; 
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageDiv.textContent = "Đã xảy ra lỗi khi đăng ký. Vui lòng thử lại.";
        });
    }
});


