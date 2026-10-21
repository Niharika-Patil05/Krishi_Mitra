"""Every piece of interface text, in the three supported languages (keyed by Sarvam language code).

Keeping it here means app.py has no hard-coded strings and adding a language is one new block.
"""
from src import config

TEXT = {
    "mr-IN": {
        "title": "कृषी मित्र",
        "kicker": "ICAR · MPKV · PM-KISAN स्रोतांवर आधारित",
        "sub": "ऊस, द्राक्ष आणि हळद यांबद्दल प्रश्न विचारा. उत्तर मराठीत, पान क्रमांकासह स्रोत दाखवून.",
        "settings": "सेटिंग्ज", "answer_lang": "उत्तराची भाषा", "crop": "पीक",
        "tab_type": "लिहा", "tab_speak": "बोला",
        "placeholder": "उदा. हळदीवरील कंदकुज रोग कसा टाळावा?",
        "speak_label": "प्रश्न बोला", "speak_hint": "रेकॉर्ड थांबवल्यावर खालील बटण दाबा.",
        "ask": "उत्तर मिळवा", "try": "उदाहरणे",
        "listening": "आवाज ऐकत आहे...", "searching": "उत्तर शोधत आहे...", "loading": "माहिती भांडार लोड होत आहे...",
        "heard": "तुम्ही म्हणालात", "cached": "जतन केलेले उत्तर (ऑफलाइन)", "sec": "से.",
        "sources": "स्रोत", "page": "पान",
        "err_empty": "कृपया प्रश्न लिहा किंवा बोला.",
        "err_busy": "सेवा सध्या उपलब्ध नाही, कृपया थोड्या वेळाने प्रयत्न करा.",
        "err_index": "माहिती भांडार सापडले नाही. आधी `python -m src.ingest` चालवा.",
        "about": "माहिती आणि मर्यादा",
        "about_points": [
            "उत्तरे फक्त ICAR, कृषी विद्यापीठे आणि सरकारी दस्तऐवजांतून येतात.",
            "माहिती स्रोतांत नसेल तर अॅप तसे सांगते; अंदाज लावत नाही.",
            "तुमचा आवाज लिप्यंतरणासाठी Sarvam AI कडे जातो; हे अॅप काहीही साठवत नाही.",
            "बोली भाषा किंवा गोंगाटामुळे आवाज ओळखण्यात चुका होऊ शकतात.",
            "कृषी अधिकारी किंवा KVK चा सल्ला याला पर्याय नाही."],
        "kcc": "किसान कॉल सेंटर",
        "crops": {"all": "सर्व पिके", "sugarcane": "ऊस", "grapes": "द्राक्ष", "turmeric": "हळद", "scheme": "सरकारी योजना"},
    },
    "hi-IN": {
        "title": "कृषि मित्र",
        "kicker": "ICAR · MPKV · PM-KISAN स्रोतों पर आधारित",
        "sub": "गन्ना, अंगूर और हल्दी के बारे में सवाल पूछें। जवाब हिंदी में, पेज नंबर के साथ स्रोत दिखाकर।",
        "settings": "सेटिंग्स", "answer_lang": "उत्तर की भाषा", "crop": "फसल",
        "tab_type": "लिखें", "tab_speak": "बोलें",
        "placeholder": "जैसे: हल्दी में कंद सड़न रोग से कैसे बचें?",
        "speak_label": "सवाल बोलें", "speak_hint": "रिकॉर्डिंग रोकने के बाद नीचे का बटन दबाएँ।",
        "ask": "जवाब पाएँ", "try": "उदाहरण",
        "listening": "आवाज़ सुन रहे हैं...", "searching": "जवाब खोज रहे हैं...", "loading": "जानकारी भंडार लोड हो रहा है...",
        "heard": "आपने कहा", "cached": "सहेजा हुआ जवाब (ऑफ़लाइन)", "sec": "सेकंड",
        "sources": "स्रोत", "page": "पेज",
        "err_empty": "कृपया सवाल लिखें या बोलें।",
        "err_busy": "सेवा अभी उपलब्ध नहीं है, कृपया थोड़ी देर बाद कोशिश करें।",
        "err_index": "जानकारी भंडार नहीं मिला। पहले `python -m src.ingest` चलाएँ।",
        "about": "जानकारी और सीमाएँ",
        "about_points": [
            "जवाब सिर्फ़ ICAR, कृषि विश्वविद्यालयों और सरकारी दस्तावेज़ों से आते हैं।",
            "जानकारी स्रोतों में न हो तो ऐप यह बता देता है; अंदाज़ा नहीं लगाता।",
            "आपकी आवाज़ लिखित रूप में बदलने के लिए Sarvam AI को जाती है; यह ऐप कुछ भी सहेजता नहीं।",
            "बोली या शोर की वजह से आवाज़ पहचानने में गलतियाँ हो सकती हैं।",
            "यह कृषि अधिकारी या KVK की सलाह का विकल्प नहीं है।"],
        "kcc": "किसान कॉल सेंटर",
        "crops": {"all": "सभी फसलें", "sugarcane": "गन्ना", "grapes": "अंगूर", "turmeric": "हल्दी", "scheme": "सरकारी योजनाएँ"},
    },
    "en-IN": {
        "title": "Krishi Mitra",
        "kicker": "Based on ICAR · MPKV · PM-KISAN sources",
        "sub": "Ask about sugarcane, grapes and turmeric. Answers come with the source document and page number.",
        "settings": "Settings", "answer_lang": "Answer language", "crop": "Crop",
        "tab_type": "Type", "tab_speak": "Speak",
        "placeholder": "e.g. How can I prevent rhizome rot in turmeric?",
        "speak_label": "Speak your question", "speak_hint": "Press the button below after you stop recording.",
        "ask": "Get answer", "try": "Try asking",
        "listening": "Listening...", "searching": "Searching for the answer...", "loading": "Loading the knowledge base...",
        "heard": "You said", "cached": "Saved answer (offline)", "sec": "s",
        "sources": "Sources", "page": "page",
        "err_empty": "Please type or speak a question.",
        "err_busy": "The service is busy right now, please try again shortly.",
        "err_index": "Knowledge base not found. Run `python -m src.ingest` first.",
        "about": "About & limitations",
        "about_points": [
            "Answers come only from ICAR, agricultural university and government documents.",
            "If the answer is not in them, the app says so; it does not guess.",
            "Your voice is sent to Sarvam AI for transcription; this app stores nothing.",
            "Dialects or background noise can cause speech-recognition mistakes.",
            "This is not a replacement for your agriculture officer or KVK."],
        "kcc": "Kisan Call Centre",
        "crops": {"all": "All crops", "sugarcane": "Sugarcane", "grapes": "Grapes", "turmeric": "Turmeric", "scheme": "Government schemes"},
    },
}

