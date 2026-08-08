import streamlit as st
import pandas as pd
import re
import os
import io
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client
from pptx import Presentation

# Load environment variables from local .env file
load_dotenv()

# ---------------------------------------------------------
# 1. Page Configuration & Session State Initialization
# ---------------------------------------------------------
st.set_page_config(
    page_title="Founder Assistant | AI Copilot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global Session Memory
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "global_startup_name" not in st.session_state:
    st.session_state.global_startup_name = ""
if "global_idea" not in st.session_state:
    st.session_state.global_idea = ""

# Persistent Storage across Tab Navigation
if "results" not in st.session_state:
    st.session_state.results = {
        "market": None,
        "business": None,
        "competitor": None,
        "fundraising": None,
        "execution": None
    }

# NEW: State for viewing history from the sidebar
if "viewing_history" not in st.session_state:
    st.session_state.viewing_history = None

# Initialize Supabase Client
@st.cache_resource
def init_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key:
        return create_client(url, key)
    return None

supabase = init_supabase()

# ---------------------------------------------------------
# 2. Cinematic CSS & Guaranteed Animated Background
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Space+Grotesk:wght@300;400;700&display=swap');

    /* Protect Streamlit Icons */
    html, body, p, h1, h2, h3, h4, h5, h6, input, textarea, select, button {
        font-family: 'Space Grotesk', sans-serif;
        color: #C0C0C0;
    }
    
    .stIcon, span[class*="icon"], span.material-symbols-rounded, i {
        font-family: 'Material Symbols Rounded' !important;
        color: inherit;
    }

    /* Animated Cyberspace Background */
    .stApp {
        background: linear-gradient(270deg, #050509, #0a0f24, #050509, #0a0514);
        background-size: 400% 400%;
        animation: energyPulse 15s ease infinite;
    }

    [data-testid="stAppViewContainer"] {
        background-color: transparent !important;
        background-image: 
            linear-gradient(rgba(56, 189, 248, 0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(56, 189, 248, 0.07) 1px, transparent 1px) !important;
        background-size: 40px 40px !important;
        animation: scrollGrid 10s linear infinite !important;
    }

    @keyframes energyPulse {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes scrollGrid {
        0% { background-position: 0px 0px; }
        100% { background-position: 40px 40px; }
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 10, 20, 0.75) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.2);
        backdrop-filter: blur(15px);
        z-index: 20;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1 {
        font-family: 'Orbitron', sans-serif;
        color: #38BDF8;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.8);
    }

    /* Cinematic Header styling */
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38BDF8, #818CF8, #38BDF8);
        background-size: 200% auto;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: shine 4s linear infinite;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
        margin-top: -20px;
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }

    .subtitle {
        font-size: 1.3rem;
        color: #38BDF8;
        margin-bottom: 25px;
        font-weight: 400;
        border-left: 4px solid #38BDF8;
        padding-left: 15px;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }

    /* 3D Glassmorphism Cards */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div {
        background: rgba(15, 23, 42, 0.65);
        border-radius: 16px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        backdrop-filter: blur(16px);
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6);
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }

    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 10px 40px 0 rgba(56, 189, 248, 0.2);
    }

    /* High Tech Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px;
        color: #94A3B8;
        font-family: 'Space Grotesk', sans-serif;
        transition: 0.3s;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(56, 189, 248, 0.2);
        color: white;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(56, 189, 248, 0.3);
        border-color: #38BDF8;
        color: white;
        font-weight: 700;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
    }

    /* Inputs & Action Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #0F172A, #1E1B4B);
        color: #38BDF8;
        border: 1px solid #38BDF8;
        border-radius: 8px;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.3s;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(45deg, #38BDF8, #818CF8);
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.6);
        color: #050509;
        border-color: transparent;
    }

    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        color: white !important;
        border-radius: 8px !important;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.6);
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4) !important;
    }

    /* Metrics Display */
    div[data-testid="stMetricValue"] > div {
        font-family: 'Orbitron', sans-serif;
        color: #38BDF8;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.6);
        font-size: 1.8rem !important;
    }
    
    /* Decorative Divider Line */
    .cinematic-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #38BDF8, #818CF8, transparent);
        margin: 20px 0;
        box-shadow: 0 0 10px #38BDF8;
    }
    
    /* Sidebar History Button Styling */
    .history-btn > button {
        background: transparent !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        color: #94A3B8 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 15px !important;
        font-size: 0.85rem !important;
        text-transform: none !important;
        letter-spacing: 0px !important;
        box-shadow: none !important;
    }
    .history-btn > button:hover {
        background: rgba(56, 189, 248, 0.1) !important;
        color: #38BDF8 !important;
        border-color: #38BDF8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Helper Functions, Nemotron SDK, Gibberish Filter & PPT
# ---------------------------------------------------------
def is_valid_input(text):
    if not text or len(text.strip()) < 2:
        return False
    clean_text = text.strip().lower()
    letters_only = re.sub(r'[^a-z]', '', clean_text)
    if len(letters_only) < 3:
        return True
    vowels = len(re.findall(r'[aeiouy]', letters_only))
    if len(letters_only) > 5 and vowels == 0:
        return False
    if re.search(r'[^aeiouy]{5,}', letters_only):
        return False
    if re.search(r'(.)\1{3,}', letters_only):
        return False
    smashes = ['asdf', 'qwer', 'zxcv', 'hjkl']
    for smash in smashes:
        if smash in letters_only:
            return False
    return True

def generate_ai_response(api_key, prompt, system_prompt=""):
    if not api_key:
        st.error("⚠️ CRITICAL: API Key Missing. Enter it in the sidebar or .env file.")
        return None
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1"
        )
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are a top-tier Silicon Valley venture partner and Y-Combinator strategist. Provide exhaustive, highly detailed, strictly factual data-driven startup analysis using clean markdown text without code blocks or backticks."})
            
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-ultra-550b-a55b", 
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def create_ppt(report_text, report_title):
    prs = Presentation()
    
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = report_title
    slide.placeholders[1].text = "Generated by AI Startup Copilot"
    
    sections = report_text.split("## ")
    for section in sections[1:]:
        lines = section.split('\n')
        slide_header = lines[0].strip()
        slide_body = '\n'.join(lines[1:]).strip()
        
        slide_body = re.sub(r'[*_`#]', '', slide_body)
        
        if len(slide_body) > 800:
            slide_body = slide_body[:800] + "...\n\n[Details truncated for presentation]"
            
        bullet_slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(bullet_slide_layout)
        slide.shapes.title.text = slide_header
        slide.placeholders[1].text_frame.text = slide_body
        
    ppt_stream = io.BytesIO()
    prs.save(ppt_stream)
    ppt_stream.seek(0)
    return ppt_stream

