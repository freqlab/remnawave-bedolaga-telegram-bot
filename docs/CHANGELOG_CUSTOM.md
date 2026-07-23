# Лог кастомных изменений

> Все доработки, не входящие в официальный релиз проекта.
> Этот файл содержит правила оформления, шаблоны и историю изменений.

## 📌 Правила оформления записей (обязательны)

Каждая запись должна содержать следующие **обязательные поля**:
- **Дата** — в формате `ГГГГ-ММ-ДД`.
- **Версия / название** — например, «Версия №» или «CryptoLink в гайде».
- **Заголовок** — краткая суть изменения.
- **Что сделано** — описание функциональности или исправления.
- **Зачем** — причина внедрения (бизнес-требование, пользовательский запрос, баг).
- **Изменённые файлы** — перечень всех затронутых файлов с пометками (новый, изменён, удалён).
- **Важные замечания** — что нужно сделать при деплое (пересборка Docker, правка `.env`, ручные шаги, проверки).
- **Разделитель** — после завершения каждой записи (включая «Важные замечания») ставится строка-разделитель: `================================================================================` (ровно 80 символов `=`). Это отделяет одну запись от другой и обеспечивает единообразие при просмотре лога.

**Необязательные, но рекомендуемые разделы**:
- **Как работает** — для сложных изменений (механика, цепочки, настройки, маппинги).
- **Причина / Исправление** — для баг-фиксов (что было не так и как починили).

**Правила добавления**:
- Запись создаётся **после** завершения всех шагов по внедрению изменения (включая тестирование и финальный коммит).
- Если изменение затрагивает несколько логических частей – можно сгруппировать в одной записи, но лучше разделить, если они независимы.
- Записи сортируются по дате (новые сверху).

## 📋 Шаблоны для записей

Используйте один из двух шаблонов в зависимости от типа изменения.

### Шаблон для нового функционала

