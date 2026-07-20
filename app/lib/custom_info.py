"""
Модуль для кастомного режима кнопки "Инфо".

Позволяет заменить стандартное меню раздела «Инфо» на набор
пользовательских кнопок-ссылок, заданных в JSON-файле.

Режимы работы (переменная окружения INFO_BUTTON_MODE):
- "standard" — стандартное поведение (FAQ, правила, оферта и т.д.)
- "custom"   — показывать кнопки из custom_info_buttons.json
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.config import settings

logger = structlog.get_logger(__name__)

# Путь к файлу с кастомными кнопками по умолчанию
DEFAULT_CUSTOM_INFO_PATH: str = "data/custom_info_buttons.json"


# Префикс callback_data для кнопок подменю
SUBMENU_CALLBACK_PREFIX: str = "custom_info_submenu:"


@dataclass
class CustomInfoSubmenu:
    """Подменю — набор кнопок, открываемый по нажатию на кнопку."""

    buttons: list["CustomInfoButton"] = field(default_factory=list)
    """Кнопки внутри подменю."""
    title: str | dict[str, str] | None = None
    """Заголовок подменю (опционально)."""
    prompt: str | dict[str, str] | None = None
    """Подпись под заголовком подменю (опционально)."""


@dataclass
class CustomInfoButton:
    """Одна кастомная кнопка для раздела «Инфо».

    Если type="url" — кнопка-ссылка (требуется url).
    Если type="submenu" — кнопка-меню (требуется submenu).
    """

    text: str | dict[str, str]
    """Текст кнопки. Если dict — {language_code: text}."""
    url: str | None = None
    """URL для type="url"."""
    type: str = "url"
    """Тип кнопки: "url" или "submenu"."""
    submenu: CustomInfoSubmenu | None = None
    """Вложенное подменю для type="submenu"."""


@dataclass
class CustomInfoConfig:
    """Конфигурация кастомного раздела «Инфо»."""

    buttons: list[CustomInfoButton] = field(default_factory=list)
    """Список кастомных кнопок."""

    title: str | dict[str, str] | None = None
    """Заголовок сообщения (опционально). Если None — используется стандартный."""

    prompt: str | dict[str, str] | None = None
    """Подпись под заголовком (опционально)."""


def _parse_button(item: dict[str, Any], index: int = 0) -> CustomInfoButton | None:
    """Распарсить одну кнопку из JSON-словаря.

    Поддерживает два типа:
      - {"text": ..., "url": "https://..."} — type="url"
      - {"text": ..., "type": "submenu", "submenu": {...}} — type="submenu"
    """
    text = item.get("text", "Кнопка")
    btn_type = item.get("type", "url")

    if btn_type == "submenu":
        submenu_data = item.get("submenu")
        if not submenu_data:
            logger.warning("custom_info_submenu_missing_data", index=index)
            return None

        raw_buttons = submenu_data.get("buttons", [])
        parsed_buttons: list[CustomInfoButton] = []
        for si, sub_item in enumerate(raw_buttons):
            sub_text = sub_item.get("text", "Кнопка")
            sub_url = sub_item.get("url", "")
            if sub_url:
                parsed_buttons.append(CustomInfoButton(text=sub_text, url=sub_url))

        submenu = CustomInfoSubmenu(
            buttons=parsed_buttons,
            title=submenu_data.get("title"),
            prompt=submenu_data.get("prompt"),
        )
        return CustomInfoButton(text=text, type="submenu", submenu=submenu)

    # По умолчанию — url-кнопка
    url = item.get("url", "")
    if not url:
        return None
    return CustomInfoButton(text=text, url=url)


def get_custom_info_path() -> str:
    """Вернуть путь к файлу с кастомными кнопками.

    Берётся из settings.CUSTOM_INFO_BUTTONS_PATH (если задано),
    иначе — DEFAULT_CUSTOM_INFO_PATH.
    """
    custom_path: str | None = getattr(settings, "CUSTOM_INFO_BUTTONS_PATH", None)
    if custom_path:
        return custom_path
    return DEFAULT_CUSTOM_INFO_PATH


def is_custom_info_mode() -> bool:
    """Проверить, включён ли кастомный режим кнопки «Инфо»."""
    mode: str = getattr(settings, "INFO_BUTTON_MODE", "standard")
    return mode.strip().lower() == "custom"


def _resolve_text(
    text: str | dict[str, str],
    language: str,
    fallback: str = "",
) -> str:
    """Извлечь текст с учётом языка.

    Если text — строка, возвращается как есть.
    Если text — dict, ищется ключ language, затем ключ 'ru', затем первый попавшийся.
    """
    if isinstance(text, str):
        return text
    if isinstance(text, dict):
        # Прямое совпадение языка
        if language in text:
            return text[language]
        # Русский как fallback
        if "ru" in text:
            return text["ru"]
        # Первый попавшийся
        for val in text.values():
            if isinstance(val, str):
                return val
    return fallback


def load_custom_info_config(path: str | None = None) -> CustomInfoConfig:
    """Загрузить конфигурацию кастомных кнопок из JSON-файла.

    Args:
        path: Путь к JSON-файлу. Если None — используется путь по умолчанию.

    Returns:
        CustomInfoConfig с загруженными данными.

    Формат JSON-файла:
    .. code-block:: json

        {
            "title": {"ru": "ℹ️ Информация", "en": "ℹ️ Information"},
            "prompt": {"ru": "Полезные ссылки:", "en": "Useful links:"},
            "buttons": [
                {
                    "text": {"ru": "📘 Документация", "en": "📘 Docs"},
                    "url": "https://docs.example.com"
                },
                {
                    "text": "📊 Статус серверов",
                    "url": "https://stats.example.com"
                }
            ]
        }

    Упрощённый формат (только массив кнопок):
    .. code-block:: json

        [
            {"text": "📘 Документация", "url": "https://docs.example.com"},
            {"text": "📊 Статус серверов", "url": "https://stats.example.com"}
        ]
    """
    file_path = path or get_custom_info_path()
    config = CustomInfoConfig()

    try:
        resolved_path = _resolve_path(file_path)
        if not resolved_path.exists():
            logger.warning("custom_info_file_not_found", path=str(resolved_path))
            return config

        raw = resolved_path.read_text(encoding="utf-8")
        data: Any = json.loads(raw)

        if isinstance(data, list):
            # Упрощённый формат — просто массив кнопок
            for i, item in enumerate(data):
                btn = _parse_button(item, index=i)
                if btn:
                    config.buttons.append(btn)

        elif isinstance(data, dict):
            # Расширенный формат — объект с title/prompt/buttons
            config.title = data.get("title")
            config.prompt = data.get("prompt")

            for i, item in enumerate(data.get("buttons", [])):
                btn = _parse_button(item, index=i)
                if btn:
                    config.buttons.append(btn)

        logger.info(
            "custom_info_loaded",
            path=str(resolved_path),
            button_count=len(config.buttons),
        )

    except json.JSONDecodeError as exc:
        logger.error("custom_info_json_error", path=str(file_path), error=str(exc))
    except OSError as exc:
        logger.error("custom_info_read_error", path=str(file_path), error=str(exc))

    return config


def _resolve_path(path: str) -> Path:
    """Преобразовать путь в абсолютный Path.

    Если путь относительный — считается от корня проекта (рядом с main.py).
    """
    p = Path(path)
    if p.is_absolute():
        return p
    # Относительно корня проекта (папка, где лежит main.py)
    return Path(os.getcwd()) / p


def build_custom_info_keyboard(
    config: CustomInfoConfig,
    language: str = "ru",
    back_callback: str = "back_to_menu",
) -> InlineKeyboardMarkup:
    """Сформировать InlineKeyboardMarkup из кастомных кнопок.

    Для type="url" — кнопка-ссылка (url).
    Для type="submenu" — кнопка с callback_data, открывающая подменю.

    Args:
        config: Загруженная конфигурация кастомных кнопок.
        language: Код языка для отображения текста.
        back_callback: callback_data для кнопки «Назад».

    Returns:
        InlineKeyboardMarkup с кнопками.
    """
    from app.localization.texts import get_texts

    texts = get_texts(language)
    rows: list[list[InlineKeyboardButton]] = []

    for idx, btn in enumerate(config.buttons):
        label = _resolve_text(btn.text, language, fallback="Кнопка")

        if btn.type == "submenu":
            callback = f"{SUBMENU_CALLBACK_PREFIX}{idx}"
            rows.append([InlineKeyboardButton(text=label, callback_data=callback)])
        else:
            url = btn.url or ""
            rows.append([InlineKeyboardButton(text=label, url=url)])

    # Кнопка «Назад»
    rows.append(
        [
            InlineKeyboardButton(
                text=texts.BACK,
                callback_data=back_callback,
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_submenu_keyboard(
    submenu: CustomInfoSubmenu,
    language: str = "ru",
    back_callback: str = "back_to_custom_info_root",
) -> InlineKeyboardMarkup:
    """Сформировать клавиатуру для подменю.

    Кнопки внутри подменю — всегда url-ссылки.

    Args:
        submenu: Подменю с кнопками.
        language: Код языка.
        back_callback: callback_data для кнопки «Назад» (на корень Info).

    Returns:
        InlineKeyboardMarkup с кнопками подменю.
    """
    from app.localization.texts import get_texts

    texts = get_texts(language)
    rows: list[list[InlineKeyboardButton]] = []

    for btn in submenu.buttons:
        label = _resolve_text(btn.text, language, fallback="Кнопка")
        url = btn.url or ""
        rows.append([InlineKeyboardButton(text=label, url=url)])

    # Кнопка «Назад» — возвращает в корень кастомного Info
    rows.append(
        [
            InlineKeyboardButton(
                text=texts.BACK,
                callback_data=back_callback,
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_submenu_by_index(config: CustomInfoConfig, index: int) -> CustomInfoSubmenu | None:
    """Получить подменю по индексу кнопки в корневом списке."""
    if index < 0 or index >= len(config.buttons):
        return None
    btn = config.buttons[index]
    if btn.type != "submenu":
        return None
    return btn.submenu


def get_custom_info_title(config: CustomInfoConfig, language: str) -> str | None:
    """Вернуть заголовок для кастомного режима с учётом локализации."""
    if config.title is None:
        return None
    return _resolve_text(config.title, language)


def get_custom_info_prompt(config: CustomInfoConfig, language: str) -> str | None:
    """Вернуть подпись для кастомного режима с учётом локализации."""
    if config.prompt is None:
        return None
    return _resolve_text(config.prompt, language)


def get_submenu_title(submenu: CustomInfoSubmenu, language: str) -> str | None:
    """Вернуть заголовок подменю с учётом локализации."""
    if submenu.title is None:
        return None
    return _resolve_text(submenu.title, language)


def get_submenu_prompt(submenu: CustomInfoSubmenu, language: str) -> str | None:
    """Вернуть подпись подменю с учётом локализации."""
    if submenu.prompt is None:
        return None
    return _resolve_text(submenu.prompt, language)
