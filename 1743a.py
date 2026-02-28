  import streamlit as st
from openai import OpenAI
import os
from io import BytesIO
import re

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
.output-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(245,197,24,0.2);
    border-left: 4px solid #f5c518; border-radius: 8px;
    padding: 1.4rem 1.6rem; margin: 1rem 0;
}
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
.visual-banner {
    border-radius: 8px; overflow: hidden; position: relative;
    border: 1px solid rgba(245,197,24,0.3);
}
.visual-label {
    font-family: 'Bebas Neue', cursive; font-size: 0.85rem;
    letter-spacing: 2px; color: #f5c518; margin-bottom: 0.4rem;
    text-transform: uppercase;
}
.img-overlay-card {
    position: relative; border-radius: 8px; overflow: hidden;
    border: 1px solid rgba(245,197,24,0.25);
    margin: 4px 0;
}
.tone-grid-label {
    font-family: 'Bebas Neue', cursive; font-size: 1.1rem;
    letter-spacing: 2px; color: #f5c518; margin: 0.8rem 0 0.5rem;
}
.scene-visual-header {
    font-family: 'Bebas Neue', cursive; font-size: 1.2rem;
    letter-spacing: 2px; color: #ff6b35; margin: 1rem 0 0.6rem;
}
.aspect-ratio-frame {
    border: 2px solid #f5c518;
    background: linear-gradient(135deg, rgba(245,197,24,0.05), rgba(255,107,53,0.05));
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    position: relative; overflow: hidden; margin: 0 auto;
}
.color-swatch-row { display: flex; gap: 8px; margin: 0.6rem 0; flex-wrap: wrap; }
.color-swatch {
    width: 48px; height: 48px; border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.15);
    display: inline-block; position: relative; cursor: pointer;
    transition: transform 0.15s;
}
.color-swatch:hover { transform: scale(1.1); }
.color-hex { font-size: 0.62rem; color: #aaa; text-align: center; margin-top: 2px; font-family: monospace; }
.prompt-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(245,197,24,0.25);
    border-radius: 8px; padding: 1rem 1.2rem; margin: 0.6rem 0;
    font-family: 'Courier New', monospace; font-size: 0.82rem;
    color: #c8c8e0; line-height: 1.5; position: relative;
}
.prompt-card-label {
    font-family: 'Bebas Neue', cursive; font-size: 0.85rem;
    letter-spacing: 2px; color: #f5c518; margin-bottom: 0.4rem;
}
.director-ref-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(245,197,24,0.2);
    border-radius: 8px; overflow: hidden; text-align: center; padding-bottom: 0.6rem;
}
.sidebar-preview-card {
    background: rgba(245,197,24,0.06); border: 1px solid rgba(245,197,24,0.2);
    border-radius: 6px; padding: 0.6rem; margin-top: 0.4rem; text-align: center;
}
.section-visual-banner {
    font-family: 'Bebas Neue', cursive; font-size: 1.0rem;
    letter-spacing: 2px; color: #f5c518; margin: 0.8rem 0 0.5rem;
    padding-bottom: 0.3rem; border-bottom: 1px solid rgba(245,197,24,0.2);
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

DIRECTOR_IMAGES = {
    "Christopher Nolan":  "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=300&q=80",
    "Quentin Tarantino":  "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=300&q=80",
    "Wes Anderson":       "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=300&q=80",
    "Denis Villeneuve":   "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=300&q=80",
    "Bong Joon-ho":       "https://images.unsplash.com/photo-1555400038-63f5ba517a47?w=300&q=80",
    "Ari Aster":          "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&q=80",
    "Sofia Coppola":      "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=300&q=80",
    "No Specific Style":  "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=300&q=80",
}

DIRECTOR_KEYWORDS = {
    "Christopher Nolan":  "Time · Practical FX · IMAX",
    "Quentin Tarantino":  "Dialogue · Chapter cuts · Tension",
    "Wes Anderson":       "Symmetry · Pastels · Whimsy",
    "Denis Villeneuve":   "Silence · Philosophy · Scale",
    "Bong Joon-ho":       "Class · Dark comedy · Genre-blend",
    "Ari Aster":          "Dread · Folk horror · Long takes",
    "Sofia Coppola":      "Mood · Atmosphere · Female gaze",
    "No Specific Style":  "Balanced · Industry-standard",
}

GENRES    = ["Crime/Thriller", "Sci-Fi", "Drama", "Horror", "Romance",
             "Comedy", "Action/Adventure", "Fantasy", "Historical Epic"]
TONES     = ["Dark & Brooding", "Suspenseful", "Emotional & Raw",
             "Light-hearted", "Intense", "Whimsical", "Satirical"]
AUDIENCES = ["General Audiences (PG-13)", "Young Adults 18-25", "Adults 25-45",
             "Family (All Ages)", "Niche/Art-house", "Genre Enthusiasts"]
BUDGETS   = ["Micro-budget (<$1M)", "Indie ($1M-$10M)", "Mid-range ($10M-$50M)",
             "Studio ($50M-$150M)", "Blockbuster ($150M+)"]

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
    "2.39:1 (Cinemascope)",
    "1.85:1 (Flat Widescreen)",
    "1.33:1 (Academy / Vintage)",
    "1.78:1 (16:9 Streaming)",
    "2.76:1 (Ultra Panavision)",
]
ASPECT_RATIO_VALUES = {
    "2.39:1 (Cinemascope)":    (2.39, 1),
    "1.85:1 (Flat Widescreen)":(1.85, 1),
    "1.33:1 (Academy / Vintage)":(1.33, 1),
    "1.78:1 (16:9 Streaming)": (1.78, 1),
    "2.76:1 (Ultra Panavision)":(2.76, 1),
}
ASPECT_RATIO_NOTES = {
    "2.39:1 (Cinemascope)":    "Ultra-wide — epic landscapes, intimate close-ups with breathing room",
    "1.85:1 (Flat Widescreen)":"Most common cinema ratio — balanced framing",
    "1.33:1 (Academy / Vintage)":"Square-ish — vintage feel, claustrophobic or intimate stories",
    "1.78:1 (16:9 Streaming)": "Native streaming — maximises platform delivery",
    "2.76:1 (Ultra Panavision)":"Extreme widescreen — reserved for true epics",
}

RATINGS = [
    "G / U (Universal)", "PG / PG-13", "R / 15 (Mature)",
    "NC-17 / 18 (Adult)", "Not Yet Rated",
]
SHOOTING_FMTS = [
    "Digital (ARRI Alexa)", "Digital (RED Camera)",
    "35mm Film", "16mm Film", "IMAX", "Handheld / Verite",
]

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

TITLE_STYLES = [
    "Poetic & Evocative",
    "Short & Punchy (1-2 words)",
    "Mysterious & Cryptic",
    "Action / Thriller Style",
    "Character Name as Title",
    "Question / Provocative",
    "Metaphorical / Symbolic",
]

