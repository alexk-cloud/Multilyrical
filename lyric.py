def translate(text: str | list[str], 
            orig_lang: str | None = None, 
            target_lang: str = "en"
            ) -> dict:
    
    from google.cloud import translate_v2 as translate

    tr = translate.Client()

    if isinstance(text, str):
        text = [text]

    results = tr.translate(
        values=text,
        target_language=target_lang,
        source_language=orig_lang
    )

    for result in results:
        if "detectedSourceLanguage" in result:
            print(f"\nDetected source language: {result['detectedSourceLanguage']}")
        else:
            print("\nCould not detect source language.")

        print(f"Input text: {result['input']}")
        print(f"Translated text: {result['translatedText']}\n")

    return results