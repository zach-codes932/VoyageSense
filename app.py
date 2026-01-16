import streamlit as st
import pandas as pd
import time
from src.recommender import TravelRecommender
from src.llm_explainer import TravelLLMExplainer
from src.youtube_manager import YouTubeVlogManager

# Page Configuration
st.set_page_config(
    page_title="VoyageSense",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (UI POLISH ONLY)
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }

    /* ---------- Title ---------- */
    .big-font {
        font-size: 40px !important;
        font-weight: 800;
        color: #1F77B4;
        margin-bottom: 4px;
    }
    .sub-font {
        font-size: 24px !important;
        color: #D7DBDE;
        margin-top: 0px;
        margin-bottom: 35px;
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        padding-top: 18px;
    }

    [data-testid="stSidebar"] h1 {
        font-size: 22px !important;
        margin-bottom: 1px;
    }

    [data-testid="stSidebar"] label {
        font-size: 17px !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stRadio,
    [data-testid="stSidebar"] .stSlider {
        margin-bottom: 14px;
    }

    /* ---------- Buttons ---------- */
    .stButton>button {
        width: 100%;
        height: 48px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 700;
    }

    /* ---------- Recommendation Cards ---------- */
    .recommend-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 14px;
        margin-bottom: 26px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.06);
        border-left: 6px solid #1F77B4;
    }

    .recommend-meta {
        font-size: 16px;
        color: #B3B7BA;
        margin-bottom: 10px;
    }

    .recommend-explain {
        font-size: 15px;
        color: #A1A4A6; /* Darker than app2 for visibility */
        font-style: italic;
    }
    
    .colorful-separator {
        width: 100%;
        height: 2px !important;
        background: linear-gradient(90deg, #FF5F6D 0%, #FFC371 100%) !important;
        border-radius: 2px;
        margin: 25px 0 25px 0;
        border: none !important;
    }

    /* ---------- Profile Summary Card ---------- */
    .profile-summary {
        background-color: #F8F9FA;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 25px;
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: space-around;
        border: 1px solid #E9ECEF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .profile-item {
        font-size: 15px;
        font-weight: 600;
        color: #495057;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .profile-icon {
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'recommender' not in st.session_state:
    with st.spinner("Initializing VoyageSense Engine..."):
        st.session_state.recommender = TravelRecommender()
if 'explainer' not in st.session_state:
    st.session_state.explainer = TravelLLMExplainer()
if 'youtube' not in st.session_state:
    st.session_state.youtube = YouTubeVlogManager()
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

# --- Sidebar: User Profile ---
with st.sidebar:
    st.title("🪧 User Profile")

    st.markdown('<hr class="colorful-separator">', unsafe_allow_html=True)

    st.markdown("### 🧍 Travel Preferences")

    activity_type = st.selectbox(
        "Preferred Activity Type",
        ["Nature", "Heritage", "Adventure", "Religious", "Leisure"]
    )

    purpose = st.selectbox(
        "Travel Interest / Purpose",
        ["Relaxation", "Exploration", "Pilgrimage", "Family outing", "Photography"]
    )

    st.markdown("### ⏱️ Time & Budget")

    time_raw = st.radio(
        "Available Travel Time",
        ["1 Day", "2 Days", "3+ Days"]
    )

    duration_map = {"1 Day": "Short", "2 Days": "Medium", "3+ Days": "Long"}
    duration_bucket = duration_map[time_raw]

    budget_pref = st.select_slider(
        "Budget Preference",
        options=["Low", "Medium", "High"],
        value="Medium"
    )

    expected_cost = st.slider(
        "Maximum Budget (₹)",
        0, 50000, 10000, step=500
    )

    st.markdown("### 🌍 Location Preferences")

    current_region = st.selectbox(
        "Current Location / Region",
        ["North", "South", "East", "West", "Central"]
    )

    target_zone = st.selectbox(
        "Preferred Zone",
        ["Northern", "Southern", "Eastern", "Western", "NorthEastern", "Central"],
        index=1
    )

    st.markdown("### 🧠 Context")

    job_type = st.radio(
        "Job Type (Time Flexibility)",
        ["Fixed Schedule", "Flexible / Remote"]
    )

    job_backend = "Flexible" if "Flexible" in job_type else "Fixed Schedule"

    season = st.selectbox(
        "Preferred Travel Season",
        ["Any", "Summer", "Winter", "Monsoon"]
    )

    st.markdown("---")

    if st.button("🚀 Find My Destinations", type="primary"):

        profile = {
            "type": activity_type,
            "significance": purpose,
            "budget_bucket": budget_pref,
            "duration_bucket": duration_bucket,
            "zone": target_zone,
            "job_type": job_backend,
            "season": season,
            "current_region": current_region
        }

        if profile["type"] == "Heritage":
            profile["type"] = "Historical"
        if profile["type"] == "Leisure":
            profile["type"] = "Relaxation"

        st.session_state.user_profile = profile

        with st.spinner("Analyzing preferences & computing similarity scores..."):
            st.session_state.recommendations = (
                st.session_state.recommender.recommend(profile, top_n=5)
            )

# --- Main Content ---
st.markdown('<p class="big-font">🚞 VoyageSense</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-font">An Intelligent Travel Recommendation System</p>', unsafe_allow_html=True)

if st.session_state.recommendations is not None:
    # --- Profile Summary Card ---
    p = st.session_state.user_profile
    if p:
        st.markdown(f"""
        <div class="profile-summary">
            <div class="profile-item"><span class="profile-icon">🏔️</span> {p.get('type', 'Any')}</div>
            <div class="profile-item"><span class="profile-icon">⏳</span> {p.get('duration_bucket', 'Any')}</div>
            <div class="profile-item"><span class="profile-icon">💰</span> {p.get('budget_bucket', 'Any')}</div>
            <div class="profile-item"><span class="profile-icon">📍</span> {p.get('zone', 'Any')} Zone</div>
        </div>
        """, unsafe_allow_html=True)

    st.info("💡 Click on **View Details** to know more about the place and see travel vlogs.")

if st.session_state.recommendations is None:
    st.info("👈 Please configure your profile in the sidebar and click **Find My Destinations** to start.")
    st.image("https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2021&auto=format&fit=crop", caption="Where will you go next?")

else:
    recs = st.session_state.recommendations
    
    if recs.empty:
        st.warning("No destinations found matching your strict criteria. Try loosening the 'Job Type' or 'Budget' filters.")
    else:
        # Iterate over recommendations
        for index, row in recs.iterrows():
            with st.container():
                # Card Wrapper (Visual only, sidebar-border handled by CSS if wrapped, 
                # but we'll specific styling within columns for clean look)
                
                # Header: Name (App2 Style)
                st.markdown(f"### 📍 {row['name']}")
                
                # Layout: Info (Left) | Button (Right)
                col1, col2 = st.columns([3, 1])
                
                match_score = int(row['match_score'] * 100)
                
                with col1:
                    # Meta Data (App2 Style but with BOLD Location, Match, Rating)
                    st.markdown(
                        f"<div class='recommend-meta'>"
                        f"<b>Location:</b> {row['city']}, {row['state']} &nbsp;|&nbsp; "
                        f"<b>Match:</b> {match_score}% &nbsp;|&nbsp; "
                        f"<b>Rating:</b> {row['google_rating']} ⭐"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Explanation (App2 Style)
                    st.markdown(
                        f"<div class='recommend-explain'>{row['explanation']}</div>",
                        unsafe_allow_html=True
                    )
                    
                with col2:
                    # 'View Details' Button (App1 Position)
                    st.write("") # Slight spacer
                    if st.button(f"View Details 🔍", key=f"btn_{index}"):
                        st.session_state[f"show_details_{index}"] = not st.session_state.get(f"show_details_{index}", False)

                # --- Detail View (Collapsible) ---
                if st.session_state.get(f"show_details_{index}", False):
                    st.markdown('<hr style="border-top: 1px dashed #bbb;">', unsafe_allow_html=True) # Subtle inner separator
                    detail_col1, detail_col2 = st.columns([1, 1])
                    
                    with detail_col1:
                        st.markdown("### 🤖 VoyageSense Insight")
                        with st.spinner("Generating personalized narrative..."):
                            # Call Gemini API
                            narrative = st.session_state.explainer.generate_detailed_explanation(
                                row.to_dict(), st.session_state.user_profile
                            )
                            st.write(narrative)
                            
                        st.markdown("#### essentials")
                        st.write(f"- **Best Time:** {row.get('best_time_to_visit', 'All Year')}")
                        st.write(f"- **Time Needed:** {row.get('duration_bucket')}")
                        st.write(f"- **Est. Entry Fee:** ₹{row.get('entrance_fee', 0)}")
                        
                    with detail_col2:
                        st.markdown("### 🎥 Experience It")
                        with st.spinner("Finding vlogs..."):
                            # Call YouTube API
                            vlogs = st.session_state.youtube.search_vlogs(row['name'])
                            
                            if vlogs:
                                # Embed the first video (Top Result)
                                top_video = vlogs[0]
                                st.video(f"https://www.youtube.com/watch?v={top_video['video_id']}")
                                st.caption(f"Playing: {top_video['title']}")
                            else:
                                st.warning("No relevant vlogs found.")
                    st.info("Tip: Check local guidelines and weather before booking.")
                st.markdown('<hr class="colorful-separator">', unsafe_allow_html=True) # Colorful Separator
