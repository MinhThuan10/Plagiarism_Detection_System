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