// Отрисовка карточек планировок из data/planirovki.json + фильтр по комнатам.
// Данные наполняются через /admin/plans (admin/server.py).
(function () {
  var grid = document.getElementById('plans-grid');
  if (!grid) return;

  var countEl = document.getElementById('plans-count');
  var emptyEl = document.getElementById('plans-empty');
  var filtersWrap = document.getElementById('plans-filters');

  var ROOM_LABELS = { 0: 'Студия', 1: '1-комнатная', 2: '2-комнатная', 3: '3-комнатная', 4: '4+ комнат' };

  var allPlans = [];
  var activeRooms = 'all';

  function formatRub(n) {
    if (n === null || n === undefined || n === '') return '';
    return Math.round(n).toLocaleString('ru-RU') + ' ₽';
  }

  function formatNum(n) {
    if (n === null || n === undefined || n === '') return '';
    return String(n).replace('.', ',');
  }

  function matchesRooms(plan) {
    if (activeRooms === 'all') return true;
    return String(plan.rooms) === activeRooms;
  }

  function cardHTML(plan) {
    var img = plan.image
      ? '<img class="plan-card__img" src="' + plan.image + '" alt="">'
      : '<div class="plan-card__img plan-card__img--ph">планировка</div>';

    var roomsLabel = ROOM_LABELS[plan.rooms] || (plan.rooms + '-комнатная');

    var ppm = plan.pricePerMeter
      ? '<div class="plan-card__ppm">' + formatRub(plan.pricePerMeter) + '/м²</div>'
      : '<div class="plan-card__ppm"></div>';

    var priceTop = plan.discountPrice
      ? '<div class="plan-card__price-top">' +
          '<span class="plan-card__price-old">' + formatRub(plan.price) + '</span>' +
          '<span class="plan-card__badge">−' + plan.discountPercent + '%</span>' +
        '</div>'
      : '';
    var priceNew = formatRub(plan.discountPrice || plan.price);

    return (
      '<article class="plan-card">' +
        '<div class="plan-card__media">' + img + '</div>' +
        '<div class="plan-card__body">' +
          '<h3 class="plan-card__title">' + roomsLabel + ', ' + formatNum(plan.area) + ' м²</h3>' +
          '<p class="plan-card__line">' + plan.tower + ' башня</p>' +
          '<p class="plan-card__line">' + plan.floor + ' этаж</p>' +
          '<div class="plan-card__pricing">' +
            ppm +
            '<div class="plan-card__price-block">' +
              priceTop +
              '<div class="plan-card__price-new">' + priceNew + '</div>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</article>'
    );
  }

  function render() {
    var filtered = allPlans.filter(matchesRooms);
    countEl.textContent = filtered.length ? 'Найдено планировок: ' + filtered.length : '';
    grid.innerHTML = filtered.map(cardHTML).join('');
    grid.style.display = filtered.length ? '' : 'none';
    emptyEl.style.display = filtered.length ? 'none' : '';
  }

  filtersWrap.addEventListener('click', function (e) {
    var btn = e.target.closest('.plans__filter');
    if (!btn) return;
    activeRooms = btn.dataset.rooms;
    filtersWrap.querySelectorAll('.plans__filter').forEach(function (b) { b.classList.remove('is-active'); });
    btn.classList.add('is-active');
    render();
  });

  fetch('data/planirovki.json')
    .then(function (r) { return r.ok ? r.json() : []; })
    .then(function (data) {
      allPlans = data;
      render();
    })
    .catch(function () {
      countEl.textContent = 'Не удалось загрузить планировки';
    });
})();
