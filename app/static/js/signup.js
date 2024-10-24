document.addEventListener("DOMContentLoaded", function() {
    fetch('/api/list_school', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hiển thị dữ liệu trường học lên giao diện
            let schools = data.list_school;
            let schoolSelect = document.getElementById('userRole');
            let defaultOption = schoolSelect.querySelector('option[value=""]');
                if (defaultOption) {
                    defaultOption.style.display = 'none';
                }
            schools.forEach(school => {
                let option = document.createElement('option');
                option.value = school.school_id; 
                option.textContent = school.school_name;
                schoolSelect.appendChild(option);
            });
        } else {
            console.error("Không thể tải dữ liệu trường học");
        }
    })
    .catch(error => console.error('Lỗi:', error));
});




document.getElementById("signupButton").addEventListener("click", function(event) {
    event.preventDefault();

    const firstNameInput = document.getElementById("form3Example1");
    const lastNameInput = document.getElementById("form3Example2");
    const emailInput = document.getElementById("form3Example3");
    const passwordInput = document.getElementById("form3Example4");
    const messageDiv = document.getElementById("signupMessage");
    const signupForm = document.getElementById("signupForm");
    const verificationForm = document.getElementById("verificationForm");
    const schoolSelect = document.getElementById('userRole');
    messageDiv.textContent = '';

    let allFilled = true;

    if (!firstNameInput.value) {
        messageDiv.textContent += "Please give your first name! ";
        allFilled = false;
    }
    if (!lastNameInput.value) {
        messageDiv.textContent += "Please give your lasr name! ";
        allFilled = false;
    }

    if (!schoolSelect.value) {
        messageDiv.textContent += "Please select school! ";
        allFilled = false;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; 
    if (!emailInput.value || !emailPattern.test(emailInput.value)) {
        messageDiv.textContent += "Invalid email! ";
        allFilled = false;
    }

    if (!passwordInput.value) {
        messageDiv.textContent += "Password cannot be blank! ";
        allFilled = false;
    } else if (passwordInput.value.length < 6) {
        messageDiv.textContent += "Password must be at least 6 characters! ";
        allFilled = false;
    }

    if (allFilled) {
        fetch('/api/send_verification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: emailInput.value })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                signupForm.style.display = "none";
                verificationForm.style.display = "block";
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




document.getElementById("verifyButton").addEventListener("click", function(event) {
    event.preventDefault();

    const verificationCode = document.getElementById("verificationCode").value;
    const verificationMessage = document.getElementById("verificationMessage");
    const firstNameInput = document.getElementById("form3Example1");
    const lastNameInput = document.getElementById("form3Example2");
    const role = document.querySelector('input[name="userType"]:checked');
    const emailInput = document.getElementById("form3Example3");
    const passwordInput = document.getElementById("form3Example4");
    const schoolSelect = document.getElementById('userRole');

    if (!verificationCode) {
        verificationMessage.textContent = "Mã xác nhận không được để trống.";
    } else {
        fetch('/api/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                first_name: firstNameInput.value,
                last_name: lastNameInput.value,
                role: role.value,
                email: emailInput.value,
                password: passwordInput.value,
                school_id: schoolSelect.value,
                verificationCode: verificationCode
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                verificationMessage.textContent = "Xác minh thành công!";
                setTimeout(() => {
                    window.location.href = "login"; 
                }, 3000);
            } else {
                verificationMessage.textContent = data.message;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            verificationMessage.textContent = "Đã xảy ra lỗi khi xác minh. Vui lòng thử lại.";
        });
    }
});