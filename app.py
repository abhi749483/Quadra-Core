import streamlit as st
from openai import OpenAI
import os

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

st.set_page_config(page_title="AI Film Preproduction", layout="wide")

st.title("🎬 Generative AI Film Preproduction System")
st.markdown("Generate screenplay, characters, and structure based on your idea.")

genre = st.selectbox(
    "Select Genre",
    ["Crime/Thriller", "Romance", "Sci-Fi", "Horror", "Comedy", "Drama"]
)

tone = st.selectbox(
    "Select Tone",
    ["Dark", "Emotional", "Suspenseful", "Light-hearted", "Intense"]
)

idea = st.text_area("Enter your basic story idea")

if st.button("Generate Script"):
    if idea.strip() == "":
        st.warning("Please enter a story idea.")
    else:
        with st.spinner("Generating screenplay..."):

            prompt = f"""
Genre: {genre}
Tone: {tone}
Idea: {idea}

Generate the following:

1. Logline
2. Three-Act Structure
3. Three Main Characters (with personality + character arc)
4. Three Key Scenes in proper screenplay format
5. Sound Design Suggestions
"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # or "mixtral-8x7b-32768"
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            st.success("Generation Complete!")
            st.write(response.choices[0].message.content)