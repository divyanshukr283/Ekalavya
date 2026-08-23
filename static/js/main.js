/**
 * main.js — Ekalavya v2 Frontend
 * ==========================================================================
 * 1. Theme (dark/light) — localStorage + prefers-color-scheme
 * 2. Navbar — sticky shrink + mobile hamburger
 * 3. AOS init
 * 4. Particle animation (hero canvas)
 * 5. Animated counters
 * 6. Hero dashboard bar animations
 * 7. Multi-step form (5 steps + progress bar)
 * 8. Form validation (per-step + full)
 * 9. Loading overlay with sequential step messages
 * 10. Scroll-reveal for demo section elements
 * ==========================================================================
 */

'use strict';

/* ── 1. Theme ────────────────────────────────────────────────────────────── */
(function initTheme() {
  const html        = document.documentElement;
  const toggleBtn   = document.getElementById('themeToggle');
  const iconDark    = document.getElementById('themeIconDark');
  const iconLight   = document.getElementById('themeIconLight');
  const KEY         = 'ek-theme';

  function apply(theme) {
    html.setAttribute('data-theme', theme);
    if (theme === 'dark') {
      iconDark  && (iconDark.style.display  = 'none');
      iconLight && (iconLight.style.display = '');
    } else {
      iconDark  && (iconDark.style.display  = '');
      iconLight && (iconLight.style.display = 'none');
    }
  }

  // Determine initial theme: saved > system preference > light
  const saved  = localStorage.getItem(KEY);
  const system = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  apply(saved || system);

  toggleBtn && toggleBtn.addEventListener('click', function () {
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    apply(next);
    localStorage.setItem(KEY, next);
  });

  // Listen for OS-level theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!localStorage.getItem(KEY)) apply(e.matches ? 'dark' : 'light');
  });
})();


/* ── 2. Navbar ───────────────────────────────────────────────────────────── */
(function initNavbar() {
  const nav       = document.getElementById('mainNav');
  const hamburger = document.getElementById('navHamburger');
  const mobileMenu= document.getElementById('mobileMenu');
  if (!nav) return;

  // Shrink on scroll
  window.addEventListener('scroll', function () {
    nav.style.boxShadow = window.scrollY > 50
      ? '0 2px 20px rgba(0,0,0,0.12)'
      : '0 1px 12px rgba(0,0,0,0.05)';
  }, { passive: true });

  // Mobile hamburger toggle
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', function () {
      const isHidden = mobileMenu.hidden;
      mobileMenu.hidden = !isHidden;
      hamburger.setAttribute('aria-expanded', String(isHidden));
    });
    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!nav.contains(e.target)) {
        mobileMenu.hidden = true;
        hamburger.setAttribute('aria-expanded', 'false');
      }
    });
    // Close on mobile link click
    mobileMenu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        mobileMenu.hidden = true;
        hamburger.setAttribute('aria-expanded', 'false');
      });
    });
  }
})();


