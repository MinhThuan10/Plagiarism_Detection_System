import { http } from "./httpConfig.js";

document.getElementById("loginButton").addEventListener("click", function(event) {
    event.preventDefault();

    const emailInput = document.getElementById("form2Example18");
    const passwordInput = document.getElementById("form2Example28");
    const messageDiv = document.getElementById("loginMessage");
    
    messageDiv.textContent = '';

    let allFilled = true;

    if (!emailInput.value) {
        messageDiv.textContent += "Emamil không được để trống. ";
        allFilled = false;
    }
    if (!passwordInput.value) {
        messageDiv.textContent += "Password không được để trống. ";
        allFilled = false;
    }

    if (allFilled) {

        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: emailInput.value,
                password: passwordInput.value,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                messageDiv.textContent = "Xác minh thành công!";
                
                window.location.href = "home"; 
                
            } else {
                messageDiv.textContent = data.message;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageDiv.textContent = "Đã xảy ra lỗi khi xác minh. Vui lòng thử lại.";
        });
    }
    
});

console.log(document.getElementById("forgot_passwd"))

document.getElementById("forgot_passwd").addEventListener("click", function(event) {
    console.log('Code chay vao day')
    event.preventDefault();
    const emailInput = document.getElementById("form2Example18");
    const messageDiv = document.getElementById("loginMessage");
    const loginForm = document.getElementById("loginForm");
    const verificationForm = document.getElementById("verificationForm");
    const loadingSpinner = document.getElementById("loadingSpinner");
    
    messageDiv.textContent = '';

    let allFilled = true;

    if (!emailInput.value) {
        messageDiv.textContent += "Email không được để trống. ";
        allFilled = false;
    }

    if (allFilled) {
        // Hiển thị vòng tròn xoay
        loadingSpinner.style.display = "block";
        fetch('/api/send_verification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: emailInput.value,
            })
        })
        .then(response => response.json())
        .then(data => {
             // Ẩn vòng tròn xoay
             loadingSpinner.style.display = "none";
            if (data.success) {
                loginForm.style.display = "none";
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

    const verificationCode = document.getElementById("verificationCode");
    const verificationMessage = document.getElementById("verificationMessage");
    const emailInput = document.getElementById("form2Example18");
    console.log(emailInput)
    const newPassWord1 = document.getElementById("new_password1");
    const newPassWord2 = document.getElementById("new_password2");
    verificationMessage.textContent = '';

    let allFilled = true;

    if (!newPassWord1.value) {
        verificationMessage.textContent += "Mật khẩu không được để trống. ";
        allFilled = false;
    } else if (newPassWord1.value.length < 6) {
        verificationMessage.textContent += "Mật khẩu phải có ít nhất 6 ký tự. ";
        allFilled = false;
    }

    if (!newPassWord2.value) {
        verificationMessage.textContent += "Mật khẩu không được để trống. ";
        allFilled = false;
    } else if (newPassWord2.value.length < 6) {
        verificationMessage.textContent += "Mật khẩu phải có ít nhất 6 ký tự. ";
        allFilled = false;
    }

    if (newPassWord1.value != newPassWord2.value) {
        verificationMessage.textContent += "Password không giống nhau";
        allFilled = false;
    }
    if (!verificationCode.value) {
        verificationMessage.textContent += "Mã xác nhận không được để trống. ";
        allFilled = false;
    }

    if (allFilled) {

        http('/api/forgot_password', 'POST', {
            email: emailInput.value,
            password: newPassWord1.value,
            verificationCode: verificationCode.value
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