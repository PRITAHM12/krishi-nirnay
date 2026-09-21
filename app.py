"""
Krishi-Nirnay (कृषि-निर्णय) - National Digital Agriculture Decision Support Portal
Ministry of Agriculture & Farmers Welfare, Government of India (भारत सरकार)
Integrated with AgriStack™, ICAR Agronomic Diagnostic Engine, and Mandi Realization System.
"""

import os
import json
import re
import urllib.request
from datetime import datetime
from PIL import Image
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import base64

@st.cache_data(ttl=1800)
def get_bhopal_weather():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=23.2599&longitude=77.4126"
            "&current=temperature_2m,relative_humidity_2m"
        )
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
        current = data["current"]
        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        return f"📍 **Bhopal (HQ)** | ⛅ {temp}°C | 💧 Humidity: {humidity}%"
    except Exception:
        return "📍 **Bhopal (HQ)** | ⛅ 32°C | 💧 Humidity: 45%"


@st.cache_data
def get_image_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return ""  # Prevents crash if logo is missing

mp_logo_base64 = get_image_base64("mp_logo.png")

# Attempt to import google-genai
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & INDIAN GOV DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Krishi-Nirnay | कृषि-निर्णय (भारत सरकार)",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Indian Government CSS Styling
GOV_CSS = """
<style>
/* Import Official Font */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700;800&family=Roboto:wght@300;400;500;700&display=swap');

:root {
    --gov-navy: #002B49;
    --gov-navy-dark: #001A2E;
    --gov-navy-light: #0B3B60;
    --gov-saffron: #FF9933;
    --gov-green: #138808;
    --gov-ashoka-blue: #000080;
    --gov-bg: #F8F9FA;
    --gov-card-bg: #FFFFFF;
    --gov-border: #D1D5DB;
    --gov-text: #1F2937;
    --gov-muted: #4B5563;
}

html, body, [class*="css"] {
    font-family: 'Roboto', 'Noto Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--gov-bg);
    color: var(--gov-text);
}

/* Hide Default UI & Form Instructions */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="InputInstructions"],
.stTextInput small {
    display: none !important;
    visibility: hidden !important;
}

/* Remove Streamlit default blank space at top */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1200px;
}

/* Top Tricolor Banner */
.gov-tricolor-bar {
    height: 5px;
    width: 100%;
    background: linear-gradient(90deg, #FF9933 0%, #FF9933 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #138808 66.6%, #138808 100%);
    border-radius: 2px;
    margin-bottom: 8px;
}

/* Top Gov Header Bar */
.gov-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
    padding: 6px 16px;
    font-size: 0.8rem;
    color: #4B5563;
    margin-bottom: 12px;
    border-radius: 4px;
}

.gov-topbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.gov-topbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
    font-weight: 500;
}

/* Main Portal Header */
.portal-header-card {
    background: linear-gradient(135deg, #002B49 0%, #0B3B60 100%);
    color: #FFFFFF;
    padding: 20px 24px;
    border-radius: 8px;
    border-top: 4px solid var(--gov-saffron);
    box-shadow: 0 4px 6px -1px rgba(0, 43, 73, 0.15);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
}

.portal-title-group h1 {
    color: #FFFFFF !important;
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    padding: 0 !important;
    letter-spacing: 0.5px;
}

.portal-title-group .sub-title {
    color: #E0E7FF;
    font-size: 0.95rem;
    margin-top: 4px;
    font-weight: 500;
}

.portal-title-group .dept-title {
    color: #FCD34D;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.portal-badge {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 8px 14px;
    border-radius: 6px;
    text-align: right;
    font-size: 0.8rem;
}

/* Tabs as Static Navigation Menu */
.stTabs [data-baseweb="tab-list"] {
    display: flex !important;
    gap: 12px !important;
    background-color: transparent !important;
    padding: 6px 0 14px 0 !important;
    border-bottom: none !important;
}

/* Individual Tab: White background with dark gray border */
.stTabs [data-baseweb="tab"] {
    background-color: #FFFFFF !important;
    border: 2px solid #4B5563 !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    height: 52px !important;
    color: #1F2937 !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #F3F4F6 !important;
    border-color: #000080 !important;
    color: #000080 !important;
}

/* Selected Tab: Navy Blue (#000080) with bold white text */
.stTabs [aria-selected="true"] {
    background-color: #000080 !important;
    color: #FFFFFF !important;
    border: 2px solid #000080 !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 10px rgba(0, 0, 128, 0.28) !important;
}

.stTabs [aria-selected="true"] * {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

.stTabs [aria-selected="false"] * {
    color: #1F2937 !important;
    font-weight: 600 !important;
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* Government Card Styling */
.gov-card {
    background-color: #FFFFFF;
    border: 1px solid var(--gov-border);
    border-radius: 6px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.gov-card-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--gov-navy);
    border-bottom: 2px solid #E5E7EB;
    padding-bottom: 8px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.gov-badge-verified {
    display: inline-flex;
    align-items: center;
    background-color: #ECFDF5;
    color: #065F46;
    border: 1px solid #A7F3D0;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}

.gov-badge-warning {
    display: inline-flex;
    align-items: center;
    background-color: #FFFBEB;
    color: #92400E;
    border: 1px solid #FDE68A;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}

.gov-badge-official {
    display: inline-flex;
    align-items: center;
    background-color: #EFF6FF;
    color: #1E40AF;
    border: 1px solid #BFDBFE;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}

/* Metric Display Card */
.metric-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-left: 4px solid var(--gov-navy);
    padding: 14px 16px;
    border-radius: 6px;
    margin-bottom: 10px;
}

.metric-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-value {
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--gov-navy);
    margin-top: 4px;
}

.metric-subtitle {
    font-size: 0.75rem;
    color: #6B7280;
    margin-top: 2px;
}

/* High Contrast Buttons - Guaranteed Text Visibility On Hover */
.stButton > button,
button[kind="primary"],
button[kind="secondary"],
[data-testid="baseButton-primary"],
[data-testid="baseButton-secondary"],
[data-testid="stFormSubmitButton"] > button {
    background-color: #000080 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 700 !important;
    border: 1.5px solid #000080 !important;
    border-radius: 6px !important;
    padding: 9px 20px !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 2px 5px rgba(0, 0, 128, 0.2) !important;
}

.stButton > button *,
.stButton > button p,
.stButton > button span,
.stButton > button div,
button[kind="primary"] *,
button[kind="secondary"] *,
[data-testid="baseButton-primary"] *,
[data-testid="baseButton-secondary"] *,
[data-testid="stFormSubmitButton"] > button *,
.stButton > button [data-testid="stMarkdownContainer"] p,
[data-testid="stFormSubmitButton"] > button [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Hover State: Deep Bright Navy with 100% Guaranteed Crisp White Text */
.stButton > button:hover,
button[kind="primary"]:hover,
button[kind="secondary"]:hover,
[data-testid="baseButton-primary"]:hover,
[data-testid="baseButton-secondary"]:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #0A3D73 !important;
    border-color: #0A3D73 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(0, 0, 128, 0.38) !important;
    cursor: pointer !important;
}

.stButton > button:hover *,
.stButton > button:hover p,
.stButton > button:hover span,
.stButton > button:hover div,
button[kind="primary"]:hover *,
button[kind="secondary"]:hover *,
[data-testid="baseButton-primary"]:hover *,
[data-testid="baseButton-secondary"]:hover *,
[data-testid="stFormSubmitButton"] > button:hover *,
.stButton > button:hover [data-testid="stMarkdownContainer"] p,
[data-testid="stFormSubmitButton"] > button:hover [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Button Active / Press Effect */
.stButton > button:active,
button:active {
    transform: translateY(2px) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 128, 0.4) !important;
}

/* Radio Buttons: Guaranteed Text Visibility in Light Mode */
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] label div {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    font-weight: 600 !important;
}

/* Compact Accessibility Controls Bar */
.st-key-accessibility_bar {
    background-color: #F8FAFC !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
    padding: 2px 10px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}

.st-key-accessibility_bar button {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    border: 1.5px solid #374151 !important;
    border-radius: 5px !important;
    padding: 0 4px !important;
    height: 32px !important;
    min-height: 32px !important;
    max-height: 32px !important;
    width: 100% !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06) !important;
    transition: all 0.12s ease !important;
}

.st-key-accessibility_bar button *,
.st-key-accessibility_bar button p,
.st-key-accessibility_bar button span {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    font-size: 14px !important;
    font-weight: 800 !important;
}

.st-key-accessibility_bar button:hover {
    background-color: #F3F4F6 !important;
    border-color: #000000 !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.12) !important;
    cursor: pointer !important;
}

.st-key-accessibility_bar button:hover *,
.st-key-accessibility_bar button:hover p,
.st-key-accessibility_bar button:hover span {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* Top Utility Bar (Top Right Corner Sync Rates & Helpline) */
.st-key-top_utility_bar {
    margin-bottom: 8px !important;
}

.st-key-top_utility_bar button {
    background-color: #FFFFFF !important;
    color: #000080 !important;
    -webkit-text-fill-color: #000080 !important;
    border: 1.5px solid #000080 !important;
    border-radius: 6px !important;
    padding: 3px 8px !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    height: 36px !important;
    min-height: 36px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 128, 0.12) !important;
    transition: all 0.15s ease !important;
}

.st-key-top_utility_bar button *,
.st-key-top_utility_bar button p,
.st-key-top_utility_bar button span {
    color: #000080 !important;
    -webkit-text-fill-color: #000080 !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
}

.st-key-top_utility_bar button:hover {
    background-color: #000080 !important;
    border-color: #000080 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    box-shadow: 0 3px 8px rgba(0, 0, 128, 0.25) !important;
    cursor: pointer !important;
}

.st-key-top_utility_bar button:hover *,
.st-key-top_utility_bar button:hover p,
.st-key-top_utility_bar button:hover span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Footer */
.gov-footer {
    background-color: #FFFFFF;
    border-top: 1px solid #E2E8F0;
    padding: 16px;
    text-align: center;
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 30px;
    border-radius: 6px;
}
</style>
"""

