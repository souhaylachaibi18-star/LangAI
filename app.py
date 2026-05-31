import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import urllib.parse
import json
import urllib.request

# ============================================
# 1. إعدادات الصفحة الأساسية
# ============================================
st.set_page_config(
    page_title="LangAI",
    page_icon="🇨🇳",
    layout="wide"
)

# ============================================
# 2. دالة الذكاء الاصطناعي المعزولة والمطورة (تم تحديث منطق اللغات هنا ✨)
# ============================================
def ask_ai_about_word(word, pinyin, arabic, ui_lang):
    try:
        if ui_lang == "العربية":
            instruction = (
                f"اشرح الكلمة الصينية {word} ذات النطق {pinyin} والمعنى {arabic}. "
                "أعطني الإجابة في 4 أسطر نصية عادية ومباشرة جداً بدون أي مقدمات أو نجوم أو علامات اقتباس أو أكواد:\n"
                "السطر الأول: نوع الكلمة فقط\n"
                "السطر الثاني: شرح مبسط ومفهوم لطريقة استخدام هذه الكلمة باللغة العربية\n"
                "السطر الثالث: جملة صينية جديدة تماماً كمثال إضافي\n"
                "السطر الرابع: ترجمة الجملة الصينية الجديدة (السطر الثالث) إلى اللغة العربية حتماً ولزاماً"
            )
        elif ui_lang == "English":
            instruction = (
                f"Explain the Chinese word {word} ({pinyin}) which means {arabic}. "
                "Provide exactly 4 raw text lines without any asterisks, quotes, markdown, or code blocks:\n"
                "Line 1: Part of speech only\n"
                "Line 2: A brief, clear explanation in English of how to use it\n"
                "Line 3: A completely new alternative Chinese example sentence\n"
                "Line 4: Strict English translation of that new alternative Chinese sentence"
            )
        else:  # Mandarin (简体中文)
            instruction = (
                f"分析中文词汇 {word} ({pinyin}) 意思为 {arabic}. "
                "请给出 4 行纯文本答案，不要包含任何星号、括号、引文或任何代码符号：\n"
                "第一行：词性\n"
                "第二行：用简单的中文解释其具体用法\n"
                "第三行：提供一个全新的中文实用生动例句\n"
                "第四行：该新例句的完全中文意思说明与翻译"
            )

        encoded_prompt = urllib.parse.quote(instruction)
        url = f"https://text.pollinations.ai/{encoded_prompt}?system=You+are+a+precise+multilingual+linguistic+professor+who+strictly+follows+the+requested+output+language."
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=9) as response:
            res_text = response.read().decode('utf-8').strip()
            res_text = res_text.replace('"', '').replace("'", "").replace("`", "")
            lines = [line.strip() for line in res_text.split('\n') if line.strip()]
            
            cleaned_lines = []
            prefixes = ["السطر الأول:", "السطر الثاني:", "السطر الثالث:", "السطر الرابع:", "Line 1:", "Line 2:", "Line 3:", "Line 4:", "1.", "2.", "3.", "4."]
            for line in lines:
                for prefix in prefixes:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                cleaned_lines.append(line)

            return {
                "type": cleaned_lines[0] if len(cleaned_lines) > 0 else ("اسم / فعل" if ui_lang == "العربية" else "Noun / Verb"),
                "explanation": cleaned_lines[1] if len(cleaned_lines) > 1 else f"كلمة تدل على {arabic}",
                "extra_example_zh": cleaned_lines[2] if len(cleaned_lines) > 2 else f"我使用 {word}。",
                "extra_example_lang": cleaned_lines[3] if len(cleaned_lines) > 3 else ""
            }
    except Exception:
        if ui_lang == "العربية":
            return {
                "type": "فعل / اسم", "explanation": f"تُستخدم للتعبير عن دلالة ({arabic}).", "extra_example_zh": f"我喜欢 {word}。", "extra_example_lang": f"أنا يعجبني/أحب {arabic}."
            }
        else:
            return {
                "type": "Noun / Verb", "explanation": f"This word is essential to express the meaning of ({arabic}).", "extra_example_zh": f"我喜欢 {word}。", "extra_example_lang": f"I like {word}."
            }

# ============================================
# 3. دالة توليد النطق الصوتي التفاعلي
# ============================================
def play_audio(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3")
    except Exception:
        st.error("تعذر تشغيل الصوت حالياً.")

# ============================================
# 4. قراءة ملف البيانات وتجهيز الأعمدة
# ============================================
try:
    df = pd.read_csv("words.csv", encoding="utf-8")
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        'Chinese': 'chinese', 'Pinyin': 'pinyin', 'Arabic Translation': 'arabic',
        'Chinese Example': 'example_chinese', 'Arabic Example': 'example_arabic'
    })
