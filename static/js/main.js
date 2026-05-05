// FR-02: Клієнтська валідація форми заявки

document.addEventListener("DOMContentLoaded", function () {

  const form = document.getElementById("requestForm");
  if (!form) return;

  const phoneInput = form.querySelector("[name='phone']");
  if (phoneInput) {
    phoneInput.addEventListener("blur", function () {
      const val = this.value.trim();
      const valid = /^\+380\d{9}$/.test(val);
      this.classList.toggle("is-invalid", !valid && val.length > 0);
      this.classList.toggle("is-valid", valid);
    });

    phoneInput.addEventListener("input", function () {
      if (this.value.startsWith("0") && !this.value.startsWith("+")) {
        this.value = "+38" + this.value;
      }
    });
  }

  const submitBtn = document.getElementById("submitBtn");
  if (submitBtn) {
    form.addEventListener("submit", function () {
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Відправляємо...';
      submitBtn.disabled = true;
    });
  }

  document.querySelectorAll("table tbody tr[data-href]").forEach(row => {
    row.addEventListener("click", function () {
      window.location.href = this.dataset.href;
    });
  });

});
