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
- Если изменение затрагивает несколько логических частей — можно сгруппировать в одной записи, но лучше разделить, если они независимы.
- Записи сортируются по дате (новые сверху).
- **Структура файла**: блок «Правила оформления» → блок «Шаблоны» → разделитель → записи. Правила и шаблоны всегда остаются вверху файла, новые записи добавляются **под ними**, перед самой старой записью.
  ```
  # Лог кастомных изменений
  │
  ├── 📌 Правила оформления    ← всегда вверху
  ├── 📋 Шаблоны               ← всегда вверху
  ├── ===== разделитель =====
  ├── Запись N (новая)         ← новые дописываются сюда
  ├── Запись N-1
  └── ...
  ```

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

## 2026-07-27 — Версия 6: Промогруппа для промокода «Тариф»

### Что сделано
Добавлена возможность прикреплять промогруппу к промокоду типа «Тариф» при создании — как в боте, так и в веб-кабинете.

### Зачем
Чтобы tariff-промокод мог не только подключать тариф, но и назначать пользователю промогруппу (скидочную группу) при активации.

### Как работает
- При создании tariff-промокода в админке бота после ввода дней появляется вопрос «Хотите прикрепить промогруппу?».
- При ответе «Да» открывается список промогрупп для выбора.
- При ответе «Нет» или «Пропустить» — переход к следующему шагу без группы.
- В веб-кабинете добавлен switch «🏷️ Назначить промогруппу» и селект выбора группы.
- `promo_group_id` передаётся в `create_promocode()` (для tariff так же, как для group).
- Логика активации не менялась — блок назначения промогруппы в `promocode_service.py` уже универсальный.

### Изменённые файлы
- `app/handlers/admin/promocodes.py` — новые хендлеры `process_tariff_promo_group_yes`, `process_tariff_promo_group_no`, `process_tariff_promo_group_select`; изменён `process_promocode_value` (опрос про группу) и `process_promocode_expiry` (передача `promo_group_id`)
- `src/pages/AdminPromocodeCreate.tsx` (кабинет) — switch + select для промогруппы в tariff mode, передача `promo_group_id` в payload, валидация

### Важные замечания
- Требуется пересборка Docker для обоих проектов: `docker compose up -d --build` (бот) и `docker compose build cabinet-frontend` + извлечение статики (кабинет) — выполнено.
- Изменения в кабинете также включены в этот коммит (проект `/opt/bedolaga-cabinet`).

================================================================================

## 2026-07-30 — Версия 7: Юридические документы из кастомного Info при онбординге

### Что сделано
При `INFO_BUTTON_MODE=custom` и `SKIP_RULES_ACCEPT=false` во время регистрации нового пользователя вместо стандартного текста правил показывается содержимое подменю, помеченного маркером `"onboarding": true` в `custom_info_buttons.json`.

### Зачем
В кастомном режиме Info юридические документы (оферта, политика) хранятся в JSON-файле с внешними ссылками. При онбординге пользователь видел стандартные правила из БД, которые не соответствовали актуальным документам в кастомном Info. Теперь онбординг использует те же документы, что и раздел Info.

### Как работает
- В `CustomInfoSubmenu` добавлено поле `onboarding: bool = False`.
- Новая функция `get_onboarding_submenu()` — ищет в конфиге подменю с `onboarding=true`.
- Новая функция `build_onboarding_keyboard()` — строит клавиатуру: url-кнопки из подменю + кнопки «Принимаю»/«Отклоняю».
- В `_continue_registration_after_language()`: если `INFO_BUTTON_MODE=custom` и найдено onboarding-подменю, показывается его заголовок, подпись и ссылки на документы вместо стандартного текста правил.
- Если onboarding-подменю не найдено — работает стандартный механизм (правила из БД).

### Изменённые файлы
- `app/lib/custom_info.py` — добавлено поле `onboarding` в `CustomInfoSubmenu`, функции `get_onboarding_submenu()` и `build_onboarding_keyboard()` (изменён)
- `app/handlers/start.py` — изменена логика показа правил при онбординге (изменён)
- `data/custom_info_buttons.json` — добавлен `"onboarding": true` в подменю «Юридическая информация» (изменён)