def display_report_actions(report_text, report_title, state_key):
    st.markdown(report_text)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.download_button(
            label="📄 Download (.md)", 
            data=report_text, 
            file_name=f"{report_title.replace(' ', '_')}.md", 
            mime="text/markdown", 
            key=f"dl_md_{state_key}"
        )
    with col2:
        try:
            ppt_data = create_ppt(report_text, report_title)
            st.download_button(
                label="📊 Download as PPT",
                data=ppt_data,
                file_name=f"{report_title.replace(' ', '_')}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                key=f"dl_ppt_{state_key}"
            )
        except Exception as e:
            st.error(f"PPT Compilation Error: {e}")
            
    with col3:
        if st.button("💾 Save to Profile", key=f"sv_{state_key}"):
            if supabase:
                try:
                    supabase.table("saved_reports").insert({
                        "user_email": st.session_state.user_email,
                        "report_type": report_title,
                        "content": report_text
                    }).execute()
                    st.success("✅ Saved to database!")
                except Exception as e:
                    st.error(f"Failed to save: {e}")
            else:
                st.error("Supabase client disconnected.")

# ---------------------------------------------------------
# 4. SUPABASE Authentication Gateway
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='main-title' style='text-align: center;'>AI Startup Copilot</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle' style='text-align: center; border: none;'>Founder Portal</div>", unsafe_allow_html=True)
        
        if supabase is None:
            st.error("⚠️ Supabase Backend Disconnected. Please check your SUPABASE_URL and SUPABASE_KEY in Secrets.")
            st.stop()
            
        with st.container():
            st.markdown("<h3 style='text-align: center; color: #38BDF8; font-family: Orbitron, sans-serif; margin-bottom: 20px;'>System Authentication</h3>", unsafe_allow_html=True)
            
            tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
            
            with tab_login:
                login_email = st.text_input("Corporate Email / Founder ID", placeholder="founder@startup.com", key="l_email")
                login_pwd = st.text_input("Password", type="password", placeholder="••••••••", key="l_pwd")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("SECURE LOGIN", type="primary", use_container_width=True, key="btn_login"):
                    if login_email and login_pwd:
                        try:
                            response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_pwd})
                            st.session_state.logged_in = True
                            st.session_state.user_email = login_email
                            st.rerun()
                        except Exception as e:
                            st.error("⚠️ Access Denied: Incorrect email or password.")
                    else:
                        st.error("⚠️ Credentials Required.")
            
            with tab_signup:
                signup_email = st.text_input("New Email Address", placeholder="founder@startup.com", key="s_email")
                signup_pwd = st.text_input("Create Password (Min 6 chars)", type="password", placeholder="••••••••", key="s_pwd")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("CREATE ACCOUNT", type="primary", use_container_width=True, key="btn_signup"):
                    if signup_email and len(signup_pwd) >= 6:
                        try:
                            response = supabase.auth.sign_up({"email": signup_email, "password": signup_pwd})
                            st.success("✅ Account created successfully! You can now switch to the Login tab.")
                        except Exception as e:
                            st.error(f"⚠️ Error creating account: {e}")
                    elif len(signup_pwd) < 6:
                        st.error("⚠️ Password must be at least 6 characters long.")
                    else:
                        st.error("⚠️ Email and Password are required.")
            
            st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #94A3B8; margin-top: 20px;'>🔒 Secured by Supabase Authentication</p>", unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# 5. Sidebar Configuration & CHAT MEMORY
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h1>Founder Assistant</h1>", unsafe_allow_html=True)
    
    user_identity = st.session_state.user_email.split('@')[0].capitalize()
    st.caption(f"Authenticated as: **{user_identity}**")
    st.markdown("<div class='cinematic-divider'></div>", unsafe_allow_html=True)
    
    # ------------------ RECENT LIBRARY (Like Gemini Left Bar) ------------------
    st.markdown("### 🗂️ Recent Library")
    if supabase:
        try:
            # Fetch user's saved reports from newest to oldest
            res = supabase.table("saved_reports").select("*").eq("user_email", st.session_state.user_email).order("created_at", desc=True).limit(15).execute()
            if res.data:
                for row in res.data:
                    # Create a snippet for the button name
                    date_str = row['created_at'].split("T")[0]
                    btn_label = f"📄 {row['report_type']} ({date_str})"
                    
                    st.markdown('<div class="history-btn">', unsafe_allow_html=True)
                    if st.button(btn_label, key=f"hist_{row['id']}", use_container_width=True):
                        st.session_state.viewing_history = row
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.caption("No saved projects yet.")
        except Exception as e:
            st.caption("Could not load history.")
    
    st.markdown("<div class='cinematic-divider'></div>", unsafe_allow_html=True)
    
    env_key = os.getenv("NVIDIA_API_KEY", "")
    if env_key:
        api_key = env_key
        st.success("✅ Secure AI Core Connected")
    else:
        api_key = st.text_input("API Key", type="password", help="Enter your NVIDIA API Key")
        
    st.caption("Powered by: **Nemotron-3-Ultra-550B**")
    
    st.markdown("<div class='cinematic-divider'></div>", unsafe_allow_html=True)
    if st.button("DISCONNECT (Log Out)"):
        try:
            supabase.auth.sign_out()
        except:
            pass
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.viewing_history = None
        st.session_state.results = {"market": None, "business": None, "competitor": None, "fundraising": None, "execution": None}
        st.rerun()

