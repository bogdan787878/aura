// Переключатель табов для блоков "Архитектура" / "Благоустройство":
// клик по пункту меняет активное фото и (если есть) активное описание
// внутри этого же .tab-block — блоки независимы друг от друга.
(function () {
  document.querySelectorAll('.tab-block').forEach(function (block) {
    var tabs = Array.prototype.slice.call(block.querySelectorAll('.tab-block__tab'));
    var photos = Array.prototype.slice.call(block.querySelectorAll('.tab-block__photo'));
    var descs = Array.prototype.slice.call(block.querySelectorAll('.tab-block__desc'));

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        var index = tab.dataset.tab;
        tabs.forEach(function (el) { el.classList.toggle('is-active', el === tab); });
        photos.forEach(function (el) { el.classList.toggle('is-active', el.dataset.tab === index); });
        descs.forEach(function (el) { el.classList.toggle('is-active', el.dataset.tab === index); });
      });
    });
  });
})();
