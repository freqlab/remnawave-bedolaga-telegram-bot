# Лог кастомных изменений

> Все доработки, не входящие в официальный релиз проекта.
> Формат: дата, версия, что сделано, зачем, почему, какие файлы затронуты.

## 2026-07-16 — Версия 3: CryptoLink в гайде подключения

### Что сделано
Добавлена возможность в режиме `CONNECT_BUTTON_MODE=guide` подменять ссылку подписки на кнопке «Подключиться» на cryptoLink с редиректом через `HAPP_CRYPTOLINK_REDIRECT_TEMPLATE` (аналогично режиму `happ_cryptolink`).

### Зачем
В режиме guide пользователь выбирает устройство и видит гайд с кнопкой «Подключиться». Эта кнопка вела на обычную `subscription_url`. Потребовалось, чтобы она возвращала crypt-ссылку (`happ://crypt5/...`), обёрнутую в HTTPS-редирект (`https://vpn.freqlab.io/?redirect=...`), что позволяет открывать Happ-клиент из Telegram без поддержки кастомных схем.

### Как работает
- В `.env` добавлена переменная `CONNECT_BUTTON_GUIDE_CRYPTOLINK_ENABLED` (`false` по умолчанию).
- При `true` + `CONNECT_BUTTON_MODE=guide`:
  - **Кнопка «Подключиться» в гайде устройства** — хендлеры `handle_device_guide()` и `handle_specific_app_guide()` вычисляют редирект-ссылку через `get_guide_cryptolink_redirect_url()`. Функция берёт `subscription_crypto_link`, прогоняет через `_build_redirect_link()`, подставляя в `HAPP_CRYPTOLINK_REDIRECT_TEMPLATE`. Готовая HTTPS-ссылка передаётся через параметр `crypto_redirect_url` в `get_connection_guide_keyboard()`, где используется для кнопки `subscriptionLink`.
  - **Кнопка «Показать ссылку подписки»** — хендлер `handle_open_subscription_link()` подменяет `subscription_link` на `subscription.subscription_crypto_link` (raw cryptoLink, `happ://crypt4/...`) и оборачивает его в `<blockquote expandable>` — аналогично режиму `happ_cryptolink`.
- При `false` (или отсутствии параметра) — поведение полностью идентично исходному.

### Изменённые файлы
- `app/lib/guide_cryptolink.py` — **новый модуль**. Содержит `is_guide_cryptolink_enabled()`, `get_guide_cryptolink_redirect_url()`, `_build_redirect_link()`.
- `app/config.py` — добавлено поле `CONNECT_BUTTON_GUIDE_CRYPTOLINK_ENABLED: bool = False`.
- `app/keyboards/inline.py` — в `get_connection_guide_keyboard()` добавлен параметр `crypto_redirect_url`. В `get_specific_app_keyboard()` добавлен сквозной параметр `crypto_redirect_url`.
- `app/handlers/subscription/devices.py` — в `handle_device_guide()` и `handle_specific_app_guide()` добавлен вызов `get_guide_cryptolink_redirect_url()` и передача результата в клавиатуру.
- `app/handlers/subscription/links.py` — в `handle_open_subscription_link()` добавлена подмена `subscription_link` на raw cryptoLink при активном флаге, с обёрткой в `<blockquote expandable>`.
- `app/bot.py` — добавлена валидация при старте: предупреждение, если `GUIDE_CRYPTOLINK_ENABLED=true` без `HAPP_CRYPTOLINK_REDIRECT_TEMPLATE`.
- `app/services/system_settings_service.py` — параметр добавлен в маппинг категории `CONNECT_BUTTON` для админ-панели.
- `.env` / `.env.example` — добавлен новый параметр с комментарием.

### Важные замечания
- После добавления нового Python-файла (`app/lib/guide_cryptolink.py`) требуется **пересборка Docker-образа**: `docker compose up -d --build`.
- Для включения нужно раскомментировать `CONNECT_BUTTON_GUIDE_CRYPTOLINK_ENABLED=true` в `.env`.
- Параметр работает только при `CONNECT_BUTTON_MODE=guide`. В других режимах игнорируется.
- Требуется заданный `HAPP_CRYPTOLINK_REDIRECT_TEMPLATE`, иначе cryptoLink не сможет сформироваться и кнопка вернётся к стандартному поведению.
- При `CONNECT_BUTTON_GUIDE_CRYPTOLINK_ENABLED=false` регрессии нет — поведение полностью идентично исходному.