# ---------------------------------------------------------
# 6. Header & Personal Greeting OR Archive Viewer
# ---------------------------------------------------------
# ARCHIVE VIEWER (Overrides main screen if a sidebar history item is clicked)
if st.session_state.viewing_history:
    rep = st.session_state.viewing_history
    st.markdown(f"<div class='main-title'>🗂️ Archive: {rep['report_type']}</div>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Active Workspace", type="primary"):
        st.session_state.viewing_history = None
        st.rerun()
        
    st.markdown("<div class='cinematic-divider'></div>", unsafe_allow_html=True)
    display_report_actions(rep['content'], rep['report_type'], f"hist_view_{rep['id']}")
    st.stop()  # Stop rendering the rest of the tabs

# STANDARD ACTIVE WORKSPACE
st.markdown("<div class='main-title'>AI Startup Copilot</div>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>Hello, {user_identity}. How can I help you today?</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Market Research", "Business Planning", "Competitor Intel", "Fundraising Prep", "Task Execution", "Strategic Advisor"
])

# ---------------------------------------------------------
# TAB 1: MARKET RESEARCH
# ---------------------------------------------------------
with tab1:
    with st.container():
        st.markdown("### Market Intelligence & Deep Validation")
        st.write("Exhaustive analysis: Market Opportunity Score, ICP, TAM/SAM/SOM in ₹ (INR), GTM Channels, Macro Trends, Scenario Matrix, & 48-Hour Experiment.")
        
        col1, col2 = st.columns(2)
        with col1:
            idea = st.text_area("Initialize Core Concept:", value=st.session_state.global_idea, placeholder="Input startup idea or product description...")
            industry = st.text_input("Define Niche / Sector:", placeholder="e.g., Creator Economy, Fintech SaaS, Robotics PaaS")
        with col2:
            geography = st.text_input("Geographic Focus:", placeholder="e.g., India, Global, US/Canada, SE Asia")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_research = st.button("RUN MARKET PROTOCOL", type="primary")

        if btn_research:
            if not is_valid_input(idea):
                st.warning("⚠️ Invalid input detected. Please enter a meaningful startup concept.")
            else:
                st.session_state.global_idea = idea
                with st.spinner("Accessing global market data vectors... Performing deep VC analysis in Rupees (₹)..."):
                    prompt = f"""
                    Perform an exhaustive, highly detailed Venture Capital Market Intelligence Analysis for this startup idea:
                    - Idea: {idea}
                    - Sector: {industry}
                    - Region: {geography}

                    CRITICAL MANDATORY INSTRUCTIONS:
                    - ALL FINANCIAL FIGURES, MARKET SIZES, COST ESTIMATES, AND PRICING MUST BE PRESENTED STRICTLY IN INDIAN RUPEES (₹ / INR). Use standard notation (e.g., ₹12 Lakhs, ₹1.5 Crore).
                    - USE PLAIN TEXT ONLY. DO NOT use markdown code blocks, backticks (`), or LaTeX math blocks. Keep text clean, readable, and beautifully formatted in bullet points and tables.
                    - Provide deep, highly specific, numerical, and strictly factual insights. Avoid fluff.

                    Structure your response into 8 comprehensive sections:
                    ## 1. Executive Summary & Market Opportunity Score
                    - Opportunity Score (0-100) with clear justification.
                    - Core Thesis: Why is now the exact right time to build this?

                    ## 2. Granular Ideal Customer Profile (ICP) & Buyer Persona
                    - Target Role, Decision Maker, and Team Headcount.
                    - Primary Operational Pain Points.
                    - Buying Triggers & Budget Authority in ₹.

                    ## 3. Comprehensive Market Sizing (TAM / SAM / SOM in ₹)
                    Provide a detailed Markdown Table with columns: [Segment, Estimated Value in ₹, Sizing Logic].

                    ## 4. Scenario & Sensitivity Analysis Matrix (in ₹)
                    Provide a Markdown Table for Bear, Base, and Bull cases over 24 months.

                    ## 5. Macro Trends & Regulatory Vectors
                    - Industry Tailwinds & Regulatory/Compliance drivers (e.g., DPDP Act, BIS, RBI frameworks).

                    ## 6. Go-To-Market (GTM) Channels & Unit Economics (in ₹)
                    - Top 3 specific channels to acquire the first 100 users/customers.
                    - Estimated CAC in ₹ and payback period.

                    ## 7. Strategic Pros & Hidden Risks
                    - 3 major advantages and 3 brutal, unvarnished systemic risks.

                    ## 8. 48-Hour Tactical Validation Experiment
                    - Exact landing page headline, outbound cold email script, and minimum viable signals.
                    """
                    result = generate_ai_response(api_key, prompt)
                    if result:
                        st.session_state.results["market"] = result

        if st.session_state.results["market"]:
            st.markdown("#### Deep Market Intelligence Completed:")
            display_report_actions(st.session_state.results["market"], "Market Research", "market")

