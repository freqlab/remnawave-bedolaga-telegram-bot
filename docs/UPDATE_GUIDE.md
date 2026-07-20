# Инструкция по обновлению форка

> Как обновить свой форк `remnawave-bedolaga-telegram-bot` при выходе новой версии upstream.

## Подготовка

Перед началом убедись, что:

- Все твои кастомные изменения **закоммичены** или хотя бы сохранены
- У тебя есть доступ к `upstream` (оригинальному репозиторию)
- Ты находишься в корне проекта (`cd /opt/remnawave-bedolaga-telegram-bot`)

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

### Шаг 7: Запушить в свой форк

```bash
git push origin main
```

> Отправляет обновлённую версию в твой репозиторий на GitHub.

## Если что-то пошло не так

```bash
# Вернуться на резервную копию
git checkout backup/v3.64.0-custom

# Посмотреть историю
git log --oneline --graph --all

# Отменить merge (если ещё не закоммичен)
git merge --abort
```
