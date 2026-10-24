(() => {
  "use strict";

  const body = document.body;
  const navigation = document.querySelector("#app-navigation");
  const toggle = document.querySelector("[data-nav-toggle]");

  const setNavigation = (open) => {
    if (!navigation || !toggle) return;
    navigation.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    body.classList.toggle("nav-open", open);
    if (open) {
      navigation.querySelector("a, button")?.focus();
    } else {
      toggle.focus();
    }
  };

  toggle?.addEventListener("click", () => {
    setNavigation(toggle.getAttribute("aria-expanded") !== "true");
  });

  document.querySelector("[data-nav-close]")?.addEventListener("click", () => {
    setNavigation(false);
  });

  navigation?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (window.matchMedia("(max-width: 991.98px)").matches) {
        setNavigation(false);
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && body.classList.contains("nav-open")) {
      setNavigation(false);
    }
  });

  document.querySelectorAll("[data-dismiss-message]").forEach((button) => {
    button.addEventListener("click", () => button.closest(".alert")?.remove());
  });

  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      const question = form.dataset.confirm;
      if (question && !window.confirm(question)) {
        event.preventDefault();
        return;
      }

      const submit = form.querySelector("button[type='submit']");
      if (submit) {
        submit.disabled = true;
        submit.setAttribute("aria-busy", "true");
        submit.dataset.originalText = submit.textContent;
        submit.textContent = submit.dataset.busyText || "Procesando…";
      }
    });
  });
})();
