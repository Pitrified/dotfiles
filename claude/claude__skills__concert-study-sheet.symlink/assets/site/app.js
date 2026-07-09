(function () {
  'use strict';

  var root = document.documentElement;
  // storage keys derive from the project slug the build stamps on <html>,
  // so this file needs no per-project edits
  var project = root.getAttribute('data-project') || 'concert';
  var ENKEY = project + '.showTranslation';
  var VKEY = project + '.vibes';

  // --- translation toggle ---
  var enBtn = document.getElementById('toggle-en');
  // no translation on this page (e.g. Ábreme Paso): keep the button hidden
  if (enBtn && document.querySelector('.line .en')) {
    enBtn.hidden = false;
    var applyEn = function (on) {
      root.classList.toggle('show-en', on);
      enBtn.textContent = on ? 'hide translation' : 'show translation';
    };
    applyEn(localStorage.getItem(ENKEY) === '1');
    enBtn.addEventListener('click', function () {
      var on = !root.classList.contains('show-en');
      localStorage.setItem(ENKEY, on ? '1' : '0');
      applyEn(on);
    });
  }

  // --- vibe tagging ---
  // in "tag vibes" mode a click toggles the section's energy accent; the
  // choice is kept in localStorage (full selector list per touched song)
  // and "copy vibes json" exports the visible state in energy.json format,
  // to be pasted into scripts/energy.json and rebuilt.
  var vibeBtn = document.getElementById('vibe-toggle');
  var exportBtn = document.getElementById('vibe-export');
  if (!vibeBtn || !exportBtn || !document.querySelector('section[data-sel]')) return;
  vibeBtn.hidden = false;

  function loadVibes() {
    try { return JSON.parse(localStorage.getItem(VKEY)) || {}; }
    catch (e) { return {}; }
  }

  function eachScope(fn) {
    Array.prototype.forEach.call(document.querySelectorAll('[data-slug]'), fn);
  }

  function selsOn(scope) {
    return Array.prototype.map.call(
      scope.querySelectorAll('section.energy[data-sel]'),
      function (s) { return s.getAttribute('data-sel'); }
    );
  }

  // replay stored choices over the baked-in defaults
  var stored = loadVibes();
  eachScope(function (scope) {
    var sels = stored[scope.getAttribute('data-slug')];
    if (!sels) return;
    Array.prototype.forEach.call(
      scope.querySelectorAll('section[data-sel]'),
      function (s) {
        s.classList.toggle('energy', sels.indexOf(s.getAttribute('data-sel')) !== -1);
      }
    );
  });

  vibeBtn.addEventListener('click', function () {
    var on = root.classList.toggle('vibe-edit');
    vibeBtn.textContent = on ? 'done' : 'tag vibes';
    exportBtn.hidden = !on;
  });

  document.addEventListener('click', function (e) {
    if (!root.classList.contains('vibe-edit')) return;
    if (e.target.closest('a, button')) return;
    var sec = e.target.closest('section[data-sel]');
    if (!sec) return;
    sec.classList.toggle('energy');
    var scope = sec.closest('[data-slug]');
    var v = loadVibes();
    v[scope.getAttribute('data-slug')] = selsOn(scope);
    localStorage.setItem(VKEY, JSON.stringify(v));
  });

  exportBtn.addEventListener('click', function () {
    var touched = loadVibes();
    var out = {};
    eachScope(function (scope) {
      var slug = scope.getAttribute('data-slug');
      var sels = selsOn(scope);
      if (sels.length || touched[slug]) out[slug] = sels;
    });
    var text = JSON.stringify(out, null, 2);
    var done = function () {
      exportBtn.textContent = 'copied!';
      setTimeout(function () { exportBtn.textContent = 'copy vibes json'; }, 1500);
    };
    var fallback = function () { window.prompt('paste into scripts/energy.json:', text); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else {
      fallback();
    }
  });
})();
