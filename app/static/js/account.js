const btnSave = document.getElementById("btn_save");
btnSave.addEventListener("click", function () {
  const messageDiv = document.getElementById("signupMessage");
  const first_name = document.getElementById("first-name");
  const last_name = document.getElementById("last-name");
  const old_password = document.getElementById("old_password");
  const new_password = document.getElementById("new_password");

  messageDiv.textContent = "";
  allFilled = true;
  if (!new_password.value) {
    messageDiv.textContent += "Password cannot be blank! ";
    messageDiv.style.color = "red";

    allFilled = false;
  } else if (new_password.value.length < 6) {
    messageDiv.textContent += "Password must be at least 6 characters! ";
    messageDiv.style.color = "red";

    allFilled = false;
  }
  if (allFilled) {
    fetch(`/api/update_user`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        first_name: first_name.value,
        last_name: last_name.value,
        old_password: old_password.value,
        new_password: new_password.value,
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
        messageDiv.textContent = data.message;
        messageDiv.style.color = "red";
      });
  }
});