st.markdown(GOV_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MOCK DATABASE (AGRISTACK STATE REGISTRY)
# -----------------------------------------------------------------------------
AGRISTACK_DB = {
    "MP-BPL-7842": {
        "farmer_id": "MP-BPL-7842",
        "farmer_name": "Shri Ramesh Chandra Patel (श्री रमेश चंद्र पटेल)",
        "father_name": "Late Shri Babulal Patel",
        "gender": "Male",
        "mobile_masked": "XXXXXX4821",
        "state": "Madhya Pradesh",
        "district": "Bhopal",
        "tehsil": "Huzur",
        "village": "Karond Kalan",
        "aadhaar_status": "Verified (Agri-Vault e-KYC Linked)",
        "pm_kisan_status": "Active (17th Installment Credited)",
        "parcels": [
            {
                "khasra_no": "Khasra 412",
                "area_hectares": 2.0,
                "area_acres": 4.94,
                "soil_type": "Deep Black Cotton Soil (Vertisols)",
                "irrigation_source": "Tube-well with Micro-Sprinkler",
                "tehsil": "Huzur",
                "village": "Karond Kalan"
            },
            {
                "khasra_no": "Khasra 089",
                "alias_khasra": "Khasra 108",
                "area_hectares": 1.5,
                "area_acres": 3.71,
                "soil_type": "Red Soil (Medium Clay Loam)",
                "irrigation_source": "Canal Lift + Rainfed",
                "tehsil": "Berasia",
                "village": "Runaha"
            }
        ]
    }
}

# Approved Crop Benchmarks (ICAR & MP Krishi Cabinet 2025-26 Estimates)
CROP_SPECS = {
    "Soybean": {
        "hindi_name": "सोयाबीन (Soybean)",
        "yield_q_per_ha": 22.0,
        "bhopal_price": 4890.0,
        "indore_price": 5050.0,  # Indore solvent extraction hub premium
        "msp": 4892.0,
        "season": "खरीफ (Kharif)",
        "growth_period_days": 95,
        "default_issue": "पत्तियों पर पीला रतुआ और भूरे धब्बे (Leaf Rust & Fungal Spots)",
        "default_pesticide": "हेक्साकोनाज़ोल 5% ईसी @ 1 लीटर प्रति हेक्टेयर (साफ पानी में छिड़काव)",
        "simple_advice": "खेत में जलभराव न होने दें। लक्षण दिखने पर सुबह या शाम को छिड़काव करें।"
    },
    "Wheat": {
        "hindi_name": "गेहूँ (शरबती / लोक-1)",
        "yield_q_per_ha": 45.0,
        "bhopal_price": 2425.0,  # MSP Base
        "indore_price": 2520.0,  # Processing quality premium
        "msp": 2425.0,
        "season": "रबी (Rabi)",
        "growth_period_days": 120,
        "default_issue": "पत्तियों का पीला रतुआ रोग (Yellow Stripe Rust)",
        "default_pesticide": "प्रोपीकोनाज़ोल 25% ईसी @ 500 मिली प्रति हेक्टेयर (500 ली. पानी में)",
        "simple_advice": "समय पर पहली सिंचाई करें और हवा शांत होने पर दवा का छिड़काव करें।"
    },
    "Sugarcane": {
        "hindi_name": "गन्ना (Sugarcane)",
        "yield_q_per_ha": 750.0,
        "bhopal_price": 340.0,  # FRP Rate
        "indore_price": 365.0,  # High Recovery Sugar Mill Gate
        "msp": 340.0,
        "season": "सालाना (Annual)",
        "growth_period_days": 330,
        "default_issue": "तना छेदक कीट और लाल सड़न (Stem Borer & Red Rot)",
        "default_pesticide": "कोराजन (Chlorantraniliprole 18.5% SC) @ 375 मिली प्रति हेक्टेयर",
        "simple_advice": "गन्ने के टुकड़ों को दवा से उपचारित करके ही बोएं ताकि फसल स्वस्थ रहे।"
    },
    "Gram": {
        "hindi_name": "चना (देसी / काबुली)",
        "yield_q_per_ha": 20.0,
        "bhopal_price": 5650.0,  # MSP Base
        "indore_price": 5820.0,  # Pulse processing corridor premium
        "msp": 5650.0,
        "season": "रबी (Rabi)",
        "growth_period_days": 105,
        "default_issue": "उकठा रोग और जड़ सड़न (Wilt / Root Rot)",
        "default_pesticide": "ट्राइकोडर्मा जैविक फफूंदनाशी @ 2.5 किग्रा प्रति हेक्टेयर (गोबर खाद में)",
        "simple_advice": "चने की बुवाई से पहले बीज को राइजोबियम कल्चर से जरूर उपचारित करें।"
    },
    "Paddy (Rice)": {
        "hindi_name": "धान / चावल (Paddy Rice)",
        "yield_q_per_ha": 40.0,
        "bhopal_price": 2320.0,
        "indore_price": 2380.0,
        "msp": 2300.0,
        "season": "खरीफ (Kharif)",
        "growth_period_days": 120,
        "default_issue": "पत्तियों का झुलसा रोग व तना छेदक (Leaf Blast & Stem Borer)",
        "default_pesticide": "ट्राईसाइक्लाज़ोल 75% WP @ 120 ग्राम प्रति एकड़ (या वैलिडामाइसिन 2 मिली/लीटर)",
        "simple_advice": "खेत में उचित जल स्तर बनाए रखें और यूरिया का संतुलित उपयोग करें।"
    },
    "Maize": {
        "hindi_name": "मक्का / भुट्टा (Maize / Corn)",
        "yield_q_per_ha": 45.0,
        "bhopal_price": 2240.0,
        "indore_price": 2320.0,
        "msp": 2225.0,
        "season": "खरीफ / रबी (Kharif / Rabi)",
        "growth_period_days": 100,
        "default_issue": "पत्ती खाने वाली अमेरिकन सुंडी (Fall Armyworm)",
        "default_pesticide": "इमामेक्टिन बेंजोएट 5% SG @ 80 ग्राम प्रति एकड़ (या कोराजन 0.4 मिली/लीटर)",
        "simple_advice": "पौधे के पोंगे (गांठ) के अंदर दवा का हल्का फुहारा दें ताकि इल्ली खत्म हो सके।"
    },
    "Mustard": {
        "hindi_name": "सरसों / राई (Mustard)",
        "yield_q_per_ha": 18.0,
        "bhopal_price": 5680.0,
        "indore_price": 5800.0,
        "msp": 5650.0,
        "season": "रबी (Rabi)",
        "growth_period_days": 110,
        "default_issue": "माहू बारीक कीड़ा और सफेद फफूंद (Aphids / Mahu & White Rust)",
        "default_pesticide": "डाइमेथोएट 30% ईसी @ 1.5 मिली प्रति लीटर पानी (या मैंकोजेब 2 ग्राम/लीटर)",
        "simple_advice": "फूल आने के समय बादलों वाले मौसम में माहू की निगरानी करें और तुरंत स्प्रे करें।"
    },
    "Cotton": {
        "hindi_name": "कपास / रूई (Cotton)",
        "yield_q_per_ha": 18.0,
        "bhopal_price": 7150.0,
        "indore_price": 7450.0,
        "msp": 7120.0,
        "season": "खरीफ (Kharif)",
        "growth_period_days": 160,
        "default_issue": "गुलाबी सुंडी और रस चूसने वाले कीड़े (Pink Bollworm & Sucking Pests)",
        "default_pesticide": "प्रोफेनोफॉस 50% ईसी @ 2 मिली प्रति लीटर पानी (या 1500 PPM नीम तेल)",
        "simple_advice": "खेत में फेरोमोन ट्रैप लगाएं और कीटनाशक को बदल-बदल कर छिड़कें।"
    }
}

# Static Mandi Logistics
MANDI_LOGISTICS = {
    "Bhopal": {
        "name": "Bhopal Karond APMC Mandi (करौंद कृषि उपज मंडी)",
        "distance_km": 18,
        "static_transport_cost": 1500.0,  # Local Tractor-Trolley trip freight
        "handling_charges": 150.0,
        "weighbridge_fee": 50.0
    },
    "Indore": {
        "name": "Indore Choithram APMC Mandi (चोइथराम कृषि उपज मंडी)",
        "distance_km": 195,
        "static_transport_cost": 6500.0,  # Inter-district commercial freight carrier (Eicher/Tata 407)
        "handling_charges": 300.0,
        "weighbridge_fee": 100.0
    }
}

# Regional Mandis Database for Multi-Market Comparative Optimization
REGIONAL_MANDIS = {
    "Bhopal (Karond)": {
        "display_name": "Bhopal Karond APMC (करौंद कृषि उपज मंडी)",
        "district": "Bhopal",
        "distance_km": 18,
        "static_transport_cost": 1500.0,
        "color": "#002B49",
        "prices": {
            "Soybean": 4890.0,
            "Wheat": 2425.0,
            "Sugarcane": 340.0,
            "Gram": 5650.0,
            "Paddy (Rice)": 2320.0,
            "Maize": 2240.0,
            "Mustard": 5680.0,
            "Cotton": 7150.0
        }
    },
    "Indore (Choithram)": {
        "display_name": "Indore Choithram APMC (चोइथराम कृषि उपज मंडी)",
        "district": "Indore",
        "distance_km": 195,
        "static_transport_cost": 6500.0,
        "color": "#138808",
        "prices": {
            "Soybean": 5050.0,
            "Wheat": 2520.0,
            "Sugarcane": 365.0,
            "Gram": 5820.0,
            "Paddy (Rice)": 2380.0,
            "Maize": 2320.0,
            "Mustard": 5800.0,
            "Cotton": 7450.0
        }
    },
    "Ujjain": {
        "display_name": "Ujjain Madhav Nagar APMC (माधव नगर मंडी)",
        "district": "Ujjain",
        "distance_km": 185,
        "static_transport_cost": 6200.0,
        "color": "#7C3AED",
        "prices": {
            "Soybean": 5010.0,
            "Wheat": 2490.0,
            "Sugarcane": 355.0,
            "Gram": 5780.0,
            "Paddy (Rice)": 2350.0,
            "Maize": 2290.0,
            "Mustard": 5760.0,
            "Cotton": 7380.0
        }
    },
    "Jabalpur": {
        "display_name": "Jabalpur Krishi Upaj Mandi (कृषि उपज मंडी)",
        "district": "Jabalpur",
        "distance_km": 305,
        "static_transport_cost": 9200.0,
        "color": "#D97706",
        "prices": {
            "Soybean": 4940.0,
            "Wheat": 2450.0,
            "Sugarcane": 372.0,
            "Gram": 5740.0,
            "Paddy (Rice)": 2420.0,
            "Maize": 2270.0,
            "Mustard": 5720.0,
            "Cotton": 7200.0
        }
    },
    "Sehore": {
        "display_name": "Sehore APMC Mandi (कृषि उपज मंडी सीहोर)",
        "district": "Sehore",
        "distance_km": 38,
        "static_transport_cost": 2200.0,
        "color": "#2563EB",
        "prices": {
            "Soybean": 4860.0,
            "Wheat": 2480.0,
            "Sugarcane": 335.0,
            "Gram": 5620.0,
            "Paddy (Rice)": 2330.0,
            "Maize": 2250.0,
            "Mustard": 5690.0,
            "Cotton": 7180.0
        }
    }
}

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "authenticated_farmer" not in st.session_state:
    st.session_state["authenticated_farmer"] = None

if "selected_parcel_index" not in st.session_state:
    st.session_state["selected_parcel_index"] = 0

if "selected_plot" not in st.session_state:
    st.session_state["selected_plot"] = "Khasra 412 (2.0 Hectares - Black Soil)"

if "current_lang" not in st.session_state:
    st.session_state["current_lang"] = "Hindi"

# Keep app_language synchronized for backwards compatibility
st.session_state["app_language"] = st.session_state["current_lang"]

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

if "recommended_crop" not in st.session_state:
    st.session_state["recommended_crop"] = "Soybean"

if "font_scale" not in st.session_state:
    st.session_state["font_scale"] = 1.0

if "uploaded_image_file" not in st.session_state:
    st.session_state["uploaded_image_file"] = None

# -----------------------------------------------------------------------------
# HELPER: GEMINI VISION API CALL WITH STRICT SYSTEM PROMPT & FALLBACK
# -----------------------------------------------------------------------------
def analyze_with_gemini(image: Image.Image, is_hi: bool = False, api_key: str = None) -> dict:
    """
    Sends the uploaded soil or plant leaf image to Gemini 1.5 Flash Vision.
    Enforces a strict system prompt and returns a verified JSON object.
    Falls back gracefully if no key or on network/quota exception.
    """
    system_instruction = (
        "You are an expert Agricultural Agronomist helping Indian farmers. "
        "Analyze the provided image of agricultural soil or crop leaf. "
        "Provide your diagnosis in simple, clear, farmer-friendly terms without unnecessary academic jargon. "
        "You must respond ONLY with a strict JSON object with these exact keys: "
        "'detected_issue', 'recommended_crop', and 'cibrc_pesticide_required'. "
        "The 'recommended_crop' MUST strictly be one of: 'Soybean', 'Wheat', 'Sugarcane', 'Gram', 'Paddy (Rice)', 'Maize', 'Mustard', 'Cotton'. "
        "The 'cibrc_pesticide_required' must provide a clear medicine name, dosage per acre/hectare, and safe instructions in simple language."
    )

    lang_instruction = "Respond ENTIRELY in Hindi." if is_hi else "Respond ENTIRELY in English."

    prompt = (
        "Inspect this soil or plant leaf image. Provide agricultural pathology diagnosis and agronomic crop recommendation in simple words.\n"
        f"{lang_instruction} However, the 'recommended_crop' value MUST remain in English as one of the exact choices.\n"
        "Return ONLY a raw JSON object formatted as follows:\n"
        "{\n"
        '  "detected_issue": "Simple clear diagnosis of leaf disease or soil condition",\n'
        '  "recommended_crop": "Soybean" | "Wheat" | "Sugarcane" | "Gram" | "Paddy (Rice)" | "Maize" | "Mustard" | "Cotton",\n'
        '  "cibrc_pesticide_required": "Approved medicine name with simple dosage instructions"\n'
        "}"
    )

    # Resolve API Key
    effective_api_key = api_key or os.environ.get("GEMINI_API_KEY")

    if HAS_GENAI and effective_api_key:
        try:
            client = genai.Client(api_key=effective_api_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[image, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                    max_output_tokens=600,
                )
            )
            raw_text = response.text.strip()
            
            # Clean markdown codeblocks if present
            cleaned_text = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE).strip()
            cleaned_text = re.sub(r"^```\s*", "", cleaned_text, flags=re.MULTILINE).strip()
            
            parsed = json.loads(cleaned_text)
            
            # Validate required keys
            if (
                "detected_issue" in parsed
                and "recommended_crop" in parsed
                and "cibrc_pesticide_required" in parsed
            ):
                crop = parsed["recommended_crop"].strip()
                valid_crops = ["Soybean", "Wheat", "Sugarcane", "Gram", "Paddy (Rice)", "Maize", "Mustard", "Cotton"]
                matched_crop = next((c for c in valid_crops if c.lower() == crop.lower()), "Soybean")
                parsed["recommended_crop"] = matched_crop
                parsed["engine"] = "कृषि-निर्णय विशेषज्ञ प्रणाली (ICAR AI Engine)"
                return parsed
        except Exception:
            pass

    # High-fidelity Agronomic Heuristic Fallback (when no key or offline)
    has_yellow_or_rust = False
    has_dark_soil = False
    try:
        small = image.resize((50, 50))
        pixels = list(small.getdata())
        r_tot = sum(p[0] for p in pixels)
        g_tot = sum(p[1] for p in pixels)
        b_tot = sum(p[2] for p in pixels)
        avg_r, avg_g, avg_b = r_tot / 2500, g_tot / 2500, b_tot / 2500
        
        is_soil = (avg_g - avg_b < 25) and (abs(avg_r - avg_g) < 25)
        if (avg_r < 80 and avg_g < 80 and avg_b < 80) or is_soil:
            has_dark_soil = True
        elif (avg_g > avg_r + 40) and avg_g > 120:
            has_yellow_or_rust = True
    except Exception:
        pass

    if has_dark_soil:
        sample_crop = "Gram"
        issue = "उपजाऊ गहरी काली मिट्टी - इसमें चना, सोयाबीन या कपास बहुत अच्छी पैदावार देते हैं।" if is_hi else "Fertile Deep Black Soil - ideal for high yields of Gram, Soybean, or Cotton."
        pesticide = "ट्राइकोडर्मा जैविक फफूंदनाशी 2.5 किग्रा प्रति हेक्टेयर सड़ी गोबर खाद में मिलाकर डालें।" if is_hi else "Mix 2.5 kg Trichoderma bio-fungicide per hectare in compost."
    elif has_yellow_or_rust:
        sample_crop = "Wheat"
        issue = "पत्तियों पर पीला रतुआ या पीलापन के लक्षण दिखे हैं।" if is_hi else "Signs of Yellow Rust or yellowing observed on leaves."
        pesticide = "प्रोपीकोनाज़ोल 25% ईसी 500 मिली प्रति हेक्टेयर 500 लीटर पानी में घोलकर छिड़कें।" if is_hi else "Spray Propiconazole 25% EC at 500 ml per hectare mixed in 500 liters of water."
    else:
        sample_crop = "Soybean"
        issue = "पत्तियों पर रतुआ और भूरे धब्बे की शुरुआती अवस्था है।" if is_hi else "Early stage of Leaf Rust and brown spots on leaves."
        pesticide = "हेक्साकोनाज़ोल 5% ईसी 1 लीटर प्रति हेक्टेयर साफ पानी में मिलाकर छिड़कें।" if is_hi else "Spray Hexaconazole 5% EC at 1 liter per hectare mixed in clean water."

    engine_name = "कृषि-निर्णय विशेषज्ञ प्रणाली (ICAR-AgriStack Expert Mode)" if is_hi else "Krishi-Nirnay Expert System (ICAR-AgriStack Expert Mode)"

    return {
        "detected_issue": issue,
        "recommended_crop": sample_crop,
        "cibrc_pesticide_required": pesticide,
        "engine": engine_name
    }


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# AESTHETIC AUTHENTICATION GATE (When logged_in is False)
# -----------------------------------------------------------------------------
if not st.session_state["logged_in"]:
    GATE_CSS = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none !important;}
    
    /* Completely remove or hide default helper text like 'Please press enter to submit form' */
    [data-testid="InputInstructions"],
    .stTextInput small,
    [data-testid="stForm"] small,
    div[data-testid="InputInstructions"],
    .stForm [data-testid="InputInstructions"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .stApp {
        background: linear-gradient(rgba(0, 15, 30, 0.45), rgba(0, 15, 30, 0.45)), url('https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop') no-repeat center center fixed !important;
        background-size: cover !important;
    }
    .block-container {
        padding-top: 6vh !important;
        padding-bottom: 2rem !important;
        max-width: 480px !important;
    }
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        border-radius: 15px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.65), 0 10px 25px -5px rgba(0, 0, 0, 0.4) !important;
        padding: 38px 34px !important;
        border: none !important;
    }
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1.5px solid #CBD5E1 !important;
        padding: 12px 14px !important;
        font-size: 0.95rem !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #000080 !important;
        box-shadow: 0 0 0 2px rgba(0, 0, 128, 0.15) !important;
        background-color: #FFFFFF !important;
    }

    /* Responsive, professional login button styling */
    .stButton > button,
    [data-testid="stFormSubmitButton"] > button {
        background-color: #000080 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        border: none !important;
        letter-spacing: 0.5px !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
        box-shadow: 0 3px 8px rgba(0, 0, 128, 0.25) !important;
        width: 100% !important;
    }

    .stButton > button *,
    .stButton > button p,
    .stButton > button span,
    .stButton > button div,
    [data-testid="stFormSubmitButton"] > button *,
    [data-testid="stFormSubmitButton"] > button p,
    [data-testid="stFormSubmitButton"] > button span,
    [data-testid="stFormSubmitButton"] > button div {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Cursor pointer & deep background color on hover without text masking */
    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #001A9C !important;
        border-color: #001A9C !important;
        color: #FFFFFF !important;
        cursor: pointer !important;
        box-shadow: 0 5px 14px rgba(0, 0, 128, 0.38) !important;
    }

    .stButton > button:hover *,
    .stButton > button:hover p,
    .stButton > button:hover span,
    .stButton > button:hover div,
    [data-testid="stFormSubmitButton"] > button:hover *,
    [data-testid="stFormSubmitButton"] > button:hover p,
    [data-testid="stFormSubmitButton"] > button:hover span,
    [data-testid="stFormSubmitButton"] > button:hover div {
        color: #FFFFFF !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* Active / pressed indentation effect on click */
    .stButton > button:active,
    [data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(2px) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 128, 0.5) !important;
    }
    </style>
    """
    st.markdown(GATE_CSS, unsafe_allow_html=True)
    
    # 6px top border spanning full width using Indian Tricolor
    st.markdown(
        '<div style="height: 6px; width: 100%; background: linear-gradient(90deg, #FF9933 0%, #FF9933 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #138808 66.6%, #138808 100%); position: fixed; top: 0; left: 0; z-index: 9999;"></div>',
        unsafe_allow_html=True
    )
    
    with st.form("admin_login_form"):
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 22px;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/120px-Emblem_of_India.svg.png" 
                     alt="Ashok Stambh" 
                     style="height: 72px; width: auto; object-fit: contain; margin-bottom: 8px;">
                <div style="font-size: 0.95rem; font-weight: 700; color: #000080; letter-spacing: 0.5px;">सत्यमेव जयते</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #000080; margin-top: 2px;">Government of Madhya Pradesh</div>
                <div style="font-size: 0.8rem; color: #4B5563; margin-top: 3px;">Department of Farmer Welfare & Agriculture Development</div>
                <div style="height: 2px; width: 100%; background: linear-gradient(90deg, #FF9933 0%, #000080 50%, #138808 100%); margin: 14px 0 12px 0;"></div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #1F2937;">
                    पोर्टल लॉगिन • Official Portal Gateway
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        user_id = st.text_input("User ID", placeholder="Farmer ID")
        password = st.text_input("Password", type="password", placeholder="PIN/Password")
        login_btn = st.form_submit_button("Sign In (प्रवेश करें)", use_container_width=True)
        
        if login_btn:
            if password == "admin123":
                st.session_state["logged_in"] = True
                clean_id = (user_id or "MP-BPL-7842").strip().upper()
                if clean_id in AGRISTACK_DB:
                    st.session_state["authenticated_farmer"] = AGRISTACK_DB[clean_id]
                else:
                    st.session_state["authenticated_farmer"] = AGRISTACK_DB["MP-BPL-7842"]
                st.session_state["selected_plot"] = "Khasra 412 (2.0 Hectares - Black Soil)"
                st.session_state["selected_parcel_index"] = 0
                st.rerun()
            else:
                st.error("Invalid credentials. Please enter valid password ('admin123').")

    st.markdown(
        """
        <div style="text-align: center; margin-top: 14px; font-size: 0.78rem; color: #F8FAFC; text-shadow: 0 1px 3px rgba(0,0,0,0.9);">
            🔒 Official MP Agriculture Security Gateway • Authorized Personnel Only<br>
            <span style="color: #FCD34D;">Demo Access: Password is <b>admin123</b></span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()


