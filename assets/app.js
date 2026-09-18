/* Claude-free — landing page behaviour
   Everything here is progressive enhancement: the page is fully readable with JS off. */
(function () {
  'use strict';

  var root = document.documentElement;
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  };

  /* ---------- 1. Theme (system-aware, remembered per browser) ---------- */
  var themeBtn = document.getElementById('themeBtn');
  var mql = window.matchMedia ? window.matchMedia('(prefers-color-scheme: light)') : null;

  function applyTheme(next) {
    root.setAttribute('data-theme', next);
    if (themeBtn) {
      var toLight = next === 'light';
      themeBtn.setAttribute('aria-label', toLight ? 'Switch to dark theme' : 'Switch to light theme');
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', toLight ? '#f7f7fb' : '#07080d');
  }

  applyTheme(store.get('cf-theme') || (mql && mql.matches ? 'light' : 'dark'));

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      store.set('cf-theme', next);
      applyTheme(next);
    });
  }
  if (mql && !store.get('cf-theme') && mql.addEventListener) {
    mql.addEventListener('change', function (e) { applyTheme(e.matches ? 'light' : 'dark'); });
  }

  /* ---------- 2. Mobile nav ---------- */
  var navToggle = document.getElementById('navToggle');
  var nav = document.getElementById('nav');

  function setNav(open) {
    if (!nav || !navToggle) return;
    nav.classList.toggle('is-open', open);
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }

  if (navToggle) {
    navToggle.addEventListener('click', function () {
      setNav(navToggle.getAttribute('aria-expanded') !== 'true');
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      setNav(false);
      if (navToggle) navToggle.focus();
    }
  });
  document.addEventListener('click', function (e) {
    if (!nav || !nav.classList.contains('is-open')) return;
    if (!nav.contains(e.target) && !navToggle.contains(e.target)) setNav(false);
  });
  window.addEventListener('resize', function () {
    if (window.innerWidth > 760) setNav(false);
  });
  if (nav) {
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setNav(false); });
  }

  /* ---------- 3. Header shadow + reading progress ---------- */
  var head = document.getElementById('siteHead');
  var bar = document.getElementById('progressBar');
  var ticking = false;

  function onScroll() {
    var y = window.scrollY || window.pageYOffset || 0;
    if (head) head.classList.toggle('is-stuck', y > 8);
    if (bar) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(y / max, 1) : 0) + ')';
    }
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();

  /* ---------- 4. Scroll spy ---------- */
  var links = [].slice.call(document.querySelectorAll('.nav a[data-nav]'));
  if ('IntersectionObserver' in window && links.length) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) {
          var on = a.getAttribute('href') === '#' + en.target.id;
          a.classList.toggle('is-active', on);
          if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });

    links.forEach(function (a) {
      var sec = document.getElementById(a.getAttribute('href').slice(1));
      if (sec) spy.observe(sec);
    });
  }

  /* ---------- 5. Copy to clipboard ---------- */
  var toast = document.getElementById('toast');
  var toastTimer;

  function say(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove('is-on'); }, 2200);
  }

  function writeClip(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      ok ? resolve() : reject();
    });
  }

  document.addEventListener('click', function (e) {
    var direct = e.target.closest('[data-copy]');
    var target = e.target.closest('[data-copy-target]');
    var btn = direct || target;
    if (!btn) return;

    var text = '';
    if (direct) {
      text = direct.getAttribute('data-copy') || '';
    } else if (target) {
      var src = document.querySelector(target.getAttribute('data-copy-target'));
      text = src ? src.textContent : '';
    }
    if (!text) return;

    writeClip(text).then(function () {
      say('Copied to clipboard');
      var label = btn.querySelector('.copy') || btn;
      var prev = label.textContent;
      label.textContent = 'Copied ✓';
      setTimeout(function () { label.textContent = prev; }, 1600);
    }, function () {
      say('Copy blocked — select the text and press Ctrl/Cmd + C');
    });
  });

  /* ---------- 6. "What's inside" filters ---------- */
  var filters = document.querySelectorAll('.chip[data-filter]');
  var rows = document.querySelectorAll('#assetList .row');
  var empty = document.getElementById('assetEmpty');

  [].forEach.call(filters, function (chip) {
    chip.addEventListener('click', function () {
      var want = chip.getAttribute('data-filter');
      [].forEach.call(filters, function (c) {
        var on = c === chip;
        c.classList.toggle('is-on', on);
        c.setAttribute('aria-pressed', String(on));
      });
      var shown = 0;
      [].forEach.call(rows, function (row) {
        var match = want === 'all' || row.getAttribute('data-tag') === want;
        row.classList.toggle('is-hidden', !match);
        if (match) shown++;
      });
      if (empty) empty.hidden = shown !== 0;
    });
  });

  /* ---------- 7. Scroll reveal (JS opt-in, so no-JS keeps content visible) ---------- */
  var revealSel = '.card, .row, .steps li, .faq details, .code-card, .banner, .sec-head';
  var revealEls = [].slice.call(document.querySelectorAll(revealSel));
  revealEls.forEach(function (el, i) {
    el.setAttribute('data-reveal', '');
    el.style.transitionDelay = Math.min(i % 6, 5) * 55 + 'ms';
  });

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- 8. Back to top + year ---------- */
  var toTop = document.getElementById('toTop');
  if (toTop) {
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      var brand = document.querySelector('.brand');
      if (brand) setTimeout(function () { brand.focus({ preventScroll: true }); }, 420);
    });
  }
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
