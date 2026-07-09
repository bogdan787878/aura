// Переключатель табов для блоков "Архитектура" / "Благоустройство" / "Условия
// покупки": клик по пункту переключает любые дочерние элементы с data-tab
// (фото, описание, блоки цифр, карточки рассрочки) внутри этого же .tab-block
// — блоки независимы друг от друга.
(function () {
  document.querySelectorAll('.tab-block').forEach(function (block) {
    var tabs = Array.prototype.slice.call(block.querySelectorAll('.tab-block__tab'));
    var panels = Array.prototype.slice.call(block.querySelectorAll('[data-tab]:not(.tab-block__tab)'));

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        var index = tab.dataset.tab;
        tabs.forEach(function (el) { el.classList.toggle('is-active', el === tab); });
        panels.forEach(function (el) { el.classList.toggle('is-active', el.dataset.tab === index); });
      });
    });
  });
})();
