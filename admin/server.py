#!/usr/bin/env python3
"""
Локальная админка лендинга "Аура".
Запуск: python3 admin/server.py
Открыть:
  http://localhost:8092/        — сам сайт в режиме редактирования
                                   (клик по областям с пунктирной рамкой грузит картинку)
  http://localhost:8092/admin   — обзор всех слотов (что загружено, что ещё пусто)

Всё, что вы загружаете, сохраняется локально в assets/img и data/images.json.
Если папка проекта уже git-репозиторий — кнопка "Опубликовать" сделает
commit (без push, пуш делаете сами, когда решите закинуть на гит).
Если git-репозитория ещё нет — кнопка просто подтвердит, что файлы сохранены.
"""

import cgi
import json
import mimetypes
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

PORT = 8092

ADMIN_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(ADMIN_DIR)  # .../aura-landing
IMAGES_DIR = os.path.join(PROJECT_DIR, 'assets', 'img')
IMAGES_MANIFEST = os.path.join(PROJECT_DIR, 'data', 'images.json')
PLANS_DIR = os.path.join(PROJECT_DIR, 'assets', 'img', 'plans')
PLANS_FILE = os.path.join(PROJECT_DIR, 'data', 'planirovki.json')

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(PLANS_DIR, exist_ok=True)

TOWERS = ['Бронзовая', 'Серебряная']
ROOM_LABELS = {0: 'Студия', 1: '1-комнатная', 2: '2-комнатная', 3: '3-комнатная', 4: '4+ комнат'}

# Слоты, использованные в index.html (data-slot="..."), с человекочитаемыми подписями.
SLOTS = [
    ('logo', 'Логотип АУРА'),
    ('hero-bg', 'Хиро — фон (модель + кольца, одна картинка)'),
    ('about-photo-1', 'О проекте — шаг 1: 2 башни'),
    ('about-photo-2', 'О проекте — шаг 2: этажность'),
    ('about-photo-3', 'О проекте — шаг 3: квартиры на этаже'),
    ('location-map', 'Локация — карта района (одна картинка)'),
    ('infrastructure-banner-bg', 'Внутренняя инфраструктура — баннер (фото на всю ширину)'),
    ('infra-photo-1', 'Инфраструктура — 1: ресторан авторской кухни'),
    ('infra-photo-2', 'Инфраструктура — 2: медицинская клиника'),
    ('infra-photo-3', 'Инфраструктура — 3: частный детский сад'),
    ('infra-photo-4', 'Инфраструктура — 4: фитнес-центр с бассейном'),
    ('infra-photo-5', 'Инфраструктура — 5: коммерческие помещения'),
    ('infra-photo-6', 'Инфраструктура — 6: бизнес-центр «Прайм»'),
    ('arch-photo-1', 'Архитектура — таб 1: общий вид'),
    ('arch-photo-2', 'Архитектура — таб 2: бронзовая башня'),
    ('arch-photo-3', 'Архитектура — таб 3: серебряная башня'),
    ('landscaping-photo-1', 'Благоустройство — таб 1: приватный двор'),
    ('landscaping-photo-2', 'Благоустройство — таб 2: прогулочный бульвар'),
    ('amenities-banner-bg', 'Пространства для отдыха — баннер (фото на всю ширину)'),
    ('amenity-photo-1', 'Пространства для отдыха — 1: гранд-лобби с лаунж-зоной'),
    ('amenity-photo-2', 'Пространства для отдыха — 2: переговорные'),
    ('amenity-photo-3', 'Пространства для отдыха — 3: коворкинг'),
    ('amenity-photo-4', 'Пространства для отдыха — 4: детская игровая комната'),
    ('amenity-photo-5', 'Пространства для отдыха — 5: бьюти-комната'),
    ('amenity-photo-6', 'Пространства для отдыха — 6: акустические кабинеты'),
    ('amenity-photo-7', 'Пространства для отдыха — 7: спортзал и студия для тренировок'),
    ('amenity-photo-8', 'Пространства для отдыха — 8: сервисная комната'),
    ('aesthetics-banner-bg', 'Эстетика и функциональность — баннер (фото на всю ширину)'),
    ('aesthetics-photo-1', 'Эстетика и функциональность — фото 1'),
    ('aesthetics-photo-2', 'Эстетика и функциональность — фото 2'),
    ('aesthetics-photo-3', 'Эстетика и функциональность — фото 3'),
    ('aesthetics-photo-4', 'Эстетика и функциональность — фото 4'),
    ('parking-bg', 'Паркинг — фото на всю ширину'),
]


