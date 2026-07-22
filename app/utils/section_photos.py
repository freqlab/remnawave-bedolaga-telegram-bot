"""
Управление раздельными фото для разных разделов бота.

Режим ENABLE_SECTION_PHOTOS позволяет показывать разные изображения
в разных разделах вместо одного общего логотипа.

Цепочка фолбэка для каждого раздела:
    <section>.png → default.png → vpn_logo.png → текст (без фото)

Фото разделов хранятся в assets/branding/section_photos/<section>.png.
"""

from __future__ import annotations

from pathlib import Path

import structlog
from aiogram.types import FSInputFile, Message

from app.config import settings


logger = structlog.get_logger(__name__)

# Директория с фото разделов.
# Фото хранятся в assets/branding/section_photos/<section>.png относительно корня проекта.
# Берём директорию логотипа как точку отсчёта (обычно корень проекта),
# и спускаемся в assets/branding/section_photos.
_LOGO_DIR = Path(settings.LOGO_FILE).resolve().parent
if _LOGO_DIR.name == 'assets':
    # LOGO_FILE может лежать внутри assets/
    SECTION_PHOTOS_DIR = _LOGO_DIR / 'branding' / 'section_photos'
else:
    SECTION_PHOTOS_DIR = _LOGO_DIR / 'assets' / 'branding' / 'section_photos'

# Кеш file_id для каждого раздела: {section_name: file_id}
_section_file_ids: dict[str, str] = {}

# Путь к default.png (фолбэк если нет фото конкретного раздела)
_DEFAULT_SECTION_PHOTO = SECTION_PHOTOS_DIR / 'default.png'

# Путь к основному логотипу (финальный фолбэк)
_LOGO_PATH = Path(settings.LOGO_FILE)


# ──────────────────────────────────────────────
#  Маппинг callback_data / команд → разделы
# ──────────────────────────────────────────────

