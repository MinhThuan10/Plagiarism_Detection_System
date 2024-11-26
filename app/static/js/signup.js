document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/list_school", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Display the list of schools
        let schools = data.list_school;
        let schoolSelect = document.getElementById("userRole");
        let defaultOption = schoolSelect.querySelector('option[value=""]');
        if (defaultOption) {
          defaultOption.style.display = "none";
        }
        schools.forEach((school) => {
          let option = document.createElement("option");
          option.value = school.school_id;
          option.textContent = school.school_name;
          schoolSelect.appendChild(option);
        });
      } else {
        console.error("Failed to load school data.");
      }
    })
    .catch((error) => console.error("Error:", error));
});

document
  .getElementById("signupButton")
  .addEventListener("click", function (event) {
    event.preventDefault();

    const firstNameInput = document.getElementById("form3Example1");
    const lastNameInput = document.getElementById("form3Example2");
    const emailInput = document.getElementById("form3Example3");
    const passwordInput = document.getElementById("form3Example4");
    const messageDiv = document.getElementById("signupMessage");
    const signupForm = document.getElementById("signupForm");
    const verificationForm = document.getElementById("verificationForm");
    const schoolSelect = document.getElementById("userRole");
    messageDiv.textContent = "";
    messageDiv.style.color = "red"; // Mặc định là màu đỏ

    let allFilled = true;

    if (!firstNameInput.value) {
      messageDiv.textContent += "Please provide your first name! ";
      allFilled = false;
    }
    if (!lastNameInput.value) {
      messageDiv.textContent += "Please provide your last name! ";
      allFilled = false;
    }

    if (!schoolSelect.value) {
      messageDiv.textContent += "Please select your school! ";
      allFilled = false;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailInput.value || !emailPattern.test(emailInput.value)) {
      messageDiv.textContent += "Invalid email address! ";
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
      fetch("/api/send_verification", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: emailInput.value }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            signupForm.style.display = "none";
            verificationForm.style.display = "block";
            messageDiv.style.color = "#0369C3";
            messageDiv.textContent = "Verification code sent successfully!";
          } else {
            messageDiv.style.color = "red";
            messageDiv.textContent = data.message;
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          messageDiv.style.color = "red";
          messageDiv.textContent =
            "An error occurred during registration. Please try again.";
        });
    }
  });

document
  .getElementById("verifyButton")
  .addEventListener("click", function (event) {
    event.preventDefault();

    const verificationCode = document.getElementById("verificationCode").value;
    const verificationMessage = document.getElementById("verificationMessage");
    const firstNameInput = document.getElementById("form3Example1");
    const lastNameInput = document.getElementById("form3Example2");
    const role = document.querySelector('input[name="userType"]:checked');
    const emailInput = document.getElementById("form3Example3");
    const passwordInput = document.getElementById("form3Example4");
    const schoolSelect = document.getElementById("userRole");

    verificationMessage.textContent = "";

    if (!verificationCode) {
      verificationMessage.style.color = "red";
      verificationMessage.textContent = "Verification code cannot be empty.";
    } else {
      fetch("/api/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          first_name: firstNameInput.value,
          last_name: lastNameInput.value,
          role: role.value,
          email: emailInput.value,
          password: passwordInput.value,
          school_id: schoolSelect.value,
          verificationCode: verificationCode,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            verificationMessage.style.color = "#0369C3";
            verificationMessage.textContent = "Verification successful!";
            setTimeout(() => {
              window.location.href = "login";
            }, 3000);
          } else {
            verificationMessage.style.color = "red";
            verificationMessage.textContent = data.message;
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          verificationMessage.style.color = "red";
          verificationMessage.textContent =
            "An error occurred during verification. Please try again.";
        });
    }
  });
