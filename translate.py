from deep_translator import GoogleTranslator

def translate_text(text: str, target_lang: str) -> str:
    try:
        return GoogleTranslator(source='auto', target=target_lang.lower()).translate(text)
    except Exception:
        return text  
