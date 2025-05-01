# main.py
import streamlit as st
from utils import extract_mte_data
from evaluator import evaluate_mte, AVAILABLE_MODELS

# Set wide layout
st.set_page_config(page_title="🌟 MTE Rating System", layout="wide")

# App title
st.title("🌟 Monthly Thinking Exercise (MTE) Evaluator")

# Sidebar
st.sidebar.title("⚙️ Settings")
uploaded_file = st.sidebar.file_uploader("📤 Upload your MTE Excel file", type=["xlsx"])
selected_model = st.sidebar.selectbox("🤖 Choose a Model", AVAILABLE_MODELS)

# Main App
if uploaded_file:
    mte_data = extract_mte_data(uploaded_file)

    if "error" not in mte_data:
        with st.spinner("🧠 Analyzing your responses..."):
            feedback = evaluate_mte(mte_data, selected_model)

        if "error" not in feedback:
            st.success("✅ Evaluation complete!")
            
            # Show Overall Score
            overall_score = feedback.get('overall_score', 0)
            st.header(f"🏅 Overall MTE Score: {overall_score} / 10")

            # Show Progress Bar
            st.progress(overall_score / 10)

            # 🎉 Confetti Celebration if score > 8
            if overall_score > 8:
                st.balloons()
                st.toast("🎉 Fantastic Work! You're excelling!", icon="🎯")

            st.divider()

            # Tabs for clean navigation
            tabs = st.tabs(["💪 Strengths", "📈 Areas for Improvement", "📚 Learning Resources", "📋 Section-wise Evaluation"])

            # --- Strengths Tab ---
            with tabs[0]:
                st.subheader("💪 Your Strengths")
                strengths = feedback.get("strengths", [])
                if strengths:
                    for strength in strengths:
                        st.success(f"✅ {strength}")
                else:
                    st.info("No strengths detected.")

            # --- Areas for Improvement Tab ---
            with tabs[1]:
                st.subheader("📈 Areas for Improvement")
                areas = feedback.get("areas_for_improvement", [])
                if areas:
                    for area in areas:
                        st.warning(f"🔍 {area}")
                else:
                    st.info("No areas for improvement detected.")

            # --- Learning Resources Tab ---
            with tabs[2]:
                st.subheader("📚 Personalized Learning Resources & Advice")
                suggestions = feedback.get("suggestions", [])
                if suggestions:
                    num_cols = 2
                    cols = st.columns(num_cols)
                    for idx, suggestion in enumerate(suggestions):
                        with cols[idx % num_cols]:
                            st.info(f"📌 {suggestion}")
                else:
                    st.info("No personalized suggestions provided.")

            # --- Section-wise Evaluation Tab ---
            with tabs[3]:
                st.subheader("📋 Detailed Section-wise Evaluation")
                sections = feedback.get("section_scores", {})
                for section, details in sections.items():
                    with st.expander(f"🔎 {section.replace('_', ' ').title()} (Score: {details.get('score', 'N/A')}/10)"):
                        st.markdown(f"**🧠 Reasoning:** {details.get('reason', '')}")
                        st.markdown(f"**💬 Feedback:** {details.get('feedback', '')}")
                        st.markdown(f"**🔧 Suggestions:** {details.get('suggestions', '')}")

        else:
            st.error(f"❗ Error in Evaluation: {feedback['error']}")

    else:
        st.error(f"❗ Error reading MTE file: {mte_data['error']}")
else:
    st.info("📂 Please upload your MTE Excel file from the sidebar to begin.")