except Exception:
    data = {
        'chinese': ['爱', '八', '爸爸', '杯子', '北京'],
        'pinyin': ['ài', 'bā', 'bàba', 'bēizi', 'Běijīng'],
        'arabic': ['يحب / الحب', 'ثمانية', 'أب', 'كوب', 'بكين'],
        'example_chinese': ['我爱你。', '我有八本书。', '我爸爸很好。', '这是我的杯子。', '我去北京。'],
        'example_arabic': ['أنا أحبك.', 'لدي ثمانية كتب.', 'أبي جيد جداً.', 'هذا كوبي.', 'أنا أذهب إلى بكين.']
    }
    df = pd.DataFrame(data)

df['chinese'] = df['chinese'].astype(str).str.strip()
df['arabic'] = df['arabic'].astype(str).str.strip()

# ============================================
# 5. نظام إدارة الذاكرة المستقر (Session State)
# ============================================
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'reveal_clicked' not in st.session_state:
    st.session_state.reveal_clicked = False
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None
if 'quiz_index' not in st.session_state:
    st.session_state.quiz_index = 0
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_answered' not in st.session_state:
    st.session_state.quiz_answered = False
if 'has_failed' not in st.session_state:
    st.session_state.has_failed = False
if 'quiz_options' not in st.session_state:
    st.session_state.quiz_options = []
if 'previous_direction' not in st.session_state:
    st.session_state.previous_direction = ""

# ============================================
# 6. التحكم في الشريط الجانبي (Sidebar)
# ============================================
with st.sidebar:
    st.header("⚙️ Settings / الإعدادات")
    ui_lang = st.selectbox(
        "Choose UI Language / اختر لغة الواجهة",
        ["English", "العربية", "Mandarin (简体中文)"]
    )
    st.markdown("---")
    
    learning_direction = st.selectbox(
        "Learning Path / مسار التعلم",
        ["Mandarin for Arabic Speakers", "Arabic for Mandarin Speakers"]
    )
    st.markdown("---")

if st.session_state.previous_direction != learning_direction:
    st.session_state.quiz_options = []
    st.session_state.quiz_answered = False
    st.session_state.has_failed = False
    st.session_state.previous_direction = learning_direction

translations = {
    "English": {
        "title": "LangAI", "dashboard": "📊 Student Dashboard", "welcome": "Welcome to your interface ✨",
        "progress": "You are making great progress! 🚀",
        "tab1": "📚 Flashcards", "tab2": "🔍 Quick Dictionary", "tab3": "🎮 Quiz", 
        "reveal": "🔓 Reveal Meaning & Ask AI", "next": "➡️ Next Word", "celebrate": "🎉 Celebrate",
        "search_label": "Search for a word:", "search_placeholder": "Type here...", "no_results": "No words found.",
        "quiz_title": "🎮 Vocabulary Practice Quiz", "score": "Your Score", "correct": "Correct! 🎉",
        "wrong": "Incorrect, try again! ❌", "next_q": "Next Question ➡️", "quiz_done": "🏆 Congratulations! You finished the quiz!",
        "ai_pos": "📌 AI Part of Speech:", "ai_exp": "📖 AI Usage Explanation:", "ai_extra": "🤖 Extra AI Generated Example:"
    },
    "العربية": {
        "title": "LangAI", "dashboard": "📊 لوحة تحكم الطالب", "welcome": "مرحباً بك في واجهتك ✨",
        "progress": "أنت تتقدم بشكل ممتاز! 🚀",
        "tab1": "📚 بطاقات الاستذكار", "tab2": "🔍 القاموس السريع", "tab3": "🎮 اختبار", 
        "reveal": "🔓 إظهار المعنى وتحليل الذكاء الاصطناعي", "next": "➡️ الكلمة التالية", "celebrate": "🎉 احتفال",
        "search_label": "ابحث عن كلمة:", "search_placeholder": "اكتب هنا...", "no_results": "لم يتم العثور على كلمات.",
        "quiz_title": "🎮 اختبار الكلمات التفاعلي", "score": "نتيجتك الحالية", "correct": "إجابة صحيحة! 🎉",
        "wrong": "إجابة خاطئة، حاول مجدداً! ❌", "next_q": "السؤال التالي ➡️", "quiz_done": "🏆 تهانينا! لقد أنهيت الاختبار بالكامل!",
        "ai_pos": "📌 نوع الكلمة (حسب الذكاء الاصطناعي):", "ai_exp": "📖 شرح طريقة الاستخدام والتحليل:", "ai_extra": "🤖 مثال ذكي إضافي من الذكاء الاصطناعي:"
    },
    "Mandarin (简体中文)": {
        "title": "LangAI", "dashboard": "📊 学生儀表板", "welcome": "歡迎唻到您的界面 ✨",
        "progress": "您取得了很大的進步！🚀",
        "tab1": "📚 閃卡練習", "tab2": "🔍 快速词典", "tab3": "🎮 測試", 
        "reveal": "🔓 顯示含义与AI解析", "next": "➡️ 下一個單词", "celebrate": "🎉 慶祝",
        "search_label": "搜索單詞:", "search_placeholder": "在這裡輸入...", "no_results": "未找到單詞。",
        "quiz_title": "🎮 詞彙互动測試", "score": "您的得分", "correct": "回答正確！🎉",
        "wrong": "回答錯誤，請重试！ ❌", "next_q": "下一題 ➡️", "quiz_done": "🏆 恭喜！您已完成所有測試！",
        "ai_pos": "📌 AI 词性分析:", "ai_exp": "📖 AI 用法解析:", "ai_extra": "🤖 AI 生成的额外生动例句:"
    }
}