# ---------------------------------------------------------
# TAB 2: BUSINESS PLANNING
# ---------------------------------------------------------
with tab2:
    with st.container():
        st.markdown("### Interactive Lean Canvas & Unit Economics (All Financials in ₹)")
        st.write("Generate a structured, operational one-page business model with granular unit economics & a realistic $1B+ unicorn scaling roadmap.")
        
        col1, col2 = st.columns(2)
        with col1:
            startup_name = st.text_input("Startup Identifier (Name):", value=st.session_state.global_startup_name, placeholder="Enter product name...")
            product_desc = st.text_area("Product Description & Core Features:", value=st.session_state.global_idea, placeholder="Describe full product functionality...")
            
            revenue_models_list = [
                "Subscription (SaaS)", "Transactional / Per-Transaction Fee", "Freemium to Enterprise (Upsell)",
                "Usage-Based (Pay-As-You-Go)", "Marketplace Take Rate / Commission", "Direct Sales / E-commerce",
                "Ad-Based / Sponsorship", "Affiliate / Lead Generation", "Open Source / Dual Licensing",
                "Licensing / White-label", "Hardware + Software (Razors & Blades)", "Data Monetization",
                "Franchise Model", "Agency / Retainer / Services", "Other (Specify Below)"
            ]
            selected_model = st.selectbox("Revenue Model:", revenue_models_list)
            
            if selected_model == "Other (Specify Below)":
                custom_model = st.text_input("Specify Custom Revenue Model:", placeholder="e.g., Tokenomic Staking Fee")
                revenue_model = custom_model if custom_model else "Custom Revenue Model"
            else:
                revenue_model = selected_model
            
        with col2:
            target_country = st.text_input("Target Country / Region:", value="India", placeholder="e.g., India, Global")
            value_prop = st.text_area("Core Differentiator (UVP):", placeholder="What makes you uniquely positioned to solve the problem?")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_plan = st.button("BUILD BUSINESS MODEL", type="primary")

    if btn_plan:
        if not is_valid_input(startup_name) or not is_valid_input(product_desc):
            st.warning("⚠️ Invalid input detected. Please provide a valid startup name and product description.")
        else:
            st.session_state.global_startup_name = startup_name
            st.session_state.global_idea = product_desc
            with st.spinner("Synthesizing operational architecture, financial model in ₹, & unicorn scaling roadmap..."):
                prompt = f"""
                Create an exhaustive, professional Lean Business Canvas, Unit Economics blueprint in ₹, and a Realistic Scale Roadmap for:
                - Startup Name: {startup_name}
                - Product Description: {product_desc}
                - Target Region: {target_country}
                - Core Differentiator (UVP): {value_prop}
                - Revenue Model: {revenue_model}

                CRITICAL MANDATORY INSTRUCTIONS:
                - ALL FINANCIAL FIGURES, COSTS, PRICING TIERS, CAC, LTV, AND REVENUE TARGETS MUST BE PRESENTED STRICTLY IN INDIAN RUPEES (₹ / INR). Use standard notation (e.g., ₹15 Lakhs, ₹2.5 Crores).
                - USE PLAIN TEXT ONLY. DO NOT use markdown code blocks, backticks (`), or LaTeX formatting.

                Output the analysis in the following sections:
                ## 1. Comprehensive Lean Business Canvas
                Provide a detailed Markdown Table covering Problem, Solution, UVP, Unfair Advantage, Customer Segments, Key Metrics, Channels, Cost Structure in ₹, and Revenue Streams in ₹.

                ## 2. Granular Unit Economics & Financial Benchmarks (in ₹)
                - Target LTV, CAC, LTV:CAC Ratio, Gross Margin %, and Payback Period.
                - Detailed Fixed vs Variable Cost Breakdown in ₹ (salaries, compute, infrastructure, compliance).
                - 3 Clear Pricing Tiers in ₹ with exact feature limits.

                ## 3. Pragmatic Step-by-Step Scaling Roadmap
                - Phase 1: Zero to One (Product-Market Fit & Initial Validation)
                - Phase 2: Repeatable Growth Engine 
                - Phase 3: Scale-Up & Market Expansion
                - Phase 4: Market Dominance & Long-Term Sustainability
                """
                result = generate_ai_response(api_key, prompt)
                if result:
                    st.session_state.results["business"] = result
                    
    if st.session_state.results["business"]:
        display_report_actions(st.session_state.results["business"], "Business Plan", "business")

