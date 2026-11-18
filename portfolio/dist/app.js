const menuButton = document.querySelector(".menu-toggle");
const navigation = document.querySelector(".main-nav");
function closeMenu(returnFocus = false) {
  navigation.classList.remove("is-open");
  menuButton.setAttribute("aria-expanded", "false");
  if (returnFocus) menuButton.focus();
}
menuButton.addEventListener("click", () => {
  const open = menuButton.getAttribute("aria-expanded") !== "true";
  menuButton.setAttribute("aria-expanded", String(open));
  navigation.classList.toggle("is-open", open);
});
navigation.addEventListener("click", (event) => {
  if (event.target.closest("a")) closeMenu();
});
document.addEventListener("click", (event) => {
  if (!event.target.closest(".site-header")) closeMenu();
});
document.addEventListener("keydown", (event) => {
  if (
    event.key === "Escape" &&
    menuButton.getAttribute("aria-expanded") === "true"
  )
    closeMenu(true);
});
window.matchMedia("(min-width: 720px)").addEventListener("change", (event) => {
  if (event.matches) closeMenu();
});

document.querySelectorAll(".project-toggle").forEach((button) => {
  button.addEventListener("click", () => {
    const expanded = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-expanded", String(expanded));
    document.getElementById(button.getAttribute("aria-controls")).hidden =
      !expanded;
    button.closest(".project").classList.toggle("is-collapsed", !expanded);
  });
});

const sections = [...document.querySelectorAll("main section[id]")];
const navLinks = [...navigation.querySelectorAll('a[href^="#"]')];
const observer = new IntersectionObserver(
  (entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    navLinks.forEach((link) => {
      if (link.hash === `#${visible.target.id}`)
        link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  },
  { rootMargin: "-15% 0px -40% 0px", threshold: [0, 0.15, 0.5] },
);
sections.forEach((section) => observer.observe(section));

const logoStrip = document.querySelector(".affiliations");
if (logoStrip) {
  const pauseButton = logoStrip.querySelector(".affiliations-pause");
  const motionPreference = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  );
  function syncLogoMotion() {
    logoStrip.classList.toggle("is-ready", !motionPreference.matches);
    pauseButton.hidden = motionPreference.matches;
  }
  pauseButton.addEventListener("click", () => {
    const paused = logoStrip.classList.toggle("is-paused");
    pauseButton.textContent = paused ? "Resume" : "Pause";
    pauseButton.setAttribute(
      "aria-label",
      paused ? "Resume logo animation" : "Pause logo animation",
    );
  });
  motionPreference.addEventListener("change", syncLogoMotion);
  syncLogoMotion();
}
