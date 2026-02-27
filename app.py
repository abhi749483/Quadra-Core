import streamlit as st
import google.generativeai as genai

# 🔑 Replace with your real Gemini API key
genai.configure(api_key="AIzaSyCAiV1qK9zY96og3FKzBuXi8nr5L3_oyY4")

model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="AI Film Preproduction System", layout="wide")

st.title("🎬 Generative AI Film Preproduction System")
st.write("Generate screenplay, characters, and structure from your idea.")

# User Inputs
genre = st.selectbox(
    "Select Genre",
    ["Crime/Thriller", "Romance", "Sci-Fi", "Horror", "Comedy", "Drama"]
)

tone = st.selectbox(
    "Select Tone",
    ["Dark", "Emotional", "Suspenseful", "Light-hearted", "Intense"]
)

idea = st.text_area("Enter your story idea")

# Generate Button
if st.button("Generate"):
    if idea.strip() == "":
        st.warning("Please enter a story idea first.")
    else:
        with st.spinner("Generating..."):
            prompt = f"""
            Genre: {genre}
            Tone: {tone}
            Idea: {idea}

            Generate:
            1. Logline
            2. Three-Act Structure
            3. Three Main Characters with character arcs
            4. Three Key Scenes in screenplay format
            5. Sound Design Suggestions
            """

            response = model.generate_content(prompt)
            st.success("Done!")
            st.write(response.text)