(function () {
  'use strict';
  document.documentElement.classList.add('js');

  /* Mobile navigation */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* Reveal sections as they scroll into view */
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var sections = Array.prototype.slice.call(document.querySelectorAll('.main > section, .main > .panel'));
  if (!reduce && 'IntersectionObserver' in window) {
    var vh = window.innerHeight;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        en.target.classList.add('is-visible');
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    sections.forEach(function (s) {
      if (s.getBoundingClientRect().top > vh * 0.92) {
        s.classList.add('reveal');
        io.observe(s);
      }
    });
    /* Safety net: never leave content hidden if the observer does not fire. */
    setTimeout(function () {
      sections.forEach(function (s) { s.classList.add('is-visible'); });
    }, 4000);
  }

  /* Practices accordion: one open panel per group, no page reload */
  var groups = document.querySelectorAll('[data-practice-group]');
  Array.prototype.forEach.call(groups, function (group) {
    var tiles = group.querySelectorAll('[data-practice]');
    var panels = group.querySelectorAll('[data-panel]');

    function setOpen(key) {
      Array.prototype.forEach.call(tiles, function (t) {
        var on = t.getAttribute('data-practice') === key;
        t.classList.toggle('is-open', on);
        t.setAttribute('aria-expanded', on ? 'true' : 'false');
        var chevron = t.querySelector('.ptile__chevron');
        if (chevron) chevron.textContent = on ? '−' : '+';
      });
      Array.prototype.forEach.call(panels, function (p) {
        var on = p.getAttribute('data-panel') === key;
        p.classList.toggle('is-open', on);
        if (on) p.removeAttribute('hidden'); else p.setAttribute('hidden', '');
      });
      if (key) {
        var url = new URL(window.location.href);
        url.searchParams.set('open', key);
        url.hash = '';
        history.replaceState(null, '', url.toString());
      }
    }

    Array.prototype.forEach.call(tiles, function (t) {
      t.addEventListener('click', function (e) {
        e.preventDefault();
        var key = t.getAttribute('data-practice');
        setOpen(t.classList.contains('is-open') ? null : key);
      });
    });
    Array.prototype.forEach.call(group.querySelectorAll('[data-panel-close]'), function (c) {
      c.addEventListener('click', function (e) {
        e.preventDefault();
        setOpen(null);
        var url = new URL(window.location.href);
        url.searchParams.delete('open');
        history.replaceState(null, '', url.toString());
      });
    });
  });
})();