```markdown
## ГГГГ-ММ-ДД — Версия X: Краткое название

### Что сделано
Описание новой функциональности.

### Зачем
Причина внедрения (бизнес-требование, запрос пользователя).

### Как работает
Краткая механика: настройки, цепочки, маппинги, middleware и т.д.

### Изменённые файлы
- `путь/к/файлу.py` — что сделано (новый, изменён, удалён)
- ...

### Важные замечания
Например: требуется пересборка Docker, правка .env, ручное добавление файлов и т.п.

================================================================================

## 2026-07-22 — Версия 4: Режим отдельных фото для каждого раздела бота

### Что сделано
Добавлена возможность показывать РАЗНЫЕ изображения для разных разделов бота
(главное меню, подписка, рефералы, поддержка, баланс, инфо и т.д.) вместо одного
общего логотипа.

### Зачем
Ранее при `ENABLE_LOGO_MODE=true` бот отправлял один и тот же логотип (`vpn_logo.png`)
со всеми сообщениями. Новая функциональность позволяет визуально различать разделы
бота, улучшая UX.

### Как работает

**Новая настройка:**
- `ENABLE_SECTION_PHOTOS: bool = False` — выключена по умолчанию.
- При `false` поведение полностью идентично исходному (ENABLE_LOGO_MODE как работал,
  так и работает).

**Фото разделов:**
- Хранятся в `assets/branding/section_photos/<section>.png`.
- Цепочка фолбэка: `<section>.png` → `default.png` → `vpn_logo.png` → текст (без фото).

**Callback_data → раздел:**
Полный маппинг callback_data на разделы реализован в `app/utils/section_photos.py`
в функции `_map_callback_to_section()`. Более специфичные префиксы проверяются ДО общих.

Поддерживаемые разделы:
- `main_menu` — главное меню
- `subscription` — подписка, тарифы, триал, устройства, трафик
- `referral` — реферальная программа и вывод
- `support` — поддержка и тикеты
- `balance` — баланс и пополнение
- `info` — информационные разделы (правила, FAQ, политика, оферта)
- `settings` — настройки, язык

**Middleware:**
- `SectionPhotoMiddleware` — определяет раздел из callback_data/команды и сохраняет
  его в контекстной переменной `_current_section`.

**Патчи Message.answer / Message.edit_text:**
- Дополнены поддержкой секционных фото через контекстную переменную.
- При `ENABLE_SECTION_PHOTOS=true` используют фото раздела вместо общего логотипа.

**edit_or_answer_photo():**
- Добавлен опциональный параметр `section`.
- Если не передан, берётся из контекстной переменной `_current_section`.

**Кеширование:**
- После первой успешной отправки фото раздела file_id кешируется, чтобы Telegram
  не перезагружал файл при повторных отправках.

### Маппинг фото разделов

Фото помещаются в `assets/branding/section_photos/<section>.png`.

| Файл | Раздел | Описание |
|---|---|---|
| `main_menu.png` | `main_menu` | Главное меню (кнопка «Назад в меню», команда `/start`) |
| `subscription.png` | `subscription` | Подписка, тарифы, триал, устройства, трафик, промокоды, happ, autopay, gift |
| `referral.png` | `referral` | Реферальная программа, статистика, вывод средств |
| `support.png` | `support` | Поддержка, контакты, тикеты (создание/просмотр/ответ) |
| `balance.png` | `balance` | Баланс, история пополнений, все платёжные методы, проверка статуса |
| `info.png` | `info` | Информация: правила, FAQ, приватность, оферта, инфо-страницы, конкурсы, статус серверов |
| `settings.png` | `settings` | Настройки: выбор языка, подтверждение WebAuth |
| `default.png` | *(фолбэк)* | Используется для всех разделов, у которых нет отдельного фото |

Цепочка фолбэка при отсутствии файла:
`<section>.png` → `default.png` → `vpn_logo.png` (или `LOGO_FILE`) → текст без фото

### Примеры callback_data по разделам

**subscription:** `menu_subscription`, `menu_trial`, `menu_buy`, `subscription_*`, `trial_*`, `period_*`, `traffic_*`, `devices_*`, `country_*`, `autopay_*`, `buy_traffic`, `add_traffic_*`, `simple_subscription_*`, `gift_activate:*`, `activate_button`, `menu_promocode`, `promo_sub:*`

**referral:** `menu_referral`, `referral_*` (включая `referral_withdrawal`, `referral_list_page_*`)

**support:** `menu_support`, `create_ticket`, `my_tickets`, `view_ticket_*`, `reply_ticket_*`, `close_ticket_*`, `cancel_ticket_*`

**balance:** `menu_balance`, `balance_history`, `balance_topup`, `topup_*`, `check_*` (все провайдеры: yookassa, cryptobot, heleket и т.д.)

**info:** `menu_info`, `menu_rules`, `menu_faq`, `menu_privacy_policy`, `menu_public_offer`, `info_page:*`, `menu_server_status`, `contests_menu`, `menu_profile_unavailable`

**settings:** `menu_language`, `language_select:*`, `webauth_*`

### Изменённые файлы
- `app/utils/section_photos.py` — **новый модуль**. Управление фото разделов,
  маппинг callback_data → раздел, кеширование file_id.
- `app/middlewares/section_photo.py` — **новый модуль**. Middleware для определения
  раздела из callback_data/команды.
- `app/config.py` — добавлено поле `ENABLE_SECTION_PHOTOS: bool = False`.
- `app/utils/photo_message.py` — `edit_or_answer_photo()` дополнен параметром
  `section`; `_resolve_media()` использует `_get_section_or_logo_media()`;
  добавлено кеширование file_id для секционных фото.
- `app/utils/message_patch.py` — добавлена контекстная переменная `_current_section`;
  `_answer_with_photo()` и `_edit_with_photo()` дополнены поддержкой секционных фото.
- `app/bot.py` — зарегистрирован `SectionPhotoMiddleware`.
- `.env` / `.env.example` — добавлен параметр `ENABLE_SECTION_PHOTOS=false`.

### Важные замечания
- После добавления нового Python-файла (`app/utils/section_photos.py`,
  `app/middlewares/section_photo.py`) требуется **пересборка Docker-образа**:
  `docker compose up -d --build`.
- Фото разделов нужно вручную поместить в `assets/branding/section_photos/`.
  Можно начать с `default.png` — он будет использоваться как фолбэк для всех
  разделов, для которых нет отдельного фото.
- При `ENABLE_SECTION_PHOTOS=false` регрессии нет — поведение полностью идентично
  исходному. `ENABLE_LOGO_MODE` продолжает работать как раньше.
- Если фото для раздела отсутствует, используется цепочка фолбэка до `vpn_logo.png`.

================================================================================

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

================================================================================

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

### Важные замечания
- При изменении кода (файлов `app/lib/custom_info.py`, `app/handlers/menu.py`) требуется **пересборка Docker-образа**.
- Если меняется только `data/custom_info_buttons.json`, достаточно перезапустить контейнер бота (`docker compose restart bot`).
- При `INFO_BUTTON_MODE=standard` поведение не меняется — регрессии нет.

================================================================================

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

================================================================================