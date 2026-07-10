// Режим редактирования: активен только когда рядом запущена admin/server.py (см. /api/ping).
// Клик по плейсхолдеру с пунктирной рамкой — загрузка своей картинки в этот слот.
(function () {
  fetch('/api/ping').then(function (r) {
    if (r.ok) init();
  }).catch(function () {});

  function init() {
    document.querySelectorAll('[data-slot]').forEach(function (el) {
      el.style.cursor = 'pointer';
      el.style.outline = '2px dashed rgba(227,185,138,.8)';
      el.style.outlineOffset = '-2px';
      el.title = 'Нажмите, чтобы загрузить картинку (' + el.dataset.slot + ')';
      el.addEventListener('click', function (e) {
        e.stopPropagation(); // не даём клику по фото триггерить модалки и другие обработчики на родителях
        openPicker(el);
      });
    });

    var bar = document.createElement('div');
    bar.style.cssText = 'position:fixed;left:16px;bottom:16px;z-index:9999;display:flex;align-items:center;gap:10px;background:#0C0A09;color:#fff;padding:10px 14px;border-radius:100px;font-family:sans-serif;font-size:14px;box-shadow:0 8px 24px rgba(0,0,0,0.35);';
    bar.innerHTML =
      '<span id="aura-edit-status">Режим редактирования</span>' +
      '<button id="aura-edit-publish" style="background:#A9713F;color:#fff;border:none;border-radius:100px;padding:8px 16px;font-size:14px;cursor:pointer;">Опубликовать</button>';
    document.body.appendChild(bar);

    document.getElementById('aura-edit-publish').addEventListener('click', publish);
    refreshStatus();
  }

  function openPicker(el) {
    var input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.style.position = 'fixed';
    input.style.top = '-1000px';
    input.addEventListener('change', function () {
      if (input.files[0]) uploadSlot(el.dataset.slot, input.files[0]);
      input.remove();
    });
    document.body.appendChild(input);
    input.click();
  }

  function uploadSlot(slot, file) {
    var fd = new FormData();
    fd.append('image', file);
    setStatus('Загружаю…');
    fetch('/api/upload-slot?slot=' + encodeURIComponent(slot), { method: 'POST', body: fd })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.ok) {
          var url = 'url(' + data.path + '?v=' + Date.now() + ')';
          document.querySelectorAll('[data-slot="' + slot + '"]').forEach(function (target) {
            target.style.backgroundImage = url;
            target.style.backgroundSize = target.dataset.fit === 'contain' ? 'contain' : 'cover';
            target.style.backgroundRepeat = 'no-repeat';
            target.style.backgroundPosition = 'center';
            target.classList.add('has-photo');
            if (target.dataset.autoHeight === 'mobile' && window.__auraApplyAutoHeight) {
              window.__auraApplyAutoHeight(target, data.path);
            }
          });
          setStatus('Загружено, готово к публикации');
        } else {
          setStatus('Ошибка загрузки');
        }
      })
      .catch(function () { setStatus('Ошибка загрузки'); });
  }

  function publish() {
    setStatus('Публикую…');
    fetch('/api/release', { method: 'POST' })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        setStatus(data.message || (data.ok ? 'Опубликовано ✓' : 'Ошибка публикации — см. терминал админки'));
      })
      .catch(function () { setStatus('Ошибка публикации'); });
  }

  function refreshStatus() {
    fetch('/api/status').then(function (r) { return r.json(); }).then(function (data) {
      setStatus(data.pending ? data.pending + ' изменений не опубликовано' : 'Всё опубликовано');
    }).catch(function () {});
  }

  function setStatus(text) {
    var el = document.getElementById('aura-edit-status');
    if (el) el.textContent = text;
  }
})();