t = translations.get(ui_lang, translations["English"])

st.title(t["title"])
st.markdown("---")

with st.sidebar:
    st.header(t["dashboard"])
    st.write(t["welcome"])
    st.progress(int((st.session_state.current_index + 1) / len(df) * 100))
    st.caption(t["progress"])

tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

# ============================================
# TAB 1: Flashcards (بطاقات الاستذكار)
# ============================================
with tab1:
    st.markdown(f"## 🎴 {t['tab1']}")
    card_row = df.iloc[st.session_state.current_index]
    
    if learning_direction == "Mandarin for Arabic Speakers":
        display_word = card_row['chinese']
        display_sub = f"Pinyin: {card_row['pinyin']}"
        meaning_content = f"Translation: {card_row['arabic']}"
    else:
        display_word = card_row['arabic']
        display_sub = "Target Language: Mandarin (简体中文)"
        meaning_content = f"Mandarin: {card_row['chinese']} ({card_row['pinyin']})"
        
    st.markdown(f"""
    <div style="background-color: #f8fafc; padding: 45px; border-radius: 15px; text-align: center; border: 2px solid #38bdf8; margin-bottom: 20px;">
        <h1 style="color: #1e293b; font-size: 80px; margin: 0;">{display_word}</h1>
        <p style="color: #64748b; font-size: 24px; margin-top: 10px;">{display_sub}</p>
    </div>
    """, unsafe_allow_html=True)
    
    audio_col1, audio_col2 = st.columns(2)
    with audio_col1:
        if st.button("🔊 Pronounce Mandarin (نطق الصينية)", use_container_width=True, key="audio_zh_btn"):
            play_audio(card_row['chinese'], 'zh')
    with audio_col2:
        if st.button("🔊 Pronounce Arabic (نطق العربية)", use_container_width=True, key="audio_ar_btn"):
            play_audio(card_row['arabic'], 'ar')

    st.markdown("---")

    if st.session_state.reveal_clicked:
        st.success(f"💡 {meaning_content}")
        
        if st.session_state.ai_analysis is None:
            with st.spinner("🤖 Analyzing word context dynamically..."):
                st.session_state.ai_analysis = ask_ai_about_word(card_row['chinese'], card_row['pinyin'], card_row['arabic'], ui_lang)
        
        ai_data = st.session_state.ai_analysis
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"{t['ai_pos']}\n\n**{ai_data['type']}**")
        with col_info2:
            st.info(f"{t['ai_exp']}\n\n{ai_data['explanation']}")
        
        st.markdown("### 📝 Dataset Examples:")
        if 'example_chinese' in df.columns and pd.notna(card_row['example_chinese']):
            st.markdown(f"**🇨🇳 {card_row['example_chinese']}** ➡️ 🇦🇪 {card_row['example_arabic']}")
            
        st.markdown(f"### {t['ai_extra']}")
        # سيتم الآن عرض الترجمة باللغة الصحيحة تماماً بناءً على اختيار الواجهة
        st.markdown(f"**🇨🇳 {ai_data['extra_example_zh']}** ➡️ {ai_data['extra_example_lang']}")
        
    st.write(" ")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(t["reveal"], key="reveal_card_btn", use_container_width=True):
            st.session_state.reveal_clicked = True
            st.rerun()
    with col2:
        if st.button(t["next"], key="next_card_btn", use_container_width=True):
            st.session_state.current_index = (st.session_state.current_index + 1) % len(df)
            st.session_state.reveal_clicked = False
            st.session_state.ai_analysis = None
            st.rerun()
    with col3:
        if st.button(t["celebrate"], key="cel_card_btn", use_container_width=True):
            st.balloons()