---

## 2026-07-16 — Версия 2: Добавлены подменю

### Что сделано
Добавлена поддержка вложенных подменю в кастомном режиме кнопки «Инфо».

### Зачем
Пользователь запросил возможность группировать ссылки по категориям. Например:
«Юридическая информация» → раскрывается в список документов (оферта, политика и т.д.).
«Документация» → раскрывается в список руководств.

### Как работает
- В JSON-файле `data/custom_info_buttons.json` у кнопки появился новый тип `type: "submenu"`.
- Кнопка этого типа содержит вложенный объект `submenu` с массивом `buttons[]` (только url-ссылки).
- Нажатие на submenu-кнопку отправляет callback `custom_info_submenu:<index>`.
- В `menu.py` добавлен хендлер `show_custom_info_submenu()`, который загружает подменю и показывает его.
- Кнопка «Назад» возвращает в корень Info через callback `back_to_custom_info_root`.
- Добавлен хендлер `back_to_custom_info_root()`.

### Изменённые файлы
- `app/lib/custom_info.py` — новые датаклассы `CustomInfoSubmenu`, функция `_parse_button()`, `build_submenu_keyboard()`, `get_submenu_by_index()`, `get_submenu_title()`, `get_submenu_prompt()`, обновлены `load_custom_info_config()` и `build_custom_info_keyboard()`.
- `app/handlers/menu.py` — новые хендлеры `show_custom_info_submenu()`, `back_to_custom_info_root()`, регистрация в `register_handlers()`.
- `data/custom_info_buttons.json` — обновлён пример с двумя подменю.

---

## 2026-07-16 — Версия 1: Базовая кастомная кнопка «Инфо»

### Что сделано
Добавлена возможность заменять стандартное меню раздела «Инфо» на набор пользовательских кнопок-ссылок.

### Зачем
Администратору нужно было гибко управлять содержимым раздела «Инфо» без изменения кода и без привязки к БД.

### Как работает
- В `.env` добавлена переменная `INFO_BUTTON_MODE` со значениями `standard` (по умолчанию) или `custom`.
- В режиме `custom` вместо стандартного меню (FAQ, оферта, правила) показываются кнопки из `data/custom_info_buttons.json`.
- JSON-формат поддерживает два варианта: расширенный (с title/prompt) и упрощённый (только массив кнопок).
- Кнопки поддерживают локализацию: текст может быть строкой или объектом `{"ru": "...", "en": "..."}`.
- Файл `data/custom_info_buttons.json` подмонтирован в Docker через volume — можно менять без пересборки.

### Изменённые файлы
- `app/lib/custom_info.py` — **новый модуль**. Содержит датаклассы, загрузку JSON, построение клавиатуры.
- `app/config.py` — добавлены поля `INFO_BUTTON_MODE`, `CUSTOM_INFO_BUTTONS_PATH`, метод `is_custom_info_mode()`.
- `app/handlers/menu.py` — добавлен импорт `custom_info_module`, в `show_info_menu()` добавлена ветка для custom-режима.
- `data/custom_info_buttons.json` — **новый файл**, пример конфигурации.
- `.env.example` — добавлены комментарии для новых переменных.

### Важные замечания
- После добавления новых Python-файлов (`app/lib/custom_info.py`) требуется **пересборка Docker-образа**: `docker compose up -d --build`.
- Если меняется только `.env` — достаточно `docker compose up -d`.
- Если меняется `data/custom_info_buttons.json` — достаточно `docker compose restart bot`.
- Чтобы изменения кода подхватывались без пересборки, можно добавить volume `./app:/app/app:rw` в `docker-compose.yml` (не рекомендуется для продакшена).
- При `INFO_BUTTON_MODE=standard` поведение бота полностью идентично исходному — регрессии нет.
- Callback_data `custom_info_submenu:` и `back_to_custom_info_root` не конфликтуют с существующими.
