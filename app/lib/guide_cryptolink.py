"""
Модуль для режима CONNECT_BUTTON_GUIDE_CRYPTOLINK_ENABLED.

Позволяет в режиме CONNECT_BUTTON_MODE=guide подменять ссылку подписки
на cryptoLink с редиректом через HAPP_CRYPTOLINK_REDIRECT_TEMPLATE.
Кнопка "Подключиться" в гайде устройства возвращает ссылку вида:
    https://example.com/?redirect=<encoded_cryptoLink>
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

import structlog

from app.config import settings

if TYPE_CHECKING:
    from app.database.models import Subscription

logger = structlog.get_logger(__name__)


def is_guide_cryptolink_enabled() -> bool:
    """Проверяет, включён ли режим cryptoLink в гайде.

    Требует CONNECT_BUTTON_MODE=guide и CONNECT_BUTTON_GUIDE_CRYPTOLINK_ENABLED=true.
    """
    return (
        settings.CONNECT_BUTTON_MODE == 'guide'
        and settings.CONNECT_BUTTON_GUIDE_CRYPTOLINK_ENABLED
    )


def get_guide_cryptolink_redirect_url(subscription: Subscription | None) -> str | None:
    """Возвращает редирект-ссылку с cryptoLink для кнопки "Подключиться" в гайде.

    Берёт subscription_crypto_link из подписки, оборачивает его в
    HAPP_CRYPTOLINK_REDIRECT_TEMPLATE и возвращает готовую HTTPS-ссылку.

    Args:
        subscription: Объект подписки с полем subscription_crypto_link.

    Returns:
        URL для кнопки (https://...), или None если cryptoLink недоступен.
    """
    if not is_guide_cryptolink_enabled():
        return None

    if not subscription:
        return None

    crypto_link = getattr(subscription, 'subscription_crypto_link', None)
    if not crypto_link:
        logger.warning(
            'guide_cryptolink_no_crypto_link',
            subscription_id=getattr(subscription, 'id', None),
        )
        return None

    template = settings.get_happ_cryptolink_redirect_template()
    if not template:
        logger.warning(
            'guide_cryptolink_no_redirect_template',
            hint='Задайте HAPP_CRYPTOLINK_REDIRECT_TEMPLATE в .env',
        )
        return None

    return _build_redirect_link(crypto_link, template)


def _build_redirect_link(target_link: str, template: str) -> str | None:
    """Строит редирект-ссылку: подставляет target_link в template.

    Поддерживает плейсхолдеры: {subscription_link}, {link},
    {subscription_link_raw}, {link_raw}.
    Если плейсхолдеров нет — дописывает закодированную ссылку в конец.
    """
    encoded_target = quote(target_link, safe='')
    result = template
    replaced = False

    replacements = [
        ('{subscription_link}', encoded_target),
        ('{link}', encoded_target),
        ('{subscription_link_raw}', target_link),
        ('{link_raw}', target_link),
    ]

    for placeholder, replacement in replacements:
        if placeholder in result:
            result = result.replace(placeholder, replacement)
            replaced = True

    if not replaced:
        result = f'{result}{encoded_target}'

    return result