# Example questions per language (same topics, same order, so a language switch maps 1:1).
EXAMPLES = {
    "mr-IN": ["द्राक्षावरील भुरी रोगासाठी काय उपाय करावा?", "हळदीची लागवड कधी करावी?",
              "पीएम-किसान योजनेत किती रक्कम मिळते?", "हळदीवरील कंदकुज रोग कसा टाळावा?",
              "कोल्हापूर भागात ऊस लागवड कोणत्या महिन्यात करावी?", "हळदीच्या सुधारित जाती कोणत्या आहेत?"],
    "hi-IN": ["अंगूर में भुरी (पाउडरी मिल्ड्यू) रोग का उपाय क्या है?", "हल्दी की बुवाई कब करनी चाहिए?",
              "पीएम-किसान योजना में कितनी राशि मिलती है?", "हल्दी में कंद सड़न रोग से कैसे बचें?",
              "कोल्हापुर क्षेत्र में गन्ने की बुवाई किस महीने में करें?", "हल्दी की उन्नत किस्में कौन सी हैं?"],
    "en-IN": ["How do I control powdery mildew in grapes?", "When should turmeric be planted?",
              "How much money does PM-KISAN give?", "How can I prevent rhizome rot in turmeric?",
              "In which month should sugarcane be planted around Kolhapur?", "What are the improved turmeric varieties?"],
}

CROP_KEYS = ["all", "sugarcane", "grapes", "turmeric", "scheme"]
DEFAULT_CODE = config.LANGUAGES[config.DEFAULT_LANGUAGE]


# Document title + publisher per language, keyed by the PDF filename in sources.csv.
SOURCE_NAMES = {
    "GAPTableGrapes.pdf": {
        "mr-IN": ("टेबल द्राक्षांच्या दर्जेदार उत्पादनासाठी उत्तम कृषी पद्धती", "ICAR-राष्ट्रीय द्राक्ष संशोधन केंद्र, पुणे"),
        "hi-IN": ("टेबल अंगूर के गुणवत्तापूर्ण उत्पादन के लिए उत्तम कृषि पद्धतियाँ", "ICAR-राष्ट्रीय अंगूर अनुसंधान केंद्र, पुणे"),
    },
    "ipm_pop_turmeric.pdf": {
        "mr-IN": ("हळदीसाठी एकात्मिक कीड व्यवस्थापन (IPM) पद्धती", "वनस्पती संरक्षण, संगरोध व संचयन संचालनालय (भारत सरकार)"),
        "hi-IN": ("हल्दी के लिए एकीकृत कीट प्रबंधन (IPM) पद्धतियाँ", "पौध संरक्षण, संगरोध एवं संग्रह निदेशालय (भारत सरकार)"),
    },
    "mpkv_spices_varieties.pdf": {
        "mr-IN": ("मसाला पिकांच्या सुधारित जाती", "महात्मा फुले कृषी विद्यापीठ, राहुरी"),
        "hi-IN": ("मसाला फसलों की उन्नत किस्में", "महात्मा फुले कृषि विद्यापीठ, राहुरी"),
    },
    "pmkisan_guidelines.pdf": {
        "mr-IN": ("पीएम-किसान योजना कार्यान्वयन मार्गदर्शक सूचना", "कृषी व शेतकरी कल्याण मंत्रालय"),
        "hi-IN": ("पीएम-किसान योजना परिचालन दिशानिर्देश", "कृषि एवं किसान कल्याण मंत्रालय"),
    },
    "aicrp_sugarcane_kolhapur.pdf": {
        "mr-IN": ("अखिल भारतीय समन्वित ऊस संशोधन प्रकल्प, प्रादेशिक ऊस व गूळ संशोधन केंद्र, कोल्हापूर", "महात्मा फुले कृषी विद्यापीठ, राहुरी"),
        "hi-IN": ("अखिल भारतीय समन्वित गन्ना अनुसंधान परियोजना, क्षेत्रीय गन्ना एवं गुड़ अनुसंधान केंद्र, कोल्हापुर", "महात्मा फुले कृषि विद्यापीठ, राहुरी"),
    },
}


def source_name(src: dict, lang_code: str) -> tuple[str, str]:
    """(title, publisher) of a source chunk in the UI language; English falls back to sources.csv."""
    return SOURCE_NAMES.get(src["file"], {}).get(lang_code, (src["title"], src["publisher"]))
