const individualBtn = document.querySelector("[data-type='individual']");
const organizationBtn = document.querySelector("[data-type='organization']");
const orgInput = document.getElementById("org-name");
const fullNameInput = document.getElementById("full-name");
const signupText = document.getElementById("signup-text");

if (individualBtn && organizationBtn) {
  individualBtn.addEventListener("click", () => {
    individualBtn.classList.add("active");
    organizationBtn.classList.remove("active");
    orgInput.style.display = "none";
    fullNameInput.style.display = "block";
    signupText.innerText =
      "If you are an individual and don’t need any business or advertising features, select individual";
  });

  organizationBtn.addEventListener("click", () => {
    organizationBtn.classList.add("active");
    individualBtn.classList.remove("active");
    orgInput.style.display = "block";
    fullNameInput.style.display = "none";
    signupText.innerText =
      "If you are an organization and want to be verified to get access to advertising and business features, select organization";
  });
}
