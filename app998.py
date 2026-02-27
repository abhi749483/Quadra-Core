
"""
🎬 AI Film Preproduction Studio — v2.0
=======================================
NEW FEATURES in v2:
  ① 🔤 Enhanced Title Generator  — style variants, tone, taglines, regenerate
  ② 🎨 Style & Scale Settings    — visual style, film scale, aspect ratio,
                                    shooting format, content rating
  ③ 🎭 Theme Selector             — primary + secondary themes shape every prompt
  ④ 💰 Budget Estimator           — AI line-item breakdown + funding tips
"""

import streamlit as st
from openai import OpenAI
import os
from io import BytesIO

# ── Optional PDF ──────────────────────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ═════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="🎬 AI Film Preproduction Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #12121e 50%, #0d0d18 100%);
    color: #e8e8f0;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    border-right: 1px solid #f5c518;
}
.film-header {
    font-family: 'Bebas Neue', cursive; font-size: 3.2rem; letter-spacing: 4px;
    background: linear-gradient(90deg, #f5c518, #ff6b35, #f5c518);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; text-align: center; line-height: 1.1;
}
.film-subtitle {
    text-align: center; color: #8888a8; font-size: 0.9rem;
    letter-spacing: 3px; text-transform: uppercase; margin-bottom: 2rem;
}
/* Gold card — script, titles, moodboard, market */
.output-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(245,197,24,0.2);
    border-left: 4px solid #f5c518; border-radius: 8px;
    padding: 1.4rem 1.6rem; margin: 1rem 0;
}
/* Green card — budget */
.budget-card {
    background: rgba(0,200,100,0.04); border: 1px solid rgba(0,200,100,0.25);
    border-left: 4px solid #00c864; border-radius: 8px;
    padding: 1.4rem 1.6rem; margin: 1rem 0;
}
.card-title {
    font-family: 'Bebas Neue', cursive; font-size: 1.4rem;
    letter-spacing: 2px; color: #f5c518; margin-bottom: 0.6rem;
}
.budget-title {
    font-family: 'Bebas Neue', cursive; font-size: 1.4rem;
    letter-spacing: 2px; color: #00c864; margin-bottom: 0.6rem;
}
.metric-box {
    background: rgba(245,197,24,0.08); border: 1px solid rgba(245,197,24,0.3);
    border-radius: 6px; padding: 0.8rem 1rem; text-align: center;
}
.metric-label { font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; color: #8888a8; }
.metric-value { font-family: 'Bebas Neue', cursive; font-size: 1.4rem; color: #f5c518; }
.theme-pill {
    display: inline-block; background: rgba(245,197,24,0.1);
    border: 1px solid rgba(245,197,24,0.35); border-radius: 20px;
    padding: 3px 12px; margin: 3px 2px; font-size: 0.78rem; color: #f5c518;
}
.stButton > button {
    background: linear-gradient(135deg, #f5c518, #e6b800); color: #0a0a0f;
    font-weight: 700; font-size: 1rem; letter-spacing: 2px; text-transform: uppercase;
    border: none; border-radius: 4px; padding: 0.7rem 2rem; width: 100%;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #ffda44, #f5c518);
    transform: translateY(-1px); box-shadow: 0 4px 20px rgba(245,197,24,0.4);
}
.stSelectbox > div > div, .stTextArea > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(245,197,24,0.25) !important; color: #e8e8f0 !important;
}
.stSlider > div > div > div > div { background: #f5c518 !important; }
hr { border-color: rgba(245,197,24,0.15); }
.stTabs [data-baseweb="tab"] {
    font-family: 'Bebas Neue', cursive; font-size: 1.0rem;
    letter-spacing: 1.5px; color: #8888a8;
}
.stTabs [aria-selected="true"] {
    color: #f5c518 !important; border-bottom: 2px solid #f5c518 !important;
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═════════════════════════════════════════════════════════════════════════════

MODEL = "llama-3.3-70b-versatile"

DIRECTOR_STYLES = {
    "Christopher Nolan":  "nonlinear narrative, practical effects, time/memory themes, morally complex protagonists, IMAX compositions",
    "Quentin Tarantino":  "sharp pop-culture dialogue, chapter structure, non-linear storytelling, stylised tension-building",
    "Wes Anderson":       "symmetrical shots, pastel palettes, deadpan quirky humour, whimsical production design",
    "Denis Villeneuve":   "slow-burn tension, wide-angle photography, minimal dialogue, philosophical themes, grand scale",
    "Bong Joon-ho":       "class commentary, genre-blending tonal shifts, dark comedy with tragedy, symbolic design",
    "Ari Aster":          "slow dread build-up, folk-horror imagery, grief as horror metaphor, long unbroken takes",
    "Sofia Coppola":      "dreamy introspective mood, female perspective, melancholic beauty, atmosphere over plot",
    "No Specific Style":  "balanced cinematic approach with industry-standard techniques",
}

GENRES    = ["Crime/Thriller", "Sci-Fi", "Drama", "Horror", "Romance",
             "Comedy", "Action/Adventure", "Fantasy", "Historical Epic"]
TONES     = ["Dark & Brooding", "Suspenseful", "Emotional & Raw",
             "Light-hearted", "Intense", "Whimsical", "Satirical"]
AUDIENCES = ["General Audiences (PG-13)", "Young Adults 18-25", "Adults 25-45",
             "Family (All Ages)", "Niche/Art-house", "Genre Enthusiasts"]
BUDGETS   = ["Micro-budget (<$1M)", "Indie ($1M-$10M)", "Mid-range ($10M-$50M)",
             "Studio ($50M-$150M)", "Blockbuster ($150M+)"]

# ── ② Style & Scale options ───────────────────────────────────────────────────
VISUAL_STYLES = [
    "Naturalistic / Realistic", "Hyper-stylised", "Noir / High Contrast",
    "Dreamlike / Surreal", "Gritty Documentary", "Glossy Commercial",
    "Minimalist", "Epic / Grand Spectacle",
]
FILM_SCALES = [
    "Single Location (Chamber)", "City-Based", "National / Road Movie",
    "International / Multi-Country", "Sci-Fi / Fantasy World-Building",
    "Intimate Character Study",
]
ASPECT_RATIOS = [
    "2.39:1 (Cinemascope)", "1.85:1 (Flat Widescreen)",
    "1.33:1 (Academy / Vintage)", "1.78:1 (16:9 Streaming)",
    "2.76:1 (Ultra Panavision)",
]
RATINGS = [
    "G / U (Universal)", "PG / PG-13", "R / 15 (Mature)",
    "NC-17 / 18 (Adult)", "Not Yet Rated",
]
SHOOTING_FMTS = [
    "Digital (ARRI Alexa)", "Digital (RED Camera)",
    "35mm Film", "16mm Film", "IMAX", "Handheld / Verite",
]

# ── ③ Theme options ───────────────────────────────────────────────────────────
PRIMARY_THEMES = [
    "Redemption", "Identity & Self-Discovery", "Power & Corruption", "Love & Loss",
    "Survival", "Justice vs Revenge", "Technology vs Humanity", "Class & Inequality",
    "Grief & Healing", "War & Its Consequences", "Family & Legacy", "Freedom vs Control",
]
SECONDARY_THEMES = [
    "Betrayal", "Sacrifice", "Isolation", "Memory & Nostalgia", "Fate vs Free Will",
    "Coming of Age", "Trust & Deception", "Ambition", "Race & Culture",
    "Gender & Identity", "Environmental Destruction", "Religion & Faith",
    "Addiction", "Redemption of the Villain",
]

# ── ① Title style options ─────────────────────────────────────────────────────
TITLE_STYLES = [
    "Poetic & Evocative",
    "Short & Punchy (1-2 words)",
    "Mysterious & Cryptic",
    "Action / Thriller Style",
    "Character Name as Title",
    "Question / Provocative",
    "Metaphorical / Symbolic",
]


# ═════════════════════════════════════════════════════════════════════════════
# API CLIENT
# ═════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_client():
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",
        "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"))
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def call_llm(prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
    """Centralised LLM call with friendly error messages."""
    try:
        res = get_client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content":
                    "You are a world-class Hollywood screenwriter, director, "
                    "and film production expert. Produce detailed, professional, "
                    "industry-standard output."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return res.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "401" in err:                               raise RuntimeError("❌ API key invalid. Check your Groq API key.")
        elif "429" in err:                             raise RuntimeError("⏳ Rate limit hit. Wait a moment and retry.")
        elif "timeout" in err or "connect" in err:    raise RuntimeError("🌐 Network error. Check your connection.")
        else:                                          raise RuntimeError(f"🔧 API error: {err}")


# ═════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDERS
# ═════════════════════════════════════════════════════════════════════════════

def build_main_prompt(genre, tone, idea, director, ddesc, tlabel,
                      primary_theme, secondary_theme, visual_style, film_scale):
    """Main script package — themes and style/scale baked into every section."""
    return f"""
FILM PROJECT BRIEF
==================
Genre:           {genre}
Tone:            {tone}
Director Style:  {director} — {ddesc}
Creativity:      {tlabel}
Primary Theme:   {primary_theme}
Secondary Theme: {secondary_theme}
Visual Style:    {visual_style}
Film Scale:      {film_scale}
Core Idea:       {idea}

Generate a complete preproduction package:

1. LOGLINE — one powerful sentence embodying {primary_theme} and {secondary_theme}.
2. THREE-ACT STRUCTURE — Setup / Confrontation / Resolution. Weave both themes
   throughout each act.
3. MAIN CHARACTERS (3) — Name, Role, Personality, Backstory, Arc, Defining Trait.
   Each character should embody or challenge {primary_theme}.
4. THREE KEY SCENES — proper screenplay format (slug line, action, dialogue).
5. CINEMATOGRAPHY — shot types, movement, lighting, colour grading.
   Align with the {visual_style} visual style.
6. SOUND DESIGN & SCORE — instrumentation, motifs, silence, reference composers.
"""


# ── ① ENHANCED TITLE GENERATOR ────────────────────────────────────────────────
def build_title_prompt(genre, tone, idea, director,
                       primary_theme, secondary_theme, title_style):
    """Richer title prompt: style-driven with theme and commercial rationale."""
    return f"""
Generate 6 compelling film titles for this project.

Genre:           {genre}
Tone:            {tone}
Director Style:  {director}
Primary Theme:   {primary_theme}
Secondary Theme: {secondary_theme}
Title Style:     {title_style}
Core Idea:       {idea}

For EACH title provide:
  • The Title — memorable, fits the '{title_style}' naming style
  • Tagline — 1 punchy sentence
  • Why It Works — commercial + thematic rationale (1-2 sentences)
  • Tone Match — how it reflects '{tone}' and '{primary_theme}'

Number each entry clearly. Make every title distinct in feel.
"""


# ── ② STYLE & SCALE GUIDE ─────────────────────────────────────────────────────
def build_style_prompt(genre, tone, idea, director, visual_style, film_scale,
                       aspect_ratio, rating, shooting_fmt, primary_theme):
    """Full cinematic style and production scale analysis."""
    return f"""
CINEMATIC STYLE & SCALE BRIEF
==============================
Genre:           {genre}  |  Tone: {tone}
Director Style:  {director}
Visual Style:    {visual_style}
Film Scale:      {film_scale}
Aspect Ratio:    {aspect_ratio}
Rating:          {rating}
Shooting Format: {shooting_fmt}
Primary Theme:   {primary_theme}
Core Idea:       {idea}

Provide a detailed Cinematic Style & Production Scale guide:

1. VISUAL LANGUAGE
   - How '{visual_style}' shapes each scene's look and feel
   - Camera movement philosophy for this story
   - Lens choices and depth-of-field approach
   - Key visual motifs that reinforce '{primary_theme}'

2. ASPECT RATIO JUSTIFICATION
   - Why {aspect_ratio} serves this specific story
   - How to use the frame shape creatively
   - 3 reference films that used this ratio well

3. SHOOTING FORMAT NOTES
   - Why '{shooting_fmt}' fits the tone and budget
   - On-set and post-production workflow tips

4. PRODUCTION SCALE EXECUTION
   - How to execute a '{film_scale}' film effectively
   - Location scouting priorities
   - Production design approach for this scale

5. RATING IMPACT
   - How '{rating}' shapes creative content decisions
   - What it opens up and what it restricts
   - 3 comparable films at this rating in {genre}

6. VISUAL REFERENCE FILMS
   - 5 films with similar style + scale — 1 specific thing to borrow from each
"""


# ── ③ THEME DEVELOPMENT ────────────────────────────────────────────────────────
def build_theme_prompt(genre, tone, idea, director, primary_theme, secondary_theme):
    """Deep thematic analysis — how both themes weave through the story."""
    return f"""
THEMATIC DEVELOPMENT BRIEF
===========================
Genre:           {genre}  |  Tone: {tone}
Director Style:  {director}
Primary Theme:   {primary_theme}
Secondary Theme: {secondary_theme}
Core Idea:       {idea}

Provide a complete thematic guide:

1. THEME STATEMENT
   One sentence capturing how '{primary_theme}' and '{secondary_theme}'
   are explored together in this specific story.

2. HOW THE THEMES MANIFEST
   - In the protagonist's journey
   - In the antagonist's worldview
   - In the setting and world design
   - In visual symbols and recurring imagery
   - In dialogue subtext

3. THEMATIC KEY SCENES (3 scenes)
   For each: slug line, brief action, short dialogue exchange,
   and the specific thematic purpose it serves.

4. CHARACTER THEME ARCS
   How each of the 3 main characters starts, transforms, and ends
   in relation to '{primary_theme}'.

5. THEMATIC TENSION
   How '{secondary_theme}' complicates or deepens '{primary_theme}'.
   Which characters represent which side of the conflict?

6. COMPARABLE FILMS
   5 films that handled these themes well — one lesson from each.

7. PITFALLS TO AVOID
   3 common mistakes when writing about '{primary_theme}' in {genre} films.
"""


# ── ④ BUDGET ESTIMATOR ────────────────────────────────────────────────────────
def build_budget_prompt(genre, idea, budget_tier, film_scale, visual_style,
                        shooting_fmt, aspect_ratio, rating, director):
    """
    Detailed line-item budget breakdown tailored to every production setting.
    """
    return f"""
FILM BUDGET ESTIMATION
======================
Genre:           {genre}
Budget Tier:     {budget_tier}
Film Scale:      {film_scale}
Visual Style:    {visual_style}
Shooting Format: {shooting_fmt}
Aspect Ratio:    {aspect_ratio}
Rating:          {rating}
Director Style:  {director}
Core Idea:       {idea}

Produce a realistic, detailed budget estimate for a {budget_tier} production.

1. TOTAL BUDGET OVERVIEW
   - Estimated total range: low / mid / high
   - Above-the-line vs Below-the-line split (as percentages)
   - Recommended contingency (%)

2. LINE-ITEM BREAKDOWN BY DEPARTMENT
   For each, give cost range AND % of total budget:
   a)  Development & Script
   b)  Director & Producer Fees
   c)  Lead Cast
   d)  Supporting Cast & Extras
   e)  Full Crew (below-the-line)
   f)  Camera Department ({shooting_fmt} specific)
   g)  Lighting & Grip
   h)  Production Design & Art Department
   i)  Costume & Wardrobe
   j)  Hair & Makeup
   k)  Locations & Permits
   l)  Catering & Transport
   m)  VFX & Special Effects
   n)  Music & Sound Design
   o)  Post-Production (editing, colour grade, mix)
   p)  Marketing & Distribution
   q)  Insurance & Legal
   r)  Contingency Fund

3. COST-SAVING STRATEGIES
   5 smart ways to cut costs without hurting quality for this project.

4. FUNDING SOURCES
   Best funding routes for a {budget_tier} {genre} film:
   grants, co-productions, tax incentives, crowdfunding, streaming pre-sales.

5. FINANCIAL RISK AREAS
   Top 3 budget overrun risks and how to mitigate each.

6. COMPARABLE FILM BUDGETS
   3 real films made at similar budget — what they spent and what they achieved.
"""


# ── Existing prompts (unchanged) ──────────────────────────────────────────────
def build_expansion_prompt(act, genre, tone, idea, director, ddesc):
    return f"""Expand {act} for: Genre: {genre} | Tone: {tone} | Director: {director} ({ddesc}) | Idea: {idea}
Provide 5-7 scenes with: slug line, action block, key dialogue, pacing notes, emotional beats, visual/audio cues."""

def build_moodboard_prompt(genre, tone, idea, director, ddesc):
    return f"""Visual moodboard for: Genre: {genre} | Tone: {tone} | Director: {director} | Idea: {idea}
Include: 1) Color Palette (5 hex codes + meaning) 2) Visual Film References (5) 3) Poster Concept 4) Production Design Notes 5) 3 AI image prompts (Midjourney-ready)."""

def build_market_prompt(genre, tone, idea, director, audience, budget):
    return f"""Market analysis for: Genre: {genre} | Tone: {tone} | Director: {director} | Audience: {audience} | Budget: {budget} | Idea: {idea}
Cover: 1) Audience Profile 2) Box Office Potential 3) Streaming/Distribution 4) Competitive Landscape 5) Marketing Angles 6) Risk Assessment."""


# ═════════════════════════════════════════════════════════════════════════════
# PDF HELPER
# ═════════════════════════════════════════════════════════════════════════════

def generate_pdf(title: str, content: str) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                             rightMargin=72, leftMargin=72,
                             topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    ts = ParagraphStyle("T", parent=styles["Title"], fontSize=22,
                        textColor=colors.HexColor("#f5c518"),
                        spaceAfter=20, fontName="Helvetica-Bold")
    bs = ParagraphStyle("B", parent=styles["Normal"], fontSize=10,
                        leading=16, spaceAfter=6, fontName="Courier")
    story = [Paragraph(title, ts), Spacer(1, 0.2 * inch)]
    for line in content.split("\n"):
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe if safe.strip() else "&nbsp;", bs))
    doc.build(story)
    return buf.getvalue()


# ═════════════════════════════════════════════════════════════════════════════
# UI HELPER
# ═════════════════════════════════════════════════════════════════════════════

def render_card(icon, title, content,
                card_class="output-card", title_class="card-title"):
    st.markdown(
        f'<div class="{card_class}"><div class="{title_class}">'
        f'{icon} {title}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(content)


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Production Controls")
    st.divider()

    st.markdown("### 🎥 Director & Genre")
    director = st.selectbox("Director Style", list(DIRECTOR_STYLES.keys()))
    st.caption(f"*{DIRECTOR_STYLES[director][:88]}…*")
    genre = st.selectbox("Genre", GENRES)
    tone  = st.selectbox("Tone",  TONES)

    st.divider()

    # ── ③ THEMES ────────────────────────────────────────────────────────────
    st.markdown("### 🎭 Themes")
    primary_theme   = st.selectbox("Primary Theme",   PRIMARY_THEMES)
    secondary_theme = st.selectbox("Secondary Theme", SECONDARY_THEMES)
    st.markdown(
        f'<span class="theme-pill">⭐ {primary_theme}</span>'
        f'<span class="theme-pill">➕ {secondary_theme}</span>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── ② STYLE & SCALE ─────────────────────────────────────────────────────
    st.markdown("### 🎨 Style & Scale")
    visual_style = st.selectbox("Visual Style",    VISUAL_STYLES)
    film_scale   = st.selectbox("Film Scale",       FILM_SCALES)
    aspect_ratio = st.selectbox("Aspect Ratio",     ASPECT_RATIOS)
    shooting_fmt = st.selectbox("Shooting Format",  SHOOTING_FMTS)
    rating       = st.selectbox("Content Rating",   RATINGS)

    st.divider()

    st.markdown("### 👥 Market Settings")
    audience = st.selectbox("Target Audience", AUDIENCES)
    budget   = st.selectbox("Budget Tier",     BUDGETS)

    st.divider()

    st.markdown("### 🌡️ Creativity")
    temperature = st.slider("Temperature", 0.1, 1.5, 0.8, 0.05)
    temp_label  = next(
        (v for (lo, hi), v in {
            (0.1, 0.4): "🎯 Precise",
            (0.4, 0.7): "🎬 Balanced",
            (0.7, 1.0): "✨ Creative",
            (1.0, 1.5): "🔥 Experimental",
        }.items() if lo <= temperature <= hi),
        "✨ Creative",
    )
    st.caption(f"Mode: **{temp_label}**")
    st.divider()
    st.markdown(
        "<div style='text-align:center;color:#444;font-size:0.72rem'>"
        "LLaMA 3.3 70B · Groq API · Streamlit</div>",
        unsafe_allow_html=True,
    )


# ═════════════════════════════════════════════════════════════════════════════
# MAIN HEADER
# ═════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="film-header">🎬 AI FILM PREPRODUCTION STUDIO</div>',
            unsafe_allow_html=True)
st.markdown('<div class="film-subtitle">From Idea to Industry-Ready Package in Seconds</div>',
            unsafe_allow_html=True)

# Metric strip — 6 columns
c1, c2, c3, c4, c5, c6 = st.columns(6)
for col, lbl, val in zip(
    [c1, c2, c3, c4, c5, c6],
    ["Director", "Genre", "Visual Style", "Themes", "Budget", "Creativity"],
    [
        director.split()[0],
        genre.split("/")[0],
        visual_style.split("/")[0].strip(),
        f"{primary_theme[:9]}…",
        budget.split("(")[0].strip(),
        temp_label.split()[0],
    ],
):
    with col:
        st.markdown(
            f'<div class="metric-box">'
            f'<div class="metric-label">{lbl}</div>'
            f'<div class="metric-value">{val}</div></div>',
            unsafe_allow_html=True,
        )

st.divider()

idea = st.text_area(
    "📝 Your Story Idea",
    placeholder="e.g. A disgraced quantum physicist discovers her alternate self has committed a murder she hasn't committed yet…",
    height=120,
)

generate_clicked = st.button("🎬 GENERATE FULL PREPRODUCTION PACKAGE",
                              use_container_width=True)
st.divider()


# ═════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═════════════════════════════════════════════════════════════════════════════

for k in [
    "main_output", "titles_output", "moodboard_output", "market_output",
    "expansion_output", "style_output", "theme_output", "budget_output",
    "project_title",
]:
    if k not in st.session_state:
        st.session_state[k] = ""


# ═════════════════════════════════════════════════════════════════════════════
# GENERATION PIPELINE
# ═════════════════════════════════════════════════════════════════════════════

if generate_clicked:
    if not idea.strip():
        st.warning("✏️ Please enter a story idea first.")
        st.stop()

    ddesc = DIRECTOR_STYLES[director]

    steps = [
        # (spinner label, lambda, session_key)
        (
            "🔤 Generating titles…",
            lambda: call_llm(
                build_title_prompt(genre, tone, idea, director,
                                   primary_theme, secondary_theme,
                                   "Poetic & Evocative"),
                min(temperature + 0.1, 1.5), 800,
            ),
            "titles_output",
        ),
        (
            "📜 Crafting script package…",
            lambda: call_llm(
                build_main_prompt(genre, tone, idea, director, ddesc, temp_label,
                                  primary_theme, secondary_theme,
                                  visual_style, film_scale),
                temperature, 3000,
            ),
            "main_output",
        ),
        (
            "🎨 Analysing style & scale…",
            lambda: call_llm(
                build_style_prompt(genre, tone, idea, director, visual_style,
                                   film_scale, aspect_ratio, rating,
                                   shooting_fmt, primary_theme),
                max(temperature - 0.1, 0.4), 1800,
            ),
            "style_output",
        ),
        (
            "🎭 Developing themes…",
            lambda: call_llm(
                build_theme_prompt(genre, tone, idea, director,
                                   primary_theme, secondary_theme),
                temperature, 1800,
            ),
            "theme_output",
        ),
        (
            "💰 Estimating budget…",
            lambda: call_llm(
                build_budget_prompt(genre, idea, budget, film_scale, visual_style,
                                    shooting_fmt, aspect_ratio, rating, director),
                max(temperature - 0.2, 0.3), 2000,
            ),
            "budget_output",
        ),
        (
            "🖼️ Building moodboard…",
            lambda: call_llm(
                build_moodboard_prompt(genre, tone, idea, director, ddesc),
                min(temperature + 0.1, 1.5), 1200,
            ),
            "moodboard_output",
        ),
        (
            "📊 Analysing market…",
            lambda: call_llm(
                build_market_prompt(genre, tone, idea, director, audience, budget),
                max(temperature - 0.2, 0.3), 1500,
            ),
            "market_output",
        ),
    ]

    for label, fn, key in steps:
        with st.spinner(label):
            try:
                st.session_state[key] = fn()
            except RuntimeError as e:
                st.error(str(e))
                st.stop()

    # Auto-extract project title
    first = [l for l in st.session_state["titles_output"].split("\n") if l.strip()]
    raw   = first[0].replace("**", "").replace("1.", "").strip() if first else "UNTITLED"
    st.session_state["project_title"] = raw

    st.success("✅ Full package ready! Explore every tab below.")


# ═════════════════════════════════════════════════════════════════════════════
# OUTPUT DISPLAY
# ═════════════════════════════════════════════════════════════════════════════

if st.session_state["main_output"]:

    proj = st.session_state["project_title"]
    st.markdown(
        f"## 🎬 Project: *{proj}*  &nbsp;&nbsp;"
        f'<span class="theme-pill">⭐ {primary_theme}</span>'
        f'<span class="theme-pill">➕ {secondary_theme}</span>',
        unsafe_allow_html=True,
    )
    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📜 Script",
        "🔤 Titles",          # ① NEW enhanced
        "🎨 Style & Scale",   # ② NEW
        "🎭 Themes",          # ③ NEW
        "💰 Budget",          # ④ NEW
        "🖼️ Moodboard",
        "📊 Market",
        "🔭 Expand Scene",
    ])

    # ── Tab 1 · Script Package ────────────────────────────────────────────────
    with tab1:
        render_card("📜", "Full Preproduction Package", st.session_state["main_output"])

        st.markdown("#### 💾 Download")
        full_txt = (
            f"FILM: {proj}\n"
            f"Genre: {genre} | Tone: {tone} | Director: {director}\n"
            f"Themes: {primary_theme} + {secondary_theme}\n"
            f"Visual Style: {visual_style} | Scale: {film_scale}\n"
            f"{'='*60}\n\n"
            + st.session_state["main_output"]
        )
        combined_md = (
            f"# 🎬 {proj}\n\n"
            f"**Genre:** {genre} | **Tone:** {tone} | **Director:** {director}\n\n"
            f"**Themes:** {primary_theme} + {secondary_theme}\n\n---\n\n"
            f"## Script\n{st.session_state['main_output']}\n\n"
            f"## Titles\n{st.session_state['titles_output']}\n\n"
            f"## Style & Scale\n{st.session_state['style_output']}\n\n"
            f"## Themes\n{st.session_state['theme_output']}\n\n"
            f"## Budget\n{st.session_state['budget_output']}\n\n"
            f"## Moodboard\n{st.session_state['moodboard_output']}\n\n"
            f"## Market\n{st.session_state['market_output']}\n"
        )
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button("⬇️ TXT", full_txt,
                               f"{proj.replace(' ','_')}.txt",
                               "text/plain", use_container_width=True)
        with d2:
            if PDF_AVAILABLE:
                try:
                    st.download_button("⬇️ PDF",
                                       generate_pdf(proj, full_txt),
                                       f"{proj.replace(' ','_')}.pdf",
                                       "application/pdf", use_container_width=True)
                except Exception as e:
                    st.caption(f"PDF error: {e}")
            else:
                st.caption("Install `reportlab` for PDF export")
        with d3:
            st.download_button("⬇️ Full Package MD", combined_md,
                               f"{proj.replace(' ','_')}_package.md",
                               "text/markdown", use_container_width=True)

    # ── Tab 2 · ① ENHANCED TITLE GENERATOR ───────────────────────────────────
    with tab2:
        st.markdown("#### 🔤 AI Title Generator")
        st.caption("Pick a naming style and regenerate anytime — each run gives 6 fresh options.")

        tc1, tc2 = st.columns([2, 1])
        with tc1:
            chosen_title_style = st.selectbox("Title Naming Style", TITLE_STYLES)
        with tc2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Generate Titles", use_container_width=True):
                with st.spinner("Generating titles…"):
                    try:
                        st.session_state["titles_output"] = call_llm(
                            build_title_prompt(genre, tone, idea, director,
                                               primary_theme, secondary_theme,
                                               chosen_title_style),
                            min(temperature + 0.2, 1.5), 800,
                        )
                        st.rerun()
                    except RuntimeError as e:
                        st.error(str(e))

        render_card("🔤", f"Titles — {chosen_title_style}",
                    st.session_state["titles_output"])
        st.download_button("⬇️ Download Titles TXT",
                           st.session_state["titles_output"],
                           "titles.txt", "text/plain")

    # ── Tab 3 · ② STYLE & SCALE ───────────────────────────────────────────────
    with tab3:
        st.markdown("#### 🎨 Cinematic Style & Production Scale Guide")
        st.markdown(
            f'<span class="theme-pill">🎨 {visual_style}</span>'
            f'<span class="theme-pill">🗺️ {film_scale}</span>'
            f'<span class="theme-pill">📐 {aspect_ratio}</span>'
            f'<span class="theme-pill">🎞️ {shooting_fmt}</span>'
            f'<span class="theme-pill">🔞 {rating}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        if st.session_state["style_output"]:
            render_card("🎨", "Style & Scale Breakdown",
                        st.session_state["style_output"])
        else:
            st.info("Generate the full package first to see this analysis.")

        if st.button("🔄 Regenerate Style Guide", use_container_width=True):
            with st.spinner("Analysing style & scale…"):
                try:
                    st.session_state["style_output"] = call_llm(
                        build_style_prompt(genre, tone, idea, director,
                                           visual_style, film_scale,
                                           aspect_ratio, rating,
                                           shooting_fmt, primary_theme),
                        max(temperature - 0.1, 0.4), 1800,
                    )
                    st.rerun()
                except RuntimeError as e:
                    st.error(str(e))

        if st.session_state["style_output"]:
            st.download_button("⬇️ Download Style Guide TXT",
                               st.session_state["style_output"],
                               "style_guide.txt", "text/plain")

    # ── Tab 4 · ③ THEMES ──────────────────────────────────────────────────────
    with tab4:
        st.markdown("#### 🎭 Thematic Development Guide")
        st.markdown(
            f'<span class="theme-pill">⭐ Primary: {primary_theme}</span>'
            f'<span class="theme-pill">➕ Secondary: {secondary_theme}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        if st.session_state["theme_output"]:
            render_card("🎭", f"Theme Analysis: {primary_theme} + {secondary_theme}",
                        st.session_state["theme_output"])
        else:
            st.info("Generate the full package first to see the Theme analysis.")

        if st.button("🔄 Regenerate Theme Analysis", use_container_width=True):
            with st.spinner("Developing themes…"):
                try:
                    st.session_state["theme_output"] = call_llm(
                        build_theme_prompt(genre, tone, idea, director,
                                           primary_theme, secondary_theme),
                        temperature, 1800,
                    )
                    st.rerun()
                except RuntimeError as e:
                    st.error(str(e))

        if st.session_state["theme_output"]:
            st.download_button("⬇️ Download Theme Guide TXT",
                               st.session_state["theme_output"],
                               "theme_guide.txt", "text/plain")

    # ── Tab 5 · ④ BUDGET ESTIMATOR ────────────────────────────────────────────
    with tab5:
        st.markdown("#### 💰 Production Budget Estimator")
        st.caption(
            f"Detailed line-item estimate for a **{budget}** production "
            f"at **{film_scale}** scale shooting on **{shooting_fmt}**."
        )

        # Quick-stat row
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            st.markdown(
                '<div class="metric-box"><div class="metric-label">Budget Tier</div>'
                f'<div class="metric-value" style="color:#00c864;font-size:1.1rem;">'
                f'{budget.split("(")[0].strip()}</div></div>',
                unsafe_allow_html=True,
            )
        with bc2:
            st.markdown(
                '<div class="metric-box"><div class="metric-label">Film Scale</div>'
                f'<div class="metric-value" style="color:#00c864;font-size:0.95rem;">'
                f'{film_scale.split("(")[0].strip()}</div></div>',
                unsafe_allow_html=True,
            )
        with bc3:
            st.markdown(
                '<div class="metric-box"><div class="metric-label">Format</div>'
                f'<div class="metric-value" style="color:#00c864;font-size:0.95rem;">'
                f'{shooting_fmt.split("(")[0].strip()}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("")

        if st.session_state["budget_output"]:
            render_card("💰", "Budget Breakdown",
                        st.session_state["budget_output"],
                        card_class="budget-card",
                        title_class="budget-title")
        else:
            st.info("Generate the full package first to see the Budget Estimate.")

        if st.button("🔄 Regenerate Budget Estimate", use_container_width=True):
            with st.spinner("Estimating budget…"):
                try:
                    st.session_state["budget_output"] = call_llm(
                        build_budget_prompt(genre, idea, budget, film_scale,
                                            visual_style, shooting_fmt,
                                            aspect_ratio, rating, director),
                        max(temperature - 0.2, 0.3), 2000,
                    )
                    st.rerun()
                except RuntimeError as e:
                    st.error(str(e))

        if st.session_state["budget_output"]:
            st.download_button("⬇️ Download Budget TXT",
                               st.session_state["budget_output"],
                               "budget_estimate.txt", "text/plain")

    # ── Tab 6 · Moodboard ─────────────────────────────────────────────────────
    with tab6:
        render_card("🖼️", "Visual Moodboard & Production Design",
                    st.session_state["moodboard_output"])

    # ── Tab 7 · Market Analysis ───────────────────────────────────────────────
    with tab7:
        render_card("📊", "Target Audience & Market Analysis",
                    st.session_state["market_output"])

    # ── Tab 8 · Scene Expansion ───────────────────────────────────────────────
    with tab8:
        st.markdown("#### 🔭 Scene Expansion")
        ec1, ec2 = st.columns([2, 1])
        with ec1:
            act = st.selectbox("Select Section to Expand", [
                "Act 1 — Setup", "Act 2 — Confrontation", "Act 3 — Resolution",
                "Opening Scene", "Climax Scene", "Flashback Sequence",
            ])
        with ec2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔭 EXPAND", use_container_width=True):
                with st.spinner(f"Expanding {act}…"):
                    try:
                        st.session_state["expansion_output"] = call_llm(
                            build_expansion_prompt(
                                act, genre, tone, idea,
                                director, DIRECTOR_STYLES[director],
                            ),
                            temperature, 2000,
                        )
                    except RuntimeError as e:
                        st.error(str(e))

        if st.session_state["expansion_output"]:
            render_card("🔭", f"Expansion: {act}",
                        st.session_state["expansion_output"])
            st.download_button("⬇️ Download Expansion TXT",
                               st.session_state["expansion_output"],
                               "scene_expansion.txt", "text/plain")


# ═════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown(
    "<div style='text-align:center;color:#444;font-size:0.78rem;padding:0.8rem 0;'>"
    "🎬 AI Film Preproduction Studio v2.0 &nbsp;|&nbsp; "
    "LLaMA 3.3 70B via Groq &nbsp;|&nbsp; Built with Streamlit"
    "</div>",
    unsafe_allow_html=True,
)