# ── Genre concept art images ───────────────────────────────────────────────────
GENRE_CONCEPT_IMAGES = {
    "Crime/Thriller":   [
        ("https://images.unsplash.com/photo-1514036783265-fba9577fc473?w=400&q=80", "Neon-lit street"),
        ("https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400&q=80", "City at night"),
        ("https://images.unsplash.com/photo-1504253163759-c23fccaebb55?w=400&q=80", "Dark alley"),
    ],
    "Sci-Fi":           [
        ("https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=400&q=80", "Deep space"),
        ("https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80", "Earth from orbit"),
        ("https://images.unsplash.com/photo-1464802686167-b939a6910659?w=400&q=80", "Nebula"),
    ],
    "Drama":            [
        ("https://images.unsplash.com/photo-1518834107812-67b0b7c58434?w=400&q=80", "Golden hour"),
        ("https://images.unsplash.com/photo-1499084732479-de2c02d45fcc?w=400&q=80", "Window light"),
        ("https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&q=80", "Vast landscape"),
    ],
    "Horror":           [
        ("https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=400&q=80", "Abandoned building"),
        ("https://images.unsplash.com/photo-1474508eba7-f1c99e2e9401?w=400&q=80", "Foggy forest"),
        ("https://images.unsplash.com/photo-1604076913837-52ab5629fde9?w=400&q=80", "Dark corridor"),
    ],
    "Romance":          [
        ("https://images.unsplash.com/photo-1518199266791-5375a83190b7?w=400&q=80", "Sunset silhouette"),
        ("https://images.unsplash.com/photo-1474552226712-ac0f0961a954?w=400&q=80", "Paris streets"),
        ("https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=400&q=80", "Soft light mood"),
    ],
    "Comedy":           [
        ("https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400&q=80", "Bright colours"),
        ("https://images.unsplash.com/photo-1543584756-8f8b099e7a95?w=400&q=80", "Street festival"),
        ("https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=400&q=80", "Urban fun"),
    ],
    "Action/Adventure": [
        ("https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80", "Mountain epic"),
        ("https://images.unsplash.com/photo-1682686581854-5e71f58e7e3f?w=400&q=80", "Desert dunes"),
        ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80", "Alpine peak"),
    ],
    "Fantasy":          [
        ("https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=400&q=80", "Mystical forest"),
        ("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400&q=80", "Ancient ruins"),
        ("https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?w=400&q=80", "Starry sky"),
    ],
    "Historical Epic":  [
        ("https://images.unsplash.com/photo-1461360228754-6e81c478b882?w=400&q=80", "Ancient stone"),
        ("https://images.unsplash.com/photo-1548013146-72479768bada?w=400&q=80", "Roman columns"),
        ("https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=400&q=80", "Dramatic sky"),
    ],
}

# ── Extended genre images (for secondary mood boards & scene viz) ──────────────
GENRE_EXTENDED_IMAGES = {
    "Crime/Thriller": [
        ("https://images.unsplash.com/photo-1573408301185-9519f94f3ca7?w=500&q=80", "Rain-soaked pavement"),
        ("https://images.unsplash.com/photo-1596349583744-7abe7a7c0b94?w=500&q=80", "Police tape"),
        ("https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=500&q=80", "Urban surveillance"),
        ("https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=500&q=80", "Interrogation light"),
        ("https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=500&q=80", "Shadows & silhouette"),
    ],
    "Sci-Fi": [
        ("https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=500&q=80", "Robot/AI"),
        ("https://images.unsplash.com/photo-1516339901601-2e1b62dc0c45?w=500&q=80", "Futuristic city"),
        ("https://images.unsplash.com/photo-1569336415962-a4bd9f69cd83?w=500&q=80", "Space station"),
        ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500&q=80", "Alien landscape"),
        ("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500&q=80", "Neon cyberpunk"),
    ],
    "Drama": [
        ("https://images.unsplash.com/photo-1517649763962-0c623066013b?w=500&q=80", "Contemplative moment"),
        ("https://images.unsplash.com/photo-1509909756405-be0199881695?w=500&q=80", "Rainy window"),
        ("https://images.unsplash.com/photo-1542596768-5d1d21f1cf98?w=500&q=80", "Emotional portrait"),
        ("https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=500&q=80", "Human connection"),
        ("https://images.unsplash.com/photo-1516912481808-3406841bd33c?w=500&q=80", "Family drama"),
    ],
    "Horror": [
        ("https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=500&q=80", "Creepy forest"),
        ("https://images.unsplash.com/photo-1516912481808-3406841bd33c?w=500&q=80", "Moonlit night"),
        ("https://images.unsplash.com/photo-1561736778-92e52a7769ef?w=500&q=80", "Misty graveyard"),
        ("https://images.unsplash.com/photo-1572363933776-5bf6ebce3e62?w=500&q=80", "Broken windows"),
        ("https://images.unsplash.com/photo-1527488272489-1fd5c1023ae5?w=500&q=80", "Eerie darkness"),
    ],
    "Romance": [
        ("https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=500&q=80", "Golden hour couple"),
        ("https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?w=500&q=80", "Candlelit dinner"),
        ("https://images.unsplash.com/photo-1484982680576-dc8c47ee9a56?w=500&q=80", "Floral romance"),
        ("https://images.unsplash.com/photo-1494774157365-9e04c6720e47?w=500&q=80", "Beach sunset"),
        ("https://images.unsplash.com/photo-1474552226712-ac0f0961a954?w=500&q=80", "Café love"),
    ],
    "Comedy": [
        ("https://images.unsplash.com/photo-1527549993586-dff825b37782?w=500&q=80", "Confetti party"),
        ("https://images.unsplash.com/photo-1467810563316-b5476525c0f9?w=500&q=80", "Friends laughing"),
        ("https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=500&q=80", "Circus fun"),
        ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&q=80", "Absurd moment"),
        ("https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=500&q=80", "Street joy"),
    ],
    "Action/Adventure": [
        ("https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500&q=80", "Desert chase"),
        ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500&q=80", "Mountain summit"),
        ("https://images.unsplash.com/photo-1502512403831-3cc45a2e2566?w=500&q=80", "Ocean adventure"),
        ("https://images.unsplash.com/photo-1553361371-9b22f78e8b1d?w=500&q=80", "Jungle trek"),
        ("https://images.unsplash.com/photo-1519681393784-d120267933ba?w=500&q=80", "Epic vista"),
    ],
    "Fantasy": [
        ("https://images.unsplash.com/photo-1511497584788-876760111969?w=500&q=80", "Enchanted forest"),
        ("https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?w=500&q=80", "Cosmic sky"),
        ("https://images.unsplash.com/photo-1520637836993-5e68659a7c4d?w=500&q=80", "Mystical waterfall"),
        ("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&q=80", "Ancient temple"),
        ("https://images.unsplash.com/photo-1501854140801-50d01698950b?w=500&q=80", "Dragon sky"),
    ],
    "Historical Epic": [
        ("https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=500&q=80", "Roman arena"),
        ("https://images.unsplash.com/photo-1548013146-72479768bada?w=500&q=80", "Marble columns"),
        ("https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=500&q=80", "Battle sky"),
        ("https://images.unsplash.com/photo-1568402102990-bc541580b59f?w=500&q=80", "Ancient map"),
        ("https://images.unsplash.com/photo-1461360228754-6e81c478b882?w=500&q=80", "Stone fortress"),
    ],
}

