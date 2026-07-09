// ==UserScript==
// @name         Genius: collapse repeated sections
// @namespace    pmn.genius-collapse-repeats
// @version      0.1
// @description  On Genius lyrics pages, show each section once; repeats (chorus, refrain, ...) are collapsed to their header with a click-to-expand toggle.
// @match        https://genius.com/*
// @run-at       document-idle
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  const HEADER_RE = /^\s*\[[^\]]{1,80}\]\s*$/;

  // Hide inline interstitials ("You might also like", ad slots) that Genius
  // injects mid-lyrics; they carry data-exclude-from-selection="true" but
  // still break manual text selection. The lyrics header widget carries the
  // same attribute, so keep that one.
  const style = document.createElement('style');
  style.textContent =
    '[data-exclude-from-selection="true"]:not([class*="LyricsHeader"]), div[class*="RecommendedSongs"] { display: none !important; }';
  document.head.appendChild(style);

  const normalize = (s) => s.replace(/\s+/g, ' ').trim().toLowerCase();

  function splitSections(container) {
    const sections = [];
    let current = null;
    for (const node of [...container.childNodes]) {
      const text = node.textContent || '';
      if (HEADER_RE.test(text)) {
        current = { header: node, nodes: [] };
        sections.push(current);
      } else if (current) {
        current.nodes.push(node);
      }
    }
    return sections;
  }

  function collapse(section) {
    const wrap = document.createElement('span');
    wrap.style.display = 'none';
    section.header.after(wrap);
    for (const n of section.nodes) wrap.appendChild(n);

    const toggle = document.createElement('a');
    toggle.textContent = ' [repeat - show]';
    toggle.style.cssText = 'cursor:pointer;opacity:.55;font-size:.85em;user-select:none;';
    // line break after the toggle while collapsed; hidden when expanded,
    // since the section's own leading <br> takes over
    const gap = document.createElement('br');
    toggle.addEventListener('click', () => {
      const hidden = wrap.style.display === 'none';
      wrap.style.display = hidden ? '' : 'none';
      gap.style.display = hidden ? 'none' : '';
      toggle.textContent = hidden ? ' [hide]' : ' [repeat - show]';
    });
    section.header.after(toggle, gap);
  }

  function processPage() {
    const containers = document.querySelectorAll('[data-lyrics-container="true"]');
    if (!containers.length) return;
    // Collapse on repeated header label ([Chorus] seen again), not on
    // identical text: Genius transcribes repeats with small variations
    // (ad-libs, parentheticals), so exact-text matching never fires.
    // seen is shared across containers: Genius splits lyrics into several
    // containers (around ad slots), and a repeat can land in a later one.
    const seen = new Set();
    for (const c of containers) {
      if (c.dataset.repeatsCollapsed) continue;
      c.dataset.repeatsCollapsed = '1';
      for (const s of splitSections(c)) {
        const label = normalize(s.header.textContent);
        if (!s.nodes.some((n) => normalize(n.textContent))) continue;
        if (seen.has(label)) collapse(s);
        else seen.add(label);
      }
    }
  }

  processPage();
  // Genius is a SPA: lyrics containers appear/replace after navigation
  new MutationObserver(() => processPage()).observe(document.body, {
    childList: true,
    subtree: true,
  });
})();
