import time

st.set_page_config(page_title="Answer Key Extractor", layout="centered")

st.title("📄 Answer Key Extractor")
st.caption("Upload PDF → Extract → Download")

uploaded_file = st.file_uploader(
    "Drag & drop your PDF here",
    type=["pdf"],
    help="Upload question paper + answer key PDF"
)

progress_bar = st.progress(0)
status_text = st.empty()

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

    # Preview
    st.dataframe(pd.DataFrame(final_answers).head(10), use_container_width=True)

    # Downloads
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
