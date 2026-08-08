import langcodes
import streamlit as st
from deep_translator import GoogleTranslator

from langdetect import DetectorFactory, LangDetectException, detect

from nltk.tokenize import TreebankWordDetokenizer, wordpunct_tokenize

from spellchecker import SpellChecker

DetectorFactory.seed = 0
MIN_INPUT_LENGTH = 3

#pyspellchecker only supports some languages
SPELL_LANGS = {"en", "es", "fr", "pt", "de","ru","ar","eu","lv","nl"}

#target language for App 1
TARGET_LANGS = {
    "Vietnamese": "vi",
    'English': 'en',
    'French': 'fr',
    'Japanese': 'ja',
    'Chinese (simplified)': 'zh-CN',
    'Korean': 'ko',
    'Spanish': 'es',
    'German': 'de'
}

EXAMPLES_T = [
    "Every morning, I drink a cup of coffee.", 
    "Bonjour, comment allez-vous?",
    "Xin chào, hôm nay trời đẹp quá."
]

EXAMPLES_S = [
    "Yeasterday, I received a mesage from my freind.",
    "Definately a great oppurtunity.",
    "Je voudraiis allerr au marchee."
]

#--------------Helpers----------------

@st.cache_resource(show_spinner=False)

def get_spellchecker(code):
    return SpellChecker(language=code)

def language_name(code):
    try:
        return langcodes.Language.get(code).display_name()
    except Exception:
        return code or "Unknown"

def detect_language(raw):
    try:
        return detect(raw)
    except LangDetectException:
        return None

def fix_typos(text,code):
    spell = get_spellchecker(code) #load model fix bug for code language
    tokens = wordpunct_tokenize(text) #split sentence into words "hello world" => [hello, world]
    fixed = []

    for token in tokens:
        if token.isalpha() and len(token) > 1:
            suggestion = spell.correction(token.lower()) or token 
            # fix bug
            # get the right original format: Uppercase or Not
            suggestion = suggestion.title() if token.istitle() else suggestion
            suggestion = suggestion.upper() if token.isupper() else suggestion
            fixed.append(suggestion)
        else:
            #12$
            fixed.append(token)

        return TreebankWordDetokenizer().detokenize(fixed), fixed != tokens 
        # nối list từ => từ
        # " ".join(words)

def run_translation(text, target_code):
    raw = text.strip()
    if len(raw) < MIN_INPUT_LENGTH:
        return {"ok": False, 
                "error": f"Insert minimum {MIN_INPUT_LENGTH} characters."}

    source = detect_language(raw)
    if source is None:
        return {"ok": False, 
                "error": "Cannot identify the language!"}

    if source == target_code:
        return {
            "ok":True,
            "source": language_name(source),
            "target": language_name(target_code),
            "translated": raw,
            "note":"Sentence is currently in the target language, therefore does not need to be translated"
        }

    try:
        translated = GoogleTranslator(source = source, target = target_code).translate(raw)
    except Exception as e:
        return {"ok":False,
                "error":f"Translation Error: {e}"}
    return {
        "ok": True,
        "source":language_name(source),
        "target":language_name(target_code),
        "translated":translated
    }

def run_spellcheck(text):
    raw = text.strip()
    if len(raw) < MIN_INPUT_LENGTH:
        return {"ok": False,
                "error":f"Please input minimum {MIN_INPUT_LENGTH} characters."}

    code = detect_language(raw)
    if code is None:
        return {"ok": False,
                "error":"Cannot identify the language."}

    if code not in SPELL_LANGS:
        return {
            "ok": False,
            "error":f"pyspellcheck has not support this {language_name(code)} ({code})."
        }

    fixed, changed = fix_typos(raw,code)
    return {
        "ok":True,
        "language":language_name(code),
        "fixed":fixed,
        "changed":changed
    }

st.title("Streamlit NLP App")
st.caption("2 Apps: Translate text and Fix spelling typos")
tab_t, tab_s = st.tabs(["Translate text", "Fix spelling typos"])

with tab_t:
    st.session_state.setdefault("res_t", None)

    with st.expander("For example"):
        for ex in EXAMPLES_T:
            st.markdown(f"-{ex}")

    with st.form("form_translate"):
        text_t = st.text_area("Sentence that needs to be translated", height=90,
                              placeholder="Insert the sentence in any languages...")
        target = st.selectbox("Translate to", list(TARGET_LANGS.keys()))
        submitted_t = st.form_submit_button("Translate", type = "primary")

    if submitted_t:
        st.session_state.res_t = run_translation(text_t,TARGET_LANGS[target])

    res = st.session_state.res_t
    if res:
        if res["ok"]:
            st.caption(f"Source: {res['source']} -> Target: {res['target']}")
            st.success(res['translated'])
            if res.get('note'):
                st.info(res['note'])
            else:
                st.warning(res["error"])

with tab_s:
    st.session_state.setdefault('res_s', None)

    with st.expander("For example"):
        for ex in EXAMPLES_S:
            st.markdown(f"-{ex}")
    st.caption(f"Support: {', '.join(sorted(SPELL_LANGS))}")

    with st.form('form_spell'):
        text_s = st.text_area("Sentence that needs to be checked", height=90, placeholder="Insert sentence that needs to be spell-checked...")

        submitted_s = st.form_submit_button("Check", type="primary")

    if submitted_s:
        st.session_state.res_s = run_spellcheck(text_s)

    res = st.session_state.res_s

    if res: 
        if res["ok"]:
            st.caption(f"Language: {res['language']}")
            st.success(res['fixed'])
            st.caption("Fixed spelling typos" if res['changed'] else "Does not identify any spelling typos")

        else:
            st.warning(res["error"])