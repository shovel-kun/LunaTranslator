> A Visual Novel Translator

LunaTranslator is an open-source x86/x64 video game text hooker for Vista/Windows 7+/WINE based on [Textractor](https://github.com/Artikash/Textractor). It's an all-in-one solution for translating text from visual novels (galgames) and other games (like RPGMaker), with additional goodies like Text-To-Speech, Furigana Display, Anki Integration, and more.

## Features

### Text Sources

LunaTranslator supports multiple methods for extracting text from games:

1. **Clipboard**: 
   - Reads text from the clipboard for translation.

2. **OCR (Optical Character Recognition)**:
   - **Offline OCR**: Works without an internet connection.
   - **Online OCR**: Supports WindowsOCR, Baidu OCR, Youdao OCR, ocrspace, and docsumo.
   - **Game Window Binding**: Binds OCR to the game window to avoid overlap with game content.

3. **Text Hooking**:
   - Extracts text directly from the game using hooks.
   - Supports Hook codes (H-codes) for specific games.
   - Automatically saves and loads game and hook settings.
   - Some game engines support embedded translation.

### 2. Translation Services
LunaTranslator supports a wide range of translation engines:

1. **Offline Translation**:
   - J-Beijing 7, Kingsoft FastAIT, YiDianTong, Sakura, TGW, Sugoi.

2. **Free Online Translation**:
   - Google, DeepL, Bing, Baidu, Ali, Youdao, Caiyun, Sogou, Kingsoft, iFlytek, Tencent, ByteDance, Volcano, Papago, Yeekit, and more.

3. **API Online Translation** (requires user registration):
   - Google, DeepL, Azure, ChatGPT, Claude, Gemini, Baidu, Tencent, Youdao, Niutrans, Caiyun, Volcano, Yandex, IBM, Feishu, Cohere, and more.

4. **Chrome Debug Translation**:
   - Google, DeepL, Yandex, Youdao, Baidu, Tencent, Bing, Caiyun, Niutrans, Ali, OpenAI.

5. **Pre-translation**:
   - Supports using pre-translated game files as a translation source.

6. **Custom Translation Extension**:
   - Your preferred translation engine not here? You can extend it yourself with Python 

### 3. Text-to-Speech (TTS)

Bring characters to life with various TTS options:

- **Offline TTS**: Windows TTS, VoiceRoid2, VOICEVOX, VITS, and more
- **Online TTS**: Edge TTS, Google TTS, Youdao TTS, and others

### 4. Translation Enhancement

Improve quality of translations with various tools:

- **Text Processing**: 
  - Over a dozen text processing methods, from simple tasks like text de-duplication and filtering line breaks to complex regular expression replacements
  - You can also write your own Python preprocessors
- **Optimization**: 
  - Custom proper noun translations
  - VNR shared dictionary import

### 5. Japanese Language Learning Tools

LunaTranslator includes tools for Japanese learners:

- **Word Segmentation and Furigana Display**: 
  - Supports MeCab and other tokenizers.
- **Dictionary Lookup**: 
  - Supports various online and offline dictionaries such as MDICT, Shogakukan, Lingoes, EDICT, Youdao, Weblio, Goo, Moji, Jisho, and more.
- **Anki Flashcard Integration**: 
  - Easily add new vocabulary to your Anki decks for efficient learning



