// Модалки "Получить предложение" / "Заказать звонок": открытие по клику на
// любую кнопку с data-modal="offer"/"callback", маска телефона +7, чек-бокс
// согласия обязателен (required), отправка — без бэкенда, просто показывает
// текст благодарности и закрывает форму через паузу.
(function () {
  function openModal(modal) {
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeModal(modal) {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  document.querySelectorAll('[data-modal]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var modal = document.getElementById('modal-' + btn.dataset.modal);
      if (modal) openModal(modal);
    });
  });

  document.querySelectorAll('.modal').forEach(function (modal) {
    modal.querySelectorAll('[data-modal-close]').forEach(function (el) {
      el.addEventListener('click', function () { closeModal(modal); });
    });

    var form = modal.querySelector('.modal__form');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      modal.classList.add('is-sent');
      setTimeout(function () {
        closeModal(modal);
        modal.classList.remove('is-sent');
        form.reset();
      }, 2000);
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal.is-open').forEach(closeModal);
    }
  });

  // Маска телефона: +7 (___) ___-__-__
  document.querySelectorAll('.modal__input[type="tel"]').forEach(function (input) {
    input.addEventListener('focus', function () {
      if (!input.value) input.value = '+7 ';
    });
    input.addEventListener('input', function () {
      var digits = input.value.replace(/\D/g, '');
      if (digits.charAt(0) === '7' || digits.charAt(0) === '8') digits = digits.slice(1);
      digits = digits.slice(0, 10);
      var out = '+7';
      if (digits.length > 0) out += ' (' + digits.slice(0, 3);
      if (digits.length >= 3) out += ')';
      if (digits.length > 3) out += ' ' + digits.slice(3, 6);
      if (digits.length > 6) out += '-' + digits.slice(6, 8);
      if (digits.length > 8) out += '-' + digits.slice(8, 10);
      input.value = out;
    });
  });
})();
