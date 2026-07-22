"""
Middleware для определения раздела бота из callback_data / команды.

Устанавливает контекстную переменную _current_section перед вызовом
хендлера, чтобы патчи Message.answer / Message.edit_text и
edit_or_answer_photo могли использовать фото, соответствующее разделу.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

import structlog
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.utils.message_patch import _current_section
from app.utils.section_photos import get_section_from_callback, get_section_from_command


logger = structlog.get_logger(__name__)


class SectionPhotoMiddleware(BaseMiddleware):
    """Определяет раздел бота по callback_data или команде и сохраняет
    его в контекстной переменной _current_section.

    Работает только при ENABLE_SECTION_PHOTOS=true.
    При выключенном режиме проходит без изменений.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from app.config import settings

        section: str | None = None

        if isinstance(event, CallbackQuery) and event.data:
            section = get_section_from_callback(event.data)
            if section:
                logger.debug('Section determined from callback', section=section, callback_data=event.data)

        elif isinstance(event, Message) and event.text:
            section = get_section_from_command(event.text)
            if section:
                logger.debug('Section determined from command', section=section, command=event.text)

        if section:
            token = _current_section.set(section)
            try:
                return await handler(event, data)
            finally:
                _current_section.reset(token)
        else:
            return await handler(event, data)
