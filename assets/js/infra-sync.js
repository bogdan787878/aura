// Блок "Внутренняя инфраструктура": заголовок в sticky-сайдбаре больше не
// статичный — подставляем подпись/описание той карточки (.infra-pin__item),
// что сейчас ближе всего к центру экрана.
(function () {
  var section = document.querySelector('.infra-pin');
  if (!section) return;

  var items = Array.prototype.slice.call(section.querySelectorAll('.infra-pin__item'));
  var captionEl = document.getElementById('infra-pin-caption');
  var descEl = document.getElementById('infra-pin-desc');
  if (!items.length || !captionEl || !descEl) return;

  var current = -1;

  function closestToCenter() {
    var center = window.innerHeight / 2;
    var best = 0;
    var bestDist = Infinity;
    items.forEach(function (el, i) {
      var rect = el.getBoundingClientRect();
      var elCenter = rect.top + rect.height / 2;
      var dist = Math.abs(elCenter - center);
      if (dist < bestDist) { bestDist = dist; best = i; }
    });
    return best;
  }

  function update() {
    var idx = closestToCenter();
    if (idx === current) return;
    current = idx;
    var el = items[idx];
    captionEl.textContent = el.dataset.caption || '';
    descEl.textContent = el.dataset.desc || '';
  }

  var raf;
  document.addEventListener('scroll', function () {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(update);
  }, { passive: true });
  window.addEventListener('resize', update);

  update();
})();
