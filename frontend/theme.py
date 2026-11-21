"""Identidad visual de FRUIT VISION: paleta lavanda/morado sobre fondos claros."""

from __future__ import annotations

import streamlit as st

PALETA = {
    "morado_profundo": "#4C2A85",
    "morado": "#7C3AED",
    "morado_suave": "#9F7AEA",
    "lavanda": "#EDE4FF",
    "lavanda_clara": "#F7F3FF",
    "blanco": "#FFFFFF",
    "tinta": "#2D1B4E",
}

CSS = """
<style>
:root {
  --fv-deep: #4C2A85;
  --fv-purple: #7C3AED;
  --fv-soft: #9F7AEA;
  --fv-lavender: #EDE4FF;
  --fv-lavender-light: #F7F3FF;
  --fv-ink: #2D1B4E;
}
.stApp {
  background: linear-gradient(180deg, #FFFFFF 0%, #FBF9FF 55%, #F6F1FF 100%);
  color: var(--fv-ink);
  font-family: "Inter", "Segoe UI", system-ui, sans-serif;
}
header[data-testid="stHeader"] { background: rgba(255,255,255,0.86); }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #FFFFFF 0%, #F8F4FF 60%, #F1E9FF 100%);
  border-right: 1px solid #E8DEFA;
}
[data-testid="stSidebar"] > div:first-child { background: transparent; }
[data-testid="stSidebar"] * { color: var(--fv-ink) !important; }
[data-testid="stSidebar"] .stButton > button {
  background: #F7F3FF !important;
  border: 1px solid #E4D8FA !important;
  color: var(--fv-deep) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: linear-gradient(120deg, #7C3AED, #9F7AEA) !important;
  border: none !important;
  color: #FFFFFF !important;
}

.fv-hero {
  position: relative; overflow: hidden;
  background: radial-gradient(circle at 88% 12%, rgba(159,122,234,.22), transparent 40%),
              radial-gradient(circle at 8% 92%, rgba(124,58,237,.12), transparent 42%),
              linear-gradient(125deg, #FFFFFF 0%, #F7F3FF 55%, #EFE6FF 100%);
  border: 1px solid #E4D8FA;
  border-radius: 26px; padding: 44px 48px; margin-bottom: 22px;
  box-shadow: 0 14px 34px rgba(76,42,133,.10); color: var(--fv-deep);
}
.fv-hero::after {
  content: "🍍🍎🍇🍊🍌"; position: absolute; right: 34px; bottom: 18px;
  font-size: 1.6rem; letter-spacing: .35rem; opacity: .30;
}
.fv-eyebrow {
  display: inline-block; padding: 6px 14px; border-radius: 999px;
  background: #EDE4FF; border: 1px solid #DCCBFA;
  color: var(--fv-deep);
  font-size: .78rem; letter-spacing: .18em; text-transform: uppercase;
  font-weight: 700;
}
.fv-hero h1 {
  font-size: clamp(2.1rem, 4.8vw, 3.6rem); margin: 16px 0 8px;
  letter-spacing: .12em; font-weight: 800; line-height: 1.05;
  color: var(--fv-deep);
}
.fv-hero p { font-size: 1.08rem; color: #5B477A; max-width: 650px; margin: 0; }

.fv-section-title {
  display: flex; align-items: center; gap: 12px; margin: 12px 0 18px;
  font-size: 1.45rem; font-weight: 750; color: var(--fv-deep);
}
.fv-section-title::after {
  content: ""; flex: 1; height: 1px;
  background: linear-gradient(90deg, rgba(124,58,237,.35), transparent);
}
.fv-card {
  background: #FFFFFF; border: 1px solid #E8DEFA;
  border-radius: 22px; padding: 24px; height: 100%;
  box-shadow: 0 10px 28px rgba(76,42,133,.07);
}
.fv-card-soft {
  background: linear-gradient(160deg, #FFFFFF 0%, #F7F3FF 100%);
  border: 1px solid #E4D8FA; border-radius: 22px; padding: 24px;
  box-shadow: 0 10px 28px rgba(76,42,133,.06);
}
.fv-intro { color: #5B477A; }
.fv-alert {
  display: flex; align-items: flex-start; gap: 10px; margin-top: 14px;
  padding: 12px 14px; border-radius: 14px; background: #F0E8FF;
  border: 1px solid #DCCBFA; color: var(--fv-deep);
}
.fv-alert-icon { font-size: 1.2rem; line-height: 1.2; }
.fv-alert .fv-muted { color: #5B477A; }
.fv-muted { color: #75669A; font-size: .92rem; }
.fv-kicker {
  text-transform: uppercase; letter-spacing: .16em; font-size: .74rem;
  font-weight: 700; color: var(--fv-purple); margin-bottom: 8px;
}
.fv-big-number { font-size: 3.1rem; font-weight: 800; color: var(--fv-deep); line-height: 1; }
.fv-fruit-name { font-size: 1.6rem; font-weight: 750; color: var(--fv-deep); margin: 6px 0 2px; }
.fv-chip {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px;
  border-radius: 999px; font-size: .8rem; font-weight: 650;
  background: #F0E8FF; color: var(--fv-deep); border: 1px solid #DDCBFA;
}
.fv-chip-warn { background: #FDF2FF; color: #8B3A8F; border-color: #F0D0F5; }
.fv-bar { height: 10px; border-radius: 999px; background: #EDE4FF; overflow: hidden; }
.fv-bar > span { display: block; height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, #9F7AEA, #7C3AED); }
.fv-bar-top > span { background: linear-gradient(90deg, #7C3AED, #4C2A85); }
.fv-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.fv-metric { text-align: center; padding: 14px; border-radius: 16px; background: #F7F3FF; }
.fv-metric strong { display: block; font-size: 1.5rem; color: var(--fv-deep); }
.fv-date { font-variant-numeric: tabular-nums; }

[data-testid="stFileUploader"] section {
  border: 2px dashed #C9B2F5 !important; border-radius: 20px !important;
  background: #FCFAFF !important; padding: 26px !important;
  transition: border-color .2s ease, background .2s ease;
}
[data-testid="stFileUploader"] section:hover {
  border-color: var(--fv-purple) !important; background: #F7F1FF !important;
}
[data-testid="stFileUploader"] button {
  background: linear-gradient(120deg, #7C3AED, #9F7AEA) !important;
  border: none !important; color: #FFFFFF !important;
  border-radius: 10px !important; font-weight: 700 !important;
}
[data-testid="stFileUploader"] button[disabled] {
  background: #E4D8FA !important; color: #75669A !important;
  cursor: not-allowed !important;
}
.stButton > button {
  border-radius: 12px !important; font-weight: 700 !important;
  padding: .62rem 1.15rem !important; transition: transform .15s ease, box-shadow .15s ease;
  border: 1px solid #E4D8FA !important;
  background: #FFFFFF !important; color: var(--fv-deep) !important;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(76,42,133,.14); }
.stButton > button[kind="primary"] {
  background: linear-gradient(120deg, #7C3AED, #9F7AEA) !important;
  border: none !important; color: #FFFFFF !important; font-size: 1.02rem !important;
  padding: .8rem 1.6rem !important;
}
[data-testid="stMetricValue"] { color: var(--fv-deep); }
[data-testid="stImage"] img { border-radius: 16px; }
hr { border-color: #E8DEFA; }

@media (max-width: 768px) {
  .fv-hero { padding: 30px 24px; border-radius: 20px; }
  .fv-hero::after { display: none; }
  .fv-hero h1 { letter-spacing: .06em; }
  .fv-card, .fv-card-soft { padding: 18px; border-radius: 18px; }
  .fv-big-number { font-size: 2.4rem; }
}
</style>
"""


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(titulo: str = "FRUIT VISION", subtitulo: str = "") -> None:
    st.markdown(
        f"""
        <div class="fv-hero">
          <span class="fv-eyebrow">Inteligencia artificial · Visión por computadora</span>
          <h1>{titulo}</h1>
          <p>{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(texto: str) -> None:
    st.markdown(f'<div class="fv-section-title">{texto}</div>', unsafe_allow_html=True)
