import streamlit as st
from openai import OpenAI
import os
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="🎬 AI Film Preproduction Studio", page_icon="🎬",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif}
.stApp{background:linear-gradient(135deg,#0a0a0f,#12121e,#0d0d18);color:#e8e8f0}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0f1a,#1a1a2e);border-right:1px solid #f5c518}
.film-header{font-family:'Bebas Neue',cursive;font-size:3rem;letter-spacing:4px;
  background:linear-gradient(90deg,#f5c518,#ff6b35,#f5c518);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text;text-align:center}
.film-subtitle{text-align:center;color:#8888a8;font-size:.85rem;letter-spacing:3px;text-transform:uppercase;margin-bottom:1.5rem}
.output-card{background:rgba(255,255,255,.04);border:1px solid rgba(245,197,24,.2);
  border-left:4px solid #f5c518;border-radius:8px;padding:1.2rem 1.4rem;margin:.8rem 0}
.budget-card{background:rgba(0,200,100,.04);border:1px solid rgba(0,200,100,.25);
  border-left:4px solid #00c864;border-radius:8px;padding:1.2rem 1.4rem;margin:.8rem 0}
.card-title{font-family:'Bebas Neue',cursive;font-size:1.3rem;letter-spacing:2px;color:#f5c518;margin-bottom:.4rem}
.budget-title{font-family:'Bebas Neue',cursive;font-size:1.3rem;letter-spacing:2px;color:#00c864;margin-bottom:.4rem}
.metric-box{background:rgba(245,197,24,.08);border:1px solid rgba(245,197,24,.3);border-radius:6px;padding:.7rem;text-align:center}
.metric-label{font-size:.65rem;letter-spacing:2px;text-transform:uppercase;color:#8888a8}
.metric-value{font-family:'Bebas Neue',cursive;font-size:1.3rem;color:#f5c518}
.theme-pill{display:inline-block;background:rgba(245,197,24,.1);border:1px solid rgba(245,197,24,.35);
  border-radius:20px;padding:2px 11px;margin:2px;font-size:.75rem;color:#f5c518}
.stButton>button{background:linear-gradient(135deg,#f5c518,#e6b800);color:#0a0a0f;font-weight:700;
  font-size:.95rem;letter-spacing:2px;text-transform:uppercase;border:none;border-radius:4px;
  padding:.65rem 1.5rem;width:100%;transition:all .2s}
.stButton>button:hover{background:linear-gradient(135deg,#ffda44,#f5c518);transform:translateY(-1px);box-shadow:0 4px 20px rgba(245,197,24,.4)}
.stSelectbox>div>div,.stTextArea>div>div{background:rgba(255,255,255,.05)!important;border:1px solid rgba(245,197,24,.25)!important;color:#e8e8f0!important}
.stSlider>div>div>div>div{background:#f5c518!important}
hr{border-color:rgba(245,197,24,.15)}
.stTabs [data-baseweb="tab"]{font-family:'Bebas Neue',cursive;font-size:.95rem;letter-spacing:1.5px;color:#8888a8}
.stTabs [aria-selected="true"]{color:#f5c518!important;border-bottom:2px solid #f5c518!important}
</style>""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
MODEL = "llama-3.3-70b-versatile"

DIR_STYLES = {
    "Christopher Nolan":  "nonlinear narrative, practical effects, time/memory themes, IMAX compositions",
    "Quentin Tarantino":  "pop-culture dialogue, chapter structure, non-linear storytelling, stylised tension",
    "Wes Anderson":       "symmetrical shots, pastel palettes, deadpan humour, whimsical production design",
    "Denis Villeneuve":   "slow-burn tension, wide-angle photography, minimal dialogue, grand scale",
    "Bong Joon-ho":       "class commentary, genre-blending tonal shifts, dark comedy, symbolic design",
    "Ari Aster":          "slow dread, folk-horror imagery, grief as horror metaphor, long takes",
    "Sofia Coppola":      "dreamy introspective mood, melancholic beauty, atmosphere over plot",
    "No Specific Style":  "balanced cinematic approach, industry-standard techniques",
}
GENRES         = ["Crime/Thriller","Sci-Fi","Drama","Horror","Romance","Comedy","Action/Adventure","Fantasy","Historical Epic"]
TONES          = ["Dark & Brooding","Suspenseful","Emotional & Raw","Light-hearted","Intense","Whimsical","Satirical"]
AUDIENCES      = ["General (PG-13)","Young Adults 18-25","Adults 25-45","Family","Niche/Art-house","Genre Enthusiasts"]
BUDGETS        = ["Micro (<$1M)","Indie ($1M-$10M)","Mid ($10M-$50M)","Studio ($50M-$150M)","Blockbuster ($150M+)"]
VISUAL_STYLES  = ["Naturalistic","Hyper-stylised","Noir/High Contrast","Dreamlike/Surreal","Gritty Documentary","Glossy Commercial","Minimalist","Epic/Grand Spectacle"]
FILM_SCALES    = ["Single Location","City-Based","National/Road Movie","International","Sci-Fi/Fantasy World","Intimate Character Study"]
ASPECT_RATIOS  = ["2.39:1 Cinemascope","1.85:1 Flat Widescreen","1.33:1 Academy/Vintage","1.78:1 16:9 Streaming","2.76:1 Ultra Panavision"]
RATINGS        = ["G/U Universal","PG/PG-13","R/15 Mature","NC-17/18 Adult","Not Yet Rated"]
SHOOT_FMTS     = ["Digital ARRI Alexa","Digital RED Camera","35mm Film","16mm Film","IMAX","Handheld/Verite"]
PRI_THEMES     = ["Redemption","Identity & Self-Discovery","Power & Corruption","Love & Loss","Survival","Justice vs Revenge","Technology vs Humanity","Class & Inequality","Grief & Healing","War & Consequences","Family & Legacy","Freedom vs Control"]
SEC_THEMES     = ["Betrayal","Sacrifice","Isolation","Memory & Nostalgia","Fate vs Free Will","Coming of Age","Trust & Deception","Ambition","Race & Culture","Gender & Identity","Environmental Destruction","Religion & Faith","Addiction","Villain's Redemption"]
TITLE_STYLES   = ["Poetic & Evocative","Short & Punchy (1-2 words)","Mysterious & Cryptic","Action/Thriller Style","Character Name","Question/Provocative","Metaphorical/Symbolic"]

# ── API ───────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",
          "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"))
    return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

def call_llm(prompt, temp=0.7, tokens=2048):
    try:
        r = get_client().chat.completions.create(
            model=MODEL, temperature=temp, max_tokens=tokens,
            messages=[
                {"role":"system","content":"You are a world-class Hollywood screenwriter, director, and film production expert. Produce detailed, professional, industry-standard output."},
                {"role":"user","content":prompt}])
        return r.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "401" in err:   raise RuntimeError("❌ Invalid API key.")
        if "429" in err:   raise RuntimeError("⏳ Rate limit hit — wait and retry.")
        if "timeout" in err or "connect" in err: raise RuntimeError("🌐 Network error.")
        raise RuntimeError(f"🔧 API error: {err}")

# ── Prompt builders ───────────────────────────────────────────────────────────
def p_main(g,t,idea,d,dd,tl,pt,st2,vs,fs):
    return f"""Genre:{g}|Tone:{t}|Director:{d}({dd})|Creativity:{tl}|PrimaryTheme:{pt}|SecondaryTheme:{st2}|VisualStyle:{vs}|Scale:{fs}
Idea:{idea}
Generate: 1.LOGLINE 2.THREE-ACT STRUCTURE(weave themes) 3.CHARACTERS x3(Name,Role,Personality,Backstory,Arc,Trait) 4.THREE KEY SCENES(screenplay format) 5.CINEMATOGRAPHY({vs} style) 6.SOUND DESIGN & SCORE"""

def p_titles(g,t,idea,d,pt,st2,ts):
    return f"""Generate 6 film titles. Genre:{g}|Tone:{t}|Director:{d}|Theme:{pt}+{st2}|TitleStyle:{ts}|Idea:{idea}
Each: Title • Tagline • Why It Works (commercial+thematic) • Tone Match. Number each."""

def p_style(g,t,idea,d,vs,fs,ar,rat,sf,pt):
    return f"""Cinematic Style & Scale Guide. Genre:{g}|Tone:{t}|Director:{d}|VisualStyle:{vs}|Scale:{fs}|AspectRatio:{ar}|Rating:{rat}|Format:{sf}|Theme:{pt}|Idea:{idea}
Cover: 1.VISUAL LANGUAGE(motifs,camera,lenses) 2.ASPECT RATIO JUSTIFICATION(why {ar},3 ref films) 3.SHOOTING FORMAT NOTES 4.SCALE EXECUTION(locations,design) 5.RATING IMPACT 6.REFERENCE FILMS x5"""

def p_theme(g,t,idea,d,pt,st2):
    return f"""Thematic Development. Genre:{g}|Tone:{t}|Director:{d}|Primary:{pt}|Secondary:{st2}|Idea:{idea}
Cover: 1.THEME STATEMENT 2.HOW THEMES MANIFEST(protagonist,antagonist,setting,visuals,subtext) 3.THEMATIC SCENES x3(slug+action+dialogue+purpose) 4.CHARACTER ARCS vs theme 5.THEMATIC TENSION({st2} vs {pt}) 6.COMPARABLE FILMS x5 7.PITFALLS x3"""

def p_budget(g,idea,b,fs,vs,sf,ar,rat,d):
    return f"""Budget Estimate. Genre:{g}|Tier:{b}|Scale:{fs}|VisualStyle:{vs}|Format:{sf}|Ratio:{ar}|Rating:{rat}|Director:{d}|Idea:{idea}
Provide: 1.TOTAL OVERVIEW(low/mid/high range, above/below-line split, contingency%) 2.LINE-ITEMS(Script,Director,Lead Cast,Support Cast,Crew,Camera,Lighting,Production Design,Costume,Hair&MU,Locations,Catering&Transport,VFX,Music,Post,Marketing,Legal,Contingency — each with range+% of total) 3.COST-SAVING STRATEGIES x5 4.FUNDING SOURCES 5.RISK AREAS x3 6.COMPARABLE FILMS x3"""

def p_moodboard(g,t,idea,d,dd):
    return f"""Visual moodboard. Genre:{g}|Tone:{t}|Director:{d}({dd})|Idea:{idea}
Include: 1.COLOR PALETTE(5 hex codes+meaning) 2.FILM REFERENCES x5 3.POSTER CONCEPT 4.PRODUCTION DESIGN NOTES 5.AI IMAGE PROMPTS x3(Midjourney-ready)"""

def p_market(g,t,idea,d,aud,b):
    return f"""Market analysis. Genre:{g}|Tone:{t}|Director:{d}|Audience:{aud}|Budget:{b}|Idea:{idea}
Cover: 1.AUDIENCE PROFILE 2.BOX OFFICE POTENTIAL 3.STREAMING/DISTRIBUTION 4.COMPETITIVE LANDSCAPE 5.MARKETING ANGLES 6.RISK ASSESSMENT"""

def p_expand(act,g,t,idea,d,dd):
    return f"""Expand {act}. Genre:{g}|Tone:{t}|Director:{d}({dd})|Idea:{idea}
5-7 scenes each with: slug line, action block, dialogue, pacing notes, emotional beats, visual/audio cues."""

# ── PDF ───────────────────────────────────────────────────────────────────────
def make_pdf(title, content):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    S = getSampleStyleSheet()
    ts = ParagraphStyle("T", parent=S["Title"], fontSize=20, textColor=colors.HexColor("#f5c518"), fontName="Helvetica-Bold", spaceAfter=16)
    bs = ParagraphStyle("B", parent=S["Normal"], fontSize=10, leading=15, fontName="Courier", spaceAfter=4)
    body = [Paragraph(title, ts), Spacer(1, .15*inch)]
    for line in content.split("\n"):
        s = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        body.append(Paragraph(s or "&nbsp;", bs))
    doc.build(body)
    return buf.getvalue()

# ── UI helpers ────────────────────────────────────────────────────────────────
def card(icon, title, content, cc="output-card", tc="card-title"):
    st.markdown(f'<div class="{cc}"><div class="{tc}">{icon} {title}</div></div>', unsafe_allow_html=True)
    st.markdown(content)

def metric(label, val, color="#f5c518"):
    st.markdown(f'<div class="metric-box"><div class="metric-label">{label}</div>'
                f'<div class="metric-value" style="color:{color}">{val}</div></div>', unsafe_allow_html=True)

def pills(*items):
    st.markdown("".join(f'<span class="theme-pill">{i}</span>' for i in items), unsafe_allow_html=True)

def regen_btn(label, fn, key, temp, tokens):
    if st.button(f"🔄 {label}", use_container_width=True):
        with st.spinner(f"{label}…"):
            try: st.session_state[key] = call_llm(fn(), temp, tokens); st.rerun()
            except RuntimeError as e: st.error(str(e))

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Production Controls"); st.divider()
    st.markdown("### 🎥 Director & Genre")
    director = st.selectbox("Director Style", list(DIR_STYLES.keys()))
    st.caption(f"*{DIR_STYLES[director][:85]}…*")
    genre = st.selectbox("Genre", GENRES)
    tone  = st.selectbox("Tone",  TONES); st.divider()

    st.markdown("### 🎭 Themes")
    pri_theme = st.selectbox("Primary Theme",   PRI_THEMES)
    sec_theme = st.selectbox("Secondary Theme", SEC_THEMES)
    pills(f"⭐ {pri_theme}", f"➕ {sec_theme}"); st.divider()

    st.markdown("### 🎨 Style & Scale")
    vis_style  = st.selectbox("Visual Style",   VISUAL_STYLES)
    film_scale = st.selectbox("Film Scale",      FILM_SCALES)
    asp_ratio  = st.selectbox("Aspect Ratio",    ASPECT_RATIOS)
    shoot_fmt  = st.selectbox("Shooting Format", SHOOT_FMTS)
    rating     = st.selectbox("Content Rating",  RATINGS); st.divider()

    st.markdown("### 👥 Market Settings")
    audience = st.selectbox("Target Audience", AUDIENCES)
    budget   = st.selectbox("Budget Tier",     BUDGETS); st.divider()

    st.markdown("### 🌡️ Creativity")
    temp = st.slider("Temperature", 0.1, 1.5, 0.8, 0.05)
    tlabel = next((v for (lo,hi),v in {(0.1,.4):"🎯 Precise",(.4,.7):"🎬 Balanced",(.7,1.):"✨ Creative",(1.,1.5):"🔥 Experimental"}.items() if lo<=temp<=hi), "✨ Creative")
    st.caption(f"Mode: **{tlabel}**")
    st.divider()
    st.markdown("<div style='text-align:center;color:#444;font-size:.7rem'>LLaMA 3.3 70B · Groq · Streamlit</div>", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="film-header">🎬 AI FILM PREPRODUCTION STUDIO</div>', unsafe_allow_html=True)
st.markdown('<div class="film-subtitle">From Idea to Industry-Ready Package in Seconds</div>', unsafe_allow_html=True)

cols = st.columns(6)
for col, lbl, val in zip(cols,
    ["Director","Genre","Visual Style","Themes","Budget","Creativity"],
    [director.split()[0], genre.split("/")[0], vis_style.split("/")[0],
     f"{pri_theme[:9]}…", budget.split("(")[0].strip(), tlabel.split()[0]]):
    with col: metric(lbl, val)

st.divider()
idea = st.text_area("📝 Your Story Idea",
    placeholder="e.g. A disgraced quantum physicist discovers her alternate self committed a murder she hasn't committed yet…", height=110)
go = st.button("🎬 GENERATE FULL PREPRODUCTION PACKAGE", use_container_width=True)
st.divider()

# ── Session state ─────────────────────────────────────────────────────────────
for k in ["main","titles","style","theme","budget","moodboard","market","expand","proj_title"]:
    if k not in st.session_state: st.session_state[k] = ""

# ── Generation pipeline ───────────────────────────────────────────────────────
if go:
    if not idea.strip(): st.warning("✏️ Please enter a story idea first."); st.stop()
    dd = DIR_STYLES[director]
    steps = [
        ("🔤 Generating titles…",      lambda: call_llm(p_titles(genre,tone,idea,director,pri_theme,sec_theme,"Poetic & Evocative"), min(temp+.1,1.5), 800),  "titles"),
        ("📜 Crafting script…",         lambda: call_llm(p_main(genre,tone,idea,director,dd,tlabel,pri_theme,sec_theme,vis_style,film_scale), temp, 3000),     "main"),
        ("🎨 Analysing style & scale…", lambda: call_llm(p_style(genre,tone,idea,director,vis_style,film_scale,asp_ratio,rating,shoot_fmt,pri_theme), max(temp-.1,.4), 1800), "style"),
        ("🎭 Developing themes…",       lambda: call_llm(p_theme(genre,tone,idea,director,pri_theme,sec_theme), temp, 1800),                                   "theme"),
        ("💰 Estimating budget…",       lambda: call_llm(p_budget(genre,idea,budget,film_scale,vis_style,shoot_fmt,asp_ratio,rating,director), max(temp-.2,.3), 2000), "budget"),
        ("🖼️ Building moodboard…",      lambda: call_llm(p_moodboard(genre,tone,idea,director,dd), min(temp+.1,1.5), 1200),                                   "moodboard"),
        ("📊 Analysing market…",        lambda: call_llm(p_market(genre,tone,idea,director,audience,budget), max(temp-.2,.3), 1500),                           "market"),
    ]
    for label, fn, key in steps:
        with st.spinner(label):
            try: st.session_state[key] = fn()
            except RuntimeError as e: st.error(str(e)); st.stop()
    first = [l for l in st.session_state["titles"].split("\n") if l.strip()]
    st.session_state["proj_title"] = first[0].replace("**","").replace("1.","").strip() if first else "UNTITLED"
    st.success("✅ Full package ready! Explore every tab below.")

# ── Output ────────────────────────────────────────────────────────────────────
if st.session_state["main"]:
    proj = st.session_state["proj_title"]
    st.markdown(f"## 🎬 *{proj}* &nbsp;", unsafe_allow_html=True)
    pills(f"⭐ {pri_theme}", f"➕ {sec_theme}")
    st.divider()

    tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs([
        "📜 Script","🔤 Titles","🎨 Style & Scale","🎭 Themes",
        "💰 Budget","🖼️ Moodboard","📊 Market","🔭 Expand Scene"])

    # Tab 1 — Script
    with tab1:
        card("📜","Full Preproduction Package", st.session_state["main"])
        full_txt = f"FILM: {proj}\nGenre:{genre}|Tone:{tone}|Director:{director}\nThemes:{pri_theme}+{sec_theme}|Style:{vis_style}|Scale:{film_scale}\n{'='*60}\n\n{st.session_state['main']}"
        combined_md = "\n\n".join([
            f"# 🎬 {proj}\n**Genre:**{genre}|**Tone:**{tone}|**Director:**{director}\n**Themes:**{pri_theme}+{sec_theme}",
            f"## Script\n{st.session_state['main']}", f"## Titles\n{st.session_state['titles']}",
            f"## Style & Scale\n{st.session_state['style']}", f"## Themes\n{st.session_state['theme']}",
            f"## Budget\n{st.session_state['budget']}", f"## Moodboard\n{st.session_state['moodboard']}",
            f"## Market\n{st.session_state['market']}"])
        d1,d2,d3 = st.columns(3)
        with d1: st.download_button("⬇️ TXT", full_txt, f"{proj.replace(' ','_')}.txt", "text/plain", use_container_width=True)
        with d2:
            if PDF_AVAILABLE:
                try: st.download_button("⬇️ PDF", make_pdf(proj, full_txt), f"{proj.replace(' ','_')}.pdf", "application/pdf", use_container_width=True)
                except Exception as e: st.caption(f"PDF: {e}")
            else: st.caption("Install `reportlab` for PDF")
        with d3: st.download_button("⬇️ Full MD", combined_md, f"{proj.replace(' ','_')}_package.md", "text/markdown", use_container_width=True)

    # Tab 2 — ① Enhanced Title Generator
    with tab2:
        st.markdown("#### 🔤 AI Title Generator")
        tc1, tc2 = st.columns([2,1])
        with tc1: ts = st.selectbox("Title Naming Style", TITLE_STYLES)
        with tc2:
            st.markdown("<br>", unsafe_allow_html=True)
            regen_btn("Generate Titles", lambda: p_titles(genre,tone,idea,director,pri_theme,sec_theme,ts), "titles", min(temp+.2,1.5), 800)
        card("🔤", f"Titles — {ts}", st.session_state["titles"])
        st.download_button("⬇️ Titles TXT", st.session_state["titles"], "titles.txt", "text/plain")

    # Tab 3 — ② Style & Scale
    with tab3:
        st.markdown("#### 🎨 Cinematic Style & Production Scale")
        pills(f"🎨 {vis_style}", f"🗺️ {film_scale}", f"📐 {asp_ratio}", f"🎞️ {shoot_fmt}", f"🔞 {rating}")
        st.markdown("")
        if st.session_state["style"]: card("🎨","Style & Scale Breakdown", st.session_state["style"])
        else: st.info("Generate the full package first.")
        regen_btn("Regenerate Style Guide", lambda: p_style(genre,tone,idea,director,vis_style,film_scale,asp_ratio,rating,shoot_fmt,pri_theme), "style", max(temp-.1,.4), 1800)
        if st.session_state["style"]: st.download_button("⬇️ Style TXT", st.session_state["style"], "style_guide.txt", "text/plain")

    # Tab 4 — ③ Themes
    with tab4:
        st.markdown("#### 🎭 Thematic Development Guide")
        pills(f"⭐ {pri_theme}", f"➕ {sec_theme}")
        st.markdown("")
        if st.session_state["theme"]: card("🎭", f"Theme: {pri_theme} + {sec_theme}", st.session_state["theme"])
        else: st.info("Generate the full package first.")
        regen_btn("Regenerate Theme Analysis", lambda: p_theme(genre,tone,idea,director,pri_theme,sec_theme), "theme", temp, 1800)
        if st.session_state["theme"]: st.download_button("⬇️ Theme TXT", st.session_state["theme"], "theme_guide.txt", "text/plain")

    # Tab 5 — ④ Budget Estimator
    with tab5:
        st.markdown("#### 💰 Production Budget Estimator")
        bc1,bc2,bc3 = st.columns(3)
        with bc1: metric("Budget Tier",   budget.split("(")[0].strip(), "#00c864")
        with bc2: metric("Film Scale",    film_scale.split("(")[0].strip(), "#00c864")
        with bc3: metric("Format",        shoot_fmt.split("(")[0].strip(), "#00c864")
        st.markdown("")
        if st.session_state["budget"]: card("💰","Budget Breakdown", st.session_state["budget"], "budget-card","budget-title")
        else: st.info("Generate the full package first.")
        regen_btn("Regenerate Budget Estimate", lambda: p_budget(genre,idea,budget,film_scale,vis_style,shoot_fmt,asp_ratio,rating,director), "budget", max(temp-.2,.3), 2000)
        if st.session_state["budget"]: st.download_button("⬇️ Budget TXT", st.session_state["budget"], "budget_estimate.txt", "text/plain")

    # Tab 6 — Moodboard
    with tab6:
        card("🖼️","Visual Moodboard & Production Design", st.session_state["moodboard"])

    # Tab 7 — Market
    with tab7:
        card("📊","Target Audience & Market Analysis", st.session_state["market"])

    # Tab 8 — Scene Expansion
    with tab8:
        st.markdown("#### 🔭 Scene Expansion")
        ec1,ec2 = st.columns([2,1])
        with ec1: act = st.selectbox("Section", ["Act 1 — Setup","Act 2 — Confrontation","Act 3 — Resolution","Opening Scene","Climax Scene","Flashback Sequence"])
        with ec2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔭 EXPAND", use_container_width=True):
                with st.spinner(f"Expanding {act}…"):
                    try: st.session_state["expand"] = call_llm(p_expand(act,genre,tone,idea,director,DIR_STYLES[director]), temp, 2000)
                    except RuntimeError as e: st.error(str(e))
        if st.session_state["expand"]:
            card("🔭", f"Expansion: {act}", st.session_state["expand"])
            st.download_button("⬇️ Expansion TXT", st.session_state["expand"], "expansion.txt", "text/plain")

st.divider()
st.markdown("<div style='text-align:center;color:#444;font-size:.75rem;padding:.6rem'>🎬 AI Film Preproduction Studio v2.0 · LLaMA 3.3 70B via Groq · Streamlit</div>", unsafe_allow_html=True)