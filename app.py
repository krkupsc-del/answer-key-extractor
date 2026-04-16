import streamlit as st
import pdfplumber
import re
import json
import pandas as pd
import time

# =========================
# CONFIG
# =========================
START_Q = 51
END_Q = 150

# =========================
# STREAMLIT CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(page_title="Answer Key Extractor", layout="centered")

# =========================
# FUNCTIONS
# =========================

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_question_mapping(text):
    mapping = {}

    pattern = re.compile(
        r"Q\s*(\d+).*?Question\s*ID\s*[:\-]?\s*(\d+)",
        re.IGNORECASE | re.DOTALL
    )

    matches = pattern.findall(text)

    for q_num, q_id in matches:
        mapping[int(q_num)] = q_id

    return mapping


def extract_answer_key(text):
    answer_map = {}

    pattern = re.compile(r"(\d{8,})\s+([1-4D])")

    matches = pattern.findall(text)

    for q_id, ans in matches:
        if ans == "D":
            answer_map[q_id] = None
        else:
            answer_map[q_id] = int(ans)

    return answer_map


def build_final(mapping, answer_map):
    results = []

    for q in range(START_Q, END_Q + 1):
        q_id = mapping.get(q)
        ans = answer_map.get(q_id) if q_id else None

        results.append({
            "question_number": q,
            "question_id": q_id,
            "correct_option_id": ans
        })

    return results


def build_compact(results):
    return [
        {"q": i + 1, "ans": item["correct_option_id"]}
        for i, item in enumerate(results)
    ]

# =========================
# UI
# =========================

st.title("📄 Answer Key Extractor")
st.caption("Upload PDF → Extract → Download")

uploaded_file = st.file_uploader(
    "Drag & drop your PDF here",
    type=["pdf"],
    help="Upload question paper + answer key PDF"
)

progress_bar = st.progress(0)
status_text = st.empty()

# =========================
# PROCESSING
# =========================

if uploaded_file:

    status_text.text("Reading PDF...")
    progress_bar.progress(20)
    time.sleep(0.3)

    text = extract_text_from_pdf(uploaded_file)

    status_text.text("Extracting question mapping...")
    progress_bar.progress(40)
    time.sleep(0.3)

    q_map = extract_question_mapping(text)

    status_text.text("Extracting answer key...")
    progress_bar.progress(60)
    time.sleep(0.3)

    ans_map = extract_answer_key(text)

    status_text.text("Joining data...")
    progress_bar.progress(80)
    time.sleep(0.3)

    final_answers = build_final(q_map, ans_map)
    compact_answers = build_compact(final_answers)

    progress_bar.progress(100)
    status_text.text("Done ✅")

    st.success("Extraction Complete!")

    # =========================
    # VALIDATION
    # =========================
    if len(q_map) < 100:
        st.warning("⚠️ Some questions may not have been detected correctly.")

    # =========================
    # PREVIEW
    # =========================
    st.subheader("Preview")
    st.dataframe(pd.DataFrame(final_answers).head(10), use_container_width=True)

    # =========================
    # DOWNLOADS
    # =========================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "📥 Full JSON",
            data=json.dumps({"answers": final_answers}, indent=2),
            file_name="answer_full.json"
        )

    with col2:
        st.download_button(
            "📥 Compact JSON",
            data=json.dumps(compact_answers, indent=2),
            file_name="answer_compact.json"
        )

    with col3:
        df = pd.DataFrame(final_answers)
        st.download_button(
            "📥 CSV",
            data=df.to_csv(index=False),
            file_name="answer_key.csv"
        )