# ── Tone visual images ──────────────────────────────────────────────────────────
TONE_IMAGES = {
    "Dark & Brooding": [
        ("https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=400&q=80", "Noir shadows"),
        ("https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&q=80", "Urban darkness"),
        ("https://images.unsplash.com/photo-1519709042477-8de4668a10c4?w=400&q=80", "Brooding light"),
    ],
    "Suspenseful": [
        ("https://images.unsplash.com/photo-1573408301185-9519f94f3ca7?w=400&q=80", "Tension moment"),
        ("https://images.unsplash.com/photo-1524594081293-190a2fe9a1b8?w=400&q=80", "Waiting"),
        ("https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=400&q=80", "Watchful eyes"),
    ],
    "Emotional & Raw": [
        ("https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&q=80", "Raw emotion"),
        ("https://images.unsplash.com/photo-1542596768-5d1d21f1cf98?w=400&q=80", "Human feeling"),
        ("https://images.unsplash.com/photo-1517649763962-0c623066013b?w=400&q=80", "Intimate moment"),
    ],
    "Light-hearted": [
        ("https://images.unsplash.com/photo-1527549993586-dff825b37782?w=400&q=80", "Sunny joy"),
        ("https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=400&q=80", "Street cheer"),
        ("https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400&q=80", "Bright colours"),
    ],
    "Intense": [
        ("https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&q=80", "High stakes"),
        ("https://images.unsplash.com/photo-1516912481808-3406841bd33c?w=400&q=80", "Dramatic sky"),
        ("https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400&q=80", "Epic scale"),
    ],
    "Whimsical": [
        ("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80", "Pastel world"),
        ("https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=400&q=80", "Fairy tale forest"),
        ("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400&q=80", "Magical ruins"),
    ],
    "Satirical": [
        ("https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=400&q=80", "Absurdist scene"),
        ("https://images.unsplash.com/photo-1555400038-63f5ba517a47?w=400&q=80", "Urban irony"),
        ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80", "Comic tension"),
    ],
}

# ── Theme visual images ─────────────────────────────────────────────────────────
THEME_IMAGES = {
    "Redemption": [
        ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80", "Light through darkness"),
        ("https://images.unsplash.com/photo-1499084732479-de2c02d45fcc?w=400&q=80", "Journey's end"),
    ],
    "Identity & Self-Discovery": [
        ("https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&q=80", "Reflection"),
        ("https://images.unsplash.com/photo-1542596768-5d1d21f1cf98?w=400&q=80", "Inner world"),
    ],
    "Power & Corruption": [
        ("https://images.unsplash.com/photo-1555400038-63f5ba517a47?w=400&q=80", "City power"),
        ("https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&q=80", "Shadows of control"),
    ],
    "Love & Loss": [
        ("https://images.unsplash.com/photo-1518199266791-5375a83190b7?w=400&q=80", "Fleeting moment"),
        ("https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=400&q=80", "Bittersweet light"),
    ],
    "Survival": [
        ("https://images.unsplash.com/photo-1519519166432-1aa62fb68e48?w=400&q=80", "Wilderness"),
        ("https://images.unsplash.com/photo-1504253163759-c23fccaebb55?w=400&q=80", "Lone figure"),
    ],
    "Justice vs Revenge": [
        ("https://images.unsplash.com/photo-1514036783265-fba9577fc473?w=400&q=80", "Night justice"),
        ("https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=400&q=80", "Confrontation"),
    ],
    "Technology vs Humanity": [
        ("https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&q=80", "Machine vs man"),
        ("https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80", "Digital world"),
    ],
    "Class & Inequality": [
        ("https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400&q=80", "City divide"),
        ("https://images.unsplash.com/photo-1516339901601-2e1b62dc0c45?w=400&q=80", "Two worlds"),
    ],
    "Grief & Healing": [
        ("https://images.unsplash.com/photo-1509909756405-be0199881695?w=400&q=80", "Rainy solitude"),
        ("https://images.unsplash.com/photo-1517649763962-0c623066013b?w=400&q=80", "Quiet strength"),
    ],
    "War & Its Consequences": [
        ("https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=400&q=80", "Aftermath sky"),
        ("https://images.unsplash.com/photo-1461360228754-6e81c478b882?w=400&q=80", "Ruins of war"),
    ],
    "Family & Legacy": [
        ("https://images.unsplash.com/photo-1516512203093-cc62e26bbae1?w=400&q=80", "Family bond"),
        ("https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&q=80", "Heritage land"),
    ],
    "Freedom vs Control": [
        ("https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400&q=80", "Open horizon"),
        ("https://images.unsplash.com/photo-1573408301185-9519f94f3ca7?w=400&q=80", "Confined space"),
    ],
    # defaults for secondary themes not explicitly mapped
    "Betrayal": [
        ("https://images.unsplash.com/photo-1524594081293-190a2fe9a1b8?w=400&q=80", "Hidden truth"),
        ("https://images.unsplash.com/photo-1504253163759-c23fccaebb55?w=400&q=80", "Dark secrets"),
    ],
    "Sacrifice": [
        ("https://images.unsplash.com/photo-1499084732479-de2c02d45fcc?w=400&q=80", "Last light"),
        ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80", "Summit moment"),
    ],
    "Isolation": [
        ("https://images.unsplash.com/photo-1519519166432-1aa62fb68e48?w=400&q=80", "Lone wilderness"),
        ("https://images.unsplash.com/photo-1509909756405-be0199881695?w=400&q=80", "Empty room"),
    ],
    "Memory & Nostalgia": [
        ("https://images.unsplash.com/photo-1518834107812-67b0b7c58434?w=400&q=80", "Golden haze"),
        ("https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=400&q=80", "Faded beauty"),
    ],
    "Fate vs Free Will": [
        ("https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?w=400&q=80", "Starlit destiny"),
        ("https://images.unsplash.com/photo-1519709042477-8de4668a10c4?w=400&q=80", "Crossroads"),
    ],
    "Coming of Age": [
        ("https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=400&q=80", "Youth energy"),
        ("https://images.unsplash.com/photo-1517649763962-0c623066013b?w=400&q=80", "Growing moment"),
    ],
    "Trust & Deception": [
        ("https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=400&q=80", "Hidden faces"),
        ("https://images.unsplash.com/photo-1596349583744-7abe7a7c0b94?w=400&q=80", "Fractured trust"),
    ],
    "Ambition": [
        ("https://images.unsplash.com/photo-1516912481808-3406841bd33c?w=400&q=80", "Sky's the limit"),
        ("https://images.unsplash.com/photo-1555400038-63f5ba517a47?w=400&q=80", "City ambition"),
    ],
    "Race & Culture": [
        ("https://images.unsplash.com/photo-1543584756-8f8b099e7a95?w=400&q=80", "Cultural richness"),
        ("https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=400&q=80", "Many worlds"),
    ],
    "Gender & Identity": [
        ("https://images.unsplash.com/photo-1542596768-5d1d21f1cf98?w=400&q=80", "Self expression"),
        ("https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&q=80", "Own mirror"),
    ],
    "Environmental Destruction": [
        ("https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=400&q=80", "Scorched earth"),
        ("https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=400&q=80", "Last forest"),
    ],
    "Religion & Faith": [
        ("https://images.unsplash.com/photo-1548013146-72479768bada?w=400&q=80", "Ancient temple"),
        ("https://images.unsplash.com/photo-1461360228754-6e81c478b882?w=400&q=80", "Sacred stone"),
    ],
    "Addiction": [
        ("https://images.unsplash.com/photo-1527488272489-1fd5c1023ae5?w=400&q=80", "Fractured reality"),
        ("https://images.unsplash.com/photo-1519709042477-8de4668a10c4?w=400&q=80", "Hazy nights"),
    ],
    "Redemption of the Villain": [
        ("https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&q=80", "Turning point"),
        ("https://images.unsplash.com/photo-1504253163759-c23fccaebb55?w=400&q=80", "Last chance"),
    ],
}