# ---------------------------------------------------------
# TAB 3: COMPETITOR ANALYSIS
# ---------------------------------------------------------
with tab3:
    with st.container():
        st.markdown("### Competitive Intelligence Matrix & Moat Analysis")
        st.write("Exhaustive competitive benchmarking. If target competitors are left blank, AI will auto-discover at least 20 main competitors.")
        
        col1, col2 = st.columns(2)
        with col1:
            my_startup = st.text_input("Your Product Name:", value=st.session_state.global_startup_name, placeholder="e.g., FlowAI")
            competitors = st.text_input("Target Competitors (Optional):", placeholder="Leave blank for auto-discovery")
        with col2:
            differentiator = st.text_area("Your Defensive Moat / Technology:", placeholder="Why can't they just copy you?")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_comp = st.button("EXECUTE COMPETITIVE BENCHMARK", type="primary")

    if btn_comp:
        if not is_valid_input(my_startup):
            st.warning("⚠️ Please provide a valid product name.")
        else:
            with st.spinner("Analyzing competitive landscape & auto-discovering top 20 competitors..."):
                prompt = f"""
                Perform an exhaustive, institutional-grade competitive intelligence analysis for:
                - Target Startup: {my_startup}
                - Competitors: {competitors if competitors.strip() else 'AUTO-DISCOVER AT LEAST 20 MAIN COMPETITORS GLOBALLY AND IN INDIA.'}
                - Defensive Advantage: {differentiator}

                CRITICAL MANDATORY INSTRUCTIONS:
                - YOU MUST IDENTIFY, NAME, AND ANALYZE AT LEAST 20 MAIN COMPETITORS (Direct, Indirect, Legacy Incumbents, and Emerging Startups).
                - ALL FINANCIALS AND PRICING MUST BE IN INDIAN RUPEES (₹ / INR).
                - USE PLAIN TEXT ONLY. DO NOT use markdown code blocks, backticks (`), or LaTeX.

                Output Structure:
                ## 1. Master Competitor Directory (At least 20 Competitors)
                - Numbered list of 20 competitors with Name/Origin, Business Model & Pricing in ₹, Critical Weaknesses, and Tactical Exploit Strategy.

                ## 2. Summary Matrix Table
                - Markdown table comparing your startup against top competitors.

                ## 3. Strategic Blind Spots & Incumbent Vulnerabilities
                ## 4. Defensible Positioning & Moat Lock-in Plan
                """
                result = generate_ai_response(api_key, prompt)
                if result:
                    st.session_state.results["competitor"] = result
                    
    if st.session_state.results["competitor"]:
        display_report_actions(st.session_state.results["competitor"], "Competitor Intel", "competitor")