# ── Работа с данными ──────────────────────────────────────────

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


# ── Git (опционально — работает, только если PROJECT_DIR уже git-репозиторий) ──

def is_git_repo():
    r = subprocess.run(['git', '-C', PROJECT_DIR, 'rev-parse', '--is-inside-work-tree'],
                        capture_output=True, text=True)
    return r.returncode == 0


def git(*args):
    return subprocess.run(['git', '-C', PROJECT_DIR] + list(args), capture_output=True, text=True)


def git_stage(paths):
    if not paths or not is_git_repo():
        return
    git('add', *paths)


def git_pending_count():
    if not is_git_repo():
        return 0
    r = git('status', '--porcelain')
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return len(lines)


def git_release():
    if not is_git_repo():
        return True, 'Папка ещё не git-репозиторий — изменения просто сохранены локально в assets/img и data/images.json.'
    log = []
    r = git('add', '.')
    log.append('$ git add .\n' + r.stdout + r.stderr)
    r = git('commit', '-m', 'Update Aura landing images')
    log.append('$ git commit\n' + r.stdout + r.stderr)
    if r.returncode != 0 and 'nothing to commit' not in (r.stdout + r.stderr):
        return False, '\n'.join(log)
    return True, '\n'.join(log)


# ── HTML страницы ──────────────────────────────────────────────