# ── Script/scene visualization images ─────────────────────────────────────────
SCENE_VISUAL_IMAGES = {
    "Crime/Thriller": [
        ("https://images.unsplash.com/photo-1514036783265-fba9577fc473?w=600&q=80", "ACT I – The Setup"),
        ("https://images.unsplash.com/photo-1573408301185-9519f94f3ca7?w=600&q=80", "ACT II – Rising Stakes"),
        ("https://images.unsplash.com/photo-1596349583744-7abe7a7c0b94?w=600&q=80", "ACT III – The Reckoning"),
        ("https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=600&q=80", "Key Scene – Chase"),
        ("https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=600&q=80", "Key Scene – Confrontation"),
    ],
    "Sci-Fi": [
        ("https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=600&q=80", "ACT I – New World"),
        ("https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&q=80", "ACT II – First Contact"),
        ("https://images.unsplash.com/photo-1516339901601-2e1b62dc0c45?w=600&q=80", "ACT III – Beyond"),
        ("https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=80", "Key Scene – Orbit"),
        ("https://images.unsplash.com/photo-1569336415962-a4bd9f69cd83?w=600&q=80", "Key Scene – Discovery"),
    ],
    "Drama": [
        ("https://images.unsplash.com/photo-1518834107812-67b0b7c58434?w=600&q=80", "ACT I – Ordinary World"),
        ("https://images.unsplash.com/photo-1509909756405-be0199881695?w=600&q=80", "ACT II – Breaking Point"),
        ("https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&q=80", "ACT III – Resolution"),
        ("https://images.unsplash.com/photo-1542596768-5d1d21f1cf98?w=600&q=80", "Key Scene – Revelation"),
        ("https://images.unsplash.com/photo-1517649763962-0c623066013b?w=600&q=80", "Key Scene – Quiet"),
    ],
    "Horror": [
        ("https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=600&q=80", "ACT I – Unease"),
        ("https://images.unsplash.com/photo-1474508eba7-f1c99e2e9401?w=600&q=80", "ACT II – Terror"),
        ("https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=600&q=80", "ACT III – Dread"),
        ("https://images.unsplash.com/photo-1527488272489-1fd5c1023ae5?w=600&q=80", "Key Scene – Discovery"),
        ("https://images.unsplash.com/photo-1572363933776-5bf6ebce3e62?w=600&q=80", "Key Scene – Escape"),
    ],
    "Romance": [
        ("https://images.unsplash.com/photo-1518199266791-5375a83190b7?w=600&q=80", "ACT I – Meeting"),
        ("https://images.unsplash.com/photo-1474552226712-ac0f0961a954?w=600&q=80", "ACT II – Falling"),
        ("https://images.unsplash.com/photo-1494774157365-9e04c6720e47?w=600&q=80", "ACT III – Forever"),
        ("https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?w=600&q=80", "Key Scene – First Date"),
        ("https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=600&q=80", "Key Scene – Declaration"),
    ],
    "Comedy": [
        ("https://images.unsplash.com/photo-1527549993586-dff825b37782?w=600&q=80", "ACT I – The Misadventure"),
        ("https://images.unsplash.com/photo-1467810563316-b5476525c0f9?w=600&q=80", "ACT II – Chaos"),
        ("https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=600&q=80", "ACT III – Triumph"),
        ("https://images.unsplash.com/photo-1543584756-8f8b099e7a95?w=600&q=80", "Key Scene – The Joke"),
        ("https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&q=80", "Key Scene – Reunion"),
    ],
    "Action/Adventure": [
        ("https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&q=80", "ACT I – The Call"),
        ("https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80", "ACT II – The Journey"),
        ("https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600&q=80", "ACT III – The Summit"),
        ("https://images.unsplash.com/photo-1502512403831-3cc45a2e2566?w=600&q=80", "Key Scene – Danger"),
        ("https://images.unsplash.com/photo-1553361371-9b22f78e8b1d?w=600&q=80", "Key Scene – Victory"),
    ],
    "Fantasy": [
        ("https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=600&q=80", "ACT I – The Realm"),
        ("https://images.unsplash.com/photo-1511497584788-876760111969?w=600&q=80", "ACT II – The Quest"),
        ("https://images.unsplash.com/photo-1520637836993-5e68659a7c4d?w=600&q=80", "ACT III – The Magic"),
        ("https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?w=600&q=80", "Key Scene – Portal"),
        ("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&q=80", "Key Scene – Battle"),
    ],
    "Historical Epic": [
        ("https://images.unsplash.com/photo-1461360228754-6e81c478b882?w=600&q=80", "ACT I – The Era"),
        ("https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=600&q=80", "ACT II – The Conflict"),
        ("https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=600&q=80", "ACT III – The Legacy"),
        ("https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80", "Key Scene – The Court"),
        ("https://images.unsplash.com/photo-1568402102990-bc541580b59f?w=600&q=80", "Key Scene – The Plan"),
    ],
}

# ── Shooting format images ────────────────────────────────────────────────────
SHOOTING_FORMAT_IMAGES = {
    "Digital (ARRI Alexa)": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&q=80",
    "Digital (RED Camera)": "https://images.unsplash.com/photo-1516912481808-3406841bd33c?w=400&q=80",
    "35mm Film": "https://images.unsplash.com/photo-1518834107812-67b0b7c58434?w=400&q=80",
    "16mm Film": "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=400&q=80",
    "IMAX": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&q=80",
    "Handheld / Verite": "https://images.unsplash.com/photo-1573408301185-9519f94f3ca7?w=400&q=80",
}

# ── Visual style images ─────────────────────────────────────────────────────
VISUAL_STYLE_IMAGES = {
    "Naturalistic / Realistic": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&q=80",
    "Hyper-stylised": "https://images.unsplash.com/photo-1514036783265-fba9577fc473?w=400&q=80",
    "Noir / High Contrast": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&q=80",
    "Dreamlike / Surreal": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
    "Gritty Documentary": "https://images.unsplash.com/photo-1573408301185-9519f94f3ca7?w=400&q=80",
    "Glossy Commercial": "https://images.unsplash.com/photo-1516912481808-3406841bd33c?w=400&q=80",
    "Minimalist": "https://images.unsplash.com/photo-1518834107812-67b0b7c58434?w=400&q=80",
    "Epic / Grand Spectacle": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400&q=80",
}


