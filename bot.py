import os
import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from currency import CurrencyConverter, CURRENCIES

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация
converter = CurrencyConverter()

# Получение настроек из переменных окружения
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'EUR').upper()

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен. Укажите его в переменных окружения.")

if DEFAULT_CURRENCY not in CURRENCIES:
    raise ValueError(f"DEFAULT_CURRENCY '{DEFAULT_CURRENCY}' не поддерживается. Доступные: {', '.join(CURRENCIES.keys())}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        f"Привет! 👋\n\n"
        f"Валюта по умолчанию: *{DEFAULT_CURRENCY}* {CURRENCIES[DEFAULT_CURRENCY]}\n\n"
        f"Просто отправьте число для конвертации или число с кодом валюты (например, `100 EUR`).",
        parse_mode='Markdown'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений с числами"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Парсинг сообщения: "число" или "число ВАЛЮТА"
    pattern = r'^\s*([\d.,]+)\s*([A-Z]{3})?\s*$'
    match = re.match(pattern, text, re.IGNORECASE)
    
    if not match:
        await update.message.reply_text(
            "❌ Неверный формат. Отправьте число или число с кодом валюты.\n"
            "Например: `100` или `100 EUR`",
            parse_mode='Markdown'
        )
        return
    
    # Получаем сумму и валюту
    amount_str = match.group(1).replace(',', '.')
    currency_code = match.group(2)
    
    try:
        amount = float(amount_str)
    except ValueError:
        await update.message.reply_text("❌ Неверное число. Попробуйте еще раз.")
        return
    
    if amount <= 0:
        await update.message.reply_text("❌ Сумма должна быть больше нуля.")
        return
    
    # Определяем исходную валюту
    if currency_code:
        currency_code = currency_code.upper()
        if currency_code not in CURRENCIES:
            await update.message.reply_text(
                f"❌ Неподдерживаемая валюта: {currency_code}\n\n"
                f"Доступные валюты: {', '.join(CURRENCIES.keys())}"
            )
            return
        source_currency = currency_code
    else:
        source_currency = DEFAULT_CURRENCY
    
    # Выполняем конвертацию
    try:
        results = converter.convert_to_all(amount, source_currency)
        formatted_results = converter.format_results(results, amount, source_currency)
        
        await update.message.reply_text(formatted_results, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка конвертации: {e}")
        await update.message.reply_text("❌ Произошла ошибка при конвертации. Попробуйте позже.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления: {context.error}")


def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