# ---------------------------------------------------------
# TAB 4: FUNDRAISING PREPARATION
# ---------------------------------------------------------
with tab4:
    with st.container():
        st.markdown("### Advanced Investor Protocol & Pitch Prep (Financials in ₹)")
        st.write("Institutional-grade fundraising prep: 30-sec hook, valuation caps in ₹, Cap Table dilution models, term sheet tactics, data room checklist, & VC Q&A.")
        
        col1, col2 = st.columns(2)
        with col1:
            stage = st.selectbox("Current Round Stage:", ["Pre-Seed", "Seed", "Series A", "Series B", "Strategic Partner Round"])
            ask_amount = st.text_input("Target Raise (in ₹):", placeholder="e.g., ₹1.5 Crore or ₹10 Crore")
        with col2:
            traction = st.text_area("Key Milestones / Traction:", placeholder="e.g., 4,500 waitlist, ₹12 Lakhs ARR, 3 enterprise LOIs.")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_fund = st.button("INITIALIZE PITCH ASSETS", type="primary")

    if btn_fund:
        with st.spinner("Generating institutional fundraising suite in ₹..."):
            prompt = f"""
            Generate an advanced, highly detailed investor fundraising suite for:
            - Stage: {stage}
            - Target Raise: {ask_amount}
            - Traction: {traction}

            CRITICAL MANDATORY INSTRUCTIONS: 
            - ALL FINANCIAL FIGURES, VALUATIONS, AND DILUTION MUST BE IN INDIAN RUPEES (₹ / INR). 
            - USE PLAIN TEXT ONLY. DO NOT use markdown code blocks, backticks (`), or LaTeX.

            Provide an advanced 7-part blueprint:
            ## 1. The 30-Second Elevator Pitch & Narrative Hook
            ## 2. Valuation Benchmarks & Cap Table Dilution Scenarios (in ₹)
            ## 3. Investor Persona Targeting Matrix (Angels & VCs in India/Global)
            ## 4. Granular Use of Funds Allocation Breakdown (in ₹)
            ## 5. Term Sheet Negotiation Tactics & Protection Clauses
            ## 6. Investor Due Diligence Data Room Checklist
            ## 7. Top 7 Hardest VC Questions & Battle-Tested Winning Answers
            """
            result = generate_ai_response(api_key, prompt)
            if result:
                st.session_state.results["fundraising"] = result
                
    if st.session_state.results["fundraising"]:
        display_report_actions(st.session_state.results["fundraising"], "Fundraising Prep", "fundraising")

