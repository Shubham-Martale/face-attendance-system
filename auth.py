"""
auth.py
-------
Login / logout helpers for the Smart Attendance System.
Default credentials → username: admin  |  password: admin123
"""

import hashlib
import streamlit as st

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()


def _check_password(username: str, plain_password: str) -> bool:
    try:
        import database as db
        stored_hash = db.get_setting("admin_password_hash", DEFAULT_PASSWORD_HASH)
        stored_user = db.get_setting("admin_username", DEFAULT_USERNAME)
    except Exception:
        stored_hash = DEFAULT_PASSWORD_HASH
        stored_user = DEFAULT_USERNAME
    pwd_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return username == stored_user and pwd_hash == stored_hash


def is_logged_in() -> bool:
    return st.session_state.get("authenticated", False)


def login_page():
    """Render the centered, animated login page."""

    st.markdown("""
    <style>
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Remove all streamlit default padding so our layout fills screen ── */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1562774053-701939374585?w=1600&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }

    /* Dark blur overlay */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(8, 12, 24, 0.75);
        backdrop-filter: blur(3px);
        z-index: 0;
    }

    /* Push streamlit block container to fill full height */
    .block-container {
        padding: 0 !important;
        min-height: 100vh !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative;
        z-index: 1;
    }

    /* Column wrapper full height */
    [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* ── Animations ── */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(40px); }
        to   { opacity: 1; transform: translateY(0);    }
    }
    @keyframes pulse {
        0%,100% { box-shadow: 0 0 0 0 rgba(31,111,235,0.5); }
        50%      { box-shadow: 0 0 0 14px rgba(31,111,235,0);  }
    }
    @keyframes shimmer {
        0%   { background-position: -400px 0; }
        100% { background-position:  400px 0; }
    }
    @keyframes spin {
        from { transform: rotate(0deg);   }
        to   { transform: rotate(360deg); }
    }
    @keyframes iconBounce {
        0%,100% { transform: translateY(0);   }
        50%      { transform: translateY(-8px); }
    }

    /* ── Login card ── */
    .login-card {
        background: linear-gradient(145deg, rgba(22,27,39,0.95), rgba(13,17,23,0.98));
        border: 1px solid rgba(88,166,255,0.25);
        border-radius: 24px;
        padding: 44px 40px 36px 40px;
        width: 100%;
        max-width: 420px;
        box-shadow: 0 24px 80px rgba(0,0,0,0.7), 0 0 0 1px rgba(88,166,255,0.1);
        animation: fadeSlideUp 0.7s cubic-bezier(.23,1,.32,1) both;
        position: relative;
        overflow: hidden;
    }

    /* Shimmer top border */
    .login-card::before {
        content: "";
        position: absolute;
        top: 0; left: -100%;
        width: 300%;
        height: 2px;
        background: linear-gradient(90deg,
            transparent 0%,
            #58a6ff 40%,
            #a371f7 60%,
            transparent 100%);
        background-size: 400px 2px;
        animation: shimmer 2.5s linear infinite;
    }

    /* Icon circle */
    .login-icon {
        width: 80px; height: 80px;
        background: linear-gradient(135deg, #1f6feb, #9f7aea);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 2.2rem;
        margin: 0 auto 18px auto;
        animation: iconBounce 2.8s ease-in-out infinite, pulse 2.8s ease-in-out infinite;
        box-shadow: 0 8px 24px rgba(31,111,235,0.45);
    }

    .login-title {
        font-size: 1.7rem; font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #58a6ff, #a371f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        animation: fadeSlideUp 0.8s 0.15s both;
    }
    .login-sub {
        text-align: center; color: #8b949e;
        font-size: .85rem; margin-bottom: 28px;
        animation: fadeSlideUp 0.8s 0.25s both;
    }
    .login-label {
        color: #c9d1d9; font-size: .88rem;
        font-weight: 600; margin-bottom: 6px;
        display: block;
        animation: fadeSlideUp 0.8s 0.35s both;
    }

    /* Input fields */
    [data-testid="stTextInput"] input {
        background: rgba(13,17,23,0.9) !important;
        border: 1.5px solid rgba(88,166,255,0.35) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-size: .97rem !important;
        padding: 12px 14px !important;
        caret-color: #58a6ff !important;
        transition: border-color .25s, box-shadow .25s !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 3px rgba(88,166,255,0.18) !important;
        background: rgba(13,17,23,1) !important;
    }
    [data-testid="stTextInput"] input::placeholder { color: #484f58 !important; }
    [data-testid="stTextInput"] label {
        color: #c9d1d9 !important; font-weight: 600 !important;
        font-size: .88rem !important;
    }

    /* Login button */
    .stButton > button {
        background: linear-gradient(135deg, #1f6feb 0%, #9f7aea 100%) !important;
        color: #fff !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 1rem !important; padding: 13px !important;
        width: 100% !important;
        transition: opacity .2s, transform .2s !important;
        box-shadow: 0 4px 20px rgba(31,111,235,0.45) !important;
        animation: fadeSlideUp 0.8s 0.45s both;
    }
    .stButton > button:hover {
        opacity: .9 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(31,111,235,0.6) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* Error box */
    .login-error {
        background: rgba(61,0,0,0.85); border: 1px solid #f85149;
        border-radius: 10px; padding: 12px 16px;
        color: #f85149; font-weight: 600;
        font-size: .9rem; margin-top: 14px;
        animation: fadeSlideUp 0.4s both;
        text-align: center;
    }

    /* Hint text */
    .login-hint {
        text-align: center; color: #484f58;
        font-size: .76rem; margin-top: 18px;
        animation: fadeSlideUp 0.8s 0.55s both;
    }

    /* Floating particles */
    .particles { position:fixed; inset:0; z-index:0; pointer-events:none; overflow:hidden; }
    .particle {
        position: absolute; border-radius: 50%;
        background: rgba(88,166,255,0.15);
        animation: floatUp linear infinite;
    }
    @keyframes floatUp {
        from { transform: translateY(100vh) scale(0); opacity:0; }
        10%  { opacity: 1; }
        90%  { opacity: .4; }
        to   { transform: translateY(-10vh) scale(1); opacity:0; }
    }
    </style>

    <!-- Floating particles -->
    <div class="particles">
        <div class="particle" style="width:18px;height:18px;left:10%;animation-duration:9s;animation-delay:0s;"></div>
        <div class="particle" style="width:10px;height:10px;left:25%;animation-duration:12s;animation-delay:2s;"></div>
        <div class="particle" style="width:22px;height:22px;left:40%;animation-duration:8s;animation-delay:1s;"></div>
        <div class="particle" style="width:8px;height:8px;left:55%;animation-duration:14s;animation-delay:3s;"></div>
        <div class="particle" style="width:14px;height:14px;left:70%;animation-duration:10s;animation-delay:0.5s;"></div>
        <div class="particle" style="width:20px;height:20px;left:85%;animation-duration:11s;animation-delay:4s;"></div>
        <div class="particle" style="width:6px;height:6px;left:60%;animation-duration:7s;animation-delay:2.5s;"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Centered columns ───────────────────────────────────────────
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("""
        <div class="login-card">
            <div class="login-icon">🎓</div>
            <div class="login-title">Smart Attendance</div>
            <div class="login-sub">Face Recognition Attendance System</div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input(
            "👤  Username",
            placeholder="Enter admin username",
            key="login_username"
        )
        password = st.text_input(
            "🔒  Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
        login_clicked = st.button("🚀  Login to Dashboard", use_container_width=True)

        if st.session_state.get("login_error"):
            st.markdown("""
            <div class="login-error">
                ❌ Invalid username or password. Please try again.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="login-hint">
            Default &nbsp;·&nbsp;
            <span style="color:#58a6ff;">admin</span> / 
            <span style="color:#a371f7;">admin123</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Auth logic ─────────────────────────────────────────────────
    if login_clicked:
        if _check_password(username.strip(), password):
            st.session_state["authenticated"] = True
            st.session_state["admin_user"]    = username.strip()
            st.session_state["login_error"]   = False
            st.rerun()
        else:
            st.session_state["login_error"] = True
            st.rerun()


def logout():
    st.session_state["authenticated"] = False
    st.session_state["admin_user"]    = ""
    st.session_state["login_error"]   = False
    st.rerun()