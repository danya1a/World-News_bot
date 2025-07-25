from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from parser import get_news_by_country
from translate import translate_text
import config

LANG_CHOICES = {
    "EN": "English",
    "UA": "Українська",
    "RU": "Русский"
}

COUNTRY_TRANSLATIONS = {
    "EN": {"Ukraine": "Ukraine", "USA": "USA", "UK": "UK", "Germany": "Germany", "Poland": "Poland", "China": "China"},
    "UA": {"Ukraine": "Україна", "USA": "США", "UK": "Велика Британія", "Germany": "Німеччина", "Poland": "Польща", "China": "Китай"},
    "RU": {"Ukraine": "Украина", "USA": "США", "UK": "Великобритания", "Germany": "Германия", "Poland": "Польша", "China": "Китай"}
}

user_language = {}
user_last_country = {}

def detect_telegram_lang(telegram_lang_code):
    if telegram_lang_code.startswith("uk"):
        return "UA"
    elif telegram_lang_code.startswith("ru"):
        return "RU"
    else:
        return "EN"

async def show_language_menu(chat_id, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("English", callback_data="lang_EN")],
        [InlineKeyboardButton("Українська", callback_data="lang_UA")],
        [InlineKeyboardButton("Русский", callback_data="lang_RU")]
    ]
    await context.bot.send_message(
        chat_id=chat_id,
        text="Please choose a language / Оберіть мову / Выберите язык:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tg_lang = update.effective_user.language_code or "en"
    user_language[user_id] = detect_telegram_lang(tg_lang)
    await show_language_menu(update.effective_chat.id, context)

async def start_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    tg_lang = query.from_user.language_code or "en"
    user_language[user_id] = detect_telegram_lang(tg_lang)
    await show_language_menu(query.message.chat_id, context)

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    user_language[query.from_user.id] = lang
    await show_country_menu(query, lang)

async def show_country_menu(query, lang):
    country_buttons = [
        [InlineKeyboardButton(name, callback_data=f"country_{key}")]
        for key, name in COUNTRY_TRANSLATIONS[lang].items()
    ]
    country_buttons.append([InlineKeyboardButton({"EN": "❌ Exit", "UA": "❌ Вийти", "RU": "❌ Выход"}[lang], callback_data="exit")])
    await query.edit_message_text(
        text={"EN": "Select a country:", "UA": "Оберіть країну:", "RU": "Выберите страну:"}[lang],
        reply_markup=InlineKeyboardMarkup(country_buttons)
    )

async def send_news(query, user_id, lang, country):
    country_name = COUNTRY_TRANSLATIONS[lang][country]
    loading_text = {
        "EN": f"Fetching news from {country_name}...",
        "UA": f"Отримання новин з {country_name}...",
        "RU": f"Получаю новости из {country_name}..."
    }[lang]

    await query.edit_message_text(loading_text)

    news = get_news_by_country(country)
    translated_news = translate_text(news, lang)

    for i in range(0, len(translated_news), 4000):
        await query.message.reply_text(translated_news[i:i + 4000])

    keyboard = [
        [InlineKeyboardButton({"EN": "🔙 Back", "UA": "🔙 Назад", "RU": "🔙 Назад"}[lang], callback_data="back_to_countries")],
        [InlineKeyboardButton({"EN": "🔄 Refresh", "UA": "🔄 Оновити", "RU": "🔄 Обновить"}[lang], callback_data="refresh_news")],
        [InlineKeyboardButton({"EN": "❌ Exit", "UA": "❌ Вийти", "RU": "❌ Выход"}[lang], callback_data="exit")]
    ]

    await query.message.reply_text(
        {"EN": "Choose an action:", "UA": "Оберіть дію:", "RU": "Выберите действие:"}[lang],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_language.get(user_id, "EN")
    country = query.data.split("_")[1]
    user_last_country[user_id] = country
    await send_news(query, user_id, lang, country)

async def handle_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_language.get(user_id, "EN")
    country = user_last_country.get(user_id)

    if country:
        await send_news(query, user_id, lang, country)
    else:
        await query.edit_message_text("⚠️ No country selected yet.")

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_language.get(user_id, "EN")
    await show_country_menu(query, lang)

async def handle_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_language.get(user_id, "EN")
    goodbye_text = {"EN": "Goodbye! 👋", "UA": "До побачення! 👋", "RU": "До свидания! 👋"}[lang]
    restart_button = InlineKeyboardMarkup([
        [InlineKeyboardButton({"EN": "🔄 Start Again", "UA": "🔄 Почати знову", "RU": "🔄 Начать сначала"}[lang], callback_data="start_again")]
    ])
    await query.message.reply_text(goodbye_text, reply_markup=restart_button)

def main():
    app = ApplicationBuilder().token(config.TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(country_selected, pattern="^country_"))
    app.add_handler(CallbackQueryHandler(handle_back, pattern="^back_to_countries$"))
    app.add_handler(CallbackQueryHandler(handle_exit, pattern="^exit$"))
    app.add_handler(CallbackQueryHandler(start_again, pattern="^start_again$"))
    app.add_handler(CallbackQueryHandler(handle_refresh, pattern="^refresh_news$"))
    app.run_polling()

if __name__ == "__main__":
    main()