# ---------------------------------------------------------
# TAB 5: TASK EXECUTION
# ---------------------------------------------------------
with tab5:
    with st.container():
        st.markdown("### Hyper-Realistic 30-Day Execution Roadmap")
        st.write("Convert high-level strategy into metric-driven, day-by-day operational sprints with exact tool stacks and conversion formulas.")
        
        col1, col2 = st.columns(2)
        with col1:
            primary_goal = st.text_input("Critical 30-Day Objective:", placeholder="e.g., Convert 10% of waitlist into paying design partners generating ₹5 Lakhs MRR.")
        with col2:
            weekly_hours = st.slider("Weekly Team Sprints (Hours):", 20, 160, 60)
            st.markdown("<br>", unsafe_allow_html=True)
            btn_task = st.button("GENERATE EXECUTION PLAN", type="primary")

    if btn_task:
        if not is_valid_input(primary_goal):
            st.warning("⚠️ Please provide a meaningful objective.")
        else:
            with st.spinner("Deconstructing strategy into realistic day-by-day operational tasks..."):
                prompt = f"""
                Act as an elite Chief of Staff and Operations Lead. Create a hyper-realistic, granular 30-day execution roadmap to achieve:
                - Goal: {primary_goal}
                - Team Capacity: {weekly_hours} hrs/wk

                CRITICAL MANDATORY INSTRUCTIONS:
                - ALL FINANCIAL METRICS, BUDGETS, AND COSTS MUST BE IN INDIAN RUPEES (₹ / INR).
                - USE PLAIN TEXT ONLY. DO NOT use markdown code blocks, backticks (`), or LaTeX equations. Keep advice highly actionable, practical, and easy to read.

                Structure output into:
                ## 1. Key Success Metrics & Operational Funnel
                - Provide practical, step-by-step numbers needed to hit this goal (e.g., for software: outbound messages -> calls -> closes; for hardware/robotics: prototypes built -> beta testing -> LOIs signed).

                ## 2. Recommended Tech Stack & Tooling Suite
                ## 3. Granular Weekly Operational Sprints (Week 1, 2, 3, 4)
                ## 4. Execution Bottlenecks & Operational Contingency Triggers
                """
                result = generate_ai_response(api_key, prompt)
                if result:
                    st.session_state.results["execution"] = result
                    
    if st.session_state.results["execution"]:
        display_report_actions(st.session_state.results["execution"], "Task Execution", "execution")