def _map_callback_to_section(callback_data: str) -> str | None:
    """Определяет раздел по callback_data.

    Порядок проверки: более специфичные префиксы ДО общих.
    """
    if not callback_data:
        return None

    data = callback_data

    # ---- Главное меню и навигация ----
    if data == 'back_to_menu':
        return 'main_menu'

    # ---- Подписка ----
    if data == 'menu_subscription':
        return 'subscription'
    if data == 'menu_trial':
        return 'subscription'
    if data == 'menu_buy':
        return 'subscription'
    if data == 'subscription_upgrade':
        return 'subscription'
    if data == 'subscription_purchase':
        return 'subscription'

    # ---- Информационные разделы (menu_info и его подразделы) ----
    if data == 'menu_info':
        return 'info'
    if data == 'menu_info_promo_groups':
        return 'info'
    if data == 'menu_faq':
        return 'info'
    if data == 'menu_rules':
        return 'info'
    if data == 'menu_privacy_policy':
        return 'info'
    if data == 'menu_public_offer':
        return 'info'
    if data == 'menu_profile_unavailable':
        return 'info'
    if data == 'back_to_custom_info_root':
        return 'info'

    # ---- Рефералы ----
    if data == 'menu_referral':
        return 'referral'
    if data == 'referral_withdrawal':
        return 'referral'
    if data == 'referral_withdrawal_start':
        return 'referral'

    # ---- Поддержка ----
    if data == 'menu_support':
        return 'support'

    # ---- Баланс ----
    if data == 'menu_balance':
        return 'balance'

    # ---- Тикеты ----
    if data == 'create_ticket':
        return 'support'
    if data == 'my_tickets':
        return 'support'

    # ---- Язык ----
    if data == 'menu_language':
        return 'settings'

    # ---- Префиксные (после точных совпадений) ----
    if data.startswith('menu_rules:'):
        return 'info'
    if data.startswith('menu_faq_page:'):
        return 'info'
    if data.startswith('menu_privacy_policy:'):
        return 'info'
    if data.startswith('menu_public_offer:'):
        return 'info'
    if data.startswith('info_page:'):
        return 'info'
    if data.startswith('custom_info_submenu:'):
        return 'info'

    if data.startswith('language_select:'):
        return 'settings'

    if data.startswith('referral_'):
        return 'referral'
    if data.startswith('trial_'):
        return 'subscription'
    if data.startswith('subscription_'):
        return 'subscription'
    if data.startswith('period_'):
        return 'subscription'
    if data.startswith('traffic_'):
        return 'subscription'
    if data.startswith('devices_'):
        return 'subscription'
    if data.startswith('country_'):
        return 'subscription'
    if data.startswith('my_subscriptions'):
        return 'subscription'
    if data.startswith('sm:'):
        return 'subscription'
    if data.startswith('sl:'):
        return 'subscription'
    if data.startswith('se:'):
        return 'subscription'
    if data.startswith('st:'):
        return 'subscription'
    if data.startswith('sd:'):
        return 'subscription'
    if data.startswith('sub_del'):
        return 'subscription'
    if data.startswith('sr:'):
        return 'subscription'
    if data.startswith('buy_traffic'):
        return 'subscription'
    if data.startswith('add_traffic_'):
        return 'subscription'
    if data.startswith('claim_discount_'):
        return 'subscription'
    if data.startswith('promo_offer_'):
        return 'subscription'
    if data.startswith('autopay_'):
        return 'subscription'
    if data.startswith('happ_download_'):
        return 'subscription'
    if data.startswith('subscription_connect'):
        return 'subscription'
    if data.startswith('device_guide_'):
        return 'subscription'
    if data.startswith('app_list_'):
        return 'subscription'
    if data.startswith('app_'):
        return 'subscription'
    if data.startswith('open_subscription_link'):
        return 'subscription'
    if data.startswith('change_devices_'):
        return 'subscription'
    if data.startswith('confirm_change_devices_'):
        return 'subscription'
    if data.startswith('extend_period_'):
        return 'subscription'
    if data.startswith('confirm_reset_traffic'):
        return 'subscription'
    if data.startswith('confirm_reset_devices'):
        return 'subscription'
    if data.startswith('confirm_switch_traffic_'):
        return 'subscription'
    if data.startswith('switch_traffic_'):
        return 'subscription'
    if data.startswith('reset_device_'):
        return 'subscription'
    if data.startswith('device_rename_'):
        return 'subscription'
    if data.startswith('device_management'):
        return 'subscription'
    if data.startswith('devices_page_'):
        return 'subscription'
    if data.startswith('no_traffic_packages'):
        return 'subscription'
    if data.startswith('toggle_daily_subscription_pause'):
        return 'subscription'
    if data == 'activate_button':
        return 'subscription'
    if data == 'menu_promocode':
        return 'subscription'
    if data.startswith('promo_sub:'):
        return 'subscription'
    if data == 'subscription_purchase':
        return 'subscription'
    if data.startswith('simple_subscription_'):
        return 'subscription'
    if data.startswith('gift_activate:'):
        return 'subscription'
    if data == 'temp_disabled':
        return 'subscription'

    if data == 'menu_server_status':
        return 'info'
    if data.startswith('server_status_page:'):
        return 'info'

    if data == 'contests_menu':
        return 'info'
    if data.startswith('contest_play_'):
        return 'info'
    if data.startswith('contest_pick_'):
        return 'info'

    if data.startswith('view_ticket_'):
        return 'support'
    if data.startswith('ticket_view_page_'):
        return 'support'
    if data.startswith('reply_ticket_'):
        return 'support'
    if data.startswith('close_ticket_'):
        return 'support'
    if data.startswith('ticket_attachments_'):
        return 'support'
    if data.startswith('user_delete_message_'):
        return 'support'
    if data.startswith('cancel_ticket_'):
        return 'support'
    if data.startswith('close_ticket_notification_'):
        return 'support'

    if data.startswith('webauth_'):
        return 'settings'

    # ---- Баланс и пополнение ----
    if data == 'menu_balance':
        return 'balance'
    if data == 'balance_history':
        return 'balance'
    if data.startswith('balance_history_page_'):
        return 'balance'
    if data == 'balance_topup':
        return 'balance'
    if data.startswith('topup_'):
        return 'balance'
    if data.startswith('check_yookassa_'):
        return 'balance'
    if data.startswith('check_cryptobot_'):
        return 'balance'
    if data.startswith('check_heleket_'):
        return 'balance'
    if data.startswith('check_mulenpay_'):
        return 'balance'
    if data.startswith('check_pal24_'):
        return 'balance'
    if data.startswith('check_platega_'):
        return 'balance'
    if data.startswith('check_tribute_'):
        return 'balance'
    if data.startswith('check_wata_'):
        return 'balance'
    if data.startswith('check_cloudpayments_'):
        return 'balance'
    if data.startswith('check_freekassa_'):
        return 'balance'
    if data.startswith('check_kassa_ai_'):
        return 'balance'
    if data.startswith('check_riopay_'):
        return 'balance'
    if data.startswith('check_severpay_'):
        return 'balance'
    if data.startswith('check_paypear_'):
        return 'balance'
    if data.startswith('check_rollypay_'):
        return 'balance'
    if data.startswith('check_overpay_'):
        return 'balance'
    if data.startswith('check_aurapay_'):
        return 'balance'
    if data.startswith('check_antilopay_'):
        return 'balance'
    if data.startswith('check_jupiter_'):
        return 'balance'
    if data.startswith('check_donut_'):
        return 'balance'
    if data == 'topup_support':
        return 'balance'
    if data.startswith('pal24_method_'):
        return 'balance'
    if data.startswith('platega_method_'):
        return 'balance'
    if data.startswith('topup_platega_m'):
        return 'balance'

    return None