ADMIN_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Фото — Аура</title>
<style>
  body {{ font-family: -apple-system, sans-serif; background:#F4EAE3; color:#2B1D19; margin:0; padding:32px; }}
  h1 {{ font-size: 24px; margin-bottom: 24px; }}
  .top-link {{ margin-bottom:24px; display:inline-block; color:#8C241F; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(240px,1fr)); gap:16px; max-width:1200px; }}
  .slot {{ background:#fff; border-radius:12px; padding:14px; border:1px solid rgba(43,29,25,.1); }}
  .slot img {{ width:100%; aspect-ratio:4/3; object-fit:cover; border-radius:8px; background:#E6D1C6; display:block; }}
  .slot .ph {{ width:100%; aspect-ratio:4/3; border-radius:8px; background:linear-gradient(135deg,#A9713F,#8C241F); }}
  .slot .name {{ font-size:13px; margin-top:10px; font-weight:600; }}
  .slot .status {{ font-size:12px; opacity:0.6; }}
  .ok {{ color:#2f7d32; }}
  .missing {{ color:#B24747; }}
</style>
</head>
<body>
<a class="top-link" href="/">&larr; Вернуться на сайт (режим редактирования)</a>
&nbsp;&middot;&nbsp;
<a class="top-link" href="/admin/plans">Планировки &rarr;</a>
<h1>Фото лендинга «Аура» — {done}/{total} загружено</h1>
<div class="grid">
{cards}
</div>
</body>
</html>"""


def render_admin_page():
    manifest = load_json(IMAGES_MANIFEST, {})
    cards = []
    done = 0
    for slot, label in SLOTS:
        path = manifest.get(slot)
        if path:
            done += 1
            cards.append(
                '<div class="slot"><img src="/{path}" alt=""><div class="name">{label}</div>'
                '<div class="status ok">Загружено &middot; {slot}</div></div>'.format(
                    path=path, label=label, slot=slot)
            )
        else:
            cards.append(
                '<div class="slot"><div class="ph"></div><div class="name">{label}</div>'
                '<div class="status missing">Пусто &middot; {slot}</div></div>'.format(
                    label=label, slot=slot)
            )
    return ADMIN_PAGE.format(done=done, total=len(SLOTS), cards='\n'.join(cards))


PLANS_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Планировки — Аура</title>
<style>
  body {{ font-family: -apple-system, sans-serif; background:#F4EAE3; color:#2B1D19; margin:0; padding:32px; }}
  h1 {{ font-size: 24px; margin-bottom: 8px; }}
  .top-link {{ margin-bottom:24px; display:inline-block; color:#8C241F; }}
  .card {{ background:#fff; border-radius:16px; padding:24px; margin-bottom:32px; max-width:640px; }}
  .card h2 {{ font-size:16px; margin:0 0 4px; }}
  label {{ display:block; font-size:13px; opacity:0.6; margin-bottom:4px; margin-top:14px; }}
  input, select {{ width:100%; padding:10px 12px; border-radius:8px; border:1px solid #ddd; font-size:15px; box-sizing:border-box; font-family:inherit; }}
  .row {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  button {{ margin-top:22px; background:#8C241F; color:#fff; border:none; border-radius:100px; padding:12px 28px; font-size:15px; cursor:pointer; }}
  button.danger {{ background:#B24747; padding:6px 14px; font-size:12px; margin-top:10px; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(240px,1fr)); gap:16px; max-width:1200px; }}
  .plan {{ background:#fff; border-radius:12px; padding:14px; }}
  .plan img {{ width:100%; aspect-ratio:4/3; object-fit:cover; border-radius:8px; background:#E6D1C6; }}
  .plan .meta {{ font-size:13px; margin:10px 0; line-height:1.6; }}
  .plan .price {{ font-size:14px; font-weight:600; }}
  .plan .price .old {{ text-decoration:line-through; opacity:0.5; font-weight:400; margin-right:6px; }}
  .ok {{ color: #2f7d32; font-weight:600; }}
  .err {{ color: #b23a3a; font-weight:600; }}
  a {{ color:#8C241F; }}
</style>
</head>
<body>
<a class="top-link" href="/">&larr; Сайт</a>
&nbsp;&middot;&nbsp;
<a class="top-link" href="/admin">Фото</a>
<h1>Планировки — Аура</h1>
{message}
<div class="card">
  <h2>Добавить планировку</h2>
  <form method="POST" action="/admin/plans/upload" enctype="multipart/form-data">
    <label>Изображение планировки</label>
    <input type="file" name="image" accept="image/*" required>
    <div class="row">
      <div>
        <label>Комнат</label>
        <select name="rooms" required>
          <option value="0">Студия</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4+</option>
        </select>
      </div>
      <div>
        <label>Площадь, м²</label>
        <input type="number" name="area" step="0.1" required>
      </div>
    </div>
    <div class="row">
      <div>
        <label>Этаж</label>
        <input type="number" name="floor" required>
      </div>
      <div>
        <label>Номер квартиры</label>
        <input type="text" name="apartmentNumber" required>
      </div>
    </div>
    <label>Башня</label>
    <select name="tower" required>
      <option value="Бронзовая">Бронзовая</option>
      <option value="Серебряная">Серебряная</option>
    </select>
    <div class="row">
      <div>
        <label>Стоимость, ₽</label>
        <input type="number" name="price" required>
      </div>
      <div>
        <label>Стоимость со скидкой, ₽</label>
        <input type="number" name="discountPrice">
      </div>
    </div>
    <label>Размер скидки, %</label>
    <input type="number" name="discountPercent" step="0.1">
    <button type="submit">Добавить планировку</button>
  </form>
</div>

<h2>Все планировки ({count})</h2>
<div class="grid">
{cards}
</div>
</body>
</html>"""


def format_rub(n):
    try:
        return '{:,}'.format(int(round(float(n)))).replace(',', ' ') + ' ₽'
    except (TypeError, ValueError):
        return '—'


def next_plan_id(plans):
    nums = []
    for p in plans:
        try:
            nums.append(int(p['id'].split('-')[-1]))
        except (KeyError, ValueError, IndexError):
            pass
    n = (max(nums) + 1) if nums else 1
    return 'plan-%03d' % n


def render_plan_cards(plans):
    out = []
    for p in plans:
        img = p.get('image') or ''
        price_html = format_rub(p.get('price'))
        if p.get('discountPrice'):
            price_html = ('<span class="old">' + format_rub(p.get('price')) + '</span>'
                           + format_rub(p.get('discountPrice')))
        rooms_label = ROOM_LABELS.get(p.get('rooms'), str(p.get('rooms')))
        out.append(
            '<div class="plan">'
            '<img src="/{img}" alt="">'
            '<div class="meta"><b>{rooms}, {area} м²</b><br>'
            'Этаж {floor} &middot; кв. {num}<br>'
            '{tower} башня'
            '{discount}</div>'
            '<div class="price">{price}</div>'
            '<form method="POST" action="/admin/plans/delete" style="margin:0;">'
            '<input type="hidden" name="id" value="{id}">'
            '<button class="danger" type="submit" onclick="return confirm(\'Удалить {id}?\')">Удалить</button>'
            '</form>'
            '</div>'.format(
                img=img, rooms=rooms_label, area=p.get('area', ''),
                floor=p.get('floor', ''), num=p.get('apartmentNumber', ''),
                tower=p.get('tower', ''),
                discount=(' &middot; скидка ' + str(p.get('discountPercent')) + '%') if p.get('discountPercent') else '',
                price=price_html, id=p.get('id', '')
            )
        )
    return '\n'.join(out) or '<p style="opacity:0.5">Пока нет планировок</p>'


def render_plans_page(message=''):
    plans = load_json(PLANS_FILE, [])
    return PLANS_PAGE.format(message=message, count=len(plans), cards=render_plan_cards(plans))


# ── HTTP-сервер ─────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def _send_bytes(self, body, code=200, content_type='text/html; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html, code=200):
        self._send_bytes(html.encode('utf-8'), code)

    def _send_json(self, data, code=200):
        self._send_bytes(json.dumps(data).encode('utf-8'), code, 'application/json')

    def _serve_static(self, path):
        rel = path.lstrip('/') or 'index.html'
        fpath = os.path.join(PROJECT_DIR, rel)
        if not os.path.abspath(fpath).startswith(PROJECT_DIR) or not os.path.isfile(fpath):
            self._send_html('<h1>404</h1>', 404)
            return
        ctype, _ = mimetypes.guess_type(fpath)
        with open(fpath, 'rb') as f:
            self._send_bytes(f.read(), 200, ctype or 'application/octet-stream')

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/ping':
            self._send_json({'ok': True})
        elif path == '/api/status':
            self._send_json({'pending': git_pending_count()})
        elif path == '/admin':
            self._send_html(render_admin_page())
        elif path == '/admin/plans':
            self._send_html(render_plans_page())
        else:
            self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/upload-slot':
            self._upload_slot()
        elif path == '/api/release':
            self._release()
        elif path == '/admin/plans/upload':
            self._plans_upload()
        elif path == '/admin/plans/delete':
            self._plans_delete()
        else:
            self._send_html('<h1>404</h1>', 404)

    def _read_form(self):
        ctype = self.headers.get('Content-Type', '')
        return cgi.FieldStorage(
            fp=self.rfile, headers=self.headers,
            environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': ctype}
        )

    def _upload_slot(self):
        qs = parse_qs(urlparse(self.path).query)
        slot = (qs.get('slot') or [''])[0]
        if not slot:
            self._send_json({'ok': False, 'error': 'no slot'}, 400)
            return

        form = self._read_form()
        image_field = form['image'] if 'image' in form else None
        if image_field is None or not image_field.filename:
            self._send_json({'ok': False, 'error': 'no file'}, 400)
            return

        ext = os.path.splitext(image_field.filename)[1].lower() or '.jpg'
        filename = slot + ext
        fpath = os.path.join(IMAGES_DIR, filename)
        with open(fpath, 'wb') as f:
            f.write(image_field.file.read())

        manifest = load_json(IMAGES_MANIFEST, {})
        rel_path = 'assets/img/' + filename
        manifest[slot] = rel_path
        save_json(IMAGES_MANIFEST, manifest)

        git_stage([
            os.path.relpath(fpath, PROJECT_DIR),
            os.path.relpath(IMAGES_MANIFEST, PROJECT_DIR),
        ])

        self._send_json({'ok': True, 'path': rel_path})

    def _release(self):
        ok, log = git_release()
        print(log)
        self._send_json({'ok': ok, 'message': log if not is_git_repo() else None, 'log': log})

    def _plans_upload(self):
        form = self._read_form()
        image_field = form['image'] if 'image' in form else None
        if image_field is None or not image_field.filename:
            self._send_html(render_plans_page('<p class="err">Не выбрана картинка</p>'))
            return

        plans = load_json(PLANS_FILE, [])
        pid = next_plan_id(plans)
        ext = os.path.splitext(image_field.filename)[1].lower() or '.jpg'
        filename = pid + ext
        fpath = os.path.join(PLANS_DIR, filename)
        with open(fpath, 'wb') as f:
            f.write(image_field.file.read())

        def num(name, cast=float):
            v = form.getvalue(name, '')
            try:
                return cast(v) if v != '' else None
            except ValueError:
                return None

        entry = {
            'id': pid,
            'image': 'assets/img/plans/' + filename,
            'rooms': int(num('rooms', int) or 0),
            'area': num('area'),
            'floor': int(num('floor', int) or 0),
            'apartmentNumber': form.getvalue('apartmentNumber', ''),
            'tower': form.getvalue('tower', ''),
            'price': num('price'),
            'discountPrice': num('discountPrice'),
            'discountPercent': num('discountPercent'),
        }
        plans.append(entry)
        save_json(PLANS_FILE, plans)

        git_stage([
            os.path.relpath(fpath, PROJECT_DIR),
            os.path.relpath(PLANS_FILE, PROJECT_DIR),
        ])

        self._send_html(render_plans_page('<p class="ok">Планировка %s добавлена</p>' % pid))

    def _plans_delete(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        params = {}
        for pair in body.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k] = v
        pid = params.get('id', '')

        plans = load_json(PLANS_FILE, [])
        target = next((p for p in plans if p['id'] == pid), None)
        if not target:
            self._send_html(render_plans_page('<p class="err">Планировка %s не найдена</p>' % pid))
            return

        img_path = os.path.join(PROJECT_DIR, target['image']) if target.get('image') else None
        plans = [p for p in plans if p['id'] != pid]
        save_json(PLANS_FILE, plans)

        paths = [os.path.relpath(PLANS_FILE, PROJECT_DIR)]
        if img_path and os.path.exists(img_path):
            os.remove(img_path)
            paths.append(os.path.relpath(img_path, PROJECT_DIR))
        git_stage(paths)

        self._send_html(render_plans_page('<p class="ok">Планировка %s удалена</p>' % pid))

    def log_message(self, fmt, *args):
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))


if __name__ == '__main__':
    print('Сайт (режим редактирования): http://localhost:%d/' % PORT)
    print('Обзор фото:                  http://localhost:%d/admin' % PORT)
    print('Планировки:                  http://localhost:%d/admin/plans' % PORT)
    print('Проект: %s' % PROJECT_DIR)
    print('Git-репозиторий: %s' % ('да' if is_git_repo() else 'ещё нет — публикация просто сохранит файлы локально'))
    HTTPServer(('localhost', PORT), Handler).serve_forever()
