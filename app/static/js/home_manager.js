document.addEventListener("DOMContentLoaded", function() {
    fetch(`/api/list_school`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const tbody = document.getElementById('school_table_body');

            data.list_school.forEach(schoolInfo => {
                const row = document.createElement('tr');

                // Thêm các ô vào hàng
                row.innerHTML = `
                    <td class="ps-4">${schoolInfo.school_id}</td>
                    <td>
                        <a href="#" class="text-body" style="color: #35509a !important">${schoolInfo.school_name}</a>
                    </td>
                    <td>${schoolInfo.school_key}</td>
                    <td>${schoolInfo.school_email}</td>
                    <td>
                        <ul class="list-inline mb-0">
                            <li class="list-inline-item">
                                <a href="#" data-mdb-toggle="modal" data-mdb-target="#editModal" title="Edit" school_id="${schoolInfo.school_id}" class="px-2 text-primary edit">
                                    <i class="bx bx-pencil font-size-18"></i>
                                </a>
                            </li>
                            <li class="list-inline-item">
                                <a href="#" data-mdb-toggle="modal" data-mdb-target="#deleteModal" title="Delete" school_id="${schoolInfo.school_id}" class="px-2 text-danger delete">
                                    <i class="bx bx-trash-alt font-size-18"></i>
                                </a>
                            </li>
                        </ul>
                    </td>
                `;

                tbody.appendChild(row);

                
                const deleteicon = row.querySelector('.delete');
                deleteicon.addEventListener('click', function() {
                    const school_id = this.getAttribute('school_id');
                    console.log('Đã nhấn xóa lớp có ID:', school_id);
                    const deletebutton = document.getElementById('submit_delete');
                    deletebutton.addEventListener('click', function(){
                        fetch(`/api/delete_school@school=${school_id}`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json'
                            }
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
                
                    

                const editicon = row.querySelector('.edit');
                editicon.addEventListener('click', function() {
                    const school_id = this.getAttribute('school_id');
                    document.getElementById('schoolName_replace').value = schoolInfo.school_name
                    document.getElementById('schoolKey_replace').value = schoolInfo.school_key
                    document.getElementById('schoolEmail_replace').value = schoolInfo.school_email; 

                    const deletebutton = document.getElementById('update_btn');
                    deletebutton.addEventListener('click', function(){
                        const schoolName_replace = document.getElementById('schoolName_replace');
                        const schoolKey_replace = document.getElementById('schoolKey_replace');
                        const schoolEmail_replace = document.getElementById('schoolEmail_replace');

                        fetch(`/api/update_school@school=${school_id}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ 
                                school_name: schoolName_replace.value,
                                school_key: schoolKey_replace.value,
                                school_email: schoolEmail_replace.value
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





document.getElementById("button_create_school").addEventListener("click", function(event) {
    event.preventDefault();

    const schoolName = document.getElementById("schoolName");
    const schoolKey = document.getElementById("schoolKey");
    const schoolEmail = document.getElementById("schoolEmail");
    const messageDiv = document.getElementById("signupMessage");
   
    messageDiv.textContent = '';

    let allFilled = true;

    if (!schoolName.value) {
        messageDiv.textContent += "Please give School name! ";
        allFilled = false;
    }
    if (!schoolKey.value) {
        messageDiv.textContent += "Please give School key! ";
        allFilled = false;
    } else if (schoolKey.value.length < 6) {
        messageDiv.textContent += "School key must be at least 6 characters! ";
        allFilled = false;
    }

    if (!schoolEmail.value) {
        messageDiv.textContent += "Please give School email! ";
        allFilled = false;
    }

    
    if (allFilled) {
        fetch(`/api/create_school`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ school_name: schoolName.value,
                school_key: schoolKey.value,
                school_email: schoolEmail.value
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



