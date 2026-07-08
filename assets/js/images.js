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
        });
      });
    })
    .catch(function () {});
})();
