// Загружает data/images.json и подставляет фон в элементы [data-slot].
// Пока файл не загружен — виден плейсхолдер (градиент + подпись из style.css/.ph-label).
(function () {
  fetch('data/images.json')
    .then(function (r) { return r.ok ? r.json() : {}; })
    .then(function (map) {
      Object.keys(map).forEach(function (slot) {
        var path = map[slot];
        if (!path) return;
        document.querySelectorAll('[data-slot="' + slot + '"]').forEach(function (el) {
          el.style.backgroundImage = 'url(' + path + '?v=' + Date.now() + ')';
          el.style.backgroundSize = el.dataset.fit === 'contain' ? 'contain' : 'cover';
          el.style.backgroundRepeat = 'no-repeat';
          el.style.backgroundPosition = 'center';
          el.classList.add('has-photo');
          if (el.dataset.autoHeight === 'mobile') applyAutoHeight(el, path);
        });
      });
    })
    .catch(function () {});

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