# ============================================
# TAB 2: Quick Dictionary (القاموس السريع)
# ============================================
with tab2:
    st.header(t["tab2"])
    search_query = st.text_input(t["search_label"], placeholder=t["search_placeholder"], key="dict_search_input")
    available_cols = ['chinese', 'pinyin', 'arabic']
    
    if search_query:
        results = df[df['chinese'].astype(str).str.contains(search_query, case=False) | 
                     df['arabic'].astype(str).str.contains(search_query, case=False)]
        if not results.empty:
            st.dataframe(results[available_cols], use_container_width=True)
        else:
            st.warning(t["no_results"])
    else:
        st.dataframe(df[available_cols], use_container_width=True)

# ============================================
# TAB 3: Quiz (الاختبار التفاعلي)
# ============================================
with tab3:
    st.header(t["quiz_title"])
    
    if st.session_state.quiz_index < len(df):
        quiz_word = df.iloc[st.session_state.quiz_index]
        
        if learning_direction == "Mandarin for Arabic Speakers":
            question_text = f"Question {st.session_state.quiz_index + 1}: What does '{quiz_word['chinese']}' mean?"
            correct_answer = str(quiz_word['arabic']).strip()
            target_column = 'arabic'
        else:
            question_text = f"السؤال {st.session_state.quiz_index + 1}: ما هو المقابل في لغة الماندارين للكلمة العربية '{quiz_word['arabic']}'؟"
            correct_answer = str(quiz_word['chinese']).strip()
            target_column = 'chinese'
            
        if not st.session_state.quiz_options:
            wrong_options = df[df[target_column].astype(str).str.strip() != correct_answer][target_column].dropna().unique()
            
            if len(wrong_options) >= 3:
                sampled_wrongs = random.sample(list(wrong_options), 3)
            else:
                sampled_wrongs = list(wrong_options)
                
            all_choices = [correct_answer] + [str(opt).strip() for opt in sampled_wrongs]
            unique_choices = list(dict.fromkeys(all_choices))
            st.session_state.quiz_options = random.sample(unique_choices, len(unique_choices))
            
        st.subheader(question_text)
        
        choice = st.radio(
            "Select the correct meaning:", 
            st.session_state.quiz_options, 
            key=f"quiz_radio_live_idx_{st.session_state.quiz_index}"
        )
        
        col_q1, col_q2 = st.columns(2)
        
        with col_q1:
            if not st.session_state.quiz_answered:
                if st.button("Check Answer ✔️", use_container_width=True, key=f"check_live_btn_{st.session_state.quiz_index}"):
                    if str(choice).strip() == correct_answer:
                        st.session_state.quiz_answered = True
                        if not st.session_state.has_failed:
                            st.session_state.quiz_score += 1
                        st.success(t["correct"])
                        st.rerun()
                    else:
                        st.session_state.has_failed = True
                        st.error(t["wrong"])
            else:
                st.button("Check Answer ✔️", disabled=True, use_container_width=True, key=f"check_live_disabled_{st.session_state.quiz_index}")
                st.success(t["correct"])
                
        with col_q2:
            if st.session_state.quiz_answered:
                if st.button(t["next_q"], use_container_width=True, key=f"next_live_btn_{st.session_state.quiz_index}"):
                    st.session_state.quiz_index += 1
                    st.session_state.quiz_answered = False
                    st.session_state.has_failed = False
                    st.session_state.quiz_options = []  
                    st.rerun()
            else:
                st.button(t["next_q"], disabled=True, use_container_width=True, key=f"next_live_disabled_{st.session_state.quiz_index}")
                
        st.markdown("---")
        st.metric(label=t["score"], value=f"{st.session_state.quiz_score} / {len(df)}")
        
    else:
        st.balloons()
        st.success(t["quiz_done"])
        st.metric(label=t["score"], value=f"{st.session_state.quiz_score} / {len(df)}")
        
        if st.button("Restart Quiz 🔄", use_container_width=True, key="restart_final_live_quiz_btn"):
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_answered = False
            st.session_state.has_failed = False
            st.session_state.quiz_options = []
            st.rerun()