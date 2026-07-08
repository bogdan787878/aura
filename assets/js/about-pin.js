// Пин-анимация блока "О проекте": секция высотой 300vh, внутри — sticky-панель
// на 100vh. Пока пользователь прокручивает эти 300vh, меняем активное фото
// и текст в красной плашке по шагам (0 / 1 / 2).
(function () {
  var section = document.querySelector('.about-pin');
  if (!section) return;

  var photos = Array.prototype.slice.call(section.querySelectorAll('.about-pin__photo'));
  var badge = document.getElementById('about-pin-badge');

  var STEPS = [
    { label: '2 башни' },
    { label: '41–42 этажность' },
    { label: '4+ квартир на этаже' }
  ];

  var current = -1;

  function setStep(index) {
    if (index === current) return;
    current = index;
    photos.forEach(function (el) {
      el.classList.toggle('is-active', Number(el.dataset.step) === index);
    });
    if (badge) badge.textContent = STEPS[index].label;
  }

  function onScroll() {
    var rect = section.getBoundingClientRect();
    var scrollable = section.offsetHeight - window.innerHeight;
    if (scrollable <= 0) { setStep(0); return; }

    var progress = (-rect.top) / scrollable;
    progress = Math.min(1, Math.max(0, progress));

    var index = Math.min(STEPS.length - 1, Math.floor(progress * STEPS.length));
    setStep(index);
  }

  document.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();
})();
