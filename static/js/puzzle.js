(function () {
  'use strict';
  var root = document.querySelector('[data-puzzle]');
  if (!root) return;
  var bg = root.querySelector('.puzzle__bg');
  var piece = root.querySelector('.puzzle__piece');
  var track = root.querySelector('.puzzle__track');
  var handle = root.querySelector('[data-puzzle-handle]');
  var fill = root.querySelector('[data-puzzle-fill]');
  var hint = root.querySelector('[data-puzzle-hint]');
  var input = root.querySelector('input[name=captcha]');
  var hintText = hint.textContent;
  var width = 320, size = 68, y = 0, dragging = false, startX = 0, offset = 0;

  function load(data) {
    width = Number(data.width); size = Number(data.size); y = Number(data.y);
    bg.src = data.bg; piece.src = data.piece;
    piece.style.top = (y / (width / 2) * 50) + '%';   /* stage height = width / 2 */
    piece.style.width = (size / width * 100) + '%';
    setOffset(0);
    root.classList.remove('is-done', 'is-error');
    hint.textContent = hintText;
    input.value = '';
  }
  function setOffset(px) {
    var max = track.clientWidth - handle.offsetWidth;
    offset = Math.max(0, Math.min(max, px));
    handle.style.left = offset + 'px';
    fill.style.width = (offset + handle.offsetWidth / 2) + 'px';
    /* the piece travels across the picture; translate slider px to picture px */
    var stageW = root.querySelector('.puzzle__stage').clientWidth;
    var pieceMax = stageW - piece.offsetWidth;
    var trackMax = max || 1;
    var pieceX = offset / trackMax * pieceMax;
    piece.style.left = pieceX + 'px';
    return pieceX / stageW * width;  /* value in the server's 320px coordinate system */
  }
  function start(e) {
    if (root.classList.contains('is-done')) return;
    dragging = true; startX = (e.touches ? e.touches[0].clientX : e.clientX) - offset;
    e.preventDefault();
  }
  function move(e) {
    if (!dragging) return;
    setOffset((e.touches ? e.touches[0].clientX : e.clientX) - startX);
  }
  function end() {
    if (!dragging) return;
    dragging = false;
    if (offset < 4) return;
    input.value = String(Math.round(setOffset(offset)));
    root.classList.add('is-done');
    hint.textContent = root.getAttribute('data-done-text') || hintText;
  }
  handle.addEventListener('mousedown', start);
  handle.addEventListener('touchstart', start, { passive: false });
  document.addEventListener('mousemove', move);
  document.addEventListener('touchmove', move, { passive: false });
  document.addEventListener('mouseup', end);
  document.addEventListener('touchend', end);

  root.querySelector('[data-puzzle-refresh]').addEventListener('click', function () {
    fetch(root.getAttribute('data-refresh-url'), { credentials: 'same-origin' })
      .then(function (r) { return r.json(); }).then(load).catch(function () {});
  });

  load({ bg: root.getAttribute('data-bg'), piece: root.getAttribute('data-piece'), y: root.getAttribute('data-y'),
         size: root.getAttribute('data-size'), width: root.getAttribute('data-width') });
})();