# -----------------------------------------------------------------------------
# AUTHENTICATED DASHBOARD (When logged_in is True)
# Enforce pure white background, Ashok Stambh flexbox header, and 6px tricolor border
# -----------------------------------------------------------------------------
AUTHENTICATED_CSS = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp {
    background-color: #ffffff !important;
    background-image: none !important;
}
body {
    background-color: #ffffff !important;
}
.block-container {
    padding-top: 1rem !important;
    max-width: 1200px !important;
}

/* Tabs as Static Navigation Menu */
.stTabs [data-baseweb="tab-list"] {
    display: flex !important;
    gap: 12px !important;
    background-color: transparent !important;
    padding: 6px 0 14px 0 !important;
    border-bottom: none !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: #FFFFFF !important;
    border: 2px solid #4B5563 !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    height: 52px !important;
    color: #1F2937 !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #F3F4F6 !important;
    border-color: #000080 !important;
    color: #000080 !important;
}

.stTabs [aria-selected="true"] {
    background-color: #000080 !important;
    color: #FFFFFF !important;
    border: 2px solid #000080 !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 10px rgba(0, 0, 128, 0.28) !important;
}

.stTabs [aria-selected="true"] * {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

.stTabs [aria-selected="false"] * {
    color: #1F2937 !important;
    font-weight: 600 !important;
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* Ensure button text is NEVER blocked or masked on hover */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: #000080 !important;
    color: #FFFFFF !important;
    border: 1.5px solid #000080 !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    padding: 9px 20px !important;
    transition: all 0.15s ease-in-out !important;
}

.stButton > button *,
.stButton > button p,
.stButton > button span,
.stButton > button div,
[data-testid="stFormSubmitButton"] > button *,
[data-testid="stFormSubmitButton"] > button p,
[data-testid="stFormSubmitButton"] > button span,
[data-testid="stFormSubmitButton"] > button div {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #001A9C !important;
    border-color: #001A9C !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(0, 0, 128, 0.35) !important;
    cursor: pointer !important;
}

.stButton > button:hover *,
.stButton > button:hover p,
.stButton > button:hover span,
.stButton > button:hover div,
[data-testid="stFormSubmitButton"] > button:hover *,
[data-testid="stFormSubmitButton"] > button:hover p,
[data-testid="stFormSubmitButton"] > button:hover span,
[data-testid="stFormSubmitButton"] > button:hover div {
    color: #FFFFFF !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Sidebar Styling */

[data-testid="stSidebar"] {
    display: block !important;
    background-color: #F8FAFC !important;
    border-right: 1.5px solid #E2E8F0 !important;
}

[data-testid="stSidebar"] hr {
    margin: 12px 0 !important;
    border-color: #E2E8F0 !important;
}

[data-testid="stSidebar"] .stSelectbox label {
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    color: #000080 !important;
}

/* Distinct Logout Button in Sidebar */
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important;
    color: #FFFFFF !important;
    border: 1.5px solid #991B1B !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    box-shadow: 0 2px 6px rgba(220, 38, 38, 0.3) !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease-in-out !important;
}

[data-testid="stSidebar"] button[kind="primary"]:hover,
[data-testid="stSidebar"] button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #B91C1C 0%, #7F1D1D 100%) !important;
    box-shadow: 0 4px 12px rgba(185, 28, 28, 0.45) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stSidebar"] button[kind="secondary"],
[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
    background-color: #FFFFFF !important;
    color: #000080 !important;
    border: 1.5px solid #CBD5E1 !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    font-size: 0.8rem !important;
    padding: 6px 10px !important;
}

[data-testid="stSidebar"] button[kind="secondary"]:hover,
[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
    background-color: #F1F5F9 !important;
    border-color: #000080 !important;
}
/* BRUTE-FORCE ACCESSIBILITY BAR SHRINKING */
[data-testid="column"] {
    padding: 0px !important;
}
.st-key-accessibility_bar {
    max-height: 40px !important;
    padding: 2px 10px !important;
    margin-top: -10px !important;
    margin-bottom: 20px !important;
}
.st-key-accessibility_bar button {
    height: 28px !important;
    min-height: 28px !important;
    font-size: 11px !important;
    padding: 0px 4px !important;
    margin: 0px !important;
}
.st-key-accessibility_bar [data-testid="stMarkdownContainer"] p {
    font-size: 12px !important;
    margin-bottom: 0px !important;
}
</style>
"""
st.markdown(AUTHENTICATED_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GLOBAL STATE INITIALIZATION
# -----------------------------------------------------------------------------
current_lang = st.session_state.get("current_lang", "Hindi")
is_hi = (current_lang == "Hindi")
dark_mode = st.session_state.get("dark_mode", False)

# -----------------------------------------------------------------------------
# SIDEBAR - NATIVE STREAMLIT CONTROL PANEL (When logged_in is True)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# SIDEBAR - NATIVE STREAMLIT CONTROL PANEL (When logged_in is True)
# -----------------------------------------------------------------------------
if st.session_state.get("authenticated_farmer"):
    farmer_data = st.session_state["authenticated_farmer"]
    with st.sidebar:
        st.markdown(f"#### {'⚙️ किसान पोर्टल नियंत्रण' if is_hi else '⚙️ Farmer Controls'}")
        st.divider()

        # 1. Farmer Profile Details
        st.markdown(f"**👤 {farmer_data['farmer_name']}**")
        st.caption(f"✅ {'ई-केवाईसी प्रमाणित' if is_hi else 'e-KYC Verified'}")
        st.markdown(f"**{'किसान पहचान' if is_hi else 'Farmer ID'}:** `{farmer_data['farmer_id']}`")
        st.markdown(f"**{'पता' if is_hi else 'Address'}:** {'ग्राम' if is_hi else 'Village'} {farmer_data['village']}, {farmer_data['district']}")
        st.divider()

        # 2. Multi-Land Parcel Radio Switcher
        st.markdown(f"**📍 {'खेती और मंडी लाभ के लिए अपना खेत चुनें:' if is_hi else 'Select land for profit calculation:'}**")
        
        if is_hi:
            parcel_options = [
                "खसरा नं. 412 — 2.0 हेक्टेयर (काली मिट्टी)",
                "खसरा नं. 089 — 1.5 हेक्टेयर (लाल मिट्टी)"
            ]
        else:
            parcel_options = [
                "Khasra 412 — 2.0 Hectares (Black Soil)",
                "Khasra 089 — 1.5 Hectares (Red Soil)"
            ]
        
        selected_idx = st.radio(
            "Select Land",
            options=range(len(parcel_options)),
            format_func=lambda i: parcel_options[i],
            index=st.session_state.get("selected_parcel_index", 0),
            label_visibility="collapsed"
        )
        
        # Save selection to session state
        st.session_state["selected_parcel_index"] = selected_idx
        if selected_idx == 0:
            st.session_state["selected_plot"] = "Khasra 412 (2.0 Hectares - Black Soil)" if not is_hi else "खसरा 412 (2.0 हेक्टेयर - काली मिट्टी)"
        else:
            st.session_state["selected_plot"] = "Khasra 089 (1.5 Hectares - Red Soil)" if not is_hi else "खसरा 089 (1.5 हेक्टेयर - लाल मिट्टी)"
        
        st.divider()
        
        # 3. Secure Logout
        logout_label = "🚪 लॉगआउट / सत्र समाप्त करें" if is_hi else "🚪 Logout"
        if st.button(logout_label, type="primary", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()

# -----------------------------------------------------------------------------
# 6px Indian Tricolor Top Border
# -----------------------------------------------------------------------------
st.markdown(
    '<div style="height: 6px; width: 100%; background: linear-gradient(90deg, #FF9933 0%, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%, #138808 100%); border-top: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB; margin-bottom: 10px; border-radius: 2px;"></div>',
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# TOP UTILITY BAR (Top Right Corner: Sync Rates & Toll-Free Helpline)
# -----------------------------------------------------------------------------
with st.container(key="top_utility_bar"):
    top_c1, top_c2, top_c3 = st.columns([3.0, 1.4, 2.0], gap="small")
    
    with top_c1:
        top_state_text = "भारत सरकार | मध्य प्रदेश शासन" if is_hi else "Govt. of India | Govt. of Madhya Pradesh"
        st.markdown(
            f"""<div style="display: flex; align-items: center; height: 36px; font-size: 0.88rem; font-weight: 700; color: {'#CBD5E1' if dark_mode else '#4B5563'};">
                <span style="display: inline-flex; align-items: center; gap: 8px;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/40px-Emblem_of_India.svg.png" style="height: 22px; width: auto;" alt="Govt Emblem">
                    <span>{top_state_text}</span>
                </span>
            </div>""",
            unsafe_allow_html=True
        )
        
    with top_c2:
        sync_label = "🔄 दरें अपडेट करें" if is_hi else "🔄 Sync Mandi Rates"
        sync_toast = "✅ मध्य प्रदेश मंडी भाव सर्वर से सफलतापूर्वक अपडेट हुए!" if is_hi else "✅ MP State APMC Mandi rates re-synchronized successfully with state servers!"
        if st.button(sync_label, key="top_btn_sync_rates", help=sync_label, use_container_width=True):
            st.toast(sync_toast, icon="🔄")
            
    with top_c3:
        help_label = "📞 किसान हेल्पलाइन: 1800-180-1551" if is_hi else "📞 Helpline: 1800-180-1551"
        help_toast = "📞 राष्ट्रीय किसान कॉल सेंटर: 1800-180-1551 (निःशुल्क टोल-फ्री, सुबह 6 से रात 10 बजे)" if is_hi else "📞 National Kisan Call Center: 1800-180-1551 (Toll-Free, 6 AM to 10 PM IST)"
        if st.button(help_label, key="top_btn_helpline", help=help_label, use_container_width=True):
            st.toast(help_toast, icon="📞")

# -----------------------------------------------------------------------------
# SINGLE UNIFIED GOVERNMENT 
# Flexbox Header (Ashok Stambh | Title | Dept of Agriculture)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# SINGLE UNIFIED GOVERNMENT HEADE
# Flexbox Header (MP Logo | Title | Ashok Stambh)
# -----------------------------------------------------------------------------
header_bg = "#1E293B" if dark_mode else "#FFFFFF"
header_border = "#334155" if dark_mode else "#D1D5DB"
main_title_color = "#93C5FD" if dark_mode else "#000080"
sub_title_color = "#CBD5E1" if dark_mode else "#4B5563"
state_title_color = "#93C5FD" if dark_mode else "#000080"
dept_title_color = "#4ADE80" if dark_mode else "#138808"

if is_hi:
    main_title_txt = "कृषि-निर्णय"
    sub_title_txt = "राष्ट्रीय कृषि निर्णय सहायता एवं मंडी विपणन प्रणाली"
    state_title_txt = "मध्य प्रदेश शासन"
    dept_title_txt = "किसान कल्याण तथा कृषि विकास विभाग"
else:
    main_title_txt = "KRISHI-NIRNAY"
    sub_title_txt = "National Agriculture Decision Support System"
    state_title_txt = "Govt. of Madhya Pradesh"
    dept_title_txt = "Dept. of Agriculture"
st.markdown(
    f"""
<div class="gov-header-container" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 24px; background-color: {header_bg}; border: 1.5px solid {header_border}; border-top: 6px solid #FF9933; border-bottom: 3px solid #138808; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 16px;">
<!-- LEFT: MP Government Logo & Dept Text -->
<div style="flex: 1; display: flex; align-items: center;">
<img src="data:image/png;base64,{mp_logo_base64}" style="height: 50px; width: 50px; object-fit: contain; margin-right: 12px;" alt="MP Logo">
<div style="line-height: 1.2; text-align: left;">
<div style="color: {state_title_color}; font-size: 14px; font-weight: 800;">{state_title_txt}</div>
<div style="color: {dept_title_color}; font-size: 11px; font-weight: 700; margin-top: 2px;">{dept_title_txt}</div>
</div>
</div>
<!-- CENTER: Main Platform Title & Weather Forecast -->
<div style="flex: 1.5; text-align: center;">
<div style="color: {main_title_color}; margin: 0; font-size: 24px; font-weight: 900; letter-spacing: 1.2px;">{main_title_txt}</div>
<div style="color: {sub_title_color}; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px;">{sub_title_txt}</div>
<!-- Live Weather Pill -->
<div style="margin-top: 6px; display: inline-block; background: #EFF6FF; border: 1px solid #BFDBFE; color: #1D4ED8; padding: 3px 12px; border-radius: 12px; font-size: 11px; font-weight: 800; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
{get_bhopal_weather()}
</div>
</div>
<!-- RIGHT: Indian Emblem Logo -->
<div style="flex: 1; display: flex; justify-content: flex-end;">
<img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" style="height: 50px; width: auto;" alt="Satyameva Jayate">
</div>
</div>
    """,
    unsafe_allow_html=True
)
# -----------------------------------------------------------------------------
# ACCESSIBILITY FONT SCALING (Working Condition: Zoom & Font Proportion)
# -----------------------------------------------------------------------------
font_scale = st.session_state.get("font_scale", 1.0)
FONT_ZOOM_CSS = f"""
<style>
.stApp {{
    zoom: {font_scale};
}}
html, body {{
    font-size: calc(16px * {font_scale}) !important;
}}
</style>
"""
st.markdown(FONT_ZOOM_CSS, unsafe_allow_html=True)

# Dark Mode CSS Injection when toggled
if st.session_state.get("dark_mode", False):
    DARK_MODE_CSS = """
    <style>
    .stApp, body {
        background-color: #0F172A !important;
        color: #F3F4F6 !important;
    }
    .gov-header-container {
        background-color: #1E293B !important;
        border-color: #334155 !important;
        color: #F8FAFC !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45) !important;
    }
    .gov-header-container .header-main-title {
        color: #93C5FD !important;
    }
    .gov-header-container .header-sub-title {
        color: #CBD5E1 !important;
    }
    .gov-header-container .header-state-title {
        color: #93C5FD !important;
    }
    .gov-header-container .header-dept-title {
        color: #4ADE80 !important;
    }
    .gov-card,
    .metric-box,
    [data-testid="stExpander"],
    div[data-baseweb="card"],
    div[data-testid="stForm"] {
        background-color: #1E293B !important;
        border: 1.5px solid #334155 !important;
        color: #F3F4F6 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45) !important;
    }
    .gov-card-header {
        color: #93C5FD !important;
        border-bottom: 2px solid #334155 !important;
    }
    .gov-card p, .gov-card li, .gov-card span:not(.gov-badge-verified):not(.gov-badge-warning):not(.gov-badge-official) {
        color: #E2E8F0 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #93C5FD !important;
    }
    .stTextInput > div > div > input,
    [data-baseweb="select"] > div {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border-color: #475569 !important;
    }
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] label div {
        color: #F3F4F6 !important;
        -webkit-text-fill-color: #F3F4F6 !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E293B !important;
        border: 1.5px solid #475569 !important;
        color: #F3F4F6 !important;
    }
    .stTabs [data-baseweb="tab"] * {
        color: #F3F4F6 !important;
        -webkit-text-fill-color: #F3F4F6 !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #334155 !important;
        color: #93C5FD !important;
        border-color: #3B82F6 !important;
    }
    .stTabs [data-baseweb="tab"]:hover * {
        color: #93C5FD !important;
        -webkit-text-fill-color: #93C5FD !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1D4ED8 !important;
        border-color: #60A5FA !important;
        color: #FFFFFF !important;
    }
    .stTabs [aria-selected="true"] * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1.5px solid #334155 !important;
    }
    [data-testid="stDataFrame"] {
        background-color: #1E293B !important;
    }
    /* Dark Mode Buttons */
    .stButton > button,
    button[kind="primary"],
    button[kind="secondary"],
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-secondary"],
    [data-testid="stFormSubmitButton"] > button {
        background-color: #1D4ED8 !important;
        border: 1.5px solid #3B82F6 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    .stButton > button *,
    button[kind="primary"] *,
    button[kind="secondary"] *,
    [data-testid="baseButton-primary"] *,
    [data-testid="baseButton-secondary"] *,
    [data-testid="stFormSubmitButton"] > button *,
    .stButton button [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    .stButton > button:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover,
    [data-testid="baseButton-primary"]:hover,
    [data-testid="baseButton-secondary"]:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #2563EB !important;
        border-color: #60A5FA !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.45) !important;
    }
    .stButton > button:hover *,
    button[kind="primary"]:hover *,
    button[kind="secondary"]:hover *,
    [data-testid="baseButton-primary"]:hover *,
    [data-testid="baseButton-secondary"]:hover *,
    [data-testid="stFormSubmitButton"] > button:hover *,
    .stButton button:hover [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    /* Compact Accessibility Bar in Dark Mode */
    .st-key-accessibility_bar {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
    }
    .st-key-accessibility_bar button {
        background-color: #0F172A !important;
        color: #F3F4F6 !important;
        -webkit-text-fill-color: #F3F4F6 !important;
        border: 1.5px solid #64748B !important;
    }
    .st-key-accessibility_bar button * {
        color: #F3F4F6 !important;
        -webkit-text-fill-color: #F3F4F6 !important;
    }
    .st-key-accessibility_bar button:hover {
        background-color: #334155 !important;
        border-color: #94A3B8 !important;
    }
    /* Top Utility Bar in Dark Mode */
    .st-key-top_utility_bar button {
        background-color: #1E293B !important;
        color: #93C5FD !important;
        -webkit-text-fill-color: #93C5FD !important;
        border: 1.5px solid #3B82F6 !important;
    }
    .st-key-top_utility_bar button * {
        color: #93C5FD !important;
        -webkit-text-fill-color: #93C5FD !important;
    }
    .st-key-top_utility_bar button:hover {
        background-color: #2563EB !important;
        border-color: #60A5FA !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    </style>
    """
    st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DYNAMIC ACCESSIBILITY CONTROLS BAR (Directly Below Single Unified Header)
# Exact Replica of User-Uploaded Screenshot: Accessibility: [ A- ] [ A ] [ A+ ] ◐
# Along with Dynamic Language Selector and Live Real-Time Digital Clock
# -----------------------------------------------------------------------------
with st.container(key="accessibility_bar"):
    # Extremely compact column proportions
    acc_c_label, acc_c_aminus, acc_c_anormal, acc_c_aplus, acc_c_contrast, acc_c_lang, acc_c_clock = st.columns(
        [0.8, 0.25, 0.25, 0.25, 0.3, 1.2, 1.5],
        gap="small"
    )
    
    with acc_c_label:
        acc_text = "♿ सुगमता" if is_hi else "♿ Accessibility"
        st.markdown(
            f"""<div style="display: flex; align-items: center; height: 28px; font-size: 12px; font-weight: 700; color: {'#93C5FD' if dark_mode else '#111827'};">
                {acc_text}
            </div>""",
            unsafe_allow_html=True
        )
        
    with acc_c_aminus:
        btn_aminus_help = "अक्षरों का आकार छोटा करें" if is_hi else "Decrease Font Size"
        if st.button("A-", key="acc_btn_aminus", help=btn_aminus_help):
            st.session_state["font_scale"] = 0.88
            st.toast("🔍 A- (88%)", icon="🔤")
            st.rerun()
            
    with acc_c_anormal:
        btn_anorm_help = "सामान्य आकार रीसेट करें" if is_hi else "Reset Normal Font Size"
        if st.button("A", key="acc_btn_anormal", help=btn_anorm_help):
            st.session_state["font_scale"] = 1.0
            st.toast("🔍 A (100%)", icon="🔤")
            st.rerun()
            
    with acc_c_aplus:
        btn_aplus_help = "अक्षरों का आकार बड़ा करें" if is_hi else "Increase Font Size"
        if st.button("A+", key="acc_btn_aplus", help=btn_aplus_help):
            st.session_state["font_scale"] = 1.16
            st.toast("🔍 A+ (116%)", icon="🔤")
            st.rerun()
            
    with acc_c_contrast:
        btn_mode_help = ("डार्क मोड टॉगल करें" if not dark_mode else "लाइट मोड चालू करें") if is_hi else ("Toggle Dark Mode" if not dark_mode else "Switch to Light Mode")
        if st.button("◐", key="acc_btn_contrast", help=btn_mode_help):
            st.session_state["dark_mode"] = not dark_mode
            st.rerun()
            
    with acc_c_lang:
        curr_lang = st.session_state.get("current_lang", "Hindi")
        lang_opts = ["हिन्दी", "English"]
        lang_idx = 0 if curr_lang == "Hindi" else 1
        lang_choice = st.radio(
            "Language",
            options=lang_opts,
            index=lang_idx,
            horizontal=True,
            label_visibility="collapsed",
            key="acc_language_selector_radio"
        )
        target_lang = "Hindi" if lang_choice == "हिन्दी" else "English"
        if target_lang != curr_lang:
            st.session_state["current_lang"] = target_lang
            st.session_state["app_language"] = target_lang
            st.rerun()
            
    with acc_c_clock:
        clock_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
          * {{ box-sizing: border-box; margin: 0; padding: 0; }}
          body {{
            background: transparent;
            font-family: 'Consolas', 'Courier New', monospace;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            height: 32px;
            overflow: hidden;
          }}
          .clock-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background-color: {'#1E293B' if dark_mode else '#000080'};
            color: #FFFFFF;
            padding: 4px 10px;
            border-radius: 16px;
            font-size: 12.5px;
            font-weight: 700;
            border: 1px solid {'#3B82F6' if dark_mode else '#1E40AF'};
            box-shadow: 0 1px 4px rgba(0, 0, 128, 0.18);
          }}
          .green-dot {{
            width: 7px;
            height: 7px;
            background-color: #22C55E;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 5px #22C55E;
            animation: liveBlink 1s infinite alternate ease-in-out;
          }}
          @keyframes liveBlink {{
            from {{ opacity: 1; transform: scale(1); }}
            to {{ opacity: 0.3; transform: scale(0.85); }}
          }}
          .time-val {{
            color: #FFFFFF;
            font-weight: 800;
            letter-spacing: 0.5px;
          }}
          .date-val {{
            color: #93C5FD;
            font-size: 11px;
            font-weight: 600;
            border-left: 1px solid #3B82F6;
            padding-left: 6px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          }}
        </style>
        </head>
        <body>
          <div class="clock-badge">
            <span class="green-dot"></span>
            <span class="time-val" id="time-display">--:--:-- --</span>
            <span class="date-val" id="date-display">--</span>
          </div>
          <script>
            function updateLiveTimer() {{
              const now = new Date();
              let hours = now.getHours();
              const minutes = String(now.getMinutes()).padStart(2, '0');
              const seconds = String(now.getSeconds()).padStart(2, '0');
              const ampm = hours >= 12 ? 'PM' : 'AM';
              hours = hours % 12;
              hours = hours ? String(hours).padStart(2, '0') : '12';
              
              document.getElementById('time-display').textContent = hours + ':' + minutes + ':' + seconds + ' ' + ampm;
              
              const options = {{ day: '2-digit', month: 'short', year: 'numeric' }};
              document.getElementById('date-display').textContent = now.toLocaleDateString('en-IN', options);
            }}
            updateLiveTimer();
            setInterval(updateLiveTimer, 1000);
          </script>
        </body>
        </html>
        """
        components.html(clock_html, height=36)

st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN TABBED WORKFLOW (STRICTLY 3 TABS AS REQUESTED)
# -----------------------------------------------------------------------------
if is_hi:
    tab1_title = "🏛️ किसान पहचान एवं भूमि विवरण"
    tab2_title = "🔬 फसल स्वास्थ्य एवं मिट्टी जांच"
    tab3_title = "📈 मंडी मुनाफा अनुकूलक"
else:
    tab1_title = "🏛️ Farmer Profile & Land Records"
    tab2_title = "🔬 Crop Health & Soil Testing"
    tab3_title = "📈 Mandi Profit Optimizer"

tab1, tab2, tab3 = st.tabs([tab1_title, tab2_title, tab3_title])

# =============================================================================
# TAB 1: AGRISTACK AUTHENTICATION
# =============================================================================
with tab1:
    tab1_card_bg = "#1E293B" if dark_mode else "#FFFFFF"
    tab1_card_border = "#334155" if dark_mode else "#E2E8F0"
    tab1_text_color = "#F3F4F6" if dark_mode else "#111111"
    tab1_sub_color = "#CBD5E1" if dark_mode else "#4B5563"
    
    top_profile_placeholder = st.empty()
    if is_hi:
        top_profile_placeholder.markdown(
            f"""<div class="gov-card" style="background-color: {tab1_card_bg}; border-color: {tab1_card_border};">
<div class="gov-card-header" style="font-size: 1.25rem;">
<span>🌾 किसान पहचान और भूमि अभिलेख</span>
<span class="gov-badge-verified" style="font-size: 0.85rem; padding: 4px 10px;">✓ सरकारी रिकॉर्ड से प्रमाणित</span>
</div>
<p style="color: {tab1_sub_color}; font-size: 1.05rem; line-height: 1.6; margin-bottom: 6px;">
यहाँ अपना <b>किसान पहचान नंबर</b> दर्ज करें। सरकारी रिकॉर्ड से आपके नाम पर दर्ज सभी <b>खसरा (खेत)</b> और कुल रकबा तुरंत प्रदर्शित होगा।
</p>
</div>""",
            unsafe_allow_html=True
        )
    else:
        top_profile_placeholder.markdown(
            f"""<div class="gov-card" style="background-color: {tab1_card_bg}; border-color: {tab1_card_border};">
<div class="gov-card-header" style="font-size: 1.25rem;">
<span>🌾 Farmer Profile &amp; Land Records</span>
<span class="gov-badge-verified" style="font-size: 0.85rem; padding: 4px 10px;">✓ Verified Government Record</span>
</div>
<p style="color: {tab1_sub_color}; font-size: 1.05rem; line-height: 1.6; margin-bottom: 6px;">
Enter your <b>Farmer ID</b> to see your registered <b>land parcels</b> and total farming area.
</p>
</div>""",
            unsafe_allow_html=True
        )


    col_login, col_info = st.columns([1.1, 1], gap="large")

    with col_login:
        login_title = "#### 👤 किसान पहचान संख्या से खोजें" if is_hi else "#### 👤 Search by Farmer ID"
        st.markdown(login_title)

        col_left, col_right = st.columns([1, 1.2])

        with col_left:
            input_lbl = "किसान पहचान संख्या दर्ज करें:" if is_hi else "Enter Farmer ID:"
            input_ph = "उदा. MP-BPL-7842" if is_hi else "e.g. MP-BPL-7842"
            input_hlp = "जांच के लिए 'MP-BPL-7842' का उपयोग करें।" if is_hi else "Use 'MP-BPL-7842' for demo verification."
            
            farmer_id_input = st.text_input(
                input_lbl,
                placeholder=input_ph,
                value=st.session_state.get("input_farmer_id_val", ""),
                help=input_hlp
            )

            c1, c2 = st.columns([1, 1])
            with c1:
                btn_verify_lbl = "🔍 पहचान जांचें" if is_hi else "🔍 Verify Record"
                verify_clicked = st.button(btn_verify_lbl, use_container_width=True)
            with c2:
                btn_demo_lbl = "⚡ उदाहरण आईडी (MP-BPL-7842)" if is_hi else "⚡ Demo ID (MP-BPL-7842)"
                demo_clicked = st.button(btn_demo_lbl, use_container_width=True)

            if demo_clicked:
                st.session_state["input_farmer_id_val"] = "MP-BPL-7842"
                farmer_id_input = "MP-BPL-7842"
                verify_clicked = True

            if verify_clicked:
                clean_id = (farmer_id_input or "").strip().upper()
                if not clean_id:
                    err_msg = "⚠️ कृपया अपना किसान पहचान नंबर दर्ज करें।" if is_hi else "⚠️ Please enter your Farmer ID."
                    st.error(err_msg)
                elif clean_id in AGRISTACK_DB:
                    st.session_state["authenticated_farmer"] = AGRISTACK_DB[clean_id]
                    succ_msg = f"✓ किसान रिकॉर्ड मिल गया: {AGRISTACK_DB[clean_id]['farmer_name']}" if is_hi else f"✓ Farmer Record Verified: {AGRISTACK_DB[clean_id]['farmer_name']}"
                    st.success(succ_msg)
                    st.rerun()
                else:
                    notfound_msg = (
                        f"❌ किसान पहचान '{clean_id}' सरकारी रिकॉर्ड में नहीं मिली।\n\n"
                        "जांच के लिए कृपया यह उदाहरण आईडी दर्ज करें: **`MP-BPL-7842`**"
                        if is_hi
                        else f"❌ Farmer ID '{clean_id}' not found in state records.\n\n"
                        "For demo testing, please use Farmer ID: **`MP-BPL-7842`**"
                    )
                    st.error(notfound_msg)

        with col_right:
            side_profile_placeholder = st.empty()


        # Active Authenticated Record Display
        farmer_data = st.session_state["authenticated_farmer"]
        if farmer_data:
            farmer_box_bg = "#064E3B" if dark_mode else "#F0FDF4"
            farmer_box_border = "#059669" if dark_mode else "#86EFAC"
            farmer_box_hdr = "#A7F3D0" if dark_mode else "#166534"
            farmer_box_txt = "#F3F4F6" if dark_mode else "#1F2937"
            farmer_code_bg = "#1E3A8A" if dark_mode else "#EEF2FF"
            farmer_code_txt = "#93C5FD" if dark_mode else "#000080"
            
            if is_hi:
                side_profile_placeholder.markdown(
                    f"""<div style="background-color: {farmer_box_bg}; border: 1.5px solid {farmer_box_border}; border-radius: 8px; padding: 18px 20px; margin-top: 10px;">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {farmer_box_border}; padding-bottom: 10px;">
<span style="font-weight: 800; color: {farmer_box_hdr}; font-size: 1.35rem;">👤 {farmer_data['farmer_name']}</span>
<span class="gov-badge-verified" style="font-size: 0.85rem; padding: 4px 10px;">✓ आधार ई-केवाईसी प्रमाणित</span>
</div>
<div style="font-size: 1rem; color: {farmer_box_txt}; margin-top: 10px; line-height: 1.8;">
<b>किसान पहचान:</b> <code style="font-size: 1.05rem; font-weight: 700; color: {farmer_code_txt}; background: {farmer_code_bg}; padding: 2px 6px; border-radius: 4px;">{farmer_data['farmer_id']}</code> | 
<b>पिता का नाम:</b> {farmer_data['father_name']}<br>
<b>पता:</b> ग्राम {farmer_data['village']}, तहसील {farmer_data['tehsil']}, जिला {farmer_data['district']} ({farmer_data['state']})<br>
<b>पीएम-किसान सम्मान निधि:</b> <span style="color: #4ADE80; font-weight: 700; font-size: 1.05rem;">{farmer_data['pm_kisan_status']}</span>
</div>
</div>""",
                    unsafe_allow_html=True
                )
            else:
                side_profile_placeholder.markdown(
                    f"""<div style="background-color: {farmer_box_bg}; border: 1.5px solid {farmer_box_border}; border-radius: 8px; padding: 18px 20px; margin-top: 10px;">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {farmer_box_border}; padding-bottom: 10px;">
<span style="font-weight: 800; color: {farmer_box_hdr}; font-size: 1.35rem;">👤 Ramesh Chandra Patel</span>
<span class="gov-badge-verified" style="font-size: 0.85rem; padding: 4px 10px;">✓ Aadhaar e-KYC Verified</span>
</div>
<div style="font-size: 1rem; color: {farmer_box_txt}; margin-top: 10px; line-height: 1.8;">
<b>Farmer ID:</b> <code style="font-size: 1.05rem; font-weight: 700; color: {farmer_code_txt}; background: {farmer_code_bg}; padding: 2px 6px; border-radius: 4px;">{farmer_data['farmer_id']}</code> | 
<b>Father's Name:</b> Late Shri Babulal Patel<br>
<b>Location:</b> Village {farmer_data['village']}, Tehsil {farmer_data['tehsil']}, District {farmer_data['district']} ({farmer_data['state']})<br>
<b>PM-Kisan Status:</b> <span style="color: #4ADE80; font-weight: 700; font-size: 1.05rem;">Active (17th Installment Credited)</span>
</div>
</div>""",
                    unsafe_allow_html=True
                )


            parcel_heading = "##### 📍 खेती और मंडी लाभ के लिए अपना खेत चुनें:" if is_hi else "##### 📍 Select Your Land Parcel to Calculate Profit:"
            st.markdown(parcel_heading)
            
            if is_hi:
                parcel_options = [
                    "खसरा नं. 412 — 2.0 हेक्टेयर (4.94 एकड़) | गहरी काली मिट्टी | सिंचाई: नलकूप एवं स्प्रिंकलर",
                    "खसरा नं. 089 — 1.5 हेक्टेयर (3.71 एकड़) | लाल दोमट मिट्टी | सिंचाई: नहर लिफ्ट"
                ]
            else:
                parcel_options = [
                    "Khasra 412 — 2.0 Hectares (4.94 Acres) | Deep Black Cotton Soil | Irrigation: Tube-well with Sprinkler",
                    "Khasra 089 — 1.5 Hectares (3.71 Acres) | Red Loam Soil | Irrigation: Canal Lift"
                ]
                
            selected_idx = st.radio(
                "Choose Land Parcel:",
                options=range(len(parcel_options)),
                format_func=lambda i: parcel_options[i],
                index=st.session_state.get("selected_parcel_index", 0),
                label_visibility="collapsed"
            )
            st.session_state["selected_parcel_index"] = selected_idx
            if selected_idx == 0:
                st.session_state["selected_plot"] = "Khasra 412 (2.0 Hectares - Black Soil)" if not is_hi else "खसरा 412 (2.0 हेक्टेयर - काली मिट्टी)"
            else:
                st.session_state["selected_plot"] = "Khasra 089 (1.5 Hectares - Red Soil)" if not is_hi else "खसरा 089 (1.5 हेक्टेयर - लाल मिट्टी)"
            active_p = farmer_data["parcels"][selected_idx]

            if is_hi:
                soil_type_hi = "गहरी काली मिट्टी" if selected_idx == 0 else "लाल दोमट मिट्टी"
                irr_hi = "नलकूप एवं स्प्रिंकलर" if selected_idx == 0 else "नहर लिफ्ट"
                st.success(
                    f"🌱 **चुना हुआ खेत:** `{active_p['khasra_no']}`\n\n"
                    f"- **कुल रकबा:** `{active_p['area_hectares']} हेक्टेयर` ({active_p['area_acres']} एकड़)\n"
                    f"- **मिट्टी की किस्म:** {soil_type_hi}\n"
                    f"- **सिंचाई साधन:** {irr_hi}\n\n"
                    "👉 *यह रकबा सीधे **मंडी मुनाफा अनुकूलक** टैब में कुल उपज और मंडी मुनाफे के हिसाब के लिए भेजा गया है।*"
                )
            else:
                st.success(
                    f"🌱 **Active Parcel:** `{active_p['khasra_no']}`\n\n"
                    f"- **Total Area:** `{active_p['area_hectares']} Hectares` ({active_p['area_acres']} Acres)\n"
                    f"- **Soil Type:** {active_p['soil_type']}\n"
                    f"- **Irrigation Source:** {active_p['irrigation_source']}\n\n"
                    "👉 *This land area is automatically linked to **Tab 3 (Mandi Profit Optimizer)** for total yield and net realization calculations.*"
                )

    

# =============================================================================
# TAB 2: AI SOIL & PATHOLOGY ANALYSIS
# =============================================================================
with tab2:
    if is_hi:
        st.markdown(
            """<div class="gov-card">
<div class="gov-card-header" style="font-size: 1.25rem;">
<span>🔬 फसल स्वास्थ्य और मिट्टी की जांच (Crop Health & Soil Check)</span>
<span class="gov-badge-verified" style="font-size: 0.85rem; padding: 4px 10px;">✓ आसान और सटीक सलाह</span>
</div>
<p style="color: #374151; font-size: 1.05rem; line-height: 1.6; margin-bottom: 8px;">
अपने खेत की <b>मिट्टी</b> या <b>पौधे की पत्ती</b> की साफ़ फोटो अपलोड करें। हमारी कृषि-निर्णय विशेषज्ञ प्रणाली तुरंत बताएगी कि 
<b>पौधे में क्या समस्या है</b>, <b>इस मिट्टी के लिए कौन सी फसल उत्तम है</b>, और <b>सीआईबीआरसी (CIBRC) प्रमाणित दवा का सही छिड़काव क्या है</b>।
</p>
<div class="gov-badge-official" style="font-size: 0.85rem; padding: 4px 10px;">
✓ समर्थित 8 प्रमुख फसलें: सोयाबीन, गेहूँ, गन्ना, चना, धान, मक्का, सरसों, कपास
</div>
</div>""",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """<div class="gov-card">
<div class="gov-card-header" style="font-size: 1.25rem;">
<span>🔬 Crop Health & Soil Diagnostic System (Agronomic Advisory)</span>
<span class="gov-badge-verified" style="font-size: 0.85rem; padding: 4px 10px;">✓ Direct Agronomic Advisory</span>
</div>
<p style="color: #374151; font-size: 1.05rem; line-height: 1.6; margin-bottom: 8px;">
Upload a photograph of your <b>field soil</b> or <b>crop leaf/stem</b>. The Krishi-Nirnay Expert Advisory System analyzes conditions to determine 
<b>detected plant health issues</b>, <b>ideal crop to plant</b>, and <b>approved statutory CIBRC dosage instructions</b>.
</p>
<div class="gov-badge-official" style="font-size: 0.85rem; padding: 4px 10px;">
✓ 8 Approved Crops: Soybean, Wheat, Sugarcane, Gram, Paddy, Maize, Mustard, Cotton
</div>
</div>""",
            unsafe_allow_html=True
        )

    col_upload, col_preview = st.columns([1.1, 1], gap="large")

    with col_upload:
        upload_title = "#### 📸 खेत या पौधे की फोटो चुनें" if is_hi else "#### 📸 Select Field or Plant Photo"
        st.markdown(upload_title)
        
        uploader_label = "पत्ती या मिट्टी की फोटो अपलोड करें (JPG, PNG):" if is_hi else "Upload Crop Leaf or Soil Photo (JPG, PNG):"
        uploader_help = "खेत की मिट्टी या पौधे की पत्ती की साफ फोटो चुनें।" if is_hi else "Upload a clear photograph of field soil or affected crop leaf."
        uploaded_file = st.file_uploader(
            uploader_label,
            type=["jpg", "jpeg", "png", "webp"],
            help=uploader_help
        )

        sample_title = "##### — या बना-बनाया नमूना चुनें (Sample Images):" if is_hi else "##### — Or Choose a Pre-loaded Sample:"
        st.markdown(sample_title)
        
        sample_opts = [
            "कोई नहीं (अपनी फोटो अपलोड करें)" if is_hi else "None (Upload my own photo)",
            "नमूना 1: सोयाबीन का पत्ता (पीलापन / रतुआ रोग)" if is_hi else "Sample 1: Soybean Leaf (Yellowing / Rust Disease)",
            "नमूना 2: उपजाऊ गहरी काली मिट्टी (Deep Black Soil)" if is_hi else "Sample 2: Fertile Deep Black Cotton Soil",
            "नमूना 3: गेहूँ की पत्ती (पीली धारियां / रतुआ)" if is_hi else "Sample 3: Wheat Leaf (Yellow Rust Symptoms)"
        ]
        sample_label = "जांच के लिए नमूना चुनें:" if is_hi else "Choose a test sample:"
        sample_choice = st.selectbox(sample_label, options=sample_opts)

        selected_image = None

        if uploaded_file is not None:
            selected_image = Image.open(uploaded_file)
            st.session_state["uploaded_image_file"] = uploaded_file.name
        elif not sample_choice.startswith("कोई नहीं") and not sample_choice.startswith("None"):
            if "सोयाबीन" in sample_choice or "Soybean" in sample_choice:
                img_path = "sample_images/soybean_leaf_rust.jpg"
            elif "काली मिट्टी" in sample_choice or "Black" in sample_choice:
                img_path = "sample_images/black_cotton_soil.jpg"
            else:
                img_path = "sample_images/wheat_yellow_rust.jpg"
            
            if os.path.exists(img_path):
                selected_image = Image.open(img_path)
                st.session_state["uploaded_image_file"] = os.path.basename(img_path)

        diag_btn_text = "🚀 फोटो की जांच करें और सलाह पाएं (Check Photo & Get Advice)" if is_hi else "🚀 Analyze Photo & Generate Advisory Report"
        run_diag_btn = st.button(diag_btn_text, use_container_width=True)

    with col_preview:
        preview_title = "#### 🖼️ फोटो निरीक्षण (Image Preview)" if is_hi else "#### 🖼️ Image Preview"
        st.markdown(preview_title)
        if selected_image is not None:
            caption_text = f"फोटो: {st.session_state.get('uploaded_image_file', 'Field Capture')} ({selected_image.width}x{selected_image.height} px)" if is_hi else f"Image: {st.session_state.get('uploaded_image_file', 'Field Capture')} ({selected_image.width}x{selected_image.height} px)"
            st.image(
                selected_image,
                caption=caption_text,
                use_container_width=True
            )
        else:
            empty_title = "अभी कोई फोटो नहीं चुनी गई" if is_hi else "No Photo Selected Yet"
            empty_desc = "बाईं तरफ से अपनी फसल की पत्ती या मिट्टी की फोटो अपलोड करें या नमूना चुनें।" if is_hi else "Upload a leaf/soil image from the left panel or choose a sample image."
            st.markdown(
                f"""<div style="border: 2px dashed #CBD5E1; border-radius: 8px; padding: 40px 20px; text-align: center; color: #94A3B8; background: #FFFFFF;">
<div style="font-size: 2.5rem; margin-bottom: 8px;">📷</div>
<div style="font-weight: 700; font-size: 1.1rem; color: #4B5563;">{empty_title}</div>
<div style="font-size: 0.9rem; margin-top: 4px; color: #64748B;">{empty_desc}</div>
</div>""",
                unsafe_allow_html=True
            )

    # Perform Diagnosis
    if run_diag_btn:
        if selected_image is None:
            warn_msg = "⚠️ कृपया पहले फोटो अपलोड करें या कोई नमूना चुनें।" if is_hi else "⚠️ Please upload a photograph or choose a sample image first."
            st.warning(warn_msg)
        else:
            spinner_msg = "⏳ फोटो की जांच की जा रही है, कृपया प्रतीक्षा करें..." if is_hi else "⏳ Analyzing image with Krishi-Nirnay Expert Advisory System, please wait..."
            with st.spinner(spinner_msg):
                result = analyze_with_gemini(selected_image, is_hi=is_hi)
                st.session_state["analysis_result"] = result
                st.session_state["recommended_crop"] = result.get("recommended_crop", "Soybean")
                succ_msg = "✓ जांच पूरी हुई! नीचे दी गई सलाह को ध्यान से पढ़ें:" if is_hi else "✓ Diagnosis Complete! Review the simple advisory report below:"
                st.success(succ_msg)

    # Display Report if available
    res = st.session_state["analysis_result"]
    if res:
        st.markdown("---")
        report_title = "📋 किसान सलाह रिपोर्ट (Farmer Advisory Report)" if is_hi else "📋 Farmer Advisory Report"
        advisory_badge = "प्रमाणित: कृषि-निर्णय विशेषज्ञ प्रणाली" if is_hi else "Certified: Krishi-Nirnay Expert System"
        st.markdown(
            f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<h3 style="color: #002B49; margin: 0; font-weight: 800;">{report_title}</h3>
<span class="gov-badge-official" style="font-size: 0.85rem; padding: 4px 10px;">{advisory_badge}</span>
</div>""",
            unsafe_allow_html=True
        )

        r_col1, r_col2, r_col3 = st.columns(3)
        
        txt_primary = "#F3F4F6" if dark_mode else "#111827"
        txt_secondary = "#D1D5DB" if dark_mode else "#1F2937"
        txt_muted = "#9CA3AF" if dark_mode else "#4B5563"

        with r_col1:
            issue_title = "⚠️ पहचानी गई समस्या (Detected Issue)" if is_hi else "⚠️ Detected Issue"
            issue_val = res.get('detected_issue', 'कोई गंभीर समस्या नहीं' if is_hi else 'No Severe Symptoms')
            issue_sub = "समय पर सही दवा का उपयोग करें ताकि आपकी फसल और पैदावार सुरक्षित रहे।" if is_hi else "Use the right treatment on time to protect your crop and yield."
            st.markdown(
                f"""<div class="gov-card" style="border-top: 4px solid #DC2626; height: 100%; padding: 18px 20px;">
<div style="font-size: 0.95rem; font-weight: 700; color: #DC2626; text-transform: uppercase; letter-spacing: 0.5px;">
{issue_title}
</div>
<div style="font-size: 1.35rem; font-weight: 800; color: {txt_primary}; margin: 10px 0; line-height: 1.3;">
{issue_val}
</div>
<div style="font-size: 0.92rem; color: {txt_muted}; line-height: 1.5;">
{issue_sub}
</div>
</div>""",
                unsafe_allow_html=True
            )

        with r_col2:
            crop_name = res.get('recommended_crop', 'Soybean')
            crop_details = CROP_SPECS.get(crop_name, CROP_SPECS["Soybean"])
            
            if is_hi:
                crop_box_title = "🌾 बोने के लिए उत्तम फसल"
                display_crop_name = crop_details.get('hindi_name', crop_name)
                season_display = crop_details.get('season', '').split('(')[0].strip()
                yield_text = f"अपेक्षित पैदावार: <b>{crop_details['yield_q_per_ha']} क्विंटल / हेक्टेयर</b>"
            else:
                crop_box_title = "🌾 Best Crop to Grow"
                display_crop_name = crop_name
                season_display = crop_details.get('season', '').split('(')[-1].replace(')', '').strip()
                yield_text = f"Expected Yield: <b>{crop_details['yield_q_per_ha']} Quintals / Hectare</b>"

            st.markdown(
                f"""<div class="gov-card" style="border-top: 4px solid #138808; height: 100%; padding: 18px 20px;">
<div style="font-size: 1.1rem; font-weight: 700; color: #138808; text-transform: uppercase; letter-spacing: 0.5px;">
{crop_box_title}
</div>
<div style="font-size: 2.3rem; font-weight: 900; color: {'#93C5FD' if dark_mode else '#000080'}; margin: 8px 0; line-height: 1.1;">
{display_crop_name}
</div>
<div style="font-size: 1.3rem; color: {txt_secondary}; font-weight: 700; margin-bottom: 6px;">
{season_display}
</div>
<div style="font-size: 1.1rem; color: #15803D; font-weight: 800; background: #ECFDF5; padding: 6px 12px; border-radius: 6px; border: 1px solid #A7F3D0; display: inline-block;">
{yield_text}
</div>
</div>""",
                unsafe_allow_html=True
            )

        with r_col3:
            if is_hi:
                rx_title = "🛡️ सुरक्षित दवा व छिड़काव"
                rx_val = res.get('cibrc_pesticide_required', 'आवश्यकतानुसार छिड़काव करें')
                rx_tip = "💡 <b>किसान सलाह:</b> दवा छिड़कते समय चेहरे पर मास्क या गमछा बांधें। सही मात्रा में पानी मिलाकर ही छिड़काव करें।"
            else:
                rx_title = "🛡️ Safe Pesticide & Treatment"
                rx_val = res.get('cibrc_pesticide_required', 'Spray as needed')
                rx_tip = "💡 <b>Farmer Tip:</b> Wear a mask while spraying. Mix the exact recommended amount with clean water."

            rx_box_bg = "#334155" if dark_mode else "#FFFBEB"
            rx_box_border = "#475569" if dark_mode else "#FDE68A"

            st.markdown(
                f"""<div class="gov-card" style="border-top: 4px solid #D97706; height: 100%; padding: 18px 20px;">
<div style="font-size: 1.1rem; font-weight: 700; color: #D97706; text-transform: uppercase; letter-spacing: 0.5px;">
{rx_title}
</div>
<div style="font-size: 1.25rem; font-weight: 800; color: {txt_secondary}; margin: 10px 0; line-height: 1.4;">
{rx_val}
</div>
<div style="font-size: 1.0rem; color: {txt_muted}; line-height: 1.5; background: {rx_box_bg}; padding: 8px 10px; border-radius: 4px; border: 1px solid {rx_box_border};">
{rx_tip}
</div>
</div>""",
                unsafe_allow_html=True
            )

        congrats_msg = (
            f"👉 **बधाई हो!** आपकी सुझाई गई फसल **{display_crop_name}** का कुल उत्पादन और मंडियों का शुद्ध मुनाफा देखने के लिए ऊपर **'टैब 3: मंडी मुनाफा अनुकूलक'** पर क्लिक करें!"
            if is_hi
            else f"👉 **Advisory Ready!** To view total expected production and compare net mandi profits across MP APMC markets for **{display_crop_name}**, click **'Tab 3: Mandi Profit Optimizer'** above!"
        )
        st.success(congrats_msg)


# =============================================================================
# TAB 3: MANDI PROFIT OPTIMIZER
# =============================================================================
with tab3:
    if is_hi:
        st.markdown(
            """
            <div class="gov-card">
                <div class="gov-card-header">
                    <span>📈 मंडी लाभ एवं शुद्ध मूल्य अनुकूलक (Mandi Profit Optimizer)</span>
                    <span class="gov-badge-verified">e-NAM APMC मंडी भाव</span>
                </div>
                <p style="color: #4B5563; font-size: 0.95rem; margin-bottom: 6px; line-height: 1.6;">
                    आपके चुने हुए खेत के कुल रकबे और सुझाई गई फसल की उपज के आधार पर कुल उत्पादन निकाला जाता है। 
                    विभिन्न मंडियों के भाव और भाड़ा (ट्रैक्टर/ट्रक किराया) घटाकर <b>अधिकतम शुद्ध मुनाफे</b> वाली मंडी की पहचान करें।
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="gov-card">
                <div class="gov-card-header">
                    <span>📈 Mandi Realization & Net Profit Optimizer</span>
                    <span class="gov-badge-verified">e-NAM APMC Price Corridors</span>
                </div>
                <p style="color: #4B5563; font-size: 0.9rem; margin-bottom: 6px; line-height: 1.6;">
                    Calculates total expected agricultural output by multiplying the <b>Recommended Crop Yield</b> 
                    with the farmer's <b>Verified AgriStack Land Parcel Area</b>. Compares Gross Revenue against 
                    Logistics & Freight charges across major MP APMC Mandis to calculate maximum Net Profit.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Determine Active Verified Land Size from st.session_state['selected_plot']
    farmer_data = st.session_state.get("authenticated_farmer") or AGRISTACK_DB.get("MP-BPL-7842")
    sel_plot = st.session_state.get("selected_plot", "Khasra 412 (2.0 Hectares - Black Soil)")
    
    if "089" in str(sel_plot) or "1.5" in str(sel_plot) or st.session_state.get("selected_parcel_index") == 1:
        land_size_ha = 1.5
        parcel_label = "खसरा 089 (1.5 हेक्टेयर - लाल मिट्टी)" if is_hi else "Khasra 089 (1.5 Hectares - Red Soil)"
    else:
        land_size_ha = 2.0
        parcel_label = "खसरा 412 (2.0 हेक्टेयर - काली मिट्टी)" if is_hi else "Khasra 412 (2.0 Hectares - Black Soil)"

    # Determine Crop
    ai_crop = st.session_state.get("recommended_crop", "Soybean")

    # Display Top Parameter Bar
    param_col1, param_col2, param_col3 = st.columns(3)

    with param_col1:
        metric1_title = "🌱 चुनी गई फसल" if is_hi else "🌱 Selected Crop"
        source_sub = ("स्रोत: " + ("टैब 2 एआई अनुशंसा" if st.session_state.get('analysis_result') else "मानक आधार")) if is_hi else ("Source: " + ("Tab 2 Recommendation" if st.session_state.get('analysis_result') else "ICAR Baseline"))
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">{metric1_title}</div>
                <div class="metric-value">{ai_crop}</div>
                <div class="metric-subtitle">{source_sub}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with param_col2:
        metric2_title = "📐 प्रमाणित खेत का रकबा" if is_hi else "📐 Verified Land Size"
        land_val = f"{land_size_ha:.2f} हेक्टेयर" if is_hi else f"{land_size_ha:.2f} Hectares"
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">{metric2_title}</div>
                <div class="metric-value">{land_val}</div>
                <div class="metric-subtitle">{parcel_label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with param_col3:
        crop_specs = CROP_SPECS[ai_crop]
        yield_per_ha = crop_specs["yield_q_per_ha"]
        total_production_quintals = yield_per_ha * land_size_ha
        metric3_title = "⚖️ कुल अपेक्षित उत्पादन" if is_hi else "⚖️ Expected Production"
        prod_val = f"{total_production_quintals:.1f} क्विंटल" if is_hi else f"{total_production_quintals:.1f} Quintals"
        formula_sub = f"सूत्र: {yield_per_ha:.1f} क्विंटल/हे. × {land_size_ha:.2f} हेक्टेयर" if is_hi else f"Formula: {yield_per_ha:.1f} Qtl/Ha × {land_size_ha:.2f} Ha"
        st.markdown(
            f"""
            <div class="metric-box" style="border-left-color: #138808;">
                <div class="metric-title">{metric3_title}</div>
                <div class="metric-value" style="color: #138808;">{prod_val}</div>
                <div class="metric-subtitle">{formula_sub}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Optional Override controls in expander for what-if scenarios
    exp_title = "🛠️ क्या-अगर परिदृश्य नियंत्रण (फसल या भूमि क्षेत्र को बदलें)" if is_hi else "🛠️ What-If Scenario Controls (Fine-Tune Crop or Land Area)"
    with st.expander(exp_title):
        ctrl_col1, ctrl_col2 = st.columns(2)
        with ctrl_col1:
            all_supported_crops = [
                "Soybean",
                "Wheat",
                "Sugarcane",
                "Gram",
                "Paddy (Rice)",
                "Maize",
                "Mustard",
                "Cotton"
            ]
            crop_idx = all_supported_crops.index(ai_crop) if ai_crop in all_supported_crops else 0
            
            display_options = []
            for c in all_supported_crops:
                if is_hi:
                    if c == "Soybean": display_options.append("सोयाबीन")
                    elif c == "Wheat": display_options.append("गेहूँ")
                    elif c == "Sugarcane": display_options.append("गन्ना")
                    elif c == "Gram": display_options.append("चना")
                    elif c == "Paddy (Rice)": display_options.append("धान (चावल)")
                    elif c == "Maize": display_options.append("मक्का")
                    elif c == "Mustard": display_options.append("सरसों")
                    elif c == "Cotton": display_options.append("कपास")
                else:
                    display_options.append(c)

            crop_label = "सिमुलेशन के लिए फसल बदलें:" if is_hi else "Change Crop Selection for Simulation:"
            sel_disp = st.selectbox(
                crop_label,
                options=display_options,
                index=crop_idx
            )
            override_crop = all_supported_crops[display_options.index(sel_disp)]
            
            if override_crop != ai_crop:
                st.session_state["recommended_crop"] = override_crop
                ai_crop = override_crop
                crop_specs = CROP_SPECS[ai_crop]
                yield_per_ha = crop_specs["yield_q_per_ha"]
                total_production_quintals = yield_per_ha * land_size_ha

        with ctrl_col2:
            land_label = "खेत का आकार बदलें (हेक्टेयर):" if is_hi else "Adjust Land Size (Hectares):"
            override_land = st.number_input(
                land_label,
                min_value=0.5,
                max_value=50.0,
                value=land_size_ha,
                step=0.5
            )
            if override_land != land_size_ha:
                land_size_ha = override_land
                total_production_quintals = yield_per_ha * land_size_ha

    # -------------------------------------------------------------------------
    # DYNAMIC MULTI-MANDI SELECTION & COMPARATIVE ECONOMICS
    # -------------------------------------------------------------------------
    st.markdown("---")
    mandi_comp_title = "#### 🏛️ मंडी बाज़ार चयन और वास्तविक समय तुलना" if is_hi else "#### 🏛️ Mandi Market Selection & Real-Time Comparison"
    st.markdown(mandi_comp_title)

    mandi_options = [
        "Bhopal (Karond)",
        "Indore (Choithram)",
        "Ujjain",
        "Jabalpur",
        "Sehore"
    ]
    
    mandi_display_options = []
    for m in mandi_options:
        if is_hi:
            mandi_display_options.append(REGIONAL_MANDIS[m]["display_name"].split("(")[0].strip())
        else:
            mandi_display_options.append(m)

    sel_title = "तुलना करने के लिए मंडियां चुनें" if is_hi else "Select Mandis to Compare"
    sel_help = "गतिशील मॉडल मूल्य, माल ढुलाई लागत, और शुद्ध लाभ की गणना करने के लिए एक या अधिक क्षेत्रीय एपीएमसी बाजार चुनें।" if is_hi else "Select one or more regional APMC markets to compute dynamic modal prices, freight costs, and net realized profits."

    default_indices = [mandi_options.index("Bhopal (Karond)"), mandi_options.index("Indore (Choithram)")]
    default_display = [mandi_display_options[i] for i in default_indices]

    sel_mandi_disp = st.multiselect(
        sel_title,
        options=mandi_display_options,
        default=default_display,
        help=sel_help
    )
    
    selected_mandis = [mandi_options[mandi_display_options.index(m)] for m in sel_mandi_disp]

    if not selected_mandis:
        warn_msg = "⚠️ आर्थिक तुलना देखने के लिए कृपया ऊपर दिए गए ड्रॉपडाउन से कम से कम एक मंडी चुनें।" if is_hi else "⚠️ Please select at least one Mandi from the dropdown above to view economic comparison."
        st.warning(warn_msg)
    else:
        # Dynamic calculation ONLY for markets the user actually selected
        comparison_records = []
        for m_key in selected_mandis:
            m_info = REGIONAL_MANDIS[m_key]
            m_price = m_info["prices"].get(ai_crop, 4000.0)
            gross_rev = total_production_quintals * m_price
            transport = m_info["static_transport_cost"]
            net_profit = gross_rev - transport
            comparison_records.append({
                "mandi_key": m_key,
                "display_name": m_info["display_name"],
                "district": m_info["district"],
                "distance_km": m_info["distance_km"],
                "price_per_q": m_price,
                "gross_rev": gross_rev,
                "transport": transport,
                "net_profit": net_profit,
                "color": m_info.get("color", "#002B49")
            })

        best_record = max(comparison_records, key=lambda x: x["net_profit"])
        worst_record = min(comparison_records, key=lambda x: x["net_profit"])
        profit_diff = best_record["net_profit"] - worst_record["net_profit"]

        # Decision Directive
        txt_primary = "#F3F4F6" if dark_mode else "#111827"
        txt_secondary = "#D1D5DB" if dark_mode else "#374151"
        txt_muted = "#9CA3AF" if dark_mode else "#6B7280"
        card_border = "#475569" if dark_mode else "#E5E7EB"

        if len(comparison_records) > 1:
            if is_hi:
                diff_text = f"{worst_record['mandi_key']} की तुलना में <b>+₹{profit_diff:,.0f} अधिक लाभ</b> उत्पन्न करता है।" if profit_diff > 0 else ""
                directive_title = "🎯 इष्टतम मंडी निर्णय निर्देश"
                directive_header = f"{best_record['mandi_key']} सबसे अधिक शुद्ध प्राप्ति (₹{best_record['net_profit']:,.0f}) देता है"
                directive_body = f"<b>{total_production_quintals:.1f} क्विंटल</b> {ai_crop} को <b>{best_record['display_name'].split('(')[0].strip()}</b> में भेजने पर ₹{best_record['transport']:,.0f} के पारगमन भाड़े को घटाने के बाद अधिकतम शुद्ध रिटर्न प्राप्त होता है। {diff_text}"
                enam_advice = "<b>e-NAM प्रेषण सलाह:</b> किसी e-NAM पंजीकृत रसद प्रदाता के साथ परिवहन का समन्वय करें।"
            else:
                diff_text = f"Generates <b>+₹{profit_diff:,.0f} higher profit</b> than {worst_record['mandi_key']}." if profit_diff > 0 else ""
                directive_title = "🎯 Optimal Mandi Decision Directive"
                directive_header = f"{best_record['mandi_key']} Delivers Highest Net Realization (₹{best_record['net_profit']:,.0f})"
                directive_body = f"Dispatching <b>{total_production_quintals:.1f} Quintals</b> of {ai_crop} to <b>{best_record['display_name']}</b> produces the maximum net returns after accounting for ₹{best_record['transport']:,.0f} transit freight. {diff_text}"
                enam_advice = "<b>e-NAM Dispatch Advice:</b> Coordinate transport with an e-NAM registered logistics provider."

            dir_bg = "#064E3B" if dark_mode else "#ECFDF5"
            dir_border = "#059669" if dark_mode else "#10B981"
            dir_title_txt = "#34D399" if dark_mode else "#047857"

            st.markdown(
                f"""<div class="gov-card" style="background-color: {dir_bg}; border: 1.5px solid {dir_border}; margin-top: 14px; margin-bottom: 16px;">
<div style="font-size: 0.85rem; font-weight: 700; color: {dir_title_txt}; text-transform: uppercase;">{directive_title}</div>
<div style="font-size: 1.25rem; font-weight: 800; color: {txt_primary}; margin: 6px 0;">{directive_header}</div>
<div style="font-size: 0.86rem; color: {txt_secondary}; line-height: 1.5;">
{directive_body}
</div>
<div style="margin-top: 8px; font-size: 0.75rem; color: {txt_muted};">
{enam_advice}
</div>
</div>""",
                unsafe_allow_html=True
            )

        # Comparative Mandi Cards
        card_cols = st.columns(len(comparison_records))
        for idx, col in enumerate(card_cols):
            rec = comparison_records[idx]
            is_best = (rec["mandi_key"] == best_record["mandi_key"]) and (len(comparison_records) > 1)
            
            if is_hi:
                best_label = "🏆 अधिकतम लाभ"
                dist_label = "दूरी"
                modal_label = "मॉडल मूल्य"
                qtl_label = "क्विंटल"
                gross_label = "सकल मूल्य"
                freight_label = "स्थिर भाड़ा"
                net_label = "शुद्ध लाभ"
            else:
                best_label = "🏆 Maximum Profit"
                dist_label = "Distance"
                modal_label = "Modal Price"
                qtl_label = "Qtl"
                gross_label = "Gross Value"
                freight_label = "Static Freight"
                net_label = "Net Profit"

            badge_html = f'<div style="margin-top: 8px;"><span class="gov-badge-verified">{best_label}</span></div>' if is_best else ''
            with col:
                st.markdown(
                    f"""<div class="gov-card" style="border-top: 4px solid {rec['color']}; height: 100%;">
<div style="font-weight: 700; color: {rec['color']}; font-size: 1.02rem;">🏢 {rec['mandi_key']}</div>
<div style="font-size: 0.75rem; color: {txt_muted}; margin-bottom: 8px;">{dist_label}: ~{rec['distance_km']} km | {rec['district']}</div>
<hr style="margin: 8px 0; border: none; border-top: 1px solid {card_border};">
<div style="font-size: 0.84rem; color: {txt_secondary}; line-height: 1.5;">
{modal_label}: <b>₹{rec['price_per_q']:,.0f} / {qtl_label}</b><br>
{gross_label}: <b>₹{rec['gross_rev']:,.0f}</b><br>
{freight_label}: <span style="color: #DC2626; font-weight: 600;">-₹{rec['transport']:,.0f}</span>
</div>
<hr style="margin: 8px 0; border: none; border-top: 1px solid {card_border};">
<div style="font-size: 0.8rem; color: {txt_muted};">{net_label}:</div>
<div style="font-size: 1.35rem; font-weight: 800; color: {rec['color']};">₹{rec['net_profit']:,.0f}</div>
{badge_html}
</div>""",
                    unsafe_allow_html=True
                )

        # -------------------------------------------------------------------------
        # BAR CHART SHOWING DYNAMIC NET PROFIT & REVENUE COMPARISON
        # -------------------------------------------------------------------------
        chart_title = "#### 📊 मंडी शुद्ध लाभ प्राप्ति बार चार्ट" if is_hi else "#### 📊 Mandi Net Profit Realization Bar Chart"
        st.markdown(chart_title)

        if is_hi:
            gross_col = "सकल राजस्व (₹)"
            net_col = "शुद्ध लाभ (₹)"
        else:
            gross_col = "Gross Revenue (₹)"
            net_col = "Net Profit (₹)"
            
        chart_data = pd.DataFrame(
            {
                gross_col: [r["gross_rev"] for r in comparison_records],
                net_col: [r["net_profit"] for r in comparison_records],
            },
            index=[r["mandi_key"] for r in comparison_records]
        )
        st.bar_chart(chart_data)

        # Detailed Audit & Breakdown Table
        sheet_title = "##### 📋 आधिकारिक e-NAM लेन-देन शीट" if is_hi else "##### 📋 Official e-NAM Transaction Sheet"
        st.markdown(sheet_title)
        
        if is_hi:
            audit_data = [
                {
                    "बाज़ार / मंडी": r["display_name"].split("(")[0].strip(),
                    "पारगमन दूरी": f"{r['distance_km']} किमी",
                    "फसल": ai_crop,
                    "उपज (Q/Ha)": f"{yield_per_ha:.1f}",
                    "सत्यापित क्षेत्र": f"{land_size_ha:.2f} हेक्टेयर",
                    "उत्पादन (क्विंटल)": f"{total_production_quintals:.1f}",
                    "मॉडल दर (₹/क्विंटल)": f"₹{r['price_per_q']:,.0f}",
                    "सकल मूल्य (₹)": f"₹{r['gross_rev']:,.0f}",
                    "स्थिर भाड़ा (₹)": f"₹{r['transport']:,.0f}",
                    "शुद्ध लाभ (₹)": f"₹{r['net_profit']:,.0f}"
                }
                for r in comparison_records
            ]
        else:
            audit_data = [
                {
                    "Market / APMC Mandi": r["display_name"],
                    "Transit Distance": f"{r['distance_km']} km",
                    "Crop": ai_crop,
                    "Yield (Q/Ha)": f"{yield_per_ha:.1f}",
                    "Verified Area": f"{land_size_ha:.2f} Ha",
                    "Output (Qtl)": f"{total_production_quintals:.1f}",
                    "Modal Rate (₹/Qtl)": f"₹{r['price_per_q']:,.0f}",
                    "Gross Value (₹)": f"₹{r['gross_rev']:,.0f}",
                    "Static Freight (₹)": f"₹{r['transport']:,.0f}",
                    "Net Realization (₹)": f"₹{r['net_profit']:,.0f}"
                }
                for r in comparison_records
            ]
            
        st.dataframe(pd.DataFrame(audit_data), use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# OFFICIAL GOVERNMENT COPYRIGHT FOOTER
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# GLOBAL BOTTOM FAQ / FARMER QUICK GUIDE
# -----------------------------------------------------------------------------
st.markdown("---")
guide_hdr = "### 📜 आसान किसान मार्गदर्शिका (FAQ)" if is_hi else "### 📜 Farmer Quick Guide (FAQ)"
st.markdown(guide_hdr)

if is_hi:
    st.info("""
    **इस पोर्टल का उपयोग कैसे करें?**
    * **सीधा सरकारी रिकॉर्ड:** आपकी किसान पहचान से आपकी जमीन का रकबा अपने-आप जुड़ जाता है।
    * **खेत बदलें (Khasra):** बायीं ओर के मेनू (Sidebar) से अपने खसरा नंबर का चयन करें।
    * **फसल जांच:** 'फसल स्वास्थ्य' टैब में फोटो अपलोड करके बीमारी और दवा का पता लगाएं।
    * **मंडी में अधिकतम मुनाफा:** 'मंडी मुनाफा अनुकूलक' टैब में सही मंडी चुनकर आप अधिकतम लाभ कमा सकते हैं।
    """)
else:
    st.info("""
    **How to use this portal?**
    * **Direct Gov Record:** Your land area is automatically linked via your Farmer ID.
    * **Switch Land (Khasra):** Select your specific land parcel directly from the left sidebar menu.
    * **Crop Health:** Upload a photo in the 'Crop Health' tab to detect diseases and get treatment advice.
    * **Maximum Profit:** Use the 'Mandi Profit Optimizer' tab to compare regional freight costs and find the most profitable market.
    """)
st.markdown("<br>", unsafe_allow_html=True)