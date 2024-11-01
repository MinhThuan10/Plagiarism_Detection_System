
let  school_id = ''

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
            const schoolName = data.school_data.school_name;
            school_id = data.school_data.school_id;
            document.getElementById('school_name').innerText = schoolName;
            console.log(schoolName);
            const tbody = document.getElementById('class_table_body');

            data.classs.forEach(classInfo => {
                const row = document.createElement('tr');

                // Thêm các ô vào hàng
                row.innerHTML = `
                    <td class="ps-4">${classInfo.class_id}</td>
                    <td>
                        <a href="class=${classInfo.class_id}" class="text-body" style="color: #35509a !important">${classInfo.class_name}</a>
                    </td>
                    <td>${classInfo.teacher_name}</td>
                    <td>${classInfo.start_day}</td>
                    <td>${classInfo.end_day}</td>
                    <td>
                        <ul class="list-inline mb-0">
                            <li class="list-inline-item">
                                <a href="#" data-mdb-toggle="modal" data-mdb-target="#deleteModal" title="Delete" class_id="${classInfo.class_id}" class="px-2 text-danger delete">
                                    <i class="bx bx-trash-alt font-size-18"></i>
                                </a>
                            </li>
                        </ul>
                    </td>
                `;

                tbody.appendChild(row);

                const deleteicon = row.querySelector('.delete');
                deleteicon.addEventListener('click', function() {
                    const class_id = this.getAttribute('class_id');
                    console.log('Đã nhấn xóa lớp có ID:', class_id);
                    const deletebutton = document.getElementById('submit_delete');
                    deletebutton.addEventListener('click', function(){
                        fetch(`/api/delete_user_to_class`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ 
                                class_id: class_id
                             })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                console.log(data.message); 
                                location.reload()
                                
                            } else {
                                console.log(data.message); 
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                        });
                    })
                    

                });

            });
        } else {
            console.error("Không thể tải dữ liệu trường học");
        }
    })
    .catch(error => console.error('Lỗi:', error));
});




document.getElementById("enroll_class").addEventListener("click", function(event) {
    event.preventDefault();

    const classId = document.getElementById("classId");
    const enrollmentKey = document.getElementById("enrollmentKey");
    const messageDiv = document.getElementById("signupMessage");
   
    messageDiv.textContent = '';

    let allFilled = true;

    if (!classId.value) {
        messageDiv.textContent += "Please give class name! ";
        allFilled = false;
    }
    if (!enrollmentKey.value) {
        messageDiv.textContent += "Please give class key! ";
        allFilled = false;
    }

    if (allFilled) {
        fetch(`/api/add_user_to_class`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                class_id: classId.value,
                class_key: enrollmentKey.value,
             })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                messageDiv.textContent = data.message; 
                location.reload()
            } else {
                messageDiv.textContent = data.message; 
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageDiv.textContent = "Đã xảy ra lỗi. Vui lòng thử lại.";
        });
    }
});


