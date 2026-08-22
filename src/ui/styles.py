"""
Custom CSS Styles for Agentic NLP Framework Streamlit Web Interface.
Professional Government AI Portal Aesthetic for Major Project.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Kannada:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* App Background & Page Padding */
.stApp {
    background: #F8FAFC;
}

/* Tricolor Top Bar Accent */
.tricolor-bar {
    height: 4px;
    background: linear-gradient(90deg, #FF9933 0%, #FF9933 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #138808 66.6%, #138808 100%);
    border-radius: 4px 4px 0 0;
    margin-bottom: -4px;
}

/* Premium Header Banner */
.main-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #1E40AF 100%);
    padding: 1.8rem 2.2rem;
    border-radius: 14px;
    color: white;
    margin-bottom: 1.6rem;
    box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25), 0 8px 10px -6px rgba(30, 58, 138, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}

.main-header::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, rgba(255, 255, 255, 0) 70%);
    border-radius: 50%;
    pointer-events: none;
}

.main-header h1 {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0;
    color: #FFFFFF !important;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.main-header p {
    font-size: 1.02rem;
    margin-top: 0.5rem;
    margin-bottom: 0;
    color: #BFDBFE !important;
    font-weight: 500;
}

.header-badge {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    color: #F8FAFC;
    padding: 0.35rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 0.6rem;
}

/* Metric KPI Cards with Top Accent */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 4px solid #2563EB;
    border-radius: 12px;
    padding: 1.1rem 1rem;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.08);
    border-top-color: #1D4ED8;
}

.metric-title {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748B;
    font-weight: 700;
}

.metric-value {
    font-size: 1.65rem;
    font-weight: 800;
    color: #0F172A;
    margin: 0.25rem 0;
    letter-spacing: -0.02em;
}

.metric-sub {
    font-size: 0.78rem;
    color: #059669;
    font-weight: 600;
}

/* Modern Preset Buttons */
div.stButton > button {
    border-radius: 9px;
    font-weight: 600;
    font-size: 0.88rem;
    transition: all 0.2s ease;
    border: 1px solid #CBD5E1;
}

div.stButton > button:hover {
    border-color: #2563EB;
    color: #2563EB;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.12);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
}

div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1E40AF 0%, #1D4ED8 100%) !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.45) !important;
    transform: translateY(-1px);
}

/* Agent Trace Step Timeline */
.trace-step {
    border-left: 3px solid #3B82F6;
    padding: 0.8rem 1rem 0.8rem 1.2rem;
    margin-bottom: 0.9rem;
    background: #FFFFFF;
    border-radius: 0 10px 10px 0;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
    border-top: 1px solid #F1F5F9;
    border-right: 1px solid #F1F5F9;
    border-bottom: 1px solid #F1F5F9;
}

.trace-step-title {
    font-weight: 700;
    font-size: 0.94rem;
    color: #0F172A;
}

.trace-step-desc {
    font-size: 0.85rem;
    color: #334155;
    margin-top: 0.3rem;
}

.trace-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 14px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    margin-left: 0.5rem;
}

.badge-success {
    background-color: #ECFDF5;
    color: #065F46;
    border: 1px solid #A7F3D0;
}

.badge-warning {
    background-color: #FEF3C7;
    color: #92400E;
    border: 1px solid #FDE68A;
}

/* Entity Pills and Cards */
.entity-pill {
    display: inline-block;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    color: #1E40AF;
    padding: 0.3rem 0.75rem;
    border-radius: 24px;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 0.25rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.entity-card-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

.sidebar-team-box {
    background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1rem;
    margin-top: 0.8rem;
}

.sidebar-team-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: #1E3A8A;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.6rem;
}

.team-member {
    font-size: 0.86rem;
    color: #1E293B;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.team-usn {
    color: #64748B;
    font-size: 0.78rem;
    font-weight: 500;
}

/* Styled Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: #F1F5F9;
    padding: 6px;
    border-radius: 10px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 8px 16px;
}

.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #1E3A8A !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06) !important;
}
</style>
"""