### Важные замечания
- Требуется пересборка Docker: `docker compose up -d --build` (выполнено)
- Если в `custom_info_buttons.json` нет подменю с `"onboarding": true`, поведение онбординга не меняется (стандартные правила из БД)
- `SKIP_RULES_ACCEPT=true` по-прежнему пропускает показ любых документов при онбординге
- При `INFO_BUTTON_MODE=standard` поведение не меняется

================================================================================

## 2026-07-30 — Версия 8: Кастомные юридические ссылки в кабинете

### Что сделано
При `INFO_BUTTON_MODE=custom` веб-кабинет (account.bloomvpn.io) использует URL и подписи документов из `custom_info_buttons.json` (onboarding-подменю) вместо стандартных внутренних страниц.

### Зачем
Юридические документы в боте и кабинете теперь всегда ссылаются на одни и те же страницы (bloomvpn.io). При изменении документов достаточно обновить JSON — бот и кабинет подхватят синхронно.

### Как работает
- `GET /cabinet/info/legal-consent` теперь возвращает `document_urls` и `document_labels` — URL и подписи из кастомного JSON
- **LegalConsent (чекбоксы на логине):** ссылки в чекбоксах ведут на внешние URL из JSON. Количество чекбоксов = количеству ссылок в юридическом подменю
- **LegalFooter (футер):** ссылки «Оферта», «Политика» и т.д. ведут на внешние URL
- **PublicLegal (/offer, /privacy, /recurrent):** редирект на соответствующий внешний URL
- При `INFO_BUTTON_MODE=standard` поведение не меняется (внутренние страницы кабинета)

### Изменённые файлы
**Бот:**
- `app/services/legal_consent_service.py` — новая функция `get_custom_document_config()` (изменён)
- `app/cabinet/routes/info.py` — расширена схема `LegalConsentConfigResponse` полями `document_urls` и `document_labels` (изменён)

**Кабинет:**
- `src/types/index.ts` — добавлены `document_urls` и `document_labels` в `LegalConsentConfig` (изменён)
- `src/components/LegalConsent.tsx` — поддержка кастомных URL/подписей через пропсы (изменён)
- `src/components/LegalFooter.tsx` — поддержка внешних URL через пропсы (изменён)
- `src/pages/Login.tsx` — передача `documentUrls`/`documentLabels` в компоненты (изменён)
- `src/pages/PublicLegal.tsx` — редирект на внешний URL, если доступен (изменён)

### Важные замечания
- Требуется пересборка Docker и извлечение статики для обоих проектов (выполнено)
- При `INFO_BUTTON_MODE=standard` кабинет работает как раньше (внутренние страницы `/offer`, `/privacy`)
- Если в кастомном JSON нет onboarding-подменю, `document_urls` пустые — кабинет использует стандартные ссылки

================================================================================

## 2026-07-31 — Версия 9: Юридические вкладки в разделе Info кабинета

### Что сделано
При `INFO_BUTTON_MODE=custom` вкладки «Правила», «Конфиденциальность» и «Оферта» в разделе Info кабинета заменяются вкладками из юридического подменю `custom_info_buttons.json`. Каждая вкладка открывает внешний URL в новой вкладке браузера.

### Зачем
В кастомном режиме юр. документы заданы в JSON внешними ссылками (bloomvpn.io). Внутренние вкладки кабинета дублировали их другим контентом. Теперь раздел Info использует те же ссылки, что и бот.

### Как работает
- `GET /cabinet/info/visibility` возвращает `custom_legal: true` и `rules/privacy/offer: false` при `INFO_BUTTON_MODE=custom`
- Новый эндпоинт `GET /cabinet/info/custom-legal` возвращает `{title, prompt, links: [{label, url}]}` из onboarding-подменю JSON
- В `Info.tsx` вкладки из `custom-legal` вставляются сразу после FAQ; рендерятся как `<a target="_blank">`
- Количество вкладок = количеству ссылок в JSON (динамически)
- FAQ, Статусы (лояльность) и инфо-страницы из админки остаются без изменений

### Изменённые файлы
**Бот:**
- `app/services/legal_consent_service.py` — новая функция `get_custom_legal_content(language)` (изменён)
- `app/cabinet/routes/info.py` — `custom_legal` в visibility, новые схемы `CustomLegalLink`/`CustomLegalContentResponse`, эндпоинт `/custom-legal` (изменён)

