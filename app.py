"""
app.py  (v3 - Premium Edition)
Pages: Login | Dashboard | Register | Mark Attendance | Student Profile |
       Analytics | ID Card | Timetable | Activity Log | Report | Manage | Settings
"""

import io, os
from datetime import date, timedelta, datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import database as db
import face_utils as fu
import auth
import report_utils as ru
import id_card_utils as ic

st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()
fu.ensure_dirs()

# ══════════════════════════════════════════════════════════════════
# PREMIUM CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }

.stApp {
    background: linear-gradient(160deg, #020b18 0%, #041428 40%, #071e3d 70%, #0a2550 100%);
    background-attachment: fixed;
    font-family: 'Inter', sans-serif !important;
    color: #e6edf3;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #58a6ff; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #080c14 100%) !important;
    border-right: 1px solid #161b27 !important;
}
[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebarNav"] { display: none; }

/* ── Sidebar Navigation Menu ── */

/* Container: vertical stack, no gap */
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
    padding: 0 6px !important;
}

/* Hide the actual radio circle completely */
[data-testid="stSidebar"] .stRadio [type="radio"],
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child,
[data-testid="stSidebar"] .stRadio span[data-baseweb="radio"],
[data-testid="stSidebar"] .stRadio .st-emotion-cache-q8sbsg,
[data-testid="stSidebar"] [role="radio"] > div:first-child {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
    position: absolute !important;
}

/* Each nav item label */
[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 9px 14px !important;
    margin: 0 !important;
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: #8b949e !important;
    font-size: .84rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all .18s ease !important;
    line-height: 1.4 !important;
    white-space: nowrap !important;
}

/* Hover state */
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,.05) !important;
    color: #e6edf3 !important;
    border-color: #21262d !important;
    padding-left: 18px !important;
}

/* paragraph inside label (the text node) */
[data-testid="stSidebar"] .stRadio label p,
[data-testid="stSidebar"] .stRadio label div {
    margin: 0 !important;
    padding: 0 !important;
    font-size: .84rem !important;
    color: inherit !important;
}

/* ── ACTIVE / SELECTED item ── */
[data-testid="stSidebar"] .stRadio label[aria-checked="true"],
[data-testid="stSidebar"] .stRadio [aria-checked="true"],
[data-testid="stSidebar"] .stRadio label:has(input:checked),
[data-testid="stSidebar"] div[role="radio"][aria-checked="true"] {
    background: linear-gradient(135deg,
        rgba(31,111,235,.22) 0%,
        rgba(124,58,237,.14) 100%) !important;
    color: #58a6ff !important;
    border-color: rgba(31,111,235,.35) !important;
    border-left: 3px solid #1f6feb !important;
    padding-left: 12px !important;
    font-weight: 700 !important;
}

/* Force selected label text to blue */
[data-testid="stSidebar"] .stRadio label[aria-checked="true"] p,
[data-testid="stSidebar"] .stRadio label[aria-checked="true"] div,
[data-testid="stSidebar"] .stRadio label[aria-checked="true"] span {
    color: #58a6ff !important;
}

