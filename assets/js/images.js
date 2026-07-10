// Загружает data/images.json и подставляет фон в элементы [data-slot].
// Пока файл не загружен — виден плейсхолдер (градиент + подпись из style.css/.ph-label).
// Слоты, видимые сразу на первом экране, грузятся сразу; всё остальное —
// лениво, через IntersectionObserver, когда блок приближается к экрану.
(function () {
  var EAGER_SLOTS = ['logo', 'hero-bg', 'hero-bg-mobile'];

  fetch('data/images.json')
    .then(function (r) { return r.ok ? r.json() : {}; })
    .then(function (map) {
      var lazyEls = [];
      Object.keys(map).forEach(function (slot) {
        var path = map[slot];
        if (!path) return;
        document.querySelectorAll('[data-slot="' + slot + '"]').forEach(function (el) {
          if (EAGER_SLOTS.indexOf(slot) !== -1) {
            applyImage(el, path);
          } else {
            el.dataset.lazySrc = path;
            lazyEls.push(el);
          }
        });
      });
      observeLazy(lazyEls);
    })
    .catch(function () {});

  function observeLazy(els) {
    if (!els.length) return;
    if (!('IntersectionObserver' in window)) {
      els.forEach(function (el) { applyImage(el, el.dataset.lazySrc); });
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        applyImage(entry.target, entry.target.dataset.lazySrc);
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '600px 0px' });
    els.forEach(function (el) { observer.observe(el); });
  }

  function applyImage(el, path) {
    el.style.backgroundImage = 'url(' + path + '?v=' + Date.now() + ')';
    el.style.backgroundSize = el.dataset.fit === 'contain' ? 'contain' : 'cover';
    el.style.backgroundRepeat = 'no-repeat';
    el.style.backgroundPosition = 'center';
    el.classList.add('has-photo');
    if (el.dataset.autoHeight === 'mobile') applyAutoHeight(el, path);
  }

  // Блоки "обложка + заголовок": на мобильном высота секции подстраивается
  // под пропорции загруженного фото (см. .section-photo__bg--mobile в CSS).
  function applyAutoHeight(el, path) {
    var img = new Image();
    img.onload = function () {
      if (img.naturalWidth && img.naturalHeight) {
        el.style.aspectRatio = img.naturalWidth + ' / ' + img.naturalHeight;
      }
    };
    img.src = path;
  }
  window.__auraApplyAutoHeight = applyAutoHeight;
})();
