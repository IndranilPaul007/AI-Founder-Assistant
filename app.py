import streamlit as st
import pandas as pd
import re
from google import genai
from google.genai import types

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
if "global_startup_name" not in st.session_state:
    st.session_state.global_startup_name = ""
if "global_idea" not in st.session_state:
    st.session_state.global_idea = ""

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
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Helper Functions & Validation Logic
# ---------------------------------------------------------
def is_valid_input(text):
    """Validates if input contains meaningful text rather than random gibberish / keyboard mashing."""
    if not text or len(text.strip()) < 3:
        return False
    # Check if string has at least one vowel (gibberish keyboard smashes often lack vowels entirely)
    if not re.search(r'[aeiouAEIOU]', text) and len(text.strip()) > 3:
        return False
    return True

def generate_ai_response(api_key, prompt, system_prompt=""):
    if not api_key:
        st.error("⚠️ CRITICAL: API Key Missing. Enter it in the sidebar.")
        return None
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else "You are a top-tier Silicon Valley venture partner and Y-Combinator strategist. Provide exhaustive, highly detailed, strictly factual data-driven startup analysis.",
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# ---------------------------------------------------------
# 4. Authentication Gateway
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='main-title' style='text-align: center;'>AI Startup Copilot</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle' style='text-align: center; border: none;'>Founder Portal</div>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<h3 style='text-align: center; color: #38BDF8; font-family: Orbitron, sans-serif; margin-bottom: 20px;'>System Authentication</h3>", unsafe_allow_html=True)
            auth_email = st.text_input("Corporate Email / Founder ID", placeholder="founder@startup.com")
            auth_pwd = st.text_input("Password", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("SECURE LOGIN", type="primary", use_container_width=True):
                if auth_email and auth_pwd:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Access Denied. Credentials Required.")
            
            st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #94A3B8; margin-top: 20px;'>(Type anything to enter, log in has no backend sir.)</p>", unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# 5. Sidebar Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h1>Founder Assistant</h1>", unsafe_allow_html=True)
    st.caption("AI-Driven Startup Co-Founder")
    st.markdown("<div class='cinematic-divider'></div>", unsafe_allow_html=True)
    
    user_name = st.text_input("Your Name:", value="Indranil", help="Enter your name to personalize your assistant")
    api_key = st.text_input("API Key", type="password", help="Enter your Google AI Studio API Key")
    st.caption("Powered by: **Gemini 3.6 Flash**")
    
    st.markdown("<div class='cinematic-divider'></div>", unsafe_allow_html=True)
    st.markdown("### Operational Metrics")
    st.metric(label="Estimated Time Saved", value="40+ Hours", delta="Per Week")
    st.metric(label="Strategy Confidence", value="High", delta="Data-Driven")

    st.markdown("<div class='cinematic-divider'></div>", unsafe_allow_html=True)
    if st.button("DISCONNECT (Log Out)"):
        st.session_state.logged_in = False
        st.rerun()

# ---------------------------------------------------------
# 6. Header & Personal Greeting
# ---------------------------------------------------------
st.markdown("<div class='main-title'>AI Startup Copilot</div>", unsafe_allow_html=True)
display_name = user_name.strip() if user_name.strip() else "Founder"
st.markdown(f"<div class='subtitle'>Hello, {display_name}. How can I help you today?</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Market Research", "Business Planning", "Competitor Intel", "Fundraising Prep", "Task Execution", "Strategic Advisor"
])