def _map_command_to_section(command: str) -> str | None:
    """Определяет раздел по текстовой команде."""
    if not command:
        return None
    cmd = command.strip().lower()

    if cmd in ('/start',):
        return 'main_menu'
    return None


def get_section_photo_path(section: str | None) -> Path | None:
    """Возвращает путь к фото для указанного раздела.

    Цепочка фолбэка:
        1. <section>.png
        2. default.png
        3. vpn_logo.png (из LOGO_FILE)
        4. None (текст без фото)
    """
    if not section:
        return _resolve_fallback_chain(None)

    # 1. Пробуем фото конкретного раздела
    section_path = SECTION_PHOTOS_DIR / f'{section}.png'
    if section_path.exists() and section_path.is_file():
        return section_path

    return _resolve_fallback_chain(section)


def _resolve_fallback_chain(_section: str | None) -> Path | None:
    """Пробегает по цепочке фолбэка."""
    # 2. default.png
    if _DEFAULT_SECTION_PHOTO.exists() and _DEFAULT_SECTION_PHOTO.is_file():
        return _DEFAULT_SECTION_PHOTO

    # 3. vpn_logo.png
    if _LOGO_PATH.exists() and _LOGO_PATH.is_file():
        return _LOGO_PATH

    # 4. Нет фото
    return None


def get_section_media(section: str | None) -> str | FSInputFile | None:
    """Возвращает file_id (закешированный) или FSInputFile для фото раздела.

    После первой успешной отправки file_id кешируется,
    чтобы Telegram не перезагружал файл при повторных отправках.
    """
    if not section:
        return None

    # Проверяем кеш
    cached_id = _section_file_ids.get(section)
    if cached_id:
        return cached_id

    # Определяем путь к фото
    photo_path = get_section_photo_path(section)
    if photo_path is None:
        return None

    return FSInputFile(photo_path)


def cache_section_file_id(section: str, result: Message | None) -> None:
    """Кеширует file_id после успешной отправки фото раздела."""
    if not section or result is None:
        return
    if section in _section_file_ids:
        return
    if hasattr(result, 'photo') and result.photo:
        _section_file_ids[section] = result.photo[-1].file_id


def get_section_from_callback(callback_data: str) -> str | None:
    """Публичный API: определяет раздел из callback_data."""
    return _map_callback_to_section(callback_data)


def get_section_from_command(command: str) -> str | None:
    """Публичный API: определяет раздел из команды."""
    return _map_command_to_section(command)
