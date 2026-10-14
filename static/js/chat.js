(function () {
  'use strict';
  var root = document.getElementById('site-chat');
  if (!root) return;

  var panel = root.querySelector('#chat-panel');
  var fab = root.querySelector('.chat__fab');
  var log = root.querySelector('[data-chat-log]');
  var chips = root.querySelector('[data-chat-chips]');
  var form = root.querySelector('[data-chat-form]');
  var input = form.querySelector('textarea');
  var csrf = form.querySelector('input[name=csrfmiddlewaretoken]').value;
  var endpoint = root.getAttribute('data-endpoint');
  var lang = root.getAttribute('data-lang');
  var history = [];
  var busy = false;

  function toggle(open) {
    var isOpen = open === undefined ? panel.hidden : open;
    panel.hidden = !isOpen;
    fab.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    root.classList.toggle('is-open', isOpen);
    if (isOpen) setTimeout(function () { input.focus(); }, 50);
  }
  Array.prototype.forEach.call(root.querySelectorAll('[data-chat-toggle]'), function (b) {
    b.addEventListener('click', function () { toggle(); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !panel.hidden) toggle(false);
  });

  /* Minimal, safe Markdown: paragraphs, bullet lists, **bold**, [links](/relative). */
  function escapeHtml(s) {
    return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }
  function inline(s) {
    return escapeHtml(s)
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[([^\]]+)\]\(((?:\/|https?:\/\/)[^)\s]+)\)/g, function (_, text, url) {
        var ext = /^https?:/.test(url) ? ' target="_blank" rel="noopener"' : '';
        return '<a href="' + url + '"' + ext + '>' + text + '</a>';
      });
  }
  function render(text) {
    var html = '', list = [];
    function flush() { if (list.length) { html += '<ul>' + list.map(function (l) { return '<li>' + inline(l) + '</li>'; }).join('') + '</ul>'; list = []; } }
    text.split(/\n/).forEach(function (line) {
      var m = line.match(/^\s*(?:[-*•]|\d+[.)])\s+(.*)$/);
      if (m) { list.push(m[1]); return; }
      flush();
      if (line.trim()) html += '<p>' + inline(line.trim()) + '</p>';
    });
    flush();
    return html;
  }

  function add(role, text, isHtml) {
    var el = document.createElement('div');
    el.className = 'chat__msg chat__msg--' + (role === 'user' ? 'user' : 'bot');
    if (isHtml) el.innerHTML = render(text); else el.textContent = text;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function send(text) {
    text = (text || '').trim();
    if (!text || busy) return;
    busy = true;
    if (chips) { chips.remove(); chips = null; }
    add('user', text);
    history.push({ role: 'user', content: text });
    input.value = '';
    input.style.height = '';
    var typing = add('bot', root.getAttribute('data-thinking'));
    typing.classList.add('chat__msg--typing');
    form.classList.add('is-busy');

    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
      credentials: 'same-origin',
      body: JSON.stringify({ lang: lang, messages: history.slice(-20) })
    })
      .then(function (r) { return r.json().then(function (data) { return { ok: r.ok, data: data }; }); })
      .then(function (res) {
        typing.remove();
        if (res.ok && res.data.reply) {
          add('bot', res.data.reply, true);
          history.push({ role: 'assistant', content: res.data.reply });
        } else {
          add('bot', res.data.error || 'Error');
          history.pop();
        }
      })
      .catch(function () {
        typing.remove();
        add('bot', lang === 'ru' ? 'Нет связи с сервером. Попробуйте ещё раз.' : 'No connection. Please try again.');
        history.pop();
      })
      .then(function () { busy = false; form.classList.remove('is-busy'); input.focus(); });
  }

  form.addEventListener('submit', function (e) { e.preventDefault(); send(input.value); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input.value); }
  });
  input.addEventListener('input', function () {
    input.style.height = '';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });
  if (chips) {
    chips.addEventListener('click', function (e) {
      var b = e.target.closest('.chat__chip');
      if (b) send(b.textContent);
    });
  }
})();