# ---------------------------------------------------------
# TAB 1: MARKET RESEARCH (Exhaustive VC Analysis)
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
                st.warning("⚠️ Please enter a meaningful startup concept or idea rather than random characters.")
            else:
                st.session_state.global_idea = idea
                with st.spinner("Accessing global market data vectors... Performing deep VC analysis in Rupees (₹)..."):
                    prompt = f"""
                    Perform an exhaustive, highly detailed Venture Capital Market Intelligence Analysis for this startup idea:
                    - Idea: {idea}
                    - Sector: {industry}
                    - Region: {geography}

                    CRITICAL MANDATORY INSTRUCTIONS:
                    - ALL FINANCIAL FIGURES, MARKET SIZES, COST ESTIMATES, AND PRICING MUST BE PRESENTED STRICTLY IN INDIAN RUPEES (₹ / INR). Use standard notation (e.g., ₹12 Lakhs, ₹1.5 Crore, ₹50,000). DO NOT use USD ($).
                    - Use plain text for numbers and currencies. DO NOT use LaTeX formatting or math blocks.
                    - Provide deep, highly specific, numerical, and strictly factual insights. Avoid fluff or high-level generalizations.

                    Structure your response into 8 comprehensive sections:

                    ## 1. Executive Summary & Market Opportunity Score
                    - **Opportunity Score (0-100)**: Give a score with clear justification.
                    - **Core Thesis**: Why is now the exact right time to build this?

                    ## 2. Granular Ideal Customer Profile (ICP) & Buyer Persona
                    - **Target Role & Decision Maker**: Specific title, company size, team headcount.
                    - **Primary Pain Points**: 3 specific operational headaches they face today.
                    - **Buying Triggers & Budget Authority**: What causes them to allocate budget right now in ₹? Who holds sign-off power?

                    ## 3. Comprehensive Market Sizing (TAM / SAM / SOM in ₹ / INR)
                    Provide a detailed Markdown Table with columns: [Segment, Estimated Value in ₹ (INR), Sizing Logic & Assumptions].
                    - **Total Addressable Market (TAM)**: Valuation in ₹ Crores.
                    - **Serviceable Addressable Market (SAM)**: Regional/niche target segment valuation in ₹ Crores.
                    - **Serviceable Obtainable Market (SOM)**: Realistic 3-year achievable target revenue in ₹ Crores/Lakhs.

                    ## 4. Scenario & Sensitivity Analysis Matrix (in ₹ / INR)
                    Provide a Markdown Table for 3 financial performance scenarios over 24 months:
                    - **Bear Case (Pessimistic)**: Conservative adoption, revenue in ₹, churn risk.
                    - **Base Case (Realistic)**: Steady growth, revenue in ₹, target unit economics.
                    - **Bull Case (Optimistic)**: Viral adoption, enterprise expansion, revenue in ₹.

                    ## 5. Macro Trends & Regulatory Vectors
                    - **Industry Tailwinds**: 3 macro shifts (economic, behavioral, tech) accelerating demand.
                    - **Regulatory & Compliance Drivers**: Key Indian and global acts, laws, or compliance factors creating urgency (e.g., DPDP Act, GST compliance, RBI frameworks).

                    ## 6. Go-To-Market (GTM) Channels & Unit Economics Estimates (in ₹)
                    - **Top 3 Acquisition Channels**: Highly specific routes to acquire first 100 users.
                    - **Estimated CAC & Payback Period**: Target Customer Acquisition Cost in ₹ and month payback period.

                    ## 7. Strategic Pros & Cons of this Market
                    - **Pros**: 3 major advantages of entering this specific niche.
                    - **Cons & Hidden Risks**: 3 brutal, unvarnished realities or systemic risks the founder must prepare for.

                    ## 8. 48-Hour Tactical Validation Experiment
                    - **Step 1: Landing Page & Hook Strategy** (Exact headline and core value prop).
                    - **Step 2: Outbound Script / Cold Outreach Hook** (Exact subject line and cold outreach copy template).
                    - **Step 3: Minimum Viable Signals (MVS)** (Target metrics in ₹ / signups to prove demand within 48 hours).
                    """
                    result = generate_ai_response(api_key, prompt)
                    if result:
                        st.markdown("#### Deep Market Intelligence Completed:")
                        st.markdown(result)

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
            product_desc = st.text_area("Product Description & Core Features:", value=st.session_state.global_idea, placeholder="Describe full product functionality, technical workflow, and key features...")
            
            revenue_models_list = [
                "Subscription (SaaS)",
                "Transactional / Per-Transaction Fee",
                "Freemium to Enterprise (Upsell)",
                "Usage-Based (Pay-As-You-Go)",
                "Marketplace Take Rate / Commission",
                "Direct Sales / E-commerce",
                "Ad-Based / Sponsorship",
                "Affiliate / Lead Generation",
                "Open Source / Dual Licensing",
                "Licensing / White-label",
                "Hardware + Software (Razors & Blades)",
                "Data Monetization",
                "Franchise Model",
                "Agency / Retainer / Services",
                "Other (Specify Below)"
            ]
            selected_model = st.selectbox("Revenue Model:", revenue_models_list)
            
            if selected_model == "Other (Specify Below)":
                custom_model = st.text_input("Specify Custom Revenue Model:", placeholder="e.g., Tokenomic Staking Fee, Revenue-Share Royalty")
                revenue_model = custom_model if custom_model else "Custom Revenue Model"
            else:
                revenue_model = selected_model
            
        with col2:
            target_country = st.text_input("Target Country / Region:", value="India", placeholder="e.g., India, Global, USA, EU, SE Asia")
            value_prop = st.text_area("Core Differentiator (UVP):", placeholder="What makes you uniquely positioned to solve the problem?")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_plan = st.button("BUILD BUSINESS MODEL", type="primary")

    if btn_plan:
        if not is_valid_input(startup_name) or not is_valid_input(product_desc):
            st.warning("⚠️ Please provide a valid startup name and product description rather than random characters.")
        else:
            st.session_state.global_startup_name = startup_name
            st.session_state.global_idea = product_desc
            with st.spinner("Synthesizing operational architecture, financial model in ₹, & unicorn scaling roadmap..."):
                prompt = f"""
                Create an exhaustive, professional Lean Business Canvas, Unit Economics blueprint in ₹ (INR), and a Realistic $1B+ Unicorn Scaling Roadmap for:
                - Startup Name: {startup_name}
                - Product Description & Features: {product_desc}
                - Target Country / Region: {target_country}
                - Core Differentiator (UVP): {value_prop}
                - Revenue Model: {revenue_model}

                CRITICAL MANDATORY INSTRUCTIONS:
                - ALL FINANCIAL FIGURES, COSTS, PRICING TIERS, CAC, LTV, AND REVENUE TARGETS MUST BE PRESENTED STRICTLY IN INDIAN RUPEES (₹ / INR). Use standard notation (e.g., ₹15 Lakhs, ₹2.5 Crores). DO NOT use USD ($).
                - Use plain text formatting. DO NOT use LaTeX formatting or math blocks.

                Output the analysis in the following comprehensive sections:

                ## 1. Comprehensive Lean Business Canvas
                Provide a detailed Markdown Table covering all standard Lean Canvas blocks (Problem, Solution, UVP, Unfair Advantage, Customer Segments, Key Metrics, Channels, Cost Structure in ₹, Revenue Streams in ₹).

                ## 2. Granular Unit Economics & Financial Benchmarks (in ₹ / INR)
                - **Target Unit Economics**: LTV in ₹, CAC in ₹, LTV:CAC Ratio (target 3:1+), Gross Margin %, Payback Period in months.
                - **Detailed Cost Structure Breakdown in ₹**: Fixed vs. variable operational costs tailored to operating in {target_country} (engineering salaries in ₹/month, server compute in ₹, office lease in ₹, compliance in ₹).
                - **Pricing Tiers in ₹**: 3 clear pricing plans with exact feature limits and monthly/annual fees in Indian Rupees.
                - **Revenue Model Assessment**: Pros, cons, and cash-flow risk mitigation for {revenue_model}.

                ## 3. Realistic Step-by-Step Roadmap to $1B+ (₹8,300+ Crore) Unicorn Scale
                Provide a realistic, phase-by-phase playbook for scaling from launch to unicorn status, explicitly identifying major failure points and tactical solutions at each stage:

                ### Phase 1: Zero to One - Product-Market Fit (₹0 to ₹8 Crore ARR / $1M)
                - **Key Strategic Milestones**: Team size, active customer benchmarks, retention thresholds.
                - **Critical Problems & Failure Points**: Top 3 existential traps at this stage.
                - **Tactical Solutions & Playbook**: Step-by-step actions to resolve each problem.

                ### Phase 2: Repeatable Engine & Growth (₹8 Crore to ₹80 Crore ARR / $10M)
                - **Key Strategic Milestones**: Channel scaling, leadership hiring, unit economics stabilization in {target_country}.
                - **Critical Problems & Failure Points**: Sales bottlenecks, rising CAC in ₹, tech debt.
                - **Tactical Solutions & Playbook**: Step-by-step operational fixes.

                ### Phase 3: Scale-Up & Market Expansion (₹80 Crore to ₹400 Crore ARR / $50M)
                - **Key Strategic Milestones**: International expansion beyond {target_country}, multi-product strategy, strategic partnerships.
                - **Critical Problems & Failure Points**: Bureaucracy, market saturation, aggressive incumbent response.
                - **Tactical Solutions & Playbook**: Tactical maneuvers to maintain growth momentum.

                ### Phase 4: Hypergrowth to $1B+ Unicorn Status (₹800+ Crore ARR / ₹8,300+ Crore Valuation)
                - **Key Strategic Milestones**: Dominant market share, platform ecosystem, IPO or major liquidity readiness.
                - **Critical Problems & Failure Points**: Regulatory scrutiny, macroeconomic headwinds, executive friction.
                - **Tactical Solutions & Playbook**: Governance and defense strategies to lock in unicorn status.
                """
                result = generate_ai_response(api_key, prompt)
                if result:
                    st.markdown(result)