/* ── All text white ── */
label, .stTextInput label, .stSelectbox label,
.stRadio label, .stFileUploader label,
.stSlider label, .stTimeInput label,
p, span, div { color: #e6edf3; }

/* ── Inputs ── */
input, textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #0d1117 !important;
    border: 1.5px solid #21262d !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .9rem !important;
    padding: 10px 14px !important;
    transition: border-color .2s, box-shadow .2s !important;
}
input:focus, textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,.15) !important;
    outline: none !important;
    color: #ffffff !important;
}
input::placeholder, textarea::placeholder { color: #484f58 !important; }

/* ── Select box ── */
[data-testid="stSelectbox"] > div > div {
    background: #0d1117 !important;
    border: 1.5px solid #21262d !important;
    color: #ffffff !important;
    border-radius: 10px !important;
}
[data-testid="stSelectbox"] svg { fill: #8b949e !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #0d1117 !important;
    border-radius: 10px 10px 0 0 !important;
    border-bottom: 2px solid #21262d !important;
    padding: 0 4px !important;
    gap: 2px !important;
}
[data-testid="stTabs"] button {
    color: #8b949e !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 18px !important;
    transition: all .2s !important;
    border: none !important;
    background: transparent !important;
}
[data-testid="stTabs"] button:hover { color: #e6edf3 !important; background: #161b27 !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #58a6ff !important;
    background: #161b27 !important;
    border-bottom: 2px solid #58a6ff !important;
    font-weight: 700 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: .9rem !important;
    padding: 10px 20px !important;
    transition: all .25s !important;
    box-shadow: 0 4px 15px rgba(31,111,235,.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(31,111,235,.5) !important;
    opacity: .93 !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Download buttons */
.stDownloadButton > button {
    background: linear-gradient(135deg,#238636,#2ea043) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    font-weight:600 !important;
    box-shadow: 0 4px 15px rgba(35,134,54,.3) !important;
    transition: all .25s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(35,134,54,.5) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #21262d !important;
}
[data-testid="stDataFrame"] th {
    background: #161b27 !important;
    color: #8b949e !important;
    font-weight: 600 !important;
    font-size: .82rem !important;
    text-transform: uppercase !important;
    letter-spacing: .05em !important;
}
[data-testid="stDataFrame"] td {
    color: #e6edf3 !important;
    background: #0d1117 !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg,#0d1117 0%,#161b27 100%);
    border: 1px solid #21262d;
    border-radius: 16px;
    padding: 24px 20px 20px 20px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,.4);
    transition: all .3s cubic-bezier(.4,0,.2,1);
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content:'';
    position:absolute; top:0; left:0; right:0; height:3px;
    border-radius:16px 16px 0 0;
}
.kpi-card.blue::before  { background: linear-gradient(90deg,#1f6feb,#58a6ff); }
.kpi-card.green::before { background: linear-gradient(90deg,#238636,#3fb950); }
.kpi-card.red::before   { background: linear-gradient(90deg,#8b1a1a,#f85149); }
.kpi-card.orange::before{ background: linear-gradient(90deg,#7d4e00,#d29922); }
.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0,0,0,.5);
    border-color: #30363d;
}
.kpi-num   { font-size: 2.6rem; font-weight: 900; letter-spacing:-.02em; line-height:1; }
.kpi-label { font-size: .82rem; color: #8b949e; margin-top: 8px; font-weight:500; text-transform:uppercase; letter-spacing:.06em; }
.kpi-icon  { font-size: 1.4rem; margin-bottom: 8px; }
.c-blue   { color: #58a6ff; }
.c-green  { color: #3fb950; }
.c-red    { color: #f85149; }
.c-orange { color: #d29922; }
.c-purple { color: #bc8cff; }

/* ── Top Bar ── */
.top-bar {
    background: linear-gradient(135deg,#1f6feb 0%,#7c3aed 100%);
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(31,111,235,.25);
    position: relative;
    overflow: hidden;
}
.top-bar::after {
    content:'';
    position:absolute; top:-40%; right:-5%;
    width:300px; height:300px;
    background:rgba(255,255,255,.04);
    border-radius:50%;
}
.top-bar-title { font-size:1.5rem; font-weight:800; color:#fff; letter-spacing:-.02em; }
.top-bar-sub   { font-size:.85rem; color:rgba(255,255,255,.7); margin-top:3px; }
.top-bar-meta  { color:rgba(255,255,255,.75); font-size:.85rem; font-weight:500; z-index:1; }

/* ── Section Header ── */
.sec-hdr {
    font-size: 1rem; font-weight: 700; color: #e6edf3;
    border-left: 3px solid #1f6feb;
    padding: 4px 0 4px 12px;
    margin: 20px 0 12px 0;
    letter-spacing: .01em;
}

/* ── Glass card ── */
.glass-card {
    background: rgba(22,27,43,.7);
    border: 1px solid #21262d;
    border-radius: 14px;
    padding: 20px;
    backdrop-filter: blur(10px);
}

/* ── Alerts ── */
.alert-success {
    background: linear-gradient(135deg,#0d4429,#0a3320);
    border: 1px solid #238636; border-left: 4px solid #3fb950;
    border-radius: 10px; padding: 14px 18px;
    color: #3fb950; font-weight: 600; font-size: .92rem;
    animation: slideIn .3s ease;
}
.alert-error {
    background: linear-gradient(135deg,#3d0000,#2d0000);
    border: 1px solid #8b1a1a; border-left: 4px solid #f85149;
    border-radius: 10px; padding: 14px 18px;
    color: #f85149; font-weight: 600; font-size: .92rem;
    animation: slideIn .3s ease;
}
.alert-info {
    background: linear-gradient(135deg,#0c2a4a,#091e35);
    border: 1px solid #1f6feb; border-left: 4px solid #58a6ff;
    border-radius: 10px; padding: 14px 18px;
    color: #58a6ff; font-weight: 600; font-size: .92rem;
    animation: slideIn .3s ease;
}
.alert-warning {
    background: linear-gradient(135deg,#3d2000,#2d1800);
    border: 1px solid #7d4e00; border-left: 4px solid #d29922;
    border-radius: 10px; padding: 14px 18px;
    color: #d29922; font-weight: 600; font-size: .92rem;
}
@keyframes slideIn { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }

/* ── Badge ── */
.badge {
    display:inline-block; border-radius:20px;
    padding:3px 12px; font-size:.75rem; font-weight:700;
    letter-spacing:.04em; text-transform:uppercase;
}
.bdg-present { background:#0d4429; color:#3fb950; border:1px solid #238636; }
.bdg-late    { background:#3d2000; color:#d29922; border:1px solid #7d4e00; }
.bdg-absent  { background:#3d0000; color:#f85149; border:1px solid #8b1a1a; }
.bdg-blue    { background:#0c2a4a; color:#58a6ff; border:1px solid #1f6feb; }

/* ── Progress bar ── */
.prog-wrap   { background:#21262d; border-radius:10px; height:8px; margin:6px 0; overflow:hidden; }
.prog-fill   { height:8px; border-radius:10px; transition:width .6s ease; }
.prog-blue   { background:linear-gradient(90deg,#1f6feb,#58a6ff); }
.prog-green  { background:linear-gradient(90deg,#238636,#3fb950); }
.prog-orange { background:linear-gradient(90deg,#7d4e00,#d29922); }

/* ── Stat row ── */
.stat-row {
    display:flex; gap:12px; margin-top:12px;
}
.stat-item { flex:1; background:#0d1117; border-radius:10px; padding:12px; text-align:center; border:1px solid #21262d; }
.stat-val  { font-size:1.3rem; font-weight:800; }
.stat-lbl  { font-size:.72rem; color:#8b949e; margin-top:2px; text-transform:uppercase; letter-spacing:.05em; }

/* ── Log entry ── */
.log-entry {
    display:flex; align-items:flex-start; gap:14px;
    padding:12px 0; border-bottom:1px solid #161b27;
}
.log-dot {
    width:10px; height:10px; border-radius:50%;
    margin-top:5px; flex-shrink:0;
}
.log-time  { font-size:.78rem; color:#8b949e; white-space:nowrap; }
.log-actor { font-size:.85rem; font-weight:700; color:#58a6ff; }
.log-action{ font-size:.88rem; color:#e6edf3; font-weight:500; }
.log-detail{ font-size:.78rem; color:#8b949e; margin-top:1px; }

/* ── Timetable cell ── */
.tt-cell {
    background:#161b27; border:1px solid #21262d; border-radius:8px;
    padding:10px 12px; font-size:.82rem; color:#e6edf3;
    border-left:3px solid #1f6feb;
}
.tt-subject { font-weight:700; color:#58a6ff; }
.tt-meta    { color:#8b949e; font-size:.75rem; margin-top:2px; }

/* ── Spinner ── */
.stSpinner > div { border-top-color:#58a6ff !important; }
</style>
""", unsafe_allow_html=True)


# ── Auth Gate ──────────────────────────────────────────────────────
if not auth.is_logged_in():
    auth.login_page()
    st.stop()

admin_user = st.session_state.get("admin_user", "Admin")

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:24px 0 20px;">
        <div style="font-size:2.8rem;line-height:1;">🎓</div>
        <div style="font-weight:800;font-size:1.1rem;color:#58a6ff;margin-top:8px;
                    letter-spacing:-.02em;">Smart Attendance</div>
        <div style="font-size:.72rem;color:#8b949e;margin-top:3px;">Face Recognition System</div>
        <div style="margin-top:12px;background:#161b27;border:1px solid #21262d;
                    border-radius:20px;padding:5px 14px;display:inline-block;
                    font-size:.75rem;color:#3fb950;font-weight:600;">
            ● Online
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #161b27;margin:0 0 10px 0;">
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "🏠  Dashboard",
        "➕  Register Student",
        "📷  Mark Attendance",
        "✋  Manual Attendance",
        "👤  Student Profile",
        "📊  Analytics",
        "🗓️  Calendar Heatmap",
        "🖼️  Student Gallery",
        "⚠️  Low Attendance",
        "📈  Class Summary",
        "🪪  ID Card Generator",
        "📅  Timetable",
        "📜  Certificates",
        "🔔  Absent Students",
        "📝  Activity Log",
        "📋  Attendance Report",
        "👥  Manage Students",
        "💾  Backup & Restore",
        "⚙️   Settings",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border:none;border-top:1px solid #161b27;margin:10px 0;'>", unsafe_allow_html=True)
    total_s, present_s, absent_s, late_s = db.get_today_stats()
    st.markdown(f"""
    <div style="font-size:.78rem;color:#8b949e;text-align:center;padding:4px 0 12px;">
        <div style="font-weight:600;color:#e6edf3;margin-bottom:6px;">
            {date.today().strftime('%A, %d %b')}
        </div>
        <span style="color:#3fb950">● {present_s}</span> &nbsp;
        <span style="color:#f85149">● {absent_s}</span> &nbsp;
        <span style="color:#d29922">● {late_s} Late</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪  Logout", use_container_width=True):
        db.log_activity(admin_user, "Logout", "Admin logged out")
        auth.logout()


def top_bar(icon, title, subtitle=""):
    now = datetime.now().strftime("%I:%M %p")
    st.markdown(f"""
    <div class="top-bar">
        <div>
            <div class="top-bar-title">{icon} {title}</div>
            <div class="top-bar-sub">{subtitle}</div>
        </div>
        <div class="top-bar-meta">
            👤 {admin_user} &nbsp;·&nbsp; 🕐 {now} &nbsp;·&nbsp;
            {date.today().strftime('%d %B %Y')}
        </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(icon, num, label, color="blue"):
    return f"""<div class="kpi-card {color}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-num c-{color}">{num}</div>
        <div class="kpi-label">{label}</div>
    </div>"""


def alert(msg, kind="info"):
    st.markdown(f'<div class="alert-{kind}">{msg}</div>', unsafe_allow_html=True)


def sec(title):
    st.markdown(f'<div class="sec-hdr">{title}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# 1 · DASHBOARD 2.0
# ══════════════════════════════════════════════════════════════════
if "Dashboard" in page:
    top_bar("📊", "Admin Dashboard", "Real-time attendance overview")

    total, present, absent, late = db.get_today_stats()
    rate = round(present / total * 100, 1) if total else 0
    this_week, last_week = db.get_weekly_comparison()
    week_diff = this_week - last_week
    week_arrow = "↑" if week_diff >= 0 else "↓"
    week_color = "#3fb950" if week_diff >= 0 else "#f85149"

    # ── KPI Row ──
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi_card("🎓", total,        "Total Students",   "blue"),   unsafe_allow_html=True)
    c2.markdown(kpi_card("✅", present,      "Present Today",    "green"),  unsafe_allow_html=True)
    c3.markdown(kpi_card("❌", absent,       "Absent Today",     "red"),    unsafe_allow_html=True)
    c4.markdown(kpi_card("⚠️", late,         "Late Arrivals",    "orange"), unsafe_allow_html=True)
    c5.markdown(kpi_card("📈", f"{rate}%",  "Attendance Rate",  "blue"),   unsafe_allow_html=True)

    # ── Low attendance banner ──
    summary = db.get_all_student_attendance_summary()
    low_att  = [s for s in summary if s[3] > 0 and round(s[3]/max(s[3],1)*100) < 75]
    if low_att:
        names_str = ", ".join([s[1] for s in low_att[:4]])
        more = f" +{len(low_att)-4} more" if len(low_att) > 4 else ""
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#3d1a00,#2d1000);
             border:1px solid #7d4e00;border-left:4px solid #d29922;
             border-radius:10px;padding:12px 18px;margin:10px 0;
             display:flex;align-items:center;gap:12px;animation:slideIn .3s ease;">
            <span style="font-size:1.3rem;">⚠️</span>
            <div>
                <span style="color:#d29922;font-weight:700;">Low Attendance Alert: </span>
                <span style="color:#e6edf3;font-size:.88rem;">{names_str}{more}</span>
                <span style="color:#8b949e;font-size:.8rem;"> — below 75% threshold</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Main content ──
    left, mid, right = st.columns([2.2, 1.5, 1.3])

    with left:
        sec("📅 7-Day Attendance Trend")
        trend = db.get_weekly_trend()
        if trend:
            df_t = pd.DataFrame(trend, columns=["Date","Count"])
            fig = px.area(df_t, x="Date", y="Count",
                          color_discrete_sequence=["#1f6feb"], template="plotly_dark")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,17,23,.6)",
                margin=dict(l=0,r=0,t=10,b=0), height=190,
                font=dict(family="Inter", color="#8b949e"),
                xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
            )
            fig.update_traces(fillcolor="rgba(31,111,235,.15)", line_width=2.5)
            st.plotly_chart(fig, use_container_width=True)
        else:
            alert("Mark attendance to see trend data.", "info")

    with mid:
        sec("🏢 Departments")
        dept_data = db.get_department_stats()
        if dept_data:
            df_d = pd.DataFrame(dept_data, columns=["Dept","Total","Present"])
            df_d["Dept"] = df_d["Dept"].fillna("Unassigned")
            fig2 = px.pie(df_d, names="Dept", values="Total", hole=0.6,
                          color_discrete_sequence=["#1f6feb","#3fb950","#d29922","#bc8cff","#f85149"],
                          template="plotly_dark")
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0),
                height=190, font=dict(family="Inter", color="#8b949e"),
                showlegend=False,
                annotations=[dict(text=f"<b>{total}</b><br><span style='font-size:10'>Students</span>",
                                  x=0.5,y=0.5,showarrow=False,
                                  font=dict(size=13,color="#e6edf3"))]
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            alert("No dept. data.", "info")

    with right:
        sec("📊 This Week")
        st.markdown(f"""
        <div class="glass-card" style="padding:16px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">This Week</div>
                    <div style="font-size:1.8rem;font-weight:900;color:#58a6ff;">{this_week}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">Last Week</div>
                    <div style="font-size:1.8rem;font-weight:900;color:#8b949e;">{last_week}</div>
                </div>
            </div>
            <div class="prog-wrap" style="margin:12px 0 6px;">
                <div class="prog-fill prog-blue" style="width:{min(this_week/max(last_week,1)*100,100):.0f}%;"></div>
            </div>
            <div style="font-size:.82rem;font-weight:700;color:{week_color};">
                {week_arrow} {abs(week_diff)} records vs last week
            </div>
        </div>
        """, unsafe_allow_html=True)

        sec("📚 Today's Classes")
        today_tt = db.get_today_timetable()
        if today_tt:
            tt_html = ""
            now_hm = datetime.now().strftime("%H:%M")
            for ts, subj, teacher, room in today_tt:
                # Highlight current class
                is_now = ts[:5] <= now_hm <= (ts[-5:] if len(ts) > 5 else "23:59")
                border = "#3fb950" if is_now else "#1f6feb"
                badge  = " <span style='background:#0d4429;color:#3fb950;font-size:.7rem;padding:1px 7px;border-radius:10px;'>NOW</span>" if is_now else ""
                tt_html += f"""
                <div style="border-left:3px solid {border};padding:7px 10px;margin:4px 0;
                     background:rgba(255,255,255,.03);border-radius:0 6px 6px 0;">
                    <div style="font-size:.82rem;font-weight:700;color:#e6edf3;">{subj}{badge}</div>
                    <div style="font-size:.73rem;color:#8b949e;">🕐 {ts} &nbsp; 🏫 {room or '—'}</div>
                </div>"""
            st.markdown(tt_html, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#8b949e;font-size:.82rem;padding:8px 0;'>No classes scheduled.<br>Add via Timetable page.</div>", unsafe_allow_html=True)

    # ── Bottom row ──
    b1, b2 = st.columns([3, 2])
    with b1:
        sec("✅ Today's Live Attendance")
        rows = db.get_attendance_by_date()
        if rows:
            df_td = pd.DataFrame(rows, columns=["ID","Name","Date","Time","Subject","Status","IsLate","Conf"])
            df_td["Status"] = df_td.apply(lambda r:"⚠️ Late" if r["IsLate"] else "✅ Present", axis=1)
            df_td["Match"]  = df_td["Conf"].apply(lambda x:f"{round((1-float(x))*100,1)}%" if x else "—")
            st.dataframe(df_td[["ID","Name","Time","Subject","Status","Match"]],
                         use_container_width=True, height=220)
        else:
            alert("No attendance marked yet today.", "info")

    with b2:
        sec("🏆 Top Attendees")
        if summary:
            top5 = summary[:5]
            for rank, (sid, name, dept, days, last) in enumerate(top5, 1):
                medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][rank-1]
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:7px 0;
                     border-bottom:1px solid #161b27;">
                    <span style="font-size:1.1rem;">{medal}</span>
                    <div style="flex:1;">
                        <div style="font-size:.88rem;font-weight:600;color:#e6edf3;">{name}</div>
                        <div style="font-size:.75rem;color:#8b949e;">{dept or '—'}</div>
                    </div>
                    <span style="font-size:.85rem;font-weight:700;color:#3fb950;">{days}d</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            alert("No data yet.", "info")


# ══════════════════════════════════════════════════════════════════
# 2 · REGISTER STUDENT
# ══════════════════════════════════════════════════════════════════
elif "Register" in page:
    top_bar("➕", "Register Student", "Enroll a new student's face into the system")
    tab1, tab2 = st.tabs(["📷  Single Registration", "📂  Bulk CSV Import"])

    with tab1:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            with st.form("reg_form"):
                sec("Student Information")
                r1, r2 = st.columns(2)
                sid  = r1.text_input("Student ID *", placeholder="e.g. STU001")
                name = r2.text_input("Full Name *",  placeholder="e.g. Arjun Sharma")
                r3, r4 = st.columns(2)
                dept  = r3.text_input("Department",  placeholder="e.g. Computer Science")
                email = r4.text_input("Email",       placeholder="e.g. arjun@college.edu")
                sec("Face Photo")
                mode = st.radio("Source", ["📷 Camera","🖼️ Upload"], horizontal=True)
                img_f = st.camera_input("Capture") if "Camera" in mode else \
                        st.file_uploader("Upload", type=["jpg","jpeg","png"])
                submitted = st.form_submit_button("✅  Register Student", use_container_width=True)

        with c2:
            st.markdown("""
            <div class="glass-card" style="margin-top:0;">
                <div style="font-weight:700;color:#58a6ff;margin-bottom:12px;">📋 Guidelines</div>
                <div style="font-size:.85rem;color:#8b949e;line-height:2;">
                ✅ Use <b style="color:#e6edf3">even, bright lighting</b><br>
                ✅ Face camera <b style="color:#e6edf3">directly</b><br>
                ✅ Keep face <b style="color:#e6edf3">centred</b> in frame<br>
                ✅ Remove sunglasses / mask<br>
                ✅ Neutral expression<br>
                ✅ High-quality, clear photo<br>
                </div>
                <div style="margin-top:16px;padding:10px 14px;background:#0c2a4a;border-radius:8px;
                     font-size:.8rem;color:#58a6ff;border:1px solid #1f6feb33;">
                    ⚡ First recognition takes 30–60 s (model download)
                </div>
            </div>
            """, unsafe_allow_html=True)

        if submitted:
            if not sid or not name:
                alert("❌ Student ID and Name are required.", "error")
            elif db.student_exists(sid):
                alert(f"❌ Student ID '{sid}' already exists.", "error")
            elif img_f is None:
                alert("❌ Please capture or upload a photo.", "error")
            else:
                img_bgr = fu.bytes_to_bgr(img_f.getvalue())
                with st.spinner("🔍 Detecting face…"):
                    face_crop, box = fu.detect_face(img_bgr)
                if face_crop is None:
                    alert("❌ No face detected. Try better lighting.", "error")
                else:
                    path = fu.save_face_image(sid, img_bgr)
                    db.add_student(sid, name, dept, email, path)
                    db.log_activity(admin_user, "Register Student", f"{name} ({sid})")
                    alert(f"✅ {name} ({sid}) registered successfully!", "success")
                    preview = fu.draw_box(img_bgr.copy(), box, label=name)
                    st.image(preview, channels="BGR", width=300)

    with tab2:
        sec("Bulk Import via CSV")
        st.markdown("""
        <div class="glass-card" style="font-size:.85rem;color:#8b949e;">
            Required columns: <b style="color:#58a6ff">student_id, name, department, email</b><br>
            Note: Bulk import adds student info; face photos must be added individually.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        csv_f = st.file_uploader("Upload CSV", type=["csv"])
        if csv_f:
            df_csv = pd.read_csv(csv_f)
            st.dataframe(df_csv.head(), use_container_width=True)
            if st.button("📥  Import Students"):
                recs = []
                for _, row in df_csv.iterrows():
                    s = str(row.get("student_id","")).strip()
                    n = str(row.get("name","")).strip()
                    d = str(row.get("department","")).strip()
                    e = str(row.get("email","")).strip()
                    ph = os.path.join(fu.KNOWN_FACES_DIR, f"{s}.jpg")
                    if s and n:
                        recs.append((s, n, d, e, ph))
                added, skipped = db.bulk_add_students(recs)
                db.log_activity(admin_user, "Bulk Import", f"Added:{added} Skipped:{skipped}")
                alert(f"✅ Added: {added}  |  Skipped (duplicate): {skipped}", "success")


# ══════════════════════════════════════════════════════════════════
# 3 · MARK ATTENDANCE
# ══════════════════════════════════════════════════════════════════
elif "Mark Attendance" in page:
    top_bar("📷", "Mark Attendance", "Capture face to automatically log attendance")

    students = db.get_all_students()
    if not students:
        alert("No students registered. Please register students first.", "error")
    else:
        subjects = db.get_subjects()
        late_thr = db.get_setting("late_threshold","09:30")
        c1, c2 = st.columns([1.4, 1])
        with c1:
            subj = st.selectbox("📚 Select Subject", subjects)
            img_f = st.camera_input("📸 Look at the camera and capture")
        with c2:
            now_t = datetime.now().strftime("%H:%M:%S")
            is_late_now = now_t > late_thr + ":00"
            st.markdown(f"""
            <div class="glass-card" style="margin-top:36px;">
                <div style="font-weight:700;color:#e6edf3;margin-bottom:14px;">ℹ️ Session Info</div>
                <div style="font-size:.88rem;line-height:2.1;color:#8b949e;">
                    📚 Subject: <b style="color:#58a6ff">{subj}</b><br>
                    🕐 Current Time: <b style="color:#e6edf3">{now_t}</b><br>
                    ⏰ Late After: <b style="color:#d29922">{late_thr}</b><br>
                    📌 Status: <b style="color:{'#f85149' if is_late_now else '#3fb950'}">
                        {'⚠️ LATE Period' if is_late_now else '✅ On Time'}</b><br>
                    👥 Registered: <b style="color:#3fb950">{len(students)}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if img_f:
            img_bgr = fu.bytes_to_bgr(img_f.getvalue())
            with st.spinner("🔍 Recognizing face…"):
                face_crop, box = fu.detect_face(img_bgr)
            if face_crop is None:
                alert("❌ No face detected. Check lighting and angle.", "error")
            else:
                sid, distance = fu.recognize_face(img_bgr)
                if sid is None:
                    alert("❌ Face not recognized. Student may not be enrolled.", "error")
                    st.image(fu.draw_box(img_bgr.copy(), box, "Unknown"), channels="BGR", width=350)
                else:
                    s_row = next((s for s in students if s[0] == sid), None)
                    s_name = s_row[1] if s_row else sid
                    conf = round(max(0.0, 1 - distance) * 100, 1)
                    if db.already_marked_today(sid, subj):
                        alert(f"ℹ️ {s_name} ({sid}) already marked for {subj} today.", "info")
                    else:
                        marked, is_late = db.mark_attendance(sid, s_name, subj, round(distance,4))
                        db.log_activity(admin_user, "Mark Attendance",
                                        f"{s_name} ({sid}) — {subj} — {'Late' if is_late else 'On Time'}")
                        if is_late:
                            alert(f"⚠️ {s_name} marked LATE for {subj} (after {late_thr})", "warning")
                        else:
                            alert(f"✅ Attendance marked — {s_name} ({sid}) · {subj}", "success")
                    st.markdown(f"""
                    <div class="glass-card" style="margin-top:12px;font-size:.88rem;">
                        🎯 Match: <b style="color:#3fb950">{conf}%</b> &nbsp;·&nbsp;
                        🆔 <b>{sid}</b> &nbsp;·&nbsp; 👤 <b>{s_name}</b>
                    </div>
                    """, unsafe_allow_html=True)
                    preview = fu.draw_box(img_bgr.copy(), box, f"{s_name} ({conf}%)")
                    st.image(preview, channels="BGR", width=350)


# ══════════════════════════════════════════════════════════════════
# 4 · STUDENT PROFILE
# ══════════════════════════════════════════════════════════════════
elif "Profile" in page:
    top_bar("👤", "Student Profile", "Individual attendance history & statistics")
    students = db.get_all_students()
    if not students:
        alert("No students registered yet.", "info")
    else:
        opts    = {f"{s[1]}  ({s[0]})": s[0] for s in students}
        sel     = st.selectbox("🔍 Search Student", list(opts.keys()))
        sid     = opts[sel]
        sd      = next(s for s in students if s[0] == sid)  # sd = student data
        records  = db.get_student_attendance(sid)
        late_cnt = sum(1 for r in records if r[4] == 1)
        subjs    = list({r[2] for r in records})
        pct      = round(len(records) / max(len(records), 1) * 100, 1) if records else 0

        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            img_p = sd[4]
            if os.path.exists(img_p):
                st.image(img_p, width=130)
            else:
                st.markdown(
                    '<div style="width:130px;height:130px;background:#161b27;'
                    'border-radius:50%;display:flex;align-items:center;'
                    'justify-content:center;font-size:2.5rem;'
                    'border:3px solid #21262d;">👤</div>',
                    unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:1.25rem;font-weight:800;color:#e6edf3;">{sd[1]}</div>
                <div style="margin-top:4px;"><span class="badge bdg-blue">{sd[0]}</span></div>
                <div style="color:#58a6ff;font-weight:600;margin-top:8px;">{sd[2] or 'No Department'}</div>
                <div style="font-size:.82rem;color:#8b949e;margin-top:8px;line-height:1.9;">
                    📧 {sd[3] or '—'}<br>
                    📅 Enrolled: {str(sd[5])[:10]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            fill = min(pct, 100)
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:.82rem;color:#8b949e;font-weight:600;
                          text-transform:uppercase;letter-spacing:.06em;">Attendance Rate</span>
                    <span style="font-size:1.1rem;font-weight:800;color:#3fb950;">{pct}%</span>
                </div>
                <div class="prog-wrap">
                    <div class="prog-fill prog-green" style="width:{fill}%;"></div>
                </div>
                <div class="stat-row" style="margin-top:14px;">
                    <div class="stat-item">
                        <div class="stat-val c-green">{len(records)}</div>
                        <div class="stat-lbl">Days Present</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-val c-orange">{late_cnt}</div>
                        <div class="stat-lbl">Late</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-val c-blue">{len(subjs)}</div>
                        <div class="stat-lbl">Subjects</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        sec("📅 Attendance History")
        if records:
            df_p = pd.DataFrame(
                records, columns=["Date","Time","Subject","Status","IsLate","Conf"])
            df_p["Status"] = df_p["IsLate"].apply(
                lambda x: "⚠️ Late" if x else "✅ Present")
            df_p["Match"] = df_p["Conf"].apply(
                lambda x: f"{round((1-float(x))*100,1)}%" if x else "—")
            st.dataframe(df_p[["Date","Time","Subject","Status","Match"]],
                         use_container_width=True, height=260)
            fig = px.bar(
                df_p.groupby("Subject").size().reset_index(name="Days"),
                x="Subject", y="Days",
                color="Days", color_continuous_scale="Blues",
                template="plotly_dark", title="Attendance by Subject")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,17,23,.6)",
                margin=dict(l=0,r=0,t=40,b=0), height=200,
                font=dict(family="Inter", color="#8b949e"),
                coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            alert("No attendance records yet for this student.", "info")


# ══════════════════════════════════════════════════════════════════
# 5 · ANALYTICS
# ══════════════════════════════════════════════════════════════════
elif "Analytics" in page:
    top_bar("📊", "Analytics", "Deep attendance insights and trends")
    total, present, absent, late = db.get_today_stats()

    c1, c2 = st.columns(2)
    with c1:
        sec("🍩 Today's Split")
        if total:
            fig = go.Figure(go.Pie(
                labels=["On Time","Late","Absent"],
                values=[max(present-late,0), late, absent],
                hole=0.6,
                marker_colors=["#3fb950","#d29922","#f85149"],
                textfont=dict(family="Inter",size=12),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter",color="#8b949e"),
                margin=dict(l=0,r=0,t=20,b=0), height=260,
                legend=dict(font=dict(size=11)),
                annotations=[dict(text=f"<b>{round(present/total*100)}%</b>",
                                  x=0.5,y=0.5,font_size=20,showarrow=False,
                                  font=dict(color="#e6edf3",family="Inter"))]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            alert("No data.", "info")

    with c2:
        sec("🏢 Department Attendance")
        dept = db.get_department_stats()
        if dept:
            df_d = pd.DataFrame(dept, columns=["Dept","Total","Present"])
            df_d["Dept"]   = df_d["Dept"].fillna("Unassigned")
            df_d["Absent"] = df_d["Total"] - df_d["Present"]
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name="Present",x=df_d["Dept"],y=df_d["Present"],marker_color="#3fb950"))
            fig2.add_trace(go.Bar(name="Absent", x=df_d["Dept"],y=df_d["Absent"], marker_color="#f85149"))
            fig2.update_layout(barmode="stack",template="plotly_dark",
                               paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,17,23,.6)",
                               margin=dict(l=0,r=0,t=20,b=0),height=260,
                               font=dict(family="Inter",color="#8b949e"),
                               xaxis=dict(gridcolor="#21262d"),yaxis=dict(gridcolor="#21262d"))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            alert("No data.", "info")

    sec("📈 30-Day Trend")
    s30 = (date.today()-timedelta(days=29)).strftime("%Y-%m-%d")
    e30 = date.today().strftime("%Y-%m-%d")
    r30 = db.get_attendance_range(s30,e30)
    if r30:
        df30 = pd.DataFrame(r30,columns=["SID","Name","Date","Time","Subject","Status","IsLate","Conf"])
        t30  = df30.groupby("Date").size().reset_index(name="Count")
        fig3 = px.line(t30, x="Date", y="Count", markers=True,
                       color_discrete_sequence=["#58a6ff"], template="plotly_dark")
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,17,23,.6)",
                           margin=dict(l=0,r=0,t=10,b=0), height=200,
                           font=dict(family="Inter",color="#8b949e"),
                           xaxis=dict(gridcolor="#21262d"),yaxis=dict(gridcolor="#21262d"))
        fig3.update_traces(line_width=2.5, marker_size=6)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        alert("Not enough data for 30-day trend.", "info")

    sec("🏆 Top Attendees")
    all_r = db.get_attendance_range("2000-01-01", date.today().strftime("%Y-%m-%d"))
    if all_r:
        dfa = pd.DataFrame(all_r,columns=["SID","Name","Date","Time","Subject","Status","IsLate","Conf"])
        top = dfa.groupby(["SID","Name"]).size().reset_index(name="Days").sort_values("Days",ascending=False).head(10)
        fig4 = px.bar(top, x="Name", y="Days", color="Days",
                      color_continuous_scale=["#1f6feb","#3fb950"],
                      template="plotly_dark")
        fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,17,23,.6)",
                           margin=dict(l=0,r=0,t=10,b=0), height=220,
                           font=dict(family="Inter",color="#8b949e"), coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        alert("No data.", "info")


# ══════════════════════════════════════════════════════════════════
# 6 · ID CARD GENERATOR  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "ID Card" in page:
    top_bar("🪪", "ID Card Generator", "MGM College style student identity card with photo & QR code")
    students = db.get_all_students()
    if not students:
        alert("No students registered yet.", "info")
    else:
        # ── keep custom photo in session state ──
        if "id_card_photo_bytes" not in st.session_state:
            st.session_state.id_card_photo_bytes = None

        c1, c2 = st.columns([1, 1.6])

        with c1:
            sec("Student Details")
            opts  = {f"{s[1]} ({s[0]})": s[0] for s in students}
            sel   = st.selectbox("Select Student", list(opts.keys()),
                                 label_visibility="collapsed")
            sid   = opts[sel]
            s_row = next(s for s in students if s[0] == sid)

            college = st.text_input("College Name",
                value="Mahatma Gandhi Mission's College of Computer Science & IT")
            address = st.text_input("Address",
                placeholder="At Post Barul, Tq Kandhar, Nanded")
            r1, r2 = st.columns(2)
            dob    = r1.text_input("Date of Birth", placeholder="9/4/2005")
            blood  = r2.text_input("Blood Group",   placeholder="B+")
            r3, r4 = st.columns(2)
            contact= r3.text_input("Contact No.",
                placeholder="9876543210", value=s_row[3] or "")
            year   = r4.text_input("Academic Year", value="2025-26")

            # Photo upload (optional — overrides registered photo)
            sec("📸 Photo (Optional Upload)")
            st.caption("Upload a new photo, or leave blank to use registered photo.")
            uploaded_photo = st.file_uploader(
                "Upload Photo", type=["jpg","jpeg","png"],
                label_visibility="collapsed")
            if uploaded_photo:
                st.session_state.id_card_photo_bytes = uploaded_photo.read()
                st.image(st.session_state.id_card_photo_bytes, width=100,
                         caption="Uploaded photo")
            elif st.button("🗑️ Clear uploaded photo", use_container_width=False):
                st.session_state.id_card_photo_bytes = None

            extra = {"address": address, "dob": dob,
                     "blood_group": blood, "contact": contact, "year": year}

            st.markdown("<br>", unsafe_allow_html=True)
            bf, bb = st.columns(2)
            gen_front = bf.button("🪪 Front Side", use_container_width=True)
            gen_back  = bb.button("🔄 Back Side",  use_container_width=True)

        with c2:
            sec("Preview")

            # Resolve photo path: use uploaded bytes OR registered file
            def get_photo_path():
                if st.session_state.id_card_photo_bytes:
                    import tempfile, pathlib
                    tmp = tempfile.NamedTemporaryFile(
                        delete=False, suffix=".jpg")
                    tmp.write(st.session_state.id_card_photo_bytes)
                    tmp.close()
                    return tmp.name
                return s_row[4]  # registered photo path

            if gen_front:
                with st.spinner("🎨 Generating MGM-style ID Card…"):
                    try:
                        photo_p  = get_photo_path()
                        card_buf = ic.generate_id_card(
                            student_id=s_row[0], name=s_row[1],
                            department=s_row[2] or "SY BCA",
                            email=s_row[3], registered_on=s_row[5],
                            photo_path=photo_p,
                            college_name=college, extra_info=extra,
                        )
                        raw = card_buf.read()
                        # No extra space: use fixed width
                        st.image(raw, caption=f"ID Card — {s_row[1]}",
                                 width=560)
                        db.log_activity(admin_user, "ID Card Generated",
                                        f"{s_row[1]} ({sid})")
                        st.download_button(
                            "⬇️  Download Front (PNG)", data=raw,
                            file_name=f"id_card_front_{sid}.png",
                            mime="image/png", use_container_width=True)
                        alert("✅ ID Card generated! Click download to save.", "success")
                    except Exception as ex:
                        alert(f"❌ Error: {ex}", "error")

            elif gen_back:
                with st.spinner("🎨 Generating Back Side…"):
                    try:
                        back_buf = ic.generate_id_card_back(
                            student_id=s_row[0], name=s_row[1],
                            college_name="MGM's College of Comp. Sci. & IT, Nanded",
                        )
                        raw_back = back_buf.read()
                        st.image(raw_back, caption=f"Back Side — {s_row[1]}",
                                 width=560)
                        st.download_button(
                            "⬇️  Download Back (PNG)", data=raw_back,
                            file_name=f"id_card_back_{sid}.png",
                            mime="image/png", use_container_width=True)
                        alert("✅ Back side generated! Click download to save.", "success")
                    except Exception as ex:
                        alert(f"❌ Error: {ex}", "error")

            else:
                st.markdown("""
                <div class="glass-card" style="text-align:center;padding:30px 20px;">
                    <div style="font-size:2.5rem;">🪪</div>
                    <div style="color:#58a6ff;font-weight:700;font-size:1rem;margin-top:10px;">
                        MGM College Style ID Card
                    </div>
                    <div style="color:#8b949e;font-size:.84rem;margin-top:10px;line-height:2;">
                        ✅ Purple header with college logo<br>
                        ✅ Student photo (upload or registered)<br>
                        ✅ Name, Class, DOB, Blood Group<br>
                        ✅ Contact, Address, Year<br>
                        ✅ QR Code for verification<br>
                        ✅ Back side with rules &amp; barcode
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# 7 · TIMETABLE  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Timetable" in page:
    top_bar("📅", "Timetable Manager", "Manage weekly class schedule")
    DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

    tab1, tab2 = st.tabs(["📋  View Timetable", "➕  Add Entry"])

    with tab1:
        entries = db.get_timetable()
        if entries:
            # Group by day
            day_map = {d: [] for d in DAYS}
            for e in entries:
                if e[1] in day_map:
                    day_map[e[1]].append(e)

            for day in DAYS:
                if day_map[day]:
                    sec(f"📆 {day}")
                    cols = st.columns(min(len(day_map[day]), 4))
                    for i, e in enumerate(day_map[day]):
                        with cols[i % 4]:
                            st.markdown(f"""
                            <div class="tt-cell">
                                <div class="tt-subject">📚 {e[3]}</div>
                                <div class="tt-meta">🕐 {e[2]}</div>
                                <div class="tt-meta">👨‍🏫 {e[4] or '—'} &nbsp; 🏫 {e[5] or '—'}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button("🗑️", key=f"tt_{e[0]}", help="Delete"):
                                db.delete_timetable_entry(e[0])
                                st.rerun()
        else:
            alert("No timetable entries yet. Add some using the Add Entry tab.", "info")

    with tab2:
        sec("Add New Class")
        subjects = db.get_subjects()
        r1, r2 = st.columns(2)
        t_day   = r1.selectbox("Day", DAYS)
        t_slot  = r2.text_input("Time Slot", placeholder="e.g. 09:00 - 10:00")
        r3, r4 = st.columns(2)
        t_subj  = r3.selectbox("Subject", subjects)
        t_teach = r4.text_input("Teacher Name", placeholder="e.g. Dr. Mehta")
        t_room  = st.text_input("Room / Lab", placeholder="e.g. Room 204")
        if st.button("➕  Add to Timetable", use_container_width=True):
            if t_slot:
                ok = db.add_timetable_entry(t_day, t_slot, t_subj, t_teach, t_room)
                if ok:
                    db.log_activity(admin_user, "Timetable Entry Added",
                                    f"{t_day} {t_slot} — {t_subj}")
                    alert(f"✅ {t_subj} added to {t_day} at {t_slot}", "success")
                    st.rerun()
                else:
                    alert("❌ Entry already exists.", "error")
            else:
                alert("❌ Please fill in the time slot.", "error")


# ══════════════════════════════════════════════════════════════════
# 8 · ACTIVITY LOG  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Activity Log" in page:
    top_bar("📝", "Activity Log", "Complete audit trail of admin actions")

    logs = db.get_activity_log(200)
    if not logs:
        alert("No activity recorded yet.", "info")
    else:
        ACTION_COLORS = {
            "Login": "#3fb950", "Logout": "#f85149",
            "Register Student": "#58a6ff", "Mark Attendance": "#3fb950",
            "ID Card Generated": "#bc8cff", "Timetable Entry Added": "#d29922",
            "Bulk Import": "#58a6ff", "Delete Student": "#f85149",
        }

        search = st.text_input("🔍 Filter logs", placeholder="Search by action or name…")
        filtered = [l for l in logs if search.lower() in (l[2]+l[3]).lower()] if search else logs

        st.markdown(f"<div style='color:#8b949e;font-size:.82rem;margin:8px 0;'>Showing {len(filtered)} entries</div>", unsafe_allow_html=True)

        log_html = ""
        for ts, actor, action, details in filtered:
            color = ACTION_COLORS.get(action, "#8b949e")
            log_html += f"""
            <div class="log-entry">
                <div class="log-dot" style="background:{color};box-shadow:0 0 6px {color}66;"></div>
                <div style="flex:1;">
                    <div style="display:flex;gap:10px;align-items:center;">
                        <span class="log-action">{action}</span>
                        <span class="log-time">{ts}</span>
                    </div>
                    <div class="log-detail">{details}</div>
                </div>
            </div>
            """
        st.markdown(f'<div class="glass-card" style="max-height:500px;overflow-y:auto;">{log_html}</div>',
                    unsafe_allow_html=True)

        if st.button("⬇️  Export Log as CSV"):
            df_log = pd.DataFrame(filtered, columns=["Timestamp","Actor","Action","Details"])
            st.download_button("Download", data=df_log.to_csv(index=False).encode(),
                               file_name="activity_log.csv", mime="text/csv")


# ══════════════════════════════════════════════════════════════════
# 9 · ATTENDANCE REPORT
# ══════════════════════════════════════════════════════════════════
elif "Report" in page:
    top_bar("📋", "Attendance Report", "Filter, view and export attendance records")

    c1, c2, c3 = st.columns(3)
    rtype = c1.radio("Report Type", ["Single Day","Date Range"], horizontal=True)
    subj_f = c2.selectbox("Subject Filter", ["All"] + db.get_subjects())

    if rtype == "Single Day":
        sel_d   = c3.date_input("Date", value=date.today())
        records = db.get_attendance_by_date(sel_d.strftime("%Y-%m-%d"), subj_f)
        r_title = f"Attendance — {sel_d.strftime('%d %B %Y')}"
    else:
        c4, c5  = st.columns(2)
        s_d = c4.date_input("From", value=date.today()-timedelta(days=7))
        e_d = c5.date_input("To",   value=date.today())
        records = db.get_attendance_range(s_d.strftime("%Y-%m-%d"), e_d.strftime("%Y-%m-%d"), subj_f)
        r_title = f"Attendance — {s_d} to {e_d}"

    if records:
        df = pd.DataFrame(records, columns=["Student ID","Name","Date","Time","Subject","Status","Is Late","Confidence"])
        df["Is Late"]    = df["Is Late"].apply(lambda x:"Yes" if x else "No")
        df["Confidence"] = df["Confidence"].apply(lambda x:f"{round((1-float(x))*100,1)}%" if x else "—")

        m1, m2, m3 = st.columns(3)
        m1.markdown(kpi_card("📊", len(df),                      "Total Records",  "blue"),   unsafe_allow_html=True)
        m2.markdown(kpi_card("✅", len(df[df["Is Late"]=="No"]), "On Time",        "green"),  unsafe_allow_html=True)
        m3.markdown(kpi_card("⚠️", len(df[df["Is Late"]=="Yes"]),"Late Arrivals",  "orange"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.dataframe(df, use_container_width=True, height=300)

        sec("⬇️ Export")
        e1, e2, e3 = st.columns(3)
        e1.download_button("📄 CSV",   df.to_csv(index=False).encode(), "report.csv",  "text/csv", use_container_width=True)
        xlsx_buf = io.BytesIO()
        with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Attendance")
        e2.download_button("📊 Excel", xlsx_buf.getvalue(), "report.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)
        try:
            pdf_b = ru.generate_pdf(df, title=r_title, subtitle=f"Subject: {subj_f}")
            e3.download_button("📑 PDF", pdf_b, "report.pdf", "application/pdf", use_container_width=True)
        except Exception as ex:
            e3.warning(f"PDF error: {ex}")
    else:
        alert("No records found for the selected filters.", "info")


# ══════════════════════════════════════════════════════════════════
# 10 · MANAGE STUDENTS
# ══════════════════════════════════════════════════════════════════
elif "Manage" in page:
    top_bar("👥", "Manage Students", "Search, view and manage registered students")
    students = db.get_all_students()
    if not students:
        alert("No students registered yet.", "info")
    else:
        search = st.text_input("🔍 Search by name or ID", placeholder="Type to filter…")
        filtered = [s for s in students if search.lower() in s[1].lower() or search.lower() in s[0].lower()] \
                   if search else students
        st.markdown(f"<div style='color:#8b949e;font-size:.82rem;margin-bottom:10px;'>Showing {len(filtered)} of {len(students)}</div>", unsafe_allow_html=True)

        for s in filtered:
            sid, name, dept, email, img_p, reg_on = s
            rec_count = len(db.get_student_attendance(sid))
            with st.container():
                st.markdown(f"""
                <div class="glass-card" style="margin-bottom:8px;">
                    <div style="display:flex;align-items:center;gap:14px;">
                        <div style="width:46px;height:46px;background:linear-gradient(135deg,#1f6feb,#7c3aed);
                             border-radius:50%;display:flex;align-items:center;justify-content:center;
                             font-size:1.2rem;flex-shrink:0;">
                            {"<img src='data:image/jpg;base64,..." if False else "👤"}
                        </div>
                        <div style="flex:1;">
                            <div style="font-weight:700;font-size:.95rem;color:#e6edf3;">
                                {name} <span class="badge bdg-blue" style="margin-left:6px;">{sid}</span>
                            </div>
                            <div style="font-size:.8rem;color:#8b949e;margin-top:3px;">
                                🏢 {dept or '—'} &nbsp;|&nbsp; 📧 {email or '—'} &nbsp;|&nbsp;
                                📅 {reg_on[:10]} &nbsp;|&nbsp;
                                <span style="color:#3fb950;">✅ {rec_count} days</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                _, col_del = st.columns([10, 1])
                if col_del.button("🗑️", key=f"d_{sid}", help="Delete student"):
                    db.delete_student(sid)
                    db.log_activity(admin_user, "Delete Student", f"{name} ({sid})")
                    if os.path.exists(img_p):
                        os.remove(img_p)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════
# 11 · SETTINGS
# ══════════════════════════════════════════════════════════════════
elif "Settings" in page:
    top_bar("⚙️", "Settings", "Configure system preferences and rules")

    tab1, tab2, tab3 = st.tabs(["🔐  Admin Account", "⏰  Attendance Rules", "📚  Subjects"])

    with tab1:
        sec("Change Admin Password")
        cur_pw  = st.text_input("Current Password", type="password")
        new_pw  = st.text_input("New Password",     type="password")
        conf_pw = st.text_input("Confirm Password", type="password")
        if st.button("🔐  Update Password"):
            import hashlib
            stored = db.get_setting("admin_password_hash", hashlib.sha256("admin123".encode()).hexdigest())
            if hashlib.sha256(cur_pw.encode()).hexdigest() != stored:
                alert("❌ Current password is incorrect.", "error")
            elif new_pw != conf_pw:
                alert("❌ New passwords do not match.", "error")
            elif len(new_pw) < 6:
                alert("❌ Password must be at least 6 characters.", "error")
            else:
                db.set_setting("admin_password_hash", hashlib.sha256(new_pw.encode()).hexdigest())
                db.log_activity(admin_user, "Password Changed", "Admin password updated")
                alert("✅ Password updated successfully!", "success")

    with tab2:
        sec("Late Arrival Time")
        cur_late = db.get_setting("late_threshold","09:30")
        alert(f"Current: Students arriving after <b>{cur_late}</b> are marked Late.", "info")
        import datetime as _dt
        h, m = map(int, cur_late.split(":"))
        new_late = st.time_input("Set Late Threshold", value=_dt.time(h, m))
        if st.button("💾  Save Late Threshold"):
            db.set_setting("late_threshold", new_late.strftime("%H:%M"))
            db.log_activity(admin_user, "Settings Updated", f"Late threshold: {new_late.strftime('%H:%M')}")
            alert(f"✅ Late threshold updated to {new_late.strftime('%H:%M')}", "success")

        sec("Recognition Threshold")
        st.markdown("""
        <div class="glass-card" style="font-size:.84rem;color:#8b949e;">
            <b style="color:#e6edf3;">Lower</b> = Stricter (fewer false matches) &nbsp;|&nbsp;
            <b style="color:#e6edf3;">Higher</b> = More lenient<br>
            Recommended range: <b style="color:#58a6ff;">0.35 – 0.45</b>
        </div>
        """, unsafe_allow_html=True)
        cur_thr = float(db.get_setting("recognition_threshold","0.40"))
        new_thr = st.slider("Threshold", 0.20, 0.70, cur_thr, 0.05)
        if st.button("💾  Save Threshold"):
            db.set_setting("recognition_threshold", str(new_thr))
            fu.RECOGNITION_THRESHOLD = new_thr
            db.log_activity(admin_user, "Settings Updated", f"Recognition threshold: {new_thr}")
            alert(f"✅ Threshold set to {new_thr}", "success")

    with tab3:
        sec("Manage Subjects")
        subjs = db.get_subjects()
        for s in subjs:
            c1, c2 = st.columns([5,1])
            c1.markdown(f"<div style='padding:9px 4px;color:#e6edf3;font-size:.88rem;'>📚 {s}</div>", unsafe_allow_html=True)
            if s != "General" and c2.button("✕", key=f"rs_{s}", help="Remove"):
                db.delete_subject(s)
                st.rerun()
        st.markdown("---")
        new_s = st.text_input("New Subject Name", placeholder="e.g. Machine Learning")
        if st.button("➕  Add Subject"):
            if new_s.strip():
                ok = db.add_subject(new_s.strip())
                if ok:
                    db.log_activity(admin_user, "Subject Added", new_s.strip())
                    alert(f"✅ '{new_s}' added!", "success")
                    st.rerun()
                else:
                    alert("❌ Subject already exists.", "error")


# ══════════════════════════════════════════════════════════════════
# 12 · ATTENDANCE CERTIFICATE  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Certificate" in page:
    import certificate_utils as cu
    top_bar("📜", "Attendance Certificate", "Generate official attendance certificates for students")

    students = db.get_all_students()
    if not students:
        alert("No students registered yet.", "info")
    else:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            sec("Certificate Details")
            opts = {f"{s[1]} ({s[0]})": s[0] for s in students}
            sel  = st.selectbox("Select Student", list(opts.keys()))
            sid  = opts[sel]
            s_row = next(s for s in students if s[0] == sid)

            college = st.text_input("Institution Name", value="Smart College of Technology")
            issued_by = st.text_input("Issued By (Principal / HOD)", value="Principal")

            records = db.get_student_attendance(sid)
            if records:
                dates  = sorted([r[0] for r in records])
                s_date = dates[0]
                e_date = dates[-1]
            else:
                s_date = date.today().strftime("%Y-%m-%d")
                e_date = date.today().strftime("%Y-%m-%d")

            r1, r2 = st.columns(2)
            from_d = r1.text_input("From Date", value=s_date)
            to_d   = r2.text_input("To Date",   value=e_date)

            total_days = len(records)
            st.markdown(f"""
            <div class="glass-card" style="margin-top:12px;">
                <div style="font-size:.85rem;color:#8b949e;line-height:2;">
                    👤 Student: <b style="color:#e6edf3;">{s_row[1]}</b><br>
                    🆔 ID: <b style="color:#58a6ff;">{sid}</b><br>
                    🏢 Dept: <b style="color:#e6edf3;">{s_row[2] or '—'}</b><br>
                    📅 Days Present: <b style="color:#3fb950;">{total_days}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            gen = st.button("📜  Generate Certificate", use_container_width=True)

        with c2:
            sec("Preview")
            if gen:
                with st.spinner("🎨 Generating certificate…"):
                    try:
                        cert_bytes = cu.generate_certificate(
                            student_id=sid, name=s_row[1],
                            department=s_row[2] or "N/A",
                            college_name=college,
                            total_days=total_days,
                            start_date=from_d, end_date=to_d,
                            issued_by=issued_by,
                        )
                        db.log_activity(admin_user, "Certificate Generated", f"{s_row[1]} ({sid})")
                        st.success(f"✅ Certificate ready for {s_row[1]}!")
                        st.download_button(
                            "⬇️  Download Certificate PDF",
                            data=cert_bytes,
                            file_name=f"certificate_{sid}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                        st.markdown("""
                        <div class="glass-card" style="text-align:center;padding:30px;">
                            <div style="font-size:3rem;">📜</div>
                            <div style="color:#3fb950;font-weight:700;margin-top:10px;">Certificate Generated!</div>
                            <div style="color:#8b949e;font-size:.85rem;margin-top:6px;">
                                Click the download button above to save the PDF certificate.
                                The certificate includes a unique serial number and QR code for verification.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as ex:
                        alert(f"❌ Error: {ex}", "error")
            else:
                st.markdown("""
                <div class="glass-card" style="text-align:center;padding:50px 30px;">
                    <div style="font-size:3.5rem;">📜</div>
                    <div style="color:#58a6ff;font-weight:700;font-size:1.05rem;margin-top:14px;">
                        Official Attendance Certificate
                    </div>
                    <div style="color:#8b949e;font-size:.85rem;margin-top:8px;line-height:1.8;">
                        Includes decorative border & gold accents<br>
                        Student photo & attendance statistics<br>
                        Unique serial number & QR verification code<br>
                        Signature sections for 3 authorities<br>
                        Ready to print on A4 paper
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# 13 · ABSENT STUDENTS  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Absent" in page:
    top_bar("🔔", "Absent Students", "Today's absentee list — mark or export")

    total, present, absent, late = db.get_today_stats()
    subjects = ["All"] + db.get_subjects()
    subj_f = st.selectbox("Filter by Subject", subjects)
    sel_date = st.date_input("Date", value=date.today())

    absent_list = db.get_absent_students(sel_date.strftime("%Y-%m-%d"), subj_f)

    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi_card("👥", total,   "Registered",   "blue"),   unsafe_allow_html=True)
    c2.markdown(kpi_card("✅", present, "Present",       "green"),  unsafe_allow_html=True)
    c3.markdown(kpi_card("❌", len(absent_list), "Absent", "red"),  unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if absent_list:
        sec(f"❌ Absent Students — {sel_date.strftime('%d %B %Y')}")
        df_ab = pd.DataFrame(absent_list, columns=["Student ID","Name","Department","Email"])
        st.dataframe(df_ab, use_container_width=True, height=300)

        c_exp, c_notify = st.columns(2)
        csv_ab = df_ab.to_csv(index=False).encode()
        c_exp.download_button("⬇️  Export Absent List CSV", data=csv_ab,
                               file_name=f"absent_{sel_date}.csv", mime="text/csv",
                               use_container_width=True)
        if c_notify.button("📋  Copy Names to Clipboard List", use_container_width=True):
            names = "\n".join([f"• {r[1]} ({r[0]})" for r in absent_list])
            st.code(names, language=None)
    else:
        alert("🎉 All registered students are present today!", "success")


# ══════════════════════════════════════════════════════════════════
# 14 · MANUAL ATTENDANCE  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Manual" in page:
    top_bar("✋", "Manual Attendance", "Override or add attendance when camera is unavailable")
    alert("⚠️ Use manual attendance only when face recognition is unavailable (hardware issues, poor lighting, etc.)", "warning")

    students  = db.get_all_students()
    subjects  = db.get_subjects()

    if not students:
        alert("No students registered yet.", "info")
    else:
        sec("Mark Individual Student")
        c1, c2, c3 = st.columns(3)
        opts = {f"{s[1]} ({s[0]})": (s[0], s[1]) for s in students}
        sel  = c1.selectbox("Student", list(opts.keys()))
        subj = c2.selectbox("Subject", subjects)
        stat = c3.selectbox("Status", ["Present", "Late", "Absent"])
        sid, sname = opts[sel]

        if st.button("✋  Mark Attendance Manually", use_container_width=True):
            db.mark_manual_attendance(sid, sname, subj, stat)
            db.log_activity(admin_user, "Manual Attendance",
                            f"{sname} ({sid}) — {subj} — {stat}")
            alert(f"✅ {sname} marked as {stat} for {subj} (manual override)", "success")

        sec("Bulk Mark — Entire Class")
        st.markdown("""
        <div class="glass-card" style="font-size:.85rem;color:#8b949e;">
            Select a subject and mark <b style="color:#e6edf3;">all currently absent</b> students as Present at once.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        bulk_subj = st.selectbox("Subject for Bulk Mark", subjects, key="bulk_s")

        absent_now = db.get_absent_students(date.today().strftime("%Y-%m-%d"), bulk_subj)
        if absent_now:
            st.markdown(f"<div style='color:#f85149;font-weight:600;margin-bottom:8px;'>⚠️ {len(absent_now)} students currently absent for {bulk_subj}</div>", unsafe_allow_html=True)
            selected_ids = st.multiselect(
                "Select students to mark Present",
                options=[f"{r[1]} ({r[0]})" for r in absent_now],
                default=[f"{r[1]} ({r[0]})" for r in absent_now],
            )
            if st.button(f"✅  Mark {len(selected_ids)} Students Present", use_container_width=True):
                count = 0
                for item in selected_ids:
                    s_id  = item.split("(")[-1].rstrip(")")
                    s_nm  = item.split("(")[0].strip()
                    db.mark_manual_attendance(s_id, s_nm, bulk_subj, "Present")
                    count += 1
                db.log_activity(admin_user, "Bulk Manual Attendance",
                                f"{count} students — {bulk_subj}")
                alert(f"✅ {count} students marked Present for {bulk_subj}", "success")
                st.rerun()
        else:
            alert(f"All students already marked for {bulk_subj} today!", "success")


# ══════════════════════════════════════════════════════════════════
# 15 · BACKUP & RESTORE  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Backup" in page:
    import shutil, sqlite3 as _sq
    top_bar("💾", "Backup & Restore", "Download or restore the attendance database")

    tab1, tab2 = st.tabs(["💾  Backup", "📤  Restore"])

    with tab1:
        sec("Download Database Backup")
        db_path = os.path.join(os.path.dirname(__file__), "database", "attendance.db")
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:.88rem;color:#8b949e;line-height:2;">
                📦 This exports the <b style="color:#e6edf3;">complete SQLite database</b> including:<br>
                &nbsp;&nbsp;✅ All registered students<br>
                &nbsp;&nbsp;✅ Full attendance history<br>
                &nbsp;&nbsp;✅ Timetable entries<br>
                &nbsp;&nbsp;✅ Activity logs<br>
                &nbsp;&nbsp;✅ System settings<br><br>
                💡 Save this file regularly as your project backup.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if os.path.exists(db_path):
            with open(db_path, "rb") as f:
                db_bytes = f.read()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "⬇️  Download attendance.db",
                data=db_bytes,
                file_name=f"attendance_backup_{ts}.db",
                mime="application/octet-stream",
                use_container_width=True,
            )
            size_kb = round(len(db_bytes)/1024, 1)
            alert(f"📦 Database size: {size_kb} KB &nbsp;·&nbsp; Ready to download", "success")
            db.log_activity(admin_user, "Backup Downloaded", f"Size: {size_kb} KB")

        sec("Export All Students as CSV")
        students = db.get_all_students()
        if students:
            df_s = pd.DataFrame(students, columns=["Student ID","Name","Department","Email","Image Path","Registered On"])
            st.download_button("⬇️  Students CSV", df_s.to_csv(index=False).encode(),
                               "students_export.csv", "text/csv", use_container_width=True)

        sec("Export All Attendance as CSV")
        all_att = db.get_attendance_range("2000-01-01", date.today().strftime("%Y-%m-%d"))
        if all_att:
            df_att = pd.DataFrame(all_att, columns=["Student ID","Name","Date","Time","Subject","Status","Is Late","Confidence"])
            st.download_button("⬇️  All Attendance CSV", df_att.to_csv(index=False).encode(),
                               "all_attendance_export.csv", "text/csv", use_container_width=True)

    with tab2:
        sec("Restore from Backup")
        alert("⚠️ Restoring will REPLACE your current database. Make sure to back up first!", "warning")
        st.markdown("<br>", unsafe_allow_html=True)

        uploaded_db = st.file_uploader("Upload backup .db file", type=["db"])
        confirm = st.checkbox("I understand this will overwrite current data")

        if uploaded_db and confirm:
            if st.button("📤  Restore Database", use_container_width=True):
                db_path = os.path.join(os.path.dirname(__file__), "database", "attendance.db")
                # Verify it's a valid SQLite file
                tmp_path = db_path + ".tmp"
                with open(tmp_path, "wb") as f:
                    f.write(uploaded_db.read())
                try:
                    test_conn = _sq.connect(tmp_path)
                    test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    test_conn.close()
                    # Backup current
                    if os.path.exists(db_path):
                        shutil.copy(db_path, db_path + ".bak")
                    shutil.move(tmp_path, db_path)
                    db.log_activity(admin_user, "Database Restored", "From uploaded backup file")
                    alert("✅ Database restored successfully! Please refresh the page.", "success")
                except Exception as ex:
                    os.remove(tmp_path)
                    alert(f"❌ Invalid database file: {ex}", "error")


# ══════════════════════════════════════════════════════════════════
# 16 · CALENDAR HEATMAP  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Calendar" in page:
    top_bar("🗓️", "Attendance Calendar", "GitHub-style monthly attendance heatmap")

    import calendar as cal_mod
    now_dt = datetime.now()

    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    with col_nav2:
        months = [date(now_dt.year, m, 1).strftime("%B %Y") for m in range(1, 13)]
        sel_month_str = st.selectbox("Select Month", months,
                                     index=now_dt.month - 1, label_visibility="collapsed")
        sel_month = datetime.strptime(sel_month_str, "%B %Y")
        yr, mo = sel_month.year, sel_month.month

    daily = db.get_daily_counts_for_month(yr, mo)
    total_s = len(db.get_all_students())

    # Build calendar grid
    cal_grid = cal_mod.monthcalendar(yr, mo)
    month_name = sel_month.strftime("%B %Y")

    # ── Plotly calendar heatmap ──
    z_vals, text_vals, x_labels, y_labels = [], [], [], []
    day_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    for week in cal_grid:
        z_row, t_row = [], []
        for day in week:
            if day == 0:
                z_row.append(None)
                t_row.append("")
            else:
                d_str = f"{yr}-{mo:02d}-{day:02d}"
                cnt   = daily.get(d_str, 0)
                pct   = round(cnt / total_s * 100) if total_s else 0
                z_row.append(pct)
                t_row.append(f"<b>{day}</b><br>{cnt} students<br>{pct}%")
        z_vals.append(z_row)
        text_vals.append(t_row)

    fig_cal = go.Figure(go.Heatmap(
        z=z_vals,
        text=text_vals,
        hovertemplate="%{text}<extra></extra>",
        xgap=4, ygap=4,
        colorscale=[
            [0.0,  "#161b27"],
            [0.01, "#0d4429"],
            [0.3,  "#1a7f37"],
            [0.6,  "#2ea043"],
            [1.0,  "#3fb950"],
        ],
        showscale=True,
        colorbar=dict(
            title="% Present", tickfont=dict(color="#8b949e", family="Inter"),
            titlefont=dict(color="#8b949e", family="Inter"),
            bgcolor="rgba(0,0,0,0)", bordercolor="#21262d",
        ),
        zmin=0, zmax=100,
    ))
    fig_cal.update_layout(
        title=dict(text=f"📅 {month_name} — Attendance Heatmap",
                   font=dict(color="#e6edf3", size=16, family="Inter"), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,17,23,.6)",
        margin=dict(l=40,r=40,t=60,b=40), height=320,
        font=dict(family="Inter", color="#8b949e"),
        xaxis=dict(ticktext=day_names, tickvals=list(range(7)),
                   tickfont=dict(color="#8b949e"), showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, autorange="reversed"),
    )
    st.plotly_chart(fig_cal, use_container_width=True)

    # ── Legend + Stats ──
    present_days = len(daily)
    total_days_month = cal_mod.monthrange(yr, mo)[1]
    avg_daily = round(sum(daily.values()) / max(present_days, 1), 1)
    best_day_entry = max(daily.items(), key=lambda x: x[1]) if daily else (None, 0)

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(kpi_card("📅", present_days,    "Days with Attendance", "blue"),   unsafe_allow_html=True)
    m2.markdown(kpi_card("👥", avg_daily,        "Avg Students/Day",    "green"),  unsafe_allow_html=True)
    m3.markdown(kpi_card("🏆", best_day_entry[1],"Best Day Count",      "orange"), unsafe_allow_html=True)
    m4.markdown(kpi_card("📆", total_days_month, "Working Days",        "blue"),   unsafe_allow_html=True)

    # ── Daily breakdown table ──
    if daily:
        sec("📋 Daily Breakdown")
        df_day = pd.DataFrame(
            [(d, c, round(c/total_s*100,1) if total_s else 0)
             for d,c in sorted(daily.items(), reverse=True)],
            columns=["Date","Students Present","Attendance %"]
        )
        st.dataframe(df_day, use_container_width=True, height=220)


# ══════════════════════════════════════════════════════════════════
# 17 · STUDENT GALLERY  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Gallery" in page:
    top_bar("🖼️", "Student Gallery", "Visual photo grid with live attendance stats")

    students = db.get_all_students()
    summary  = {s[0]: s for s in db.get_all_student_attendance_summary()}

    if not students:
        alert("No students registered yet.", "info")
    else:
        # Filters
        fc1, fc2, fc3 = st.columns(3)
        search_g = fc1.text_input("🔍 Search", placeholder="Name or ID…")
        depts    = list({s[2] for s in students if s[2]}) or ["All"]
        dept_f   = fc2.selectbox("Department", ["All"] + sorted(depts))
        sort_by  = fc3.selectbox("Sort by", ["Name A-Z", "Most Attended", "Least Attended"])

        filtered = [s for s in students
                    if (search_g.lower() in s[1].lower() or search_g.lower() in s[0].lower())
                    and (dept_f == "All" or s[2] == dept_f)]

        if sort_by == "Most Attended":
            filtered.sort(key=lambda s: summary.get(s[0], (0,0,0,0,""))[3], reverse=True)
        elif sort_by == "Least Attended":
            filtered.sort(key=lambda s: summary.get(s[0], (0,0,0,0,""))[3])
        else:
            filtered.sort(key=lambda s: s[1])

        st.markdown(f"<div style='color:#8b949e;font-size:.82rem;margin-bottom:14px;'>Showing {len(filtered)} students</div>", unsafe_allow_html=True)

        # Grid – 4 cards per row
        cols_per_row = 4
        rows = [filtered[i:i+cols_per_row] for i in range(0, len(filtered), cols_per_row)]

        for row in rows:
            cols = st.columns(cols_per_row)
            for col, student in zip(cols, row):
                sid, name, dept, email, img_path, reg_on = student
                s_sum  = summary.get(sid, (sid, name, dept, 0, None))
                days   = s_sum[3]
                pct    = min(days * 5, 100)  # visual indicator
                last   = s_sum[4] or "Never"
                color  = "#3fb950" if pct >= 75 else "#d29922" if pct >= 50 else "#f85149"
                with col:
                    # Photo
                    if os.path.exists(img_path):
                        col.image(img_path, use_column_width=True)
                    else:
                        col.markdown("""<div style='height:140px;background:linear-gradient(135deg,#161b27,#21262d);
                            border-radius:12px 12px 0 0;display:flex;align-items:center;
                            justify-content:center;font-size:3rem;'>👤</div>""",
                            unsafe_allow_html=True)
                    # Info card
                    col.markdown(f"""
                    <div style="background:#161b27;border:1px solid #21262d;border-radius:0 0 12px 12px;
                         padding:12px 10px 14px;text-align:center;margin-top:-6px;">
                        <div style="font-weight:700;font-size:.9rem;color:#e6edf3;
                             white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</div>
                        <div style="font-size:.73rem;color:#58a6ff;margin:2px 0;">{sid}</div>
                        <div style="font-size:.72rem;color:#8b949e;">{dept or '—'}</div>
                        <div style="margin:8px 0 4px;">
                            <div style="background:#21262d;border-radius:6px;height:5px;overflow:hidden;">
                                <div style="width:{pct}%;height:5px;background:{color};border-radius:6px;"></div>
                            </div>
                        </div>
                        <div style="font-size:.75rem;font-weight:700;color:{color};">{days} days attended</div>
                        <div style="font-size:.68rem;color:#484f58;margin-top:2px;">Last: {last}</div>
                    </div>
                    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# 18 · LOW ATTENDANCE ALERTS  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Low Attendance" in page:
    top_bar("⚠️", "Low Attendance Alerts", "Students flagged for insufficient attendance")

    threshold = st.slider("Alert Threshold (%)", 50, 90, 75, 5,
                          help="Students below this percentage will be flagged")

    summary = db.get_all_student_attendance_summary()
    total_s = len(db.get_all_students())

    if not summary:
        alert("No attendance data yet.", "info")
    else:
        # Categorise
        critical, warning_list, good = [], [], []
        for s in summary:
            sid, name, dept, days, last = s
            pct = round(days / max(days, 1) * 100) if days > 0 else 0
            if pct < threshold * 0.66:
                critical.append((sid, name, dept, days, pct, last))
            elif pct < threshold:
                warning_list.append((sid, name, dept, days, pct, last))
            else:
                good.append((sid, name, dept, days, pct, last))

        # Summary KPIs
        m1, m2, m3 = st.columns(3)
        m1.markdown(kpi_card("🔴", len(critical),     "Critical (<50%)",   "red"),    unsafe_allow_html=True)
        m2.markdown(kpi_card("🟡", len(warning_list), f"Warning (<{threshold}%)", "orange"), unsafe_allow_html=True)
        m3.markdown(kpi_card("🟢", len(good),         "Good Standing",     "green"),  unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        def att_table(students_list, label, border_color, bg_color, text_color):
            if not students_list:
                return
            sec(label)
            for sid, name, dept, days, pct, last in students_list:
                fill = min(pct, 100)
                st.markdown(f"""
                <div style="background:#0d1117;border:1px solid {border_color}33;
                     border-left:4px solid {border_color};border-radius:10px;
                     padding:14px 18px;margin-bottom:8px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div>
                            <span style="font-weight:700;color:#e6edf3;">{name}</span>
                            <span style="font-size:.75rem;background:{bg_color};color:{text_color};
                                  padding:2px 8px;border-radius:10px;margin-left:8px;">{sid}</span>
                            <div style="font-size:.78rem;color:#8b949e;margin-top:3px;">
                                🏢 {dept or '—'} &nbsp;·&nbsp; 📅 Last seen: {last or 'Never'}
                            </div>
                        </div>
                        <div style="text-align:right;min-width:80px;">
                            <div style="font-size:1.4rem;font-weight:900;color:{border_color};">{pct}%</div>
                            <div style="font-size:.72rem;color:#8b949e;">{days} days</div>
                        </div>
                    </div>
                    <div style="background:#21262d;border-radius:6px;height:6px;margin-top:10px;overflow:hidden;">
                        <div style="width:{fill}%;height:6px;background:{border_color};border-radius:6px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        att_table(critical,      "🔴 Critical — Immediate Action Required", "#f85149", "#3d0000", "#f85149")
        att_table(warning_list,  f"🟡 Warning — Below {threshold}% Threshold",  "#d29922", "#3d2000", "#d29922")

        if good:
            sec(f"🟢 Good Standing — Above {threshold}%")
            df_good = pd.DataFrame(
                [(s[1], s[0], s[2] or "—", f"{s[4]}%", s[3], s[5] or "—")
                 for s in good],
                columns=["Name","ID","Department","Attendance %","Days","Last Seen"]
            )
            st.dataframe(df_good, use_container_width=True, height=220)

        # Export flagged list
        if critical or warning_list:
            st.markdown("<br>", unsafe_allow_html=True)
            flagged = critical + warning_list
            df_flag = pd.DataFrame(flagged, columns=["ID","Name","Dept","Days","Percentage","Last Seen"])
            st.download_button("⬇️  Export Flagged Students CSV",
                               data=df_flag.to_csv(index=False).encode(),
                               file_name="low_attendance_alert.csv", mime="text/csv",
                               use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# 19 · CLASS SUMMARY CARDS  ★ NEW
# ══════════════════════════════════════════════════════════════════
elif "Class Summary" in page:
    top_bar("📈", "Class Summary", "Subject-wise attendance performance overview")

    subj_data = db.get_subject_summary()
    all_students = db.get_all_students()
    total_s = len(all_students)

    if not subj_data:
        alert("No attendance records yet. Mark attendance for subjects first.", "info")
    else:
        # Top KPIs
        total_records = sum(s[1] for s in subj_data)
        total_subjs   = len(subj_data)
        most_active   = max(subj_data, key=lambda x: x[1])
        m1, m2, m3 = st.columns(3)
        m1.markdown(kpi_card("📚", total_subjs,       "Total Subjects",     "blue"),   unsafe_allow_html=True)
        m2.markdown(kpi_card("📝", total_records,     "Total Records",      "green"),  unsafe_allow_html=True)
        m3.markdown(kpi_card("🏆", most_active[0],    "Most Active Subject", "orange"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        sec("📚 Subject Performance Cards")
        # 3 cards per row
        card_rows = [subj_data[i:i+3] for i in range(0, len(subj_data), 3)]
        for row in card_rows:
            cols = st.columns(3)
            for col, (subj, total, students, late_cnt, last_cls) in zip(cols, row):
                att_rate  = round(students / total_s * 100) if total_s else 0
                late_rate = round(late_cnt / max(total,1) * 100)
                bar_color = "#3fb950" if att_rate >= 75 else "#d29922" if att_rate >= 50 else "#f85149"
                col.markdown(f"""
                <div class="glass-card" style="position:relative;overflow:hidden;">
                    <div style="position:absolute;top:0;left:0;right:0;height:3px;
                         background:linear-gradient(90deg,#1f6feb,#3fb950);"></div>
                    <div style="font-size:1rem;font-weight:800;color:#e6edf3;margin-bottom:12px;">
                        📚 {subj}
                    </div>
                    <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                        <div style="text-align:center;">
                            <div style="font-size:1.4rem;font-weight:900;color:#58a6ff;">{total}</div>
                            <div style="font-size:.7rem;color:#8b949e;text-transform:uppercase;">Records</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:1.4rem;font-weight:900;color:#3fb950;">{students}</div>
                            <div style="font-size:.7rem;color:#8b949e;text-transform:uppercase;">Students</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:1.4rem;font-weight:900;color:#d29922;">{late_cnt}</div>
                            <div style="font-size:.7rem;color:#8b949e;text-transform:uppercase;">Late</div>
                        </div>
                    </div>
                    <div style="font-size:.75rem;color:#8b949e;display:flex;justify-content:space-between;margin-bottom:6px;">
                        <span>Attendance Rate</span><span style="color:{bar_color};font-weight:700;">{att_rate}%</span>
                    </div>
                    <div style="background:#21262d;border-radius:6px;height:6px;overflow:hidden;margin-bottom:8px;">
                        <div style="width:{att_rate}%;height:6px;background:{bar_color};border-radius:6px;"></div>
                    </div>
                    <div style="font-size:.72rem;color:#8b949e;margin-top:4px;">
                        ⚠️ Late rate: {late_rate}% &nbsp;·&nbsp; 📅 Last: {last_cls or '—'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Bar chart comparison
        sec("📊 Subject Comparison Chart")
        df_subj = pd.DataFrame(subj_data, columns=["Subject","Total","Students","Late","Last Class"])
        df_subj["Attendance Rate"] = df_subj["Students"].apply(
            lambda x: round(x/total_s*100) if total_s else 0)

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Total Records", x=df_subj["Subject"], y=df_subj["Total"],
                             marker_color="#1f6feb", opacity=0.85))
        fig.add_trace(go.Bar(name="Unique Students", x=df_subj["Subject"], y=df_subj["Students"],
                             marker_color="#3fb950", opacity=0.85))
        fig.add_trace(go.Bar(name="Late Arrivals",  x=df_subj["Subject"], y=df_subj["Late"],
                             marker_color="#d29922", opacity=0.85))
        fig.update_layout(
            barmode="group", template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,17,23,.6)",
            margin=dict(l=0,r=0,t=20,b=0), height=260,
            font=dict(family="Inter",color="#8b949e"),
            xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
            legend=dict(font=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)