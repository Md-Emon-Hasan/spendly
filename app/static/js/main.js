/* Spendly — main.js */

document.addEventListener('DOMContentLoaded', function () {

  /* ── MOBILE SIDEBAR ── */
  var hamburger = document.getElementById('hamburgerBtn');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');

  if (hamburger && sidebar) {
    hamburger.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      overlay && overlay.classList.toggle('show');
    });
    overlay && overlay.addEventListener('click', function () {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }

  /* ── FLASH → TOAST ── */
  var flashData = document.getElementById('flash-data');
  if (flashData) {
    var spans = flashData.querySelectorAll('span');
    spans.forEach(function (span) {
      var cat = span.getAttribute('data-cat') || 'info';
      showToast(span.textContent.trim(), cat);
    });
  }

  /* ── PROGRESS BAR ANIMATION ── */
  var fills = document.querySelectorAll('.progress-fill, .goal-progress-fill, .cat-fill, .health-score-fill');
  fills.forEach(function (el) {
    el.style.transformOrigin = 'left center';
  });

  /* ── KEYBOARD SHORTCUTS (global) ── */
  document.addEventListener('keydown', function (e) {
    if (document.activeElement.tagName === 'INPUT' ||
        document.activeElement.tagName === 'TEXTAREA' ||
        document.activeElement.tagName === 'SELECT') return;

    /* Ctrl/Cmd + E → open add expense (dashboard) */
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
      e.preventDefault();
      var m = document.getElementById('addExpenseModal');
      if (m) { m.style.display = 'flex'; setTimeout(function () { m.classList.add('open'); }, 10); }
    }
    /* Ctrl/Cmd + I → open add income (dashboard) */
    if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
      e.preventDefault();
      var m = document.getElementById('addIncomeModal');
      if (m) { m.style.display = 'flex'; setTimeout(function () { m.classList.add('open'); }, 10); }
    }
  });

  /* ── STAT COUNTER ANIMATION ── */
  animateCounters();

});

/* ── TOAST SYSTEM ── */
function showToast(message, type) {
  type = type || 'info';
  var container = document.getElementById('toast-container');
  if (!container) return;

  var icons = { success: '✓', danger: '✕', warning: '⚠', info: 'ℹ' };
  var classMap = { success: 't-success', error: 't-danger', danger: 't-danger', warning: 't-warning', info: 't-info' };

  var toast = document.createElement('div');
  toast.className = 'toast ' + (classMap[type] || 't-info');
  toast.innerHTML = '<span class="toast-icon">' + (icons[type] || icons.info) + '</span>' +
                    '<span>' + escapeHtml(message) + '</span>';
  container.appendChild(toast);

  setTimeout(function () {
    toast.classList.add('hide');
    setTimeout(function () { toast.remove(); }, 320);
  }, 3500);
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* ── COUNTER ANIMATION ── */
function animateCounters() {
  var values = document.querySelectorAll('.stat-value');
  values.forEach(function (el) {
    var text = el.textContent.trim();
    var match = text.match(/৳\s*([\d,]+)/);
    if (!match) return;
    var target = parseInt(match[1].replace(/,/g, ''), 10);
    if (isNaN(target) || target < 100) return;

    var start = 0;
    var duration = 900;
    var startTime = null;
    var prefix = text.replace(match[0], '').trim();

    function step(ts) {
      if (!startTime) startTime = ts;
      var progress = Math.min((ts - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = Math.round(eased * target);
      el.textContent = (prefix ? prefix + ' ' : '') + '৳ ' + current.toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = text;
    }
    requestAnimationFrame(step);
  });
}

/* ── GLOBAL MODAL HELPERS (available to inline scripts) ── */
window.openModal = function (id) {
  var m = document.getElementById(id);
  if (!m) return;
  m.style.display = 'flex';
  setTimeout(function () { m.classList.add('open'); }, 10);
};
window.closeModal = function (id) {
  var m = document.getElementById(id);
  if (!m) return;
  m.classList.remove('open');
  setTimeout(function () { m.style.display = 'none'; }, 280);
};