# ═════════════════════════════════════════════════════════════════════════════
# API CLIENT
# ═════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_client():
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",
        "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"))
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def call_llm(prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
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
        if "401" in err:                               raise RuntimeError("❌ API key invalid.")
        elif "429" in err:                             raise RuntimeError("⏳ Rate limit hit.")
        elif "timeout" in err or "connect" in err:    raise RuntimeError("🌐 Network error.")
        else:                                          raise RuntimeError(f"🔧 API error: {err}")


# ═════════════════════════════════════════════════════════════════════════════
# IMAGE HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def section_header(icon, text):
    st.markdown(
        f'<div class="section-visual-banner">{icon} {text}</div>',
        unsafe_allow_html=True,
    )


def render_aspect_ratio_preview(ratio_key: str):
    w, h = ASPECT_RATIO_VALUES.get(ratio_key, (1.78, 1))
    ratio_float = w / h
    display_w = 340
    display_h = int(display_w / ratio_float)
    label = ratio_key.split("(")[0].strip()
    note  = ASPECT_RATIO_NOTES.get(ratio_key, "")

    svg = f"""
    <div style="text-align:center; margin: 1rem 0;">
      <svg width="{display_w}" height="{display_h + 60}" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="frameGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#1a1a2e"/>
            <stop offset="100%" stop-color="#0d0d18"/>
          </linearGradient>
        </defs>
        <rect x="2" y="2" width="{display_w - 4}" height="{display_h - 4}"
              fill="url(#frameGrad)" stroke="#f5c518" stroke-width="2" rx="3"/>
        <line x1="{display_w//3}" y1="2" x2="{display_w//3}" y2="{display_h - 4}"
              stroke="rgba(245,197,24,0.15)" stroke-width="1" stroke-dasharray="4,4"/>
        <line x1="{2*display_w//3}" y1="2" x2="{2*display_w//3}" y2="{display_h - 4}"
              stroke="rgba(245,197,24,0.15)" stroke-width="1" stroke-dasharray="4,4"/>
        <line x1="2" y1="{display_h//2}" x2="{display_w - 4}" y2="{display_h//2}"
              stroke="rgba(245,197,24,0.10)" stroke-width="1" stroke-dasharray="4,4"/>
        <circle cx="{display_w//2}" cy="{display_h//2}" r="6"
                fill="none" stroke="rgba(245,197,24,0.4)" stroke-width="1"/>
        <line x1="{display_w//2 - 12}" y1="{display_h//2}"
              x2="{display_w//2 + 12}" y2="{display_h//2}"
              stroke="rgba(245,197,24,0.4)" stroke-width="1"/>
        <line x1="{display_w//2}" y1="{display_h//2 - 12}"
              x2="{display_w//2}" y2="{display_h//2 + 12}"
              stroke="rgba(245,197,24,0.4)" stroke-width="1"/>
        <text x="{display_w//2}" y="{display_h//2 + 36}"
              text-anchor="middle" font-family="'Bebas Neue', cursive"
              font-size="22" fill="#f5c518" opacity="0.7">{label}</text>
        <text x="8" y="{display_h - 8}" font-family="monospace"
              font-size="9" fill="rgba(245,197,24,0.5)">{display_w}px</text>
        <text x="{display_w - 8}" y="16" text-anchor="end" font-family="monospace"
              font-size="9" fill="rgba(245,197,24,0.5)">{display_h}px</text>
        <path d="M2,14 L2,2 L14,2" fill="none" stroke="#f5c518" stroke-width="2"/>
        <path d="M{display_w-14},2 L{display_w-2},2 L{display_w-2},14"
              fill="none" stroke="#f5c518" stroke-width="2"/>
        <path d="M2,{display_h-14} L2,{display_h-2} L14,{display_h-2}"
              fill="none" stroke="#f5c518" stroke-width="2"/>
        <path d="M{display_w-14},{display_h-2} L{display_w-2},{display_h-2} L{display_w-2},{display_h-14}"
              fill="none" stroke="#f5c518" stroke-width="2"/>
      </svg>
      <div style="margin-top:0.4rem; color:#8888a8; font-size:0.75rem; max-width:{display_w}px; margin-left:auto; margin-right:auto;">
        {note}
      </div>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)


def extract_hex_colors(text: str) -> list[str]:
    return re.findall(r'#(?:[0-9a-fA-F]{6})', text)


def render_color_palette(hex_codes: list[str]):
    if not hex_codes:
        return
    swatches = "".join(
        f'<div style="display:inline-block;margin:4px;">'
        f'<div style="background:{c};width:52px;height:52px;border-radius:8px;'
        f'border:1px solid rgba(255,255,255,0.15);display:inline-block;"></div>'
        f'<div style="font-size:0.62rem;color:#aaa;text-align:center;margin-top:2px;font-family:monospace;">{c}</div></div>'
        for c in hex_codes[:8]
    )
    st.markdown(
        f'<div style="margin:0.8rem 0;">'
        f'<div style="font-family:\'Bebas Neue\',cursive;font-size:1rem;'
        f'letter-spacing:2px;color:#f5c518;margin-bottom:0.5rem;">🎨 Extracted Colour Palette</div>'
        f'<div style="display:flex;gap:8px;margin:0.6rem 0;flex-wrap:wrap;">{swatches}</div></div>',
        unsafe_allow_html=True,
    )


def extract_image_prompts(text: str) -> list[str]:
    prompts = []
    lines = text.split("\n")
    in_prompts = False
    for line in lines:
        stripped = line.strip()
        if any(kw in stripped.lower() for kw in ["midjourney", "image prompt", "ai prompt", "prompt:"]):
            in_prompts = True
        if in_prompts and stripped and len(stripped) > 40:
            clean = re.sub(r'^[\d\.\)\-\*]+\s*', '', stripped)
            if len(clean) > 30 and not clean.lower().startswith(("here", "below", "the following")):
                prompts.append(clean)
        if len(prompts) >= 3:
            break
    return prompts


def render_concept_art_grid(genre: str):
    images = GENRE_CONCEPT_IMAGES.get(genre, GENRE_CONCEPT_IMAGES["Drama"])
    section_header("🖼️", "Genre Concept Art Reference")
    cols = st.columns(3)
    for col, (url, caption) in zip(cols, images):
        with col:
            st.image(url, caption=caption, use_container_width=True)


def render_director_sidebar_preview(director: str):
    img_url = DIRECTOR_IMAGES.get(director, DIRECTOR_IMAGES["No Specific Style"])
    keywords = DIRECTOR_KEYWORDS.get(director, "")
    st.markdown(
        f'<div class="sidebar-preview-card">'
        f'<div style="font-family:\'Bebas Neue\',cursive;font-size:0.8rem;'
        f'letter-spacing:1.5px;color:#f5c518;margin-bottom:0.3rem;">🎥 VISUAL SIGNATURE</div>',
        unsafe_allow_html=True,
    )
    st.image(img_url, use_container_width=True)
    st.markdown(
        f'<div style="font-size:0.68rem;color:#8888a8;text-align:center;'
        f'margin-top:0.3rem;letter-spacing:1px;">{keywords}</div></div>',
        unsafe_allow_html=True,
    )


def render_character_visuals(genre: str, main_output: str):
    images = GENRE_CONCEPT_IMAGES.get(genre, GENRE_CONCEPT_IMAGES["Drama"])
    char_labels = ["Protagonist Mood", "Antagonist Atmosphere", "World / Setting"]
    section_header("🎭", "Character Visual References")
    cols = st.columns(3)
    for col, (url, _), label in zip(cols, images, char_labels):
        with col:
            st.image(url, caption=label, use_container_width=True)


def render_genre_tone_visual_panel(genre: str, tone: str):
    """NEW: Big visual panel showing genre + tone imagery side by side."""
    section_header("🎬", f"Visual Atmosphere — {genre} · {tone}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="visual-label">📽️ Genre: {genre}</div>',
            unsafe_allow_html=True,
        )
        genre_imgs = GENRE_CONCEPT_IMAGES.get(genre, GENRE_CONCEPT_IMAGES["Drama"])
        st.image(genre_imgs[0][0], caption=genre_imgs[0][1], use_container_width=True)
        cols_inner = st.columns(2)
        with cols_inner[0]:
            st.image(genre_imgs[1][0], caption=genre_imgs[1][1], use_container_width=True)
        with cols_inner[1]:
            st.image(genre_imgs[2][0], caption=genre_imgs[2][1], use_container_width=True)

    with col2:
        st.markdown(
            f'<div class="visual-label">🎭 Tone: {tone}</div>',
            unsafe_allow_html=True,
        )
        tone_imgs = TONE_IMAGES.get(tone, TONE_IMAGES["Dark & Brooding"])
        st.image(tone_imgs[0][0], caption=tone_imgs[0][1], use_container_width=True)
        cols_inner2 = st.columns(2)
        with cols_inner2[0]:
            st.image(tone_imgs[1][0], caption=tone_imgs[1][1], use_container_width=True)
        with cols_inner2[1]:
            tone_fallback = GENRE_CONCEPT_IMAGES.get(genre, GENRE_CONCEPT_IMAGES["Drama"])
            st.image(tone_fallback[2][0], caption="Atmosphere", use_container_width=True)


def render_theme_visual_panel(primary_theme: str, secondary_theme: str):
    """NEW: Visual panel for both themes."""
    section_header("🎭", f"Theme Visuals — {primary_theme} & {secondary_theme}")
    p_imgs = THEME_IMAGES.get(primary_theme, list(THEME_IMAGES.values())[0])
    s_imgs = THEME_IMAGES.get(secondary_theme, list(THEME_IMAGES.values())[1])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="visual-label">⭐ {primary_theme}</div>', unsafe_allow_html=True)
        st.image(p_imgs[0][0], caption=p_imgs[0][1], use_container_width=True)
    with col2:
        st.markdown(f'<div class="visual-label"> </div>', unsafe_allow_html=True)
        st.image(p_imgs[1][0], caption=p_imgs[1][1], use_container_width=True)
    with col3:
        st.markdown(f'<div class="visual-label">➕ {secondary_theme}</div>', unsafe_allow_html=True)
        st.image(s_imgs[0][0], caption=s_imgs[0][1], use_container_width=True)
    with col4:
        st.markdown(f'<div class="visual-label"> </div>', unsafe_allow_html=True)
        st.image(s_imgs[1][0], caption=s_imgs[1][1], use_container_width=True)


def render_scene_storyboard(genre: str):
    """NEW: Storyboard-style visual strip for the three acts + key scenes."""
    section_header("🎞️", "Script Storyboard — Visual Scene Reference")
    images = SCENE_VISUAL_IMAGES.get(genre, SCENE_VISUAL_IMAGES["Drama"])

    # Row 1: Three acts
    st.markdown(
        '<div style="font-size:0.75rem;color:#8888a8;letter-spacing:2px;margin-bottom:0.4rem;">THREE ACT STRUCTURE</div>',
        unsafe_allow_html=True,
    )
    act_cols = st.columns(3)
    for col, (url, label) in zip(act_cols, images[:3]):
        with col:
            st.image(url, caption=label, use_container_width=True)

    # Row 2: Key scenes
    st.markdown(
        '<div style="font-size:0.75rem;color:#8888a8;letter-spacing:2px;margin:0.8rem 0 0.4rem;">KEY SCENES</div>',
        unsafe_allow_html=True,
    )
    key_cols = st.columns(2)
    for col, (url, label) in zip(key_cols, images[3:5]):
        with col:
            st.image(url, caption=label, use_container_width=True)


def render_extended_genre_gallery(genre: str):
    """NEW: 5-image extended gallery for deeper genre visualization."""
    section_header("🖼️", f"Extended Visual Reference — {genre}")
    ext_imgs = GENRE_EXTENDED_IMAGES.get(genre, GENRE_EXTENDED_IMAGES["Drama"])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(ext_imgs[0][0], caption=ext_imgs[0][1], use_container_width=True)
        st.image(ext_imgs[3][0], caption=ext_imgs[3][1], use_container_width=True)
    with col2:
        st.image(ext_imgs[1][0], caption=ext_imgs[1][1], use_container_width=True)
        st.image(ext_imgs[4][0], caption=ext_imgs[4][1], use_container_width=True)
    with col3:
        st.image(ext_imgs[2][0], caption=ext_imgs[2][1], use_container_width=True)


def render_visual_style_panel(visual_style: str, shooting_fmt: str):
    """NEW: Visual style + shooting format imagery."""
    section_header("🎨", f"Visual Style Reference — {visual_style}")
    col1, col2 = st.columns(2)
    with col1:
        vs_img = VISUAL_STYLE_IMAGES.get(visual_style, list(VISUAL_STYLE_IMAGES.values())[0])
        st.image(vs_img, caption=f"Style: {visual_style}", use_container_width=True)
    with col2:
        sf_img = SHOOTING_FORMAT_IMAGES.get(shooting_fmt, list(SHOOTING_FORMAT_IMAGES.values())[0])
        st.image(sf_img, caption=f"Format: {shooting_fmt}", use_container_width=True)


def render_sidebar_genre_tone_mini(genre: str, tone: str):
    """NEW: Compact genre + tone image previews for sidebar."""
    genre_imgs = GENRE_CONCEPT_IMAGES.get(genre, GENRE_CONCEPT_IMAGES["Drama"])
    tone_imgs  = TONE_IMAGES.get(tone, TONE_IMAGES["Dark & Brooding"])

    st.markdown(
        '<div style="font-family:\'Bebas Neue\',cursive;font-size:0.75rem;'
        'letter-spacing:1.5px;color:#f5c518;margin-top:0.6rem;">📽️ GENRE PREVIEW</div>',
        unsafe_allow_html=True,
    )
    st.image(genre_imgs[0][0], caption=genre_imgs[0][1], use_container_width=True)

    st.markdown(
        '<div style="font-family:\'Bebas Neue\',cursive;font-size:0.75rem;'
        'letter-spacing:1.5px;color:#f5c518;margin-top:0.6rem;">🎭 TONE PREVIEW</div>',
        unsafe_allow_html=True,
    )
    st.image(tone_imgs[0][0], caption=tone_imgs[0][1], use_container_width=True)


def render_theme_sidebar_mini(primary_theme: str):
    """NEW: Primary theme image preview in sidebar."""
    theme_imgs = THEME_IMAGES.get(primary_theme, list(THEME_IMAGES.values())[0])
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',cursive;font-size:0.75rem;'
        'letter-spacing:1.5px;color:#f5c518;margin-top:0.6rem;">⭐ THEME PREVIEW</div>',
        unsafe_allow_html=True,
    )
    st.image(theme_imgs[0][0], caption=theme_imgs[0][1], use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDERS
# ═════════════════════════════════════════════════════════════════════════════

def build_main_prompt(genre, tone, idea, director, ddesc, tlabel,
                      primary_theme, secondary_theme, visual_style, film_scale):
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


def build_title_prompt(genre, tone, idea, director,
                       primary_theme, secondary_theme, title_style):
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


def build_style_prompt(genre, tone, idea, director, visual_style, film_scale,
                       aspect_ratio, rating, shooting_fmt, primary_theme):
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
2. ASPECT RATIO JUSTIFICATION — why {aspect_ratio} serves this story
3. SHOOTING FORMAT NOTES
4. PRODUCTION SCALE EXECUTION
5. RATING IMPACT
6. VISUAL REFERENCE FILMS (5)
"""


def build_theme_prompt(genre, tone, idea, director, primary_theme, secondary_theme):
    return f"""
THEMATIC DEVELOPMENT BRIEF
===========================
Genre:           {genre}  |  Tone: {tone}
Director Style:  {director}
Primary Theme:   {primary_theme}
Secondary Theme: {secondary_theme}
Core Idea:       {idea}

1. THEME STATEMENT
2. HOW THE THEMES MANIFEST (protagonist, antagonist, setting, symbols, dialogue)
3. THEMATIC KEY SCENES (3)
4. CHARACTER THEME ARCS
5. THEMATIC TENSION
6. COMPARABLE FILMS (5)
7. PITFALLS TO AVOID
"""


def build_budget_prompt(genre, idea, budget_tier, film_scale, visual_style,
                        shooting_fmt, aspect_ratio, rating, director):
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

1. TOTAL BUDGET OVERVIEW (low/mid/high range, ATL vs BTL split, contingency %)
2. LINE-ITEM BREAKDOWN BY DEPARTMENT (cost range + % of total)
3. COST-SAVING STRATEGIES (5)
4. FUNDING SOURCES
5. FINANCIAL RISK AREAS (top 3)
6. COMPARABLE FILM BUDGETS (3 real films)
"""


def build_moodboard_prompt(genre, tone, idea, director, ddesc):
    return f"""Visual moodboard for: Genre: {genre} | Tone: {tone} | Director: {director} | Idea: {idea}
Include:
1) Color Palette — exactly 5 hex codes (format: #RRGGBB) with meaning for each
2) Visual Film References (5 films)
3) Poster Concept
4) Production Design Notes
5) Three AI image prompts (Midjourney-ready, each starting on a new line, prefixed with 'Prompt:')
"""


def build_market_prompt(genre, tone, idea, director, audience, budget):
    return f"""Market analysis for: Genre: {genre} | Tone: {tone} | Director: {director} | Audience: {audience} | Budget: {budget} | Idea: {idea}