# ---------------------------------------------------------
# TAB 3: COMPETITOR ANALYSIS (Auto-Discover 20+ Competitors)
# ---------------------------------------------------------
with tab3:
    with st.container():
        st.markdown("### Competitive Intelligence Matrix & Moat Analysis")
        st.write("Exhaustive competitive benchmarking. If target competitors are left blank, AI will auto-discover at least 20 main competitors.")
        
        col1, col2 = st.columns(2)
        with col1:
            my_startup = st.text_input("Your Product Name:", value=st.session_state.global_startup_name, placeholder="e.g., FlowAI")
            competitors = st.text_input("Target Competitors (Optional):", placeholder="e.g., QuickBooks, Keeper Tax (Leave blank for auto-discovery)")
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
                - Competitors Provided by User: {competitors if competitors.strip() else 'NONE PROVIDED - YOU MUST AUTO-DISCOVER AND LIST AT LEAST 20 MAIN COMPETITORS IN THIS DOMAIN.'}
                - User's Defensive Advantage: {differentiator}

                CRITICAL MANDATORY INSTRUCTIONS:
                - YOU MUST IDENTIFY, NAME, AND ANALYZE AT LEAST 20 MAIN COMPETITORS (Direct, Indirect, Legacy Incumbents, and Emerging Startups globally and in India).
                - ALL FINANCIALS, PRICING, AND REVENUE NUMBERS MUST BE IN INDIAN RUPEES (₹ / INR). Use plain text notation. DO NOT use LaTeX formatting or USD.

                Output Structure:

                ## 1. Master Competitor Directory (At least 20 Main Competitors)
                Provide an exhaustive, numbered list of AT LEAST 20 COMPETITORS across the industry. For EACH of the 20 competitors, provide:
                - **Competitor Name & Origin**: (e.g., Company Name, Country/HQ)
                - **In-Depth Business Model & Pricing Structure (in ₹)**: How they make money, pricing tiers in ₹, go-to-market model.
                - **Critical Weaknesses & Where They Lack**: Their major product flaws, customer complaints, legacy tech debt, high prices, or poor customer support.
                - **Tactical Exploit Strategy**: Exactly how {my_startup} can take advantage of this competitor's weakness to steal market share.

                ## 2. High-Level Summary Matrix Table
                Provide a Markdown Summary Table comparing {my_startup} against top competitors across: [Feature Set, Pricing Tier (in ₹), Target Audience, Key Bottleneck, Win Strategy].

                ## 3. Strategic Blind Spots & Incumbent Vulnerabilities
                Identify 3 massive industry blind spots where legacy incumbents are failing users today.

                ## 4. Defensible Positioning & Moat Lock-in Plan
                A 3-step action plan to protect {my_startup} from retaliatory price wars or features copied by incumbents.
                """
                result = generate_ai_response(api_key, prompt)
                if result:
                    st.markdown(result)

# ---------------------------------------------------------
# TAB 4: FUNDRAISING PREPARATION (Advanced & Detailed)
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
            - Target Raise: {ask_amount} (Ensure all analysis is grounded in ₹ / INR)
            - Traction: {traction}

            CRITICAL MANDATORY INSTRUCTIONS:
            - ALL FINANCIAL FIGURES, VALUATION CAPS, DILUTION NUMBERS, AND ALLOCATIONS MUST BE PRESENTED STRICTLY IN INDIAN RUPEES (₹ / INR). Use standard notation (e.g., ₹5 Crore, ₹25 Lakhs). DO NOT use USD.
            - Use plain text formatting. DO NOT use LaTeX.

            Provide an advanced 7-part fundraising blueprint:

            ## 1. The 30-Second Elevator Pitch & Narrative Hook
            - High-impact story framework focused on problem severity, market timing, and unique advantage.

            ## 2. Valuation Benchmarks & Cap Table Dilution Scenarios (in ₹ / INR)
            - **Realistic Valuation Cap (SAFE / iSAFE)**: Pre-money vs. Post-money valuation range in ₹ Crores for {stage} in India/Global context.
            - **Cap Table Dilution Table**: Model dilution for Founders, Investors, and ESOP Pool (Option Pool Shuffle analysis). Show exact equity % remaining post-round.

            ## 3. Investor Persona Targeting Matrix (Angels & VCs in India/Global)
            - Breakdown exact investor archetypes to target, typical cheque sizes in ₹ Lakhs/Crores, and key deal criteria.

            ## 4. Granular Use of Funds Allocation Breakdown (in ₹)
            - Detailed itemized budget table in ₹ Lakhs/Crores for: Product R&D, Engineering Hiring, Marketing & CAC, Compliance/Legal, and Runway Buffer (Target: 18-24 months runway).

            ## 5. Term Sheet Negotiation Tactics & Protection Clauses
            - Key clauses to negotiate fiercely: Liquidation Preference (1x non-participating vs participating), Board Control seats, Anti-dilution clauses, Drag-along/Tag-along rights.

            ## 6. Investor Due Diligence Data Room Checklist
            - Exhaustive checklist of documents needed in the Data Room across 4 categories: [Corporate/Legal, Financial Model, Technical/IP Architecture, HR & Team Contracts].

            ## 7. Top 7 Hardest VC Questions & Battle-Tested Winning Answers
            - Provide 7 hardest pushback questions VCs will ask regarding traction, CAC, defensibility, competition, and team risk, with exact winning response scripts.
            """
            result = generate_ai_response(api_key, prompt)
            if result:
                st.markdown(result)