# ---------------------------------------------------------
# TAB 6: STRATEGIC ADVISOR & CHAT MEMORY
# ---------------------------------------------------------
with tab6:
    with st.container():
        st.markdown("### Strategic Advisory Protocol (Fact-Grounded Analysis)")
        st.write("Get unvarnished, deep-dive strategic guidance on pivots, hires, capital allocation, and high-stakes trade-offs.")
        
        # Adding a button to let users push the active chat into the Sidebar History
        col_chat_1, col_chat_2 = st.columns([4, 1])
        with col_chat_2:
            if st.button("💾 Save Chat to Library", use_container_width=True):
                if len(st.session_state.messages) > 1 and supabase:
                    # Compile the chat into a text report
                    chat_log = "## Strategic Chat Session\n\n"
                    for m in st.session_state.messages[1:]: # Skip initial greeting
                        role = "You" if m['role'] == 'user' else "AI Advisor"
                        chat_log += f"**{role}:**\n{m['content']}\n\n---\n\n"
                        
                    try:
                        supabase.table("saved_reports").insert({
                            "user_email": st.session_state.user_email,
                            "report_type": "Chat Session",
                            "content": chat_log
                        }).execute()
                        st.success("✅ Chat saved to library!")
                    except Exception as e:
                        st.error("Failed to save chat.")
                else:
                    st.warning("Nothing to save yet.")
        
        st.markdown("<div class='cinematic-divider'></div>", unsafe_allow_html=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": f"Welcome! I am your AI Strategic Co-Founder. What critical decision or trade-off are you evaluating today?"}
            ]

        chat_container = st.container(height=450)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if user_input := st.chat_input("Input strategic trade-off, e.g., 'Should we pivot from B2C to B2B enterprise in India?"):
            if not is_valid_input(user_input):
                st.warning("⚠️ Please ask a valid strategic question.")
            else:
                with chat_container:
                    st.chat_message("user").markdown(user_input)
                
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                with chat_container:
                    with st.spinner("Analyzing exhaustive trade-offs against verified business facts & historical case studies..."):
                        sys_instruct = f"""
                        You are a pragmatic, direct, and elite veteran serial founder advising a user. 
                        Provide an EXHAUSTIVE, highly detailed, fact-grounded strategic analysis of the user's dilemma.

                        STRICT REQUIREMENTS:
                        1. ALL FINANCIAL REFERENCES AND COST TRADE-OFFS MUST BE PRESENTED IN INDIAN RUPEES (₹ / INR).
                        2. STRICT FACTUAL GROUNDING: Rely entirely on verified business principles, real economic data, and true startup case studies.
                        3. Deeply break down the PROS and CONS of each option.
                        4. Analyze SECOND-ORDER EFFECTS (what happens 6, 12, and 24 months down the road).
                        5. Identify CRITICAL RISK VECTORS and mitigation playbooks.
                        6. Cite real historical startup case studies (e.g., Stripe, Airbnb, Razorpay, Swiggy, Brex, Freshworks) that faced this exact crossroad.
                        7. Conclude with a definitive, unvarnished, action-oriented FINAL RECOMMENDATION.
                        8. USE PLAIN TEXT ONLY. DO NOT use LaTeX formatting, code blocks, or backticks.
                        """
                        reply = generate_ai_response(api_key, user_input, system_prompt=sys_instruct)
                        
                        if reply:
                            st.chat_message("assistant").markdown(reply)
                            st.session_state.messages.append({"role": "assistant", "content": reply})