Cover: 1) Audience Profile 2) Box Office Potential 3) Streaming/Distribution 4) Competitive Landscape 5) Marketing Angles 6) Risk Assessment."""


def build_expansion_prompt(act, genre, tone, idea, director, ddesc):
    return f"""Expand {act} for: Genre: {genre} | Tone: {tone} | Director: {director} ({ddesc}) | Idea: {idea}
Provide 5-7 scenes with: slug line, action block, key dialogue, pacing notes, emotional beats, visual/audio cues."""


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

    # Director visual signature preview
    render_director_sidebar_preview(director)

    genre = st.selectbox("Genre", GENRES)
    tone  = st.selectbox("Tone",  TONES)

    # ── NEW: Genre + Tone mini previews in sidebar ─────────────────────────
    render_sidebar_genre_tone_mini(genre, tone)

    st.divider()

    st.markdown("### 🎭 Themes")
    primary_theme   = st.selectbox("Primary Theme",   PRIMARY_THEMES)
    secondary_theme = st.selectbox("Secondary Theme", SECONDARY_THEMES)
    st.markdown(
        f'<span class="theme-pill">⭐ {primary_theme}</span>'
        f'<span class="theme-pill">➕ {secondary_theme}</span>',
        unsafe_allow_html=True,
    )

    # ── NEW: Primary theme image in sidebar ────────────────────────────────
    render_theme_sidebar_mini(primary_theme)

    st.divider()

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

# ── NEW: Pre-input visual atmosphere panel ─────────────────────────────────────
render_genre_tone_visual_panel(genre, tone)
st.divider()

# ── NEW: Theme visual panel below genre/tone ───────────────────────────────────
render_theme_visual_panel(primary_theme, secondary_theme)
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
        ("🔤 Generating titles…",
         lambda: call_llm(build_title_prompt(genre, tone, idea, director,
                          primary_theme, secondary_theme, "Poetic & Evocative"),
                          min(temperature + 0.1, 1.5), 800),
         "titles_output"),
        ("📜 Crafting script package…",
         lambda: call_llm(build_main_prompt(genre, tone, idea, director, ddesc, temp_label,
                          primary_theme, secondary_theme, visual_style, film_scale),
                          temperature, 3000),
         "main_output"),
        ("🎨 Analysing style & scale…",
         lambda: call_llm(build_style_prompt(genre, tone, idea, director, visual_style,
                          film_scale, aspect_ratio, rating, shooting_fmt, primary_theme),
                          max(temperature - 0.1, 0.4), 1800),
         "style_output"),
        ("🎭 Developing themes…",
         lambda: call_llm(build_theme_prompt(genre, tone, idea, director,
                          primary_theme, secondary_theme),
                          temperature, 1800),
         "theme_output"),
        ("💰 Estimating budget…",
         lambda: call_llm(build_budget_prompt(genre, idea, budget, film_scale, visual_style,
                          shooting_fmt, aspect_ratio, rating, director),
                          max(temperature - 0.2, 0.3), 2000),
         "budget_output"),
        ("🖼️ Building moodboard…",
         lambda: call_llm(build_moodboard_prompt(genre, tone, idea, director, ddesc),
                          min(temperature + 0.1, 1.5), 1200),
         "moodboard_output"),
        ("📊 Analysing market…",
         lambda: call_llm(build_market_prompt(genre, tone, idea, director, audience, budget),
                          max(temperature - 0.2, 0.3), 1500),
         "market_output"),
    ]

    for label, fn, key in steps:
        with st.spinner(label):
            try:
                st.session_state[key] = fn()
            except RuntimeError as e:
                st.error(str(e))
                st.stop()

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
        "🔤 Titles",
        "🎨 Style & Scale",
        "🎭 Themes",
        "💰 Budget",
        "🖼️ Moodboard",
        "📊 Market",
        "🔭 Expand Scene",
    ])

    # ── Tab 1 · Script Package ────────────────────────────────────────────────
    with tab1:
        # NEW: Storyboard visual strip at the TOP of the script tab
        render_scene_storyboard(genre)
        st.divider()

        render_card("📜", "Full Preproduction Package", st.session_state["main_output"])

        # Character visual references
        st.divider()
        render_character_visuals(genre, st.session_state["main_output"])

        # NEW: Extended genre gallery below script
        st.divider()
        render_extended_genre_gallery(genre)

        st.divider()
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

    # ── Tab 2 · Titles ────────────────────────────────────────────────────────
    with tab2:
        st.markdown("#### 🔤 AI Title Generator")

        # NEW: Genre imagery in titles tab
        render_concept_art_grid(genre)
        st.divider()

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

    # ── Tab 3 · Style & Scale ─────────────────────────────────────────────────
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

        # NEW: Visual style + shooting format imagery
        render_visual_style_panel(visual_style, shooting_fmt)
        st.divider()

        # Aspect ratio visualiser
        st.markdown(
            '<div style="font-family:\'Bebas Neue\',cursive;font-size:1rem;'
            'letter-spacing:2px;color:#f5c518;margin-top:0.6rem;">📐 Aspect Ratio Preview</div>',
            unsafe_allow_html=True,
        )
        ar_col, desc_col = st.columns([1, 1])
        with ar_col:
            render_aspect_ratio_preview(aspect_ratio)
        with desc_col:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:0.8rem;color:#8888a8;margin-bottom:0.8rem;">'
                'Compare all ratios at a glance:</div>',
                unsafe_allow_html=True,
            )
            for ar_name, (w, h) in ASPECT_RATIO_VALUES.items():
                bar_w = int((w / 2.76) * 200)
                is_selected = ar_name == aspect_ratio
                color = "#f5c518" if is_selected else "rgba(245,197,24,0.3)"
                label_color = "#f5c518" if is_selected else "#8888a8"
                st.markdown(
                    f'<div style="margin:4px 0;">'
                    f'<div style="font-size:0.7rem;color:{label_color};'
                    f'margin-bottom:2px;font-family:monospace;">{ar_name}</div>'
                    f'<div style="width:{bar_w}px;height:14px;'
                    f'background:{color};border-radius:2px;"></div></div>',
                    unsafe_allow_html=True,
                )

        st.divider()

        # NEW: Genre extended gallery in style tab
        render_extended_genre_gallery(genre)
        st.divider()

        if st.session_state["style_output"]:
            render_card("🎨", "Style & Scale Breakdown", st.session_state["style_output"])
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

    # ── Tab 4 · Themes ────────────────────────────────────────────────────────
    with tab4:
        st.markdown("#### 🎭 Thematic Development Guide")
        st.markdown(
            f'<span class="theme-pill">⭐ Primary: {primary_theme}</span>'
            f'<span class="theme-pill">➕ Secondary: {secondary_theme}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        # NEW: Full theme visual panel in themes tab
        render_theme_visual_panel(primary_theme, secondary_theme)
        st.divider()

        # NEW: Tone imagery in themes tab
        section_header("🎭", f"Tone Atmosphere — {tone}")
        tone_imgs = TONE_IMAGES.get(tone, TONE_IMAGES["Dark & Brooding"])
        t_cols = st.columns(3)
        for col, (url, caption) in zip(t_cols, tone_imgs):
            with col:
                st.image(url, caption=caption, use_container_width=True)
        st.divider()

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

    # ── Tab 5 · Budget ────────────────────────────────────────────────────────
    with tab5:
        st.markdown("#### 💰 Production Budget Estimator")
        st.caption(
            f"Detailed line-item estimate for a **{budget}** production "
            f"at **{film_scale}** scale shooting on **{shooting_fmt}**."
        )
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            st.markdown(
                '<div class="metric-box"><div class="metric-label">Budget Tier</div>'
                f'<div class="metric-value" style="color:#00c864;font-size:1.1rem;">'
                f'{budget.split("(")[0].strip()}</div></div>', unsafe_allow_html=True)
        with bc2:
            st.markdown(
                '<div class="metric-box"><div class="metric-label">Film Scale</div>'
                f'<div class="metric-value" style="color:#00c864;font-size:0.95rem;">'
                f'{film_scale.split("(")[0].strip()}</div></div>', unsafe_allow_html=True)
        with bc3:
            st.markdown(
                '<div class="metric-box"><div class="metric-label">Format</div>'
                f'<div class="metric-value" style="color:#00c864;font-size:0.95rem;">'
                f'{shooting_fmt.split("(")[0].strip()}</div></div>', unsafe_allow_html=True)

        st.markdown("")

        # NEW: Genre imagery for budget context
        section_header("🎬", f"Production Scale Reference — {genre} · {film_scale}")
        budget_imgs = GENRE_EXTENDED_IMAGES.get(genre, GENRE_EXTENDED_IMAGES["Drama"])
        b_cols = st.columns(3)
        for col, (url, caption) in zip(b_cols, budget_imgs[:3]):
            with col:
                st.image(url, caption=caption, use_container_width=True)
        st.divider()

        if st.session_state["budget_output"]:
            render_card("💰", "Budget Breakdown",
                        st.session_state["budget_output"],
                        card_class="budget-card", title_class="budget-title")
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

    # ── Tab 6 · Moodboard ────────────────────────────────────────────────────
    with tab6:
        st.markdown("#### 🖼️ Visual Moodboard & Production Design")

        # Genre concept art grid
        render_concept_art_grid(genre)
        st.divider()

        # NEW: Tone imagery in moodboard
        section_header("🎭", f"Tone Atmosphere — {tone}")
        tone_imgs = TONE_IMAGES.get(tone, TONE_IMAGES["Dark & Brooding"])
        t_cols = st.columns(3)
        for col, (url, caption) in zip(t_cols, tone_imgs):
            with col:
                st.image(url, caption=caption, use_container_width=True)
        st.divider()

        # NEW: Extended genre gallery
        render_extended_genre_gallery(genre)
        st.divider()

        # Extracted colour palette from LLM output
        if st.session_state["moodboard_output"]:
            hex_codes = extract_hex_colors(st.session_state["moodboard_output"])
            if hex_codes:
                render_color_palette(hex_codes)
                st.divider()

            # AI prompt cards
            prompts = extract_image_prompts(st.session_state["moodboard_output"])
            if prompts:
                section_header("🤖", "AI Concept Art Prompts (Midjourney-ready)")
                for i, prompt in enumerate(prompts, 1):
                    st.markdown(
                        f'<div class="prompt-card">'
                        f'<div class="prompt-card-label">PROMPT {i}</div>'
                        f'{prompt}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.code(prompt, language=None)
                st.divider()

        render_card("🖼️", "Full Moodboard & Production Design",
                    st.session_state["moodboard_output"])

    # ── Tab 7 · Market ────────────────────────────────────────────────────────
    with tab7:
        # NEW: Genre imagery for market tab
        section_header("📊", f"Market Landscape — {genre}")
        mkt_imgs = GENRE_CONCEPT_IMAGES.get(genre, GENRE_CONCEPT_IMAGES["Drama"])
        m_cols = st.columns(3)
        for col, (url, caption) in zip(m_cols, mkt_imgs):
            with col:
                st.image(url, caption=caption, use_container_width=True)
        st.divider()

        render_card("📊", "Target Audience & Market Analysis",
                    st.session_state["market_output"])

    # ── Tab 8 · Scene Expansion ───────────────────────────────────────────────
    with tab8:
        st.markdown("#### 🔭 Scene Expansion")

        # NEW: Storyboard reference in expansion tab
        render_scene_storyboard(genre)
        st.divider()

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

            # NEW: Visual reference for the expanded scene
            st.divider()
            render_character_visuals(genre, st.session_state["expansion_output"])

            st.download_button("⬇️ Download Expansion TXT",
                               st.session_state["expansion_output"],
                               "scene_expansion.txt", "text/plain")


# ═════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown(
    "<div style='text-align:center;color:#444;font-size:0.78rem;padding:0.8rem 0;'>"
    "🎬 AI Film Preproduction Studio v2.2 &nbsp;|&nbsp; "
    "LLaMA 3.3 70B via Groq &nbsp;|&nbsp; Built with Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