/* ── 3. AOS ──────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  if (typeof AOS !== 'undefined') {
    AOS.init({ duration: 650, once: true, offset: 60, easing: 'ease-out-cubic' });
  }
});


/* ── 4. Particle Animation ───────────────────────────────────────────────── */
(function initParticles() {
  const canvas = document.getElementById('particleCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() {
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize, { passive: true });

  const PARTICLE_COUNT = 55;
  const particles = Array.from({ length: PARTICLE_COUNT }, function () {
    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 2 + 1,
      dx: (Math.random() - 0.5) * 0.4,
      dy: (Math.random() - 0.5) * 0.4,
      alpha: Math.random() * 0.5 + 0.15,
    };
  });

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(function (p) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,255,255,${p.alpha})`;
      ctx.fill();

      p.x += p.dx;
      p.y += p.dy;
      if (p.x < 0 || p.x > canvas.width)  p.dx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
    });

    // Draw connecting lines
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 90) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(255,255,255,${0.08 * (1 - dist / 90)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
})();


/* ── 5. Animated Counters ────────────────────────────────────────────────── */
(function initCounters() {
  const counters = document.querySelectorAll('.hero__counter-num[data-target]');
  if (!counters.length) return;

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      const el     = entry.target;
      const target = parseInt(el.dataset.target, 10);
      let current  = 0;
      const step   = Math.ceil(target / 40);
      const timer  = setInterval(function () {
        current = Math.min(current + step, target);
        el.textContent = current;
        if (current >= target) clearInterval(timer);
      }, 30);
      observer.unobserve(el);
    });
  }, { threshold: 0.6 });

  counters.forEach(function (el) { observer.observe(el); });
})();


/* ── 6. Hero Dashboard Bar Animations ───────────────────────────────────── */
(function initDashBars() {
  const bars = document.querySelectorAll('.hdash__bar[data-width]');
  if (!bars.length) return;

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.style.width = entry.target.dataset.width + '%';
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.3 });

  bars.forEach(function (b) { observer.observe(b); });

  // Also trigger confidence ring animation
  const confCircle = document.querySelector('.hdash__conf-circle');
  const gaugeFill  = document.querySelector('.hdash__gauge-fill');
  if (confCircle) {
    setTimeout(function () { confCircle.style.strokeDashoffset = '6'; }, 800);
  }
  if (gaugeFill) {
    setTimeout(function () { gaugeFill.style.strokeDashoffset = '0'; }, 800);
  }

  // AI section demos
  document.querySelectorAll('.ai-strength-bar[data-width]').forEach(function (el) {
    const obs = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) {
        el.style.width = el.dataset.width + '%';
        obs.unobserve(el);
      }
    }, { threshold: 0.3 });
    obs.observe(el);
  });

  // Readiness ring
  const readCircle = document.querySelector('.ai-readiness-circle');
  if (readCircle) {
    const obs = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) {
        readCircle.style.strokeDashoffset = '26';
        obs.unobserve(readCircle);
      }
    }, { threshold: 0.3 });
    obs.observe(readCircle);
  }
})();


/* ── 7. Multi-step Form ──────────────────────────────────────────────────── */
(function initMultiStep() {
  const form       = document.getElementById('assessmentForm');
  if (!form) return;

  const steps      = form.querySelectorAll('.form-step');
  const dots       = document.querySelectorAll('.step-progress__dot');
  const fill       = document.getElementById('stepFill');
  const prevBtn    = document.getElementById('prevBtn');
  const nextBtn    = document.getElementById('nextBtn');
  const submitWrap = document.getElementById('submitWrap');
  const navDots    = document.querySelectorAll('.form-nav__dots .dot');
  const TOTAL      = steps.length;
  let currentStep  = 1;

  function getStepFields(stepNum) {
    const stepEl = document.getElementById('step-' + stepNum);
    if (!stepEl) return [];
    return Array.from(stepEl.querySelectorAll('input[required], select[required]'));
  }

  function validateStep(stepNum) {
    const fields = getStepFields(stepNum);
    let valid = true;
    fields.forEach(function (field) {
      if (!validateField(field)) valid = false;
    });
    return valid;
  }

  function goToStep(n) {
    steps.forEach(function (s, i) {
      s.hidden = (i + 1 !== n);
      s.classList.toggle('active', i + 1 === n);
    });
    dots.forEach(function (d, i) {
      const stepNum = i + 1;
      d.classList.toggle('active',    stepNum === n);
      d.classList.toggle('complete',  stepNum < n);
      d.setAttribute('aria-current', stepNum === n ? 'step' : 'false');
    });
    navDots.forEach(function (d, i) {
      d.classList.toggle('active', i + 1 === n);
    });

    // Progress fill
    if (fill) fill.style.width = ((n - 1) / (TOTAL - 1) * 100) + '%';

    // Buttons
    if (prevBtn) prevBtn.style.visibility = n === 1 ? 'hidden' : 'visible';
    if (nextBtn) nextBtn.hidden = n === TOTAL;
    if (submitWrap) submitWrap.hidden = n !== TOTAL;

    currentStep = n;

    // Scroll to top of form
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Next button
  nextBtn && nextBtn.addEventListener('click', function () {
    if (validateStep(currentStep) && currentStep < TOTAL) {
      goToStep(currentStep + 1);
    }
  });

  // Prev button
  prevBtn && prevBtn.addEventListener('click', function () {
    if (currentStep > 1) goToStep(currentStep - 1);
  });

  // Step dot navigation (allow going back)
  dots.forEach(function (dot) {
    dot.addEventListener('click', function () {
      const target = parseInt(dot.dataset.step, 10);
      if (target < currentStep) goToStep(target);
      else if (target === currentStep + 1 && validateStep(currentStep)) goToStep(target);
    });
  });

  // Expose for server-error redirect
  window.EkalavyaForm = { goToStep: goToStep };

  // Init
  goToStep(1);
})();


/* ── 8. Form Validation ──────────────────────────────────────────────────── */
const NUMERIC_RULES = {
  age:                       { min: 3,   max: 25,       label: 'Age' },
  attendance_percentage:     { min: 0,   max: 100,      label: 'Attendance (%)' },
  math_score:                { min: 0,   max: 100,      label: 'Math Score' },
  science_score:             { min: 0,   max: 100,      label: 'Science Score' },
  english_score:             { min: 0,   max: 100,      label: 'English Score' },
  social_science_score:      { min: 0,   max: 100,      label: 'Social Science Score' },
  previous_grade_percentage: { min: 0,   max: 100,      label: 'Previous Grade (%)' },
  study_hours_per_day:       { min: 0,   max: 24,       label: 'Study Hours / Day' },
  annual_family_income:      { min: 0,   max: 10000000, label: 'Annual Family Income' },
  family_size:               { min: 1,   max: 20,       label: 'Family Size' },
  distance_to_school_km:     { min: 0,   max: 200,      label: 'Distance to School' },
};

function showError(field, msg) {
  field.classList.add('is-invalid');
  field.classList.remove('is-valid');
  field.setAttribute('aria-invalid', 'true');
  let fb = field.parentElement.querySelector('.invalid-feedback');
  if (!fb) {
    fb = document.createElement('div');
    fb.className = 'invalid-feedback';
    field.parentElement.appendChild(fb);
  }
  fb.textContent = msg;
}

function clearError(field) {
  field.classList.remove('is-invalid');
  field.classList.add('is-valid');
  field.removeAttribute('aria-invalid');
  const fb = field.parentElement.querySelector('.invalid-feedback');
  if (fb) fb.textContent = '';
}

function validateField(field) {
  const name  = field.name;
  const value = field.value.trim();
  const rule  = NUMERIC_RULES[name];
  const label = field.labels && field.labels[0]
    ? field.labels[0].textContent.replace(/\s*\*/, '').trim()
    : (rule ? rule.label : name);

  if (value === '') {
    showError(field, label + ' is required.');
    return false;
  }
  if (rule) {
    const num = parseFloat(value);
    if (isNaN(num)) { showError(field, label + ' must be a valid number.'); return false; }
    if (num < rule.min || num > rule.max) {
      showError(field, label + ' must be between ' + rule.min + ' and ' + rule.max + '.');
      return false;
    }
  }
  clearError(field);
  return true;
}

(function attachLiveValidation() {
  const form = document.getElementById('assessmentForm');
  if (!form) return;
  form.querySelectorAll('input, select').forEach(function (field) {
    field.addEventListener('blur',   function () { validateField(field); });
    field.addEventListener('change', function () { validateField(field); });
  });

  form.addEventListener('submit', function (e) {
    // Validate all fields across all steps
    let allValid = true;
    form.querySelectorAll('input[required], select[required]').forEach(function (f) {
      if (!validateField(f)) allValid = false;
    });
    if (!allValid) {
      e.preventDefault();
      const firstInvalid = form.querySelector('.is-invalid');
      if (firstInvalid) {
        const stepEl = firstInvalid.closest('.form-step');
        if (stepEl && window.EkalavyaForm) {
          const n = parseInt(stepEl.id.split('-')[1], 10);
          window.EkalavyaForm.goToStep(n);
        }
        setTimeout(function () {
          firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
          firstInvalid.focus();
        }, 200);
      }
      return;
    }
    showLoader();
  });
})();


/* ── 9. Loading Overlay ──────────────────────────────────────────────────── */
const LOADER_STEPS = [
  { text: 'Collecting Student Information…',          pct: 14 },
  { text: 'Analyzing Academic Performance…',          pct: 28 },
  { text: 'Evaluating Learning Environment…',         pct: 43 },
  { text: 'Assessing Educational Risk Factors…',      pct: 58 },
  { text: 'Generating Personalized Insights…',        pct: 72 },
  { text: 'Preparing Recommendation Dashboard…',      pct: 88 },
  { text: 'Prediction Complete ✓',                    pct: 100 },
];

function showLoader() {
  const overlay  = document.getElementById('loadingOverlay');
  const stepText = document.getElementById('loaderStep');
  const bar      = document.getElementById('loaderBar');
  const btnText  = document.getElementById('submitBtnText');

  if (overlay) overlay.hidden = false;
  if (btnText) btnText.textContent = 'Processing…';

  let i = 0;
  function next() {
    if (i >= LOADER_STEPS.length) return;
    const s = LOADER_STEPS[i++];
    if (stepText) stepText.textContent = s.text;
    if (bar) bar.style.width = s.pct + '%';
    setTimeout(next, 420);
  }
  next();
}

function hideLoader() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.hidden = true;
}

window.addEventListener('pageshow', function (e) {
  if (e.persisted) hideLoader();
});


/* ── 10. Smooth anchor scroll ────────────────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(function (a) {
  a.addEventListener('click', function (e) {
    const id = this.getAttribute('href').slice(1);
    if (!id) return;
    const target = document.getElementById(id);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
