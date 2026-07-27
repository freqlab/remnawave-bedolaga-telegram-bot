# Инструкция по обновлению форка

> Как обновить свой форк `remnawave-bedolaga-telegram-bot` при выходе новой версии upstream.

> ⚠️ **Важно:** Обновления бота и кабинета (`bedolaga-cabinet`) выходят **синхронно**.  
> После обновления бота — обязательно обнови и кабинет.  
> Инструкция по кабинету: `/opt/bedolaga-cabinet/docs/UPDATE_GUIDE.md`

## Подготовка

Перед началом убедись, что:

- Все твои кастомные изменения **закоммичены** или хотя бы сохранены
- У тебя есть доступ к `upstream` (оригинальному репозиторию)
- Ты находишься в корне проекта (`cd /opt/remnawave-bedolaga-telegram-bot`)

### О логе кастомных изменений (`docs/CHANGELOG_CUSTOM.md`)

- `CHANGELOG_CUSTOM.md` — это **локальный файл**, его нет в upstream
- При мерже upstream он **не конфликтует** и **не перетирается**
- Мы ведём его параллельно официальному `CHANGELOG.md`
- Новые записи добавляем **сверху** (новые — выше старых), когда вносим кастомные правки
- При обновлении upstream трогать `CHANGELOG_CUSTOM.md` **не нужно** — он остаётся как есть

Если `upstream` ещё не добавлен:

```bash
git remote add upstream https://github.com/BEDOLAGA-DEV/remnawave-bedolaga-telegram-bot.git
```

## Пошаговый план

### Шаг 1: Забрать новые изменения из upstream

```bash
git fetch upstream
```

> Скачивает новые коммиты и теги из оригинального репозитория, но не вливает их в твою ветку.

### Шаг 1.5: Предварительный просмотр изменений

Прежде чем мержить — посмотри, что нового появилось в upstream:

```bash
# Список новых коммитов (с датами и авторами)
git log --oneline --graph upstream/main --not main

# Сводка изменённых файлов
git diff --stat main..upstream/main

# Официальный CHANGELOG новой версии
git show upstream/main:CHANGELOG.md | head -150

# Если CHANGELOG пустой — глянь список коммитов подробнее
git log --oneline --format='%h %s' upstream/main --not main
```

> Это поможет оценить объём изменений, понять, какие фичи и баг-фиксы
> добавлены, и заранее выявить потенциально конфликтные места
> (особенно если upstream менял те же файлы, что и твои кастомные доработки).
> Сверься с `docs/CHANGELOG_CUSTOM.md` — если upstream затрагивает
> те же зоны, будь готов к конфликтам.

### Шаг 2: Создать резервную копию

```bash
git branch backup/<текущая-версия>-custom
```

Пример: `git branch backup/v3.65.1-custom`

> Создаёт ветку-бекап на текущем состоянии. Если что-то пойдёт не так — просто `git checkout backup/v3.65.1-custom` и ты вернёшься к этому моменту.

### Шаг 3: Сохранить кастомные изменения (если не закоммичены)

```bash
git add -A
git commit -m "chore: save custom features before merge v<версия>"
git branch custom-features
```

> Если у тебя уже есть ветка `custom-features` — обнови её:
> ```bash
> git branch -f custom-features HEAD
> ```

### Шаг 4: Смержить upstream

```bash
git merge upstream/main
```

> Вливает новые изменения из upstream в твою ветку `main`.
> Если возникнут **конфликты** — разреши их вручную, сохранив **оба** набора изменений (и свои, и upstream).
>
> **Обрати особое внимание на файлы, которые менялись в кастомных изменениях.**  
> Актуальный список — в последних записях `docs/CHANGELOG_CUSTOM.md`.
> Перед мержем открой этот файл, посмотри секции **«Изменённые файлы»** —
> именно в этих файлах вероятны конфликты с upstream.

### Шаг 5: Проверить синтаксис

```bash
python3 -c "
import ast
files = [
    'app/config.py', 'app/keyboards/inline.py',
    'app/handlers/menu.py', 'app/handlers/subscription/devices.py',
    'app/handlers/subscription/links.py', 'app/lib/custom_info.py',
    'app/lib/guide_cryptolink.py', 'app/services/system_settings_service.py',
    'app/bot.py',
]
for f in files:
    try:
        with open(f) as fh: ast.parse(fh.read())
        print(f'OK: {f}')
    except SyntaxError as e:
        print(f'ERROR: {f}: {e}')
"
```

> Проверяет, что во всех изменённых файлах нет синтаксических ошибок.

### Шаг 6: Пересобрать Docker

```bash
docker compose up -d --build
```

> Пересобирает образ и перезапускает контейнеры. Флаг `--build` обязателен, если добавились новые Python-файлы.

### Шаг 7: Обновить кабинет (если релиз синхронный)

Кабинет (`bedolaga-cabinet`) обычно обновляется одновременно с ботом.
Перейди в его директорию и выполни те же шаги (с учётом особенностей сборки):

```bash
cd /opt/bedolaga-cabinet
```

Подробная инструкция: `docs/UPDATE_GUIDE.md` в проекте кабинета.

### Шаг 8: Запушить в свой форк

```bash
git push origin main
```

> Отправляет обновлённую версию в твой репозиторий на GitHub.

После бота — не забудь запушить и кабинет, если обновлял его.

## Если что-то пошло не так

```bash
# Вернуться на резервную копию
git checkout backup/v<версия>-custom

# Посмотреть историю
git log --oneline --graph --all

# Отменить merge (если ещё не закоммичен)
git merge --abort
```

## Комбинированное обновление (бот + кабинет)

Рекомендуемый порядок при синхронном релизе — одной сессией:

```bash
# ===== 1. БОТ =====
cd /opt/remnawave-bedolaga-telegram-bot

git fetch upstream
git branch backup/v<версия-бота>-custom
git merge upstream/main
# разреши конфликты, если есть
python3 -c "import ast; ast.parse(open('app/config.py').read())"  # быстрая проверка
docker compose up -d --build
git push origin main

# ===== 2. КАБИНЕТ =====
cd /opt/bedolaga-cabinet

git fetch upstream
git branch backup/v<версия-кабинета>-custom
git merge upstream/main
# разреши конфликты, если есть
docker compose build cabinet-frontend
docker compose create cabinet-frontend
mkdir -p ./cabinet-dist
docker cp cabinet_frontend:/usr/share/nginx/html/. ./cabinet-dist/
docker compose rm -sf cabinet-frontend
docker restart nginx
git push origin main
```