**Кабинет:**
- `src/api/info.ts` — тип `CustomLegalContent`, функция `getCustomLegal`, поле `custom_legal` в `InfoVisibility` (изменён)
- `src/pages/Info.tsx` — юридические вкладки-ссылки после FAQ (изменён)

### Важные замечания
- Требуется пересборка Docker и извлечение статики для обоих проектов (выполнено)
- При `INFO_BUTTON_MODE=standard` поведение не меняется
- Если в JSON нет onboarding-подменю или оно пустое — `custom_legal=false`, вкладки не показываются

================================================================================

## 2026-07-23 — Версия 5.1: Баг-фикс TARIFF промокодов

### Что сделано
Исправлены две ошибки при активации промокода типа «Тариф» у пользователя без подписки.

### Причина / Исправление
1. **`NameError: name 'Subscription' is not defined`** — в `_apply_promocode_effects` для TARIFF блока отсутствовал импорт `Subscription` из `app.database.models`. Исправлено: добавлен импорт `Subscription, SubscriptionStatus`.
2. **`MissingGreenlet` при доступе к `db_user.language`** — после `db.rollback()` внутри `activate_promocode` SQLAlchemy expirит объект `db_user`. Последующее обращение к `db_user.language` в `process_promocode`, `handle_promo_subscription_select` и `_send_error_message` вызывало MissingGreenlet. Исправлено: `language` сохраняется в локальную переменную до вызова сервиса; в `_send_error_message` используется `getattr()`.

### Изменённые файлы
- `app/services/promocode_service.py` — добавлен импорт `Subscription, SubscriptionStatus` в TARIFF блок
- `app/handlers/promocode.py` — сохранение `user_language` в `process_promocode` и `handle_promo_subscription_select`
- `app/utils/decorators.py` — защита `_send_error_message` через `getattr(db_user, 'language', 'ru')`

### Важные замечания
- Требуется пересборка Docker: `docker compose up -d --build` (выполнено)

================================================================================

## 2026-07-23 — Версия 5: Новый тип промокода «Тариф»

### Что сделано
Добавлен новый тип промокода `TARIFF` (`tariff`), который позволяет подключить пользователю полноценный тариф (не триал) на указанное количество дней.

### Зачем
По запросу пользователя: нужна возможность раздавать/продавать доступ к конкретному тарифу через промокоды.

### Как работает
- При создании промокода в админке выбирается тип «Тариф», затем конкретный тариф из списка и количество дней подписки.
- При активации промокода пользователем:
  1. Проверяется, нет ли уже подписки на этот тариф (любой статус) → если есть, отказ с ошибкой `subscription_exists`.
  2. В multi-tariff режиме проверяется, нет ли активной подписки на другой тариф → отказ с ошибкой `different_tariff_active`.
  3. Создаётся новая подписка (`status=ACTIVE, is_trial=False`) с параметрами из тарифа (трафик, устройства, сквады).
  4. Создаётся пользователь в RemnaWave.
  5. Пользователь помечается как `has_had_paid_subscription`.
- К промокоду можно опционально привязать промогруппу (поведение как у других типов).

### Изменённые файлы
- `app/database/models.py` — добавлен `TARIFF = 'tariff'` в `PromoCodeType`
- `app/database/crud/promocode.py` — добавлен параметр `tariff_id` в `create_promocode()`
- `app/keyboards/admin.py` — кнопка «📋 Тариф» в клавиатуре выбора типа промокода, эмодзи для списка
- `app/handlers/admin/promocodes.py` — полная поддержка создания и отображения промокодов типа tariff
- `app/handlers/promocode.py` — сообщения об ошибках для tariff-промокодов
- `app/services/promocode_service.py` — логика активации: проверка подписок, создание подписки, создание пользователя в RemnaWave
- `app/services/admin_notification_service.py` — отображение типа tariff в уведомлениях админу
- `app/cabinet/routes/promocode.py` — error messages для cabinet API
- `app/cabinet/routes/admin_promocodes.py` — валидация TARIFF в create/update
- `app/webapi/routes/promocodes.py` — валидация TARIFF + tariff_id в create/update/serialization
- `app/webapi/schemas/promocodes.py` — tariff_id и promo_group_id в схемах

### Важные замечания
- Требуется пересборка Docker: `docker compose up -d --build`
- Миграция БД не требуется (поле `tariff_id` уже существует в таблице `promocodes` — было добавлено ранее для TRIAL_SUBSCRIPTION)

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