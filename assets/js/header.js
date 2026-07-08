// Хедер: прозрачный/белый текст поверх хиро, белый фон + бордовый текст
// после прокрутки. Плюс открытие/закрытие полноэкранного меню.
(function () {
  var header = document.getElementById('site-header');
  var menu = document.getElementById('site-menu');
  var menuToggle = document.getElementById('menu-toggle');
  var menuClose = document.getElementById('menu-close');
  if (!header) return;

  function onScroll() {
    header.classList.toggle('is-scrolled', window.scrollY > 40);
  }
  document.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  function openMenu() {
    menu.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }
  function closeMenu() {
    menu.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  menuToggle && menuToggle.addEventListener('click', openMenu);
  menuClose && menuClose.addEventListener('click', closeMenu);
  document.querySelectorAll('[data-menu-link]').forEach(function (link) {
    link.addEventListener('click', closeMenu);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeMenu();
  });
})();
