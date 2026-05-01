import streamlit as st
import streamlit.components.v1 as components
from analyzer import get_sentiment, get_keywords, get_category
from PIL import Image
import pandas as pd
import csv
import os
from datetime import datetime

HISTORY_FILE = "history.csv"

def save_to_history(review, sentiment, category, keywords, score):
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Review", "Sentiment", "Category", "Keywords", "Score"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            review,
            sentiment,
            category,
            ", ".join(keywords[:8]),
            round(score, 2)
        ])

def renderPage():
    st.markdown("# 📝 Analyze Feedback")
    st.markdown("### Customer Feedback Intelligence")
    components.html("""<hr style="height:3px;border:none;color:#333;background-color:#333; margin-bottom: 10px" /> """)

    st.markdown("Enter a customer review below and click **Analyze** to get instant insights.")
    st.text("")

    userText = st.text_area(
        "Customer Review",
        placeholder="e.g. The delivery was very slow but the product quality was excellent.",
        height=150
    )

    st.text("")

    if st.button("🔍 Analyze"):
        if userText.strip() != "":

            sentiment, score = get_sentiment(userText)
            keywords = get_keywords(userText)
            category = get_category(userText)

            # save to session
            if "history" not in st.session_state:
                st.session_state.history = []

            st.session_state.history.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Review": userText,
                "Sentiment": sentiment,
                "Category": category,
                "Keywords": ", ".join(keywords[:8]),
                "Score": round(score, 2)
            })

            # save to CSV
            save_to_history(userText, sentiment, category, keywords, score)

            st.markdown("---")
            st.markdown("## 📊 Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### Sentiment")
                if sentiment == "Positive":
                    st.success(f"😊 {sentiment}")
                    image = Image.open('./images/positive.png')
                elif sentiment == "Negative":
                    st.error(f"😔 {sentiment}")
                    image = Image.open('./images/negative.png')
                else:
                    st.warning(f"😐 {sentiment}")
                    image = Image.open('./images/neutral.png')
                st.image(image, width=100)

            with col2:
                st.markdown("### Category")
                st.info(f"{category}")
                st.markdown("### Compound Score")
                st.metric(label="Vader Score", value=round(score, 2))

            with col3:
                st.markdown("### Keywords")
                if keywords:
                    for kw in keywords[:8]:
                        st.markdown(f"- `{kw}`")
                else:
                    st.write("No keywords found.")

            st.markdown("---")
            st.markdown("### 📋 Summary")
            st.markdown(f"""
            | Field | Result |
            |---|---|
            | **Sentiment** | {sentiment} |
            | **Category** | {category} |
            | **Vader Score** | {round(score, 2)} |
            | **Keywords** | {", ".join(keywords[:8])} |
            """)

        else:
            st.warning("⚠️ Please enter a customer review first.")

    # ---- SESSION HISTORY ----
    if "history" in st.session_state and len(st.session_state.history) > 0:
        st.markdown("---")
        st.markdown("## 🕓 Session History")
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)

        # download button
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download History as CSV",
            data=csv_data,
            file_name="pulseai_history.csv",
            mime="text/csv"
        )

        if st.button("🗑️ Clear Session History"):
            st.session_state.history = []
            st.rerun()