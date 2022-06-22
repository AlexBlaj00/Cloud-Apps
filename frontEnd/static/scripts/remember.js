const rmCheck = document.getElementById("rememberMe"),
    emailInput = document.getElementById("email-username");

if (localStorage.checkbox && localStorage.checkbox !== "") {
  rmCheck.setAttribute("checked", "checked");
  emailInput.value = localStorage.email;
} else {
  rmCheck.removeAttribute("checked");
  emailInput.value = "";
}

function rememberMe() {
  if (rmCheck.checked && emailInput.value !== "") {
    localStorage.email = emailInput.value;
    localStorage.checkbox = rmCheck.value;
  } else {
    localStorage.email = "";
    localStorage.checkbox = "";
  }
}