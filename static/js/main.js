// ---------------------------------------------------------------------------
// Grey Academy — site-wide interactivity.
// Plain vanilla JS, no build step needed. Split into small, commented
// functions so it's easy to find and adjust any single piece of behaviour.
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  initScrollReveal();
  initNavbarScrollState();
  initMobileNavToggle();
  initAutoDismissMessages();
});

/**
 * Fades/slides any element with class="reveal" into view the first time it
 * scrolls into the viewport. Uses IntersectionObserver so it's cheap and
 * doesn't run on every scroll event.
 */
function initScrollReveal() {
  const revealEls = document.querySelectorAll(".reveal");
  if (!revealEls.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  revealEls.forEach((el) => observer.observe(el));
}

/** Adds a subtle shadow to the navbar once the page has scrolled a bit. */
function initNavbarScrollState() {
  const nav = document.querySelector(".navbar");
  if (!nav) return;

  const toggleScrolled = () => {
    nav.classList.toggle("scrolled", window.scrollY > 12);
  };
  toggleScrolled();
  window.addEventListener("scroll", toggleScrolled, { passive: true });
}

/** Opens/closes the mobile nav menu. */
function initMobileNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (!toggle || !links) return;

  toggle.addEventListener("click", () => {
    const isOpen = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });
}
function startVerificationPoll(statusUrl, redirectUrl, intervalMs = 3000) {
  const check = () => {
    fetch(statusUrl)
      .then((res) => res.json())
      .then((data) => { if (data.verified) window.location.href = redirectUrl; })
      .catch(() => {});
  };
  check();
  return setInterval(check, intervalMs);
}

/** Django messages auto-dismiss after a few seconds. */
function initAutoDismissMessages() {
  document.querySelectorAll(".message").forEach((msg, i) => {
    setTimeout(() => {
      msg.style.opacity = "0";
      msg.style.transform = "translateX(24px)";
      setTimeout(() => msg.remove(), 400);
    }, 5000 + i * 300);
  });
}

/**
 * Verification-link countdown (used on the "check your inbox" page).
 * Call startCountdown(seconds) from that template's inline script.
 * Ticks a ring + mm:ss label down to zero, then reveals the "resend" button.
 */
function startCountdown(totalSeconds) {
  const label = document.getElementById("countdown-label");
  const ring = document.getElementById("countdown-ring");
  const resendBtn = document.getElementById("resend-btn");
  if (!label || !ring) return;

  let remaining = totalSeconds;

  const render = () => {
    const m = String(Math.floor(remaining / 60)).padStart(2, "0");
    const s = String(remaining % 60).padStart(2, "0");
    label.textContent = `${m}:${s}`;
    const pct = totalSeconds > 0 ? (remaining / totalSeconds) * 100 : 0;
    ring.style.setProperty("--pct", pct.toFixed(2));

    if (remaining <= 0) {
      label.textContent = "Expired";
      if (resendBtn) resendBtn.removeAttribute("disabled");
      return;
    }
    remaining -= 1;
    setTimeout(render, 1000);
  };

  render();
}