# ---------------------------------------------------------
# TAB 5: TASK EXECUTION (Hyper-Realistic Sprints)
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
                - ALL FINANCIAL METRICS, BUDGETS, AND COSTS MUST BE IN INDIAN RUPEES (₹ / INR). Use plain text formatting. DO NOT use LaTeX.
                - Give realistic, pragmatic, step-by-step instructions. Recommend specific real-world tools, software, scripts, and workflows.

                Structure output into:

                ## 1. Mathematical Growth Conversion Formula
                - Breakdown exact conversion funnel numbers (e.g., "To reach target goal, send X outbound messages via LinkedIn/Email, achieve Y% open rate, convert Z% into demo calls, close W paying accounts at ₹XX per account").

                ## 2. Recommended Tech Stack & Tooling Suite
                - List exact tools for Outreach, CRM, Analytics, Automations, Payment Gateways (e.g., Razorpay/Stripe), and Project Management.

                ## 3. Granular Weekly Operational Sprints
                - **Week 1 (Days 1-7): Infrastructure & Outbound Engine Setup** (Day-by-day deliverables).
                - **Week 2 (Days 8-14): Campaign Execution & Initial Demos** (Day-by-day deliverables).
                - **Week 3 (Days 15-21): Conversion, Negotiation, & Closing** (Day-by-day deliverables).
                - **Week 4 (Days 22-30): Onboarding, Retainers in ₹, & Process Documentation** (Day-by-day deliverables).

                ## 4. Execution Bottlenecks & Operational Contingency Triggers
                - Identify top 3 single points of failure in this sprint and exact backup triggers if targets are missed by Day 15.
                """
                result = generate_ai_response(api_key, prompt)
                if result:
                    st.markdown(result)

# ---------------------------------------------------------
# TAB 6: STRATEGIC DECISION SUPPORT (Strict Facts & In-Depth)
# ---------------------------------------------------------
with tab6:
    with st.container():
        st.markdown("### Strategic Advisory Protocol (Fact-Grounded Analysis)")
        st.write("Get unvarnished, deep-dive strategic guidance on pivots, hires, capital allocation, and high-stakes trade-offs. Strictly grounded in facts.")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": f"Welcome {display_name}! I am your AI Strategic Co-Founder. What critical decision or trade-off are you evaluating today? Ask any strategic question, and I will analyze it with pure facts, historical case studies, and exhaustive depth."}
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
                        You are a pragmatic, direct, and elite veteran serial founder advising {display_name}. 
                        Provide an EXHAUSTIVE, highly detailed, fact-grounded strategic analysis of the user's dilemma.

                        STRICT REQUIREMENTS:
                        1. ALL FINANCIAL REFERENCES AND COST TRADE-OFFS MUST BE PRESENTED IN INDIAN RUPEES (₹ / INR).
                        2. STRICT FACTUAL GROUNDING: Rely entirely on verified business principles, real economic data, and true startup case studies. Do not speculate or invent ungrounded claims.
                        3. Deeply break down the PROS and CONS of each option.
                        4. Analyze SECOND-ORDER EFFECTS (what happens 6, 12, and 24 months down the road as a direct consequence of this choice).
                        5. Identify CRITICAL RISK VECTORS and mitigation playbooks for each path.
                        6. Cite real historical startup case studies (e.g., Stripe, Airbnb, Razorpay, Swiggy, Brex, Freshworks) that faced this exact crossroad and how they resolved it.
                        7. Conclude with a definitive, unvarnished, action-oriented FINAL RECOMMENDATION—do not hedge or give generic "it depends" answers. Make the call.
                        8. Use plain text formatting. DO NOT use LaTeX formatting or math blocks.
                        """
                        reply = generate_ai_response(api_key, user_input, system_prompt=sys_instruct)
                        
                        if reply:
                            st.chat_message("assistant").markdown(reply)
                            st.session_state.messages.append({"role": "assistant", "content": reply})