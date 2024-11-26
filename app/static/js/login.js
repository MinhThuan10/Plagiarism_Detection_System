import { http } from "./httpConfig.js";

document
  .getElementById("loginButton")
  .addEventListener("click", function (event) {
    event.preventDefault();

    const emailInput = document.getElementById("form2Example18");
    const passwordInput = document.getElementById("form2Example28");
    const messageDiv = document.getElementById("loginMessage");

    messageDiv.textContent = "";
    messageDiv.style.color = "red"; // Mặc định là màu đỏ

    let allFilled = true;

    if (!emailInput.value) {
      messageDiv.textContent += "Email cannot be empty.";
      allFilled = false;
    }
    if (!passwordInput.value) {
      messageDiv.textContent += " Password cannot be empty.";
      allFilled = false;
    }

    if (allFilled) {
      fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: emailInput.value,
          password: passwordInput.value,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            messageDiv.textContent = "Verification successful!";
            messageDiv.style.color = "#0369C3"; // Màu xanh dương
            window.location.href = "home";
          } else {
            messageDiv.textContent = data.message;
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          messageDiv.textContent =
            "An error occurred while verifying. Please try again.";
        });
    }
  });

document
  .getElementById("forgot_passwd")
  .addEventListener("click", function (event) {
    event.preventDefault();
    const emailInput = document.getElementById("form2Example18");
    const messageDiv = document.getElementById("loginMessage");
    const loginForm = document.getElementById("loginForm");
    const verificationForm = document.getElementById("verificationForm");
    const loadingSpinner = document.getElementById("loadingSpinner");

    messageDiv.textContent = "";
    messageDiv.style.color = "red"; // Mặc định là màu đỏ

    let allFilled = true;

    if (!emailInput.value) {
      messageDiv.textContent += "Email cannot be empty.";
      allFilled = false;
    }

    if (allFilled) {
      loadingSpinner.style.display = "block"; // Hiển thị vòng tròn xoay
      fetch("/api/send_verification", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: emailInput.value,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          loadingSpinner.style.display = "none"; // Ẩn vòng tròn xoay
          if (data.success) {
            messageDiv.textContent = "Verification code sent successfully!";
            messageDiv.style.color = "#0369C3"; // Màu xanh dương
            loginForm.style.display = "none";
            verificationForm.style.display = "block";
          } else {
            messageDiv.textContent = data.message;
            messageDiv.style.color = "red";
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          messageDiv.textContent =
            "An error occurred while sending verification. Please try again.";
        });
    }
  });

document
  .getElementById("verifyButton")
  .addEventListener("click", function (event) {
    event.preventDefault();

    const verificationCode = document.getElementById("verificationCode");
    const verificationMessage = document.getElementById("verificationMessage");
    const emailInput = document.getElementById("form2Example18");
    const newPassWord1 = document.getElementById("new_password1");
    const newPassWord2 = document.getElementById("new_password2");

    verificationMessage.textContent = "";
    verificationMessage.style.color = "red"; // Mặc định là màu đỏ

    let allFilled = true;

    if (!newPassWord1.value) {
      verificationMessage.textContent += "Password cannot be empty.";
      allFilled = false;
    } else if (newPassWord1.value.length < 6) {
      verificationMessage.textContent +=
        " Password must be at least 6 characters.";
      allFilled = false;
    }

    if (!newPassWord2.value) {
      verificationMessage.textContent += " Password cannot be empty.";
      allFilled = false;
    } else if (newPassWord2.value.length < 6) {
      verificationMessage.textContent +=
        " Password must be at least 6 characters.";
      allFilled = false;
    }

    if (newPassWord1.value != newPassWord2.value) {
      verificationMessage.textContent += " Passwords are not the same.";
      allFilled = false;
    }
    if (!verificationCode.value) {
      verificationMessage.textContent += " Verification code cannot be empty.";
      allFilled = false;
    }

    if (allFilled) {
      http("/api/forgot_password", "POST", {
        email: emailInput.value,
        password: newPassWord1.value,
        verificationCode: verificationCode.value,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            verificationMessage.textContent = "Verification successful!";
            verificationMessage.style.color = "#0369C3"; // Màu xanh dương
            setTimeout(() => {
              window.location.href = "login";
            }, 3000);
          } else {
            verificationMessage.textContent = data.message;
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          verificationMessage.textContent =
            "An error occurred while verifying. Please try again.";
        });
    }
  });
