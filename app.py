import time
from datetime import datetime
import pandas as pd
import joblib
import streamlit as st

from scraper import TravelOfferScraper
from analyzer import OfferAnalyzer
from storage import OfferStorage
from preprocessor import TravelDataPreprocessorV2
import sys
import subprocess

subprocess.run([sys.executable, "-m", 'playwright', 'install', 'chromium'])


st.set_page_config(
    page_title="Check My Trip",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #f8fafc;
    }

    .stApp {
        background-image: linear-gradient(rgba(2, 6, 23, 0.85), rgba(15, 23, 42, 0.95)), url("https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=2500&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    header[data-testid="stHeader"] { background-color: transparent !important; }

    .block-container {
        max-width: 1350px !important;
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }

    .hero-container {
        text-align: center;
        margin-bottom: 3rem;
        margin-top: 1rem;
    }
    
    .logo-svg {
        width: 110px;
        height: 110px;
        filter: drop-shadow(0px 10px 25px rgba(56, 189, 248, 0.6));
        animation: float 6s ease-in-out infinite;
        margin-bottom: 10px;
    }

    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(2deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    .hero-title {
        font-size: 4.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #e0f2fe 0%, #38bdf8 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        letter-spacing: -1.5px;
        line-height: 1.1;
        filter: drop-shadow(0px 4px 10px rgba(0,0,0,0.5));
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.3rem;
        font-weight: 300;
        margin-top: 12px;
    }

    .stTextInput input {
        height: 54px !important; 
        background: rgba(255, 255, 255, 0.92) !important; 
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        border-radius: 16px !important;
        padding: 0 20px !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); 
    }

    .stTextInput input::placeholder {
        color: #64748b !important;
        font-weight: 400 !important;
    }

    .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.4) !important; 
        background: #ffffff !important;
    }

    /* Przycisk Audytu */
    .stButton button {
        height: 54px !important; 
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%) !important;
        color: white !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0 2rem !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(56, 189, 248, 0.4) !important;
        background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 100%) !important;
    }

    /* Karty Wyników */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 24px;
        border-radius: 24px;
        box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.6);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-6px);
        border-color: rgba(56, 189, 248, 0.5);
    }
    div[data-testid="stMetric"] label { color: #cbd5e1 !important; font-size: 1.1rem !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important; font-size: 2rem !important;
    }

    div[data-testid="stAlert"] {
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
    }
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] h3,
    div[data-testid="stAlert"] strong,
    div[data-testid="stAlert"] span {
        color: #ffffff !important;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.5) !important;
    }

    div[data-testid="stStatusWidget"] {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(15px) !important;
    }
    div[data-testid="stStatusWidget"] *,
    div[data-testid="stStatusWidget"] summary span,
    div[data-testid="stStatusWidget"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    .stMarkdown p {
        color: #f8fafc !important;
    }

    .streamlit-expanderHeader,
    div[data-testid="stExpander"] details summary {
        background: rgba(255, 255, 255, 0.12) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    .streamlit-expanderHeader *,
    div[data-testid="stExpander"] details summary * {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_ml_model():
    return joblib.load('travel_price_predictor.pkl')

@st.cache_resource
def init_pipeline_services():
    return TravelOfferScraper(headless=True), OfferAnalyzer(), OfferStorage()

model = load_ml_model()
scraper, analyzer, storage = init_pipeline_services()

st.markdown('''
<div class="hero-container">
    <svg class="logo-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 2L11 13" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M22 2L15 22L11 13L2 9L22 2Z" fill="url(#grad)" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <defs>
            <linearGradient id="grad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                <stop stop-color="#38bdf8" stop-opacity="0.9"/>
                <stop offset="1" stop-color="#818cf8" stop-opacity="0.2"/>
            </linearGradient>
        </defs>
    </svg>
    <h1 class="hero-title">Check My Trip</h1>
    <p class="hero-subtitle">Sprawdź ofertę, zanim zarezerwujesz.</p>
</div>
''', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1], gap="small")
with col_input:
    url_input = st.text_input("🔗", placeholder="Wklej link do oferty (np. z wakacje.pl)...", label_visibility="collapsed")
with col_btn:
    search_clicked = st.button("Wyceń", type="primary")

st.markdown("<br>", unsafe_allow_html=True)

if search_clicked:
    if not url_input:
        st.warning("⚠️ Proszę wkleić poprawny link do oferty.")
    else:
        with st.status("✈️ Analizowanie Twojej wycieczki...", expanded=True) as status:
            
            st.write("🌐 Ładowanie strony z ofertą...")
            html_content = scraper.get_offer_text(url_input)
            
            if not html_content or html_content.startswith("Error fetching"):
                status.update(label="Nie udało się otworzyć strony!", state="error", expanded=False)
                st.error("Wystąpił problem z pobraniem oferty. Sprawdź, czy link jest poprawny.")
                st.stop()

            expired_keywords = ["oferta nieaktualna", "wyprzedane", "brak miejsc", "nie znaleziono oferty", "przepraszamy, oferta"]
            if any(kw in html_content.lower() for kw in expired_keywords):
                status.update(label="Oferta wyprzedana!", state="error", expanded=False)
                st.error("⚠️ Przepraszamy, ta oferta została wyprzedana lub jest już nieaktualna.")
                st.stop()

            st.write("🤖 Odczytywanie szczegółów oferty...")
            try:
                offer_dict = analyzer.extract_information(html_content)
            except Exception as e:
                status.update(label="Problem z analizą danych!", state="error", expanded=False)
                st.error("Nie udało się odczytać szczegółów z tej strony. Spróbuj ponownie.")
                st.stop()

            if offer_dict and offer_dict.get('hotel_name') and offer_dict.get('price_per_person') is not None:
                try:
                    storage.save_offer(url_input, offer_dict)
                    storage.update_source_status(url_input, 'PROCESSED')
                except Exception:
                    pass

            st.write("📊 Porównywanie z cenami rynkowymi...")
            
            eval_dict = offer_dict.copy()
            eval_dict['scraped_at'] = datetime.now().strftime('%Y-%m-%d')
            actual_price = eval_dict.pop('price_per_person', None)
            
            df_raw = pd.DataFrame([eval_dict])
            
            try:
                predicted_price = model.predict(df_raw)[0]
            except Exception as e:
                status.update(label="Błąd podczas wyliczania ceny!", state="error", expanded=False)
                st.error(f"Wystąpił problem podczas porównywania z bazą rynkową. {e}")
                st.stop()

            status.update(label="Wycena zakończona! 🎉", state="complete", expanded=False)

        st.markdown("---")

        st.markdown('<img src="https://images.unsplash.com/photo-1512100356356-de1b84283e18?auto=format&fit=crop&w=1600&q=80" style="width:100%; border-radius: 24px; height: 180px; object-fit: cover; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">', unsafe_allow_html=True)
        
        mcol1, mcol2, mcol3, mcol4 = st.columns(4, gap="medium")
        
        with mcol1:
            st.metric(label="🏨 Hotel", value=offer_dict.get('hotel_name', 'Brak'))
        with mcol2:
            st.metric(label="🌍 Kierunek", value=f"{offer_dict.get('country', '')}")
        with mcol3:
            st.metric(label="💰 Cena w ofercie", value=f"{actual_price:,.2f} PLN" if actual_price else "Brak")
        with mcol4:
            st.metric(label="🤖 Wycena AI", value=f"{predicted_price:,.2f} PLN")
            
        st.markdown("<br>", unsafe_allow_html=True)

        if actual_price:
            diff = predicted_price - actual_price
            diff_pct = (abs(diff) / predicted_price) * 100
            
            if diff > 300:
                st.balloons()
                st.success(f"""
                ### 🔥 SUPER OKAZJA!
                Ta wycieczka jest tańsza o **{diff:,.2f} PLN** ({diff_pct:.1f}%) w stosunku do średnich cen rynkowych za ten sam standard. 
                **Zdecydowanie warto rezerwować!**
                """)
            elif diff < -300:
                st.error(f"""
                ### ⚠️ UWAGA – PRZEPŁACASZ!
                Ta oferta jest droższa o **{abs(diff):,.2f} PLN** ({diff_pct:.1f}%) od rynkowej wartości. 
                Zalecamy poszukanie innej wycieczki w podobnym standardzie.
                """)
            else:
                st.info(f"""
                ### ⚖️ UCZCIWA CENA
                Cena tej wycieczki jest jak najbardziej odpowiednia do jej standardu i lokalizacji.
                """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔍 Zobacz szczegółowy raport techniczny AI"):
            st.json(offer_dict)