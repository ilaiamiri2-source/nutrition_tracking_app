import io
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

def inject_custom_css():
    """Injects high-end, clean, medical-grade styling tailored for non-technical users."""
    st.markdown("""
    <style>
        /* 1. Base clean typography: Standard modern system sans-serif */
        html, body, .stApp,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] span,
        div[data-testid="stMarkdownContainer"] li,
        .stMarkdown, p, span, label,
        input, textarea, select,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stSelectbox"],
        div[data-baseweb="select"],
        div[data-testid="stSidebar"],
        div[data-testid="stSidebar"] p,
        div[data-testid="stSidebar"] span,
        div[data-testid="stSidebar"] label,
        .action-box {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #0f172a;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* 2. PROTECT STREAMLIT MATERIAL ICONS (Sidebar toggle, theme toggle, header icons) */
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        .material-icons,
        button[data-testid="stSidebarCollapseButton"] span,
        [data-testid="stHeader"] span,
        header span,
        span[data-testid="stIconMaterial"] {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
        }

        header[data-testid="stHeader"] {
            background-color: transparent;
        }
        
        /* Master Roster Card Container Styling */
        div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] > div[data-testid="stContainer"],
        div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
            transition: all 0.2s ease-in-out;
            border-radius: 14px !important;
            margin-bottom: 20px !important;
            border: 1.5px solid #cbd5e1 !important;
            background: #ffffff !important;
            padding: 30px 28px !important;
        }
        /* Subtle hover elevation on roster cards */
        div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] > div[data-testid="stContainer"]:hover,
        div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"]:hover {
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
            border-color: #94a3b8 !important;
        }

        /* KPI Metric Cards - Clean uniform containers */
        .metric-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 16px 18px;
            border: 1.5px solid #cbd5e1;
            box-shadow: 0 2px 4px rgba(15, 23, 42, 0.04);
            margin-bottom: 12px;
            transition: border-color 0.2s ease;
            height: 132px;
            min-height: 132px;
            max-height: 132px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
        }
        .metric-card:hover {
            border-color: #94a3b8;
        }
        
        .metric-title {
            font-size: 0.80rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #475569;
            font-weight: 700;
            margin-bottom: 2px;
        }
        
        .metric-value {
            font-size: 1.65rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.15;
            letter-spacing: -0.03em;
        }
        
        .metric-sub {
            font-size: 0.80rem;
            color: #64748b;
            margin-top: 2px;
        }

        /* Urgent Banner & Target Badges */
        .urgent-banner {
            background: #fff1f2;
            border-left: 5px solid #e11d48;
            padding: 14px 18px;
            border-radius: 8px;
            color: #9f1239;
            font-size: 0.95rem;
            margin-bottom: 18px;
        }

        .target-badge {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            border-radius: 12px;
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }

        /* Biomarker Cards */
        .bio-card {
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 10px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
        }
        .bio-card.critical {
            background: #fff1f2;
            border-color: #fecdd3;
        }
        .bio-card.warning {
            background: #fffbeb;
            border-color: #fde68a;
        }
        .bio-card.optimal {
            background: #f0fdf4;
            border-color: #bbf7d0;
        }

        /* Supplement Cards */
        .supplement-card {
            background: #ffffff;
            border-radius: 10px;
            padding: 14px 18px;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #2563eb;
            margin-bottom: 12px;
        }
        .supplement-card.clinical {
            border-left-color: #0891b2;
        }
        .supplement-card.ergogenic {
            border-left-color: #7c3aed;
        }

        /* Action Box - Exact uniform height for both notes and action items */
        .action-box {
            background: #f8fafc;
            border-radius: 12px;
            border: 1.5px solid #cbd5e1;
            padding: 18px;
            white-space: pre-line;
            font-size: 0.95rem;
            line-height: 1.6;
            color: #1e293b;
            height: 165px !important;
            min-height: 165px !important;
            max-height: 165px !important;
            box-sizing: border-box !important;
            overflow-y: auto;
        }

        /* Equal size, height and border for ALL Action & Export Buttons */
        div[data-testid="stButton"] button,
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stDownloadButton"] a,
        button[data-testid="stBaseButton-secondary"],
        button[data-testid="baseButton-secondary"],
        .stButton button,
        .stDownloadButton button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.86rem !important;
            height: 58px !important;
            min-height: 58px !important;
            max-height: 58px !important;
            border: 1.5px solid #cbd5e1 !important;
            background-color: #ffffff !important;
            color: #0f172a !important;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            width: 100% !important;
            box-sizing: border-box !important;
            padding: 4px 8px !important;
        }

        div[data-testid="stButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover,
        div[data-testid="stDownloadButton"] a:hover,
        button[data-testid="stBaseButton-secondary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        .stButton button:hover,
        .stDownloadButton button:hover {
            border-color: #64748b !important;
            background-color: #f8fafc !important;
            color: #0284c7 !important;
            box-shadow: 0 3px 8px rgba(15, 23, 42, 0.08) !important;
            transform: translateY(-1px);
        }

        /* Center both 1-line and 2-line button text vertically */
        div[data-testid="stButton"] button p,
        div[data-testid="stButton"] button div[data-testid="stMarkdownContainer"],
        div[data-testid="stDownloadButton"] button p,
        button[data-testid="stBaseButton-secondary"] p,
        button[data-testid="baseButton-secondary"] p {
            margin: 0 !important;
            padding: 0 !important;
            font-size: 0.86rem !important;
            font-weight: 600 !important;
            line-height: 1.25 !important;
            color: inherit !important;
            text-align: center !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        div[data-testid="stDownloadButton"],
        div[data-testid="stButton"],
        .stDownloadButton,
        .stButton {
            width: 100% !important;
        }

        /* 4. DEDICATED OVERRIDE: Sleek, compact Open Card button for the master roster ONLY */
        div.roster-btn-container,
        div.roster-btn-container div[data-testid="stButton"] {
        /* DEDICATED OVERRIDE: Sleek, compact Open Card button for the master roster */
        div.roster-btn-container,
        div.roster-btn-container div[data-testid="stButton"] {
            width: 100% !important;
        }

        div.roster-btn-container button,
        div.roster-btn-container .stButton button {
            height: 36px !important;
            min-height: 36px !important;
            max-height: 36px !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            padding: 0 8px !important;
            border-radius: 8px !important;
            border: 1.5px solid #cbd5e1 !important;
            background: #ffffff !important;
            color: #0f172a !important;
            white-space: nowrap !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
            width: 100% !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 4px !important;
            box-sizing: border-box !important;
            overflow: visible !important;
        }

        div.roster-btn-container button:hover {
            border-color: #0284c7 !important;
            color: #0284c7 !important;
            background: #f0f9ff !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 2px 6px rgba(2, 132, 199, 0.15) !important;
        }

        /* Dialog Modal Form Alignment */
        div[data-testid="stDialog"] label,
        div[data-testid="stDialog"] [data-testid="stWidgetLabel"] label,
        div[data-testid="stDialog"] [data-testid="stWidgetLabel"] p {
            min-height: 42px !important;
            height: 42px !important;
            display: flex !important;
            align-items: flex-end !important;
            margin-bottom: 6px !important;
            line-height: 1.2 !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            color: #334155 !important;
        }

        div[data-testid="stDialog"] div[data-testid="stNumberInput"] > div,
        div[data-testid="stDialog"] div[data-testid="stTextInput"] > div,
        div[data-testid="stDialog"] div[data-testid="stDateInput"] > div,
        div[data-testid="stDialog"] div[data-testid="stSelectbox"] > div {
            min-height: 42px !important;
        }

        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_sport_badge(sport_name: str) -> str:
    """Returns a styled, color-coded pill tag for sports discipline."""
    if not sport_name or pd.isna(sport_name):
        return """<span style="background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">Sport</span>"""
    
    s = str(sport_name).strip()
    s_lower = s.lower()
    
    # Semantic sports color palettes (soft background, dark text, clean border)
    if any(w in s_lower for w in ["swim", "water", "diving"]):
        bg, color, border = "#e0f2fe", "#0369a1", "#bae6fd"  # Cyan Ocean
    elif any(w in s_lower for w in ["windsurf", "sail", "surf", "foil"]):
        bg, color, border = "#e0e7ff", "#3730a3", "#c7d2fe"  # Indigo Marine
    elif any(w in s_lower for w in ["triathlon", "ironman"]):
        bg, color, border = "#ccfbf1", "#0f766e", "#99f6e4"  # Teal Endurance
    elif any(w in s_lower for w in ["track", "run", "sprint", "athletics", "1500m", "marathon"]):
        bg, color, border = "#fef3c7", "#92400e", "#fde68a"  # Amber Track
    elif any(w in s_lower for w in ["basket", "ball", "soccer", "tennis", "volleyball"]):
        bg, color, border = "#f3e8ff", "#6b21a8", "#e9d5ff"  # Violet Ball Game
    elif any(w in s_lower for w in ["gymnast", "judo", "combat", "fight", "wrestl"]):
        bg, color, border = "#ffe4e6", "#9f1239", "#fecdd3"  # Rose Combat
    elif any(w in s_lower for w in ["cycl", "bike", "row"]):
        bg, color, border = "#ffedd5", "#9a3412", "#fed7aa"  # Orange Velocity
    else:
        # Stable deterministic hash fallback for any unlisted discipline
        palettes = [
            ("#e0f2fe", "#0369a1", "#bae6fd"),
            ("#e0e7ff", "#3730a3", "#c7d2fe"),
            ("#dcfce7", "#166534", "#bbf7d0"),
            ("#fef3c7", "#92400e", "#fde68a"),
            ("#f3e8ff", "#6b21a8", "#e9d5ff"),
            ("#ffe4e6", "#9f1239", "#fecdd3"),
        ]
        idx = abs(hash(s)) % len(palettes)
        bg, color, border = palettes[idx]

    return f"""<span style="background: {bg}; color: {color}; border: 1px solid {border}; font-size: 0.72rem; font-weight: 700; padding: 2.5px 8px; border-radius: 6px; display: inline-block; white-space: nowrap;">{s}</span>"""

def get_gender_badge(gender: str) -> str:
    """Returns a styled pill tag for gender."""
    g = str(gender).strip().lower() if gender and pd.notna(gender) else "other"
    if "fem" in g:
        return """<span style="background: #fdf2f8; color: #9d174d; border: 1px solid #fbcfe8; font-size: 0.72rem; font-weight: 700; padding: 2.5px 8px; border-radius: 6px; display: inline-block; white-space: nowrap;">♀ Female</span>"""
    elif "male" in g:
        return """<span style="background: #f0f9ff; color: #0369a1; border: 1px solid #bae6fd; font-size: 0.72rem; font-weight: 700; padding: 2.5px 8px; border-radius: 6px; display: inline-block; white-space: nowrap;">♂ Male</span>"""
    else:
        return """<span style="background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; font-size: 0.72rem; font-weight: 700; padding: 2.5px 8px; border-radius: 6px; display: inline-block; white-space: nowrap;">⚧ Other</span>"""

def evaluate_biomarker(name, value, gender="Female"):
    """
    Evaluates biomarker against elite athletic clinical thresholds.
    Returns: (status, status_label, color_class, target_text)
    """
    if pd.isna(value) or value is None:
        return ("unknown", "No Data", "bio-card", "No record on file")
    
    val = float(value)
    name_lower = name.lower()

    if "ferritin" in name_lower:
        threshold = 35.0 if str(gender).lower() == "female" else 40.0
        if val < threshold:
            return ("critical", f"Low ({val:.0f} ng/mL)", "bio-card critical", f"Target: ≥{threshold:.0f} ng/mL (Elite Cutoff)")
        elif val < 50.0:
            return ("warning", f"Borderline ({val:.0f} ng/mL)", "bio-card warning", f"Target: ≥{threshold:.0f} ng/mL (Sub-optimal)")
        else:
            return ("optimal", f"Optimal ({val:.0f} ng/mL)", "bio-card optimal", "Within target elite range")

    elif "hemoglobin" in name_lower:
        low = 12.5 if str(gender).lower() == "female" else 13.8
        high = 16.0 if str(gender).lower() == "female" else 17.5
        if val < low:
            return ("critical", f"Low ({val:.1f} g/dL)", "bio-card critical", f"Ref: {low} - {high} g/dL")
        elif val > high:
            return ("warning", f"Elevated ({val:.1f} g/dL)", "bio-card warning", f"Ref: {low} - {high} g/dL")
        else:
            return ("optimal", f"Normal ({val:.1f} g/dL)", "bio-card optimal", f"Optimal: {low} - {high} g/dL")

    elif "cpk" in name_lower:
        if val > 500.0:
            return ("critical", f"High Damage ({val:.0f} U/L)", "bio-card critical", "Alert: >500 U/L Muscle breakdown")
        elif val > 300.0:
            return ("warning", f"Elevated ({val:.0f} U/L)", "bio-card warning", "Recovery buffer indicated")
        else:
            return ("optimal", f"Normal ({val:.0f} U/L)", "bio-card optimal", "Reference: < 300 U/L")

    elif "vitamin_d" in name_lower:
        if val < 30.0:
            return ("critical", f"Deficient ({val:.0f} ng/mL)", "bio-card critical", "Target: ≥40 ng/mL for athletes")
        elif val < 40.0:
            return ("warning", f"Sub-optimal ({val:.0f} ng/mL)", "bio-card warning", "Target: 40-60 ng/mL")
        else:
            return ("optimal", f"Optimal ({val:.0f} ng/mL)", "bio-card optimal", "Target: 40-70 ng/mL")

    elif "vitamin_b12" in name_lower:
        if val < 350.0:
            return ("warning", f"Borderline ({val:.0f} pg/mL)", "bio-card warning", "Target: ≥450 pg/mL")
        else:
            return ("optimal", f"Adequate ({val:.0f} pg/mL)", "bio-card optimal", "Reference: > 400 pg/mL")

    elif "folic_acid" in name_lower:
        if val < 6.0:
            return ("warning", f"Low ({val:.1f} ng/mL)", "bio-card warning", "Target: ≥7.0 ng/mL")
        else:
            return ("optimal", f"Normal ({val:.1f} ng/mL)", "bio-card optimal", "Reference: > 6.0 ng/mL")

    return ("optimal", f"{val}", "bio-card", "Normal range")

def build_body_comp_chart(anthro_df, comp_name=None, comp_date_str=None):
    """Creates a dual-axis interactive trend chart with target competition markers."""
    if anthro_df.empty:
        return None

    df = anthro_df.copy()
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])
    df = df.sort_values("recorded_at")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Body weight trajectory
    fig.add_trace(
        go.Scatter(
            x=df["recorded_at"],
            y=df["weight_kg"],
            name="Body Weight (kg)",
            mode="lines+markers",
            line=dict(color="#0f172a", width=3),
            marker=dict(size=8, symbol="circle"),
            hovertemplate="<b>Weight:</b> %{y:.1f} kg<br><b>Date:</b> %{x|%d %b %Y}<extra></extra>"
        ),
        secondary_y=False
    )

    # Caliper Fat %
    if df["fat_percentage_caliper"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df["recorded_at"],
                y=df["fat_percentage_caliper"],
                name="Caliper Fat %",
                mode="lines+markers",
                line=dict(color="#2563eb", width=2, dash="dash"),
                marker=dict(size=7, symbol="diamond"),
                hovertemplate="<b>Caliper Fat:</b> %{y:.1f}%<extra></extra>"
            ),
            secondary_y=True
        )

    # DEXA Fat %
    if df["fat_percentage_dexa"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df["recorded_at"],
                y=df["fat_percentage_dexa"],
                name="DEXA Fat %",
                mode="lines+markers",
                line=dict(color="#7c3aed", width=2, dash="dot"),
                marker=dict(size=7, symbol="square"),
                hovertemplate="<b>DEXA Fat:</b> %{y:.1f}%<extra></extra>"
            ),
            secondary_y=True
        )

    # Competition marker
    if comp_date_str:
        try:
            target_dt = pd.to_datetime(comp_date_str)
            fig.add_vline(
                x=target_dt,
                line_width=2,
                line_dash="dashdot",
                line_color="#e11d48",
                annotation_text=f"🎯 {comp_name or 'Competition'}",
                annotation_position="top right"
            )
        except Exception:
            pass

    fig.update_layout(
        title=dict(
            text="<b>Body Composition & Mass Trajectory Over Training Season</b>",
            font=dict(size=14, color="#0f172a"),
            x=0.0,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        xaxis_title="Assessment Date",
        yaxis_title="Body Weight (kg)",
        yaxis2_title="Body Fat (%)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="right",
            x=1.0,
            entrywidth=140,
            entrywidthmode="pixels",
            font=dict(size=11, color="#334155")
        ),
        margin=dict(l=45, r=45, t=85, b=45),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff"
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f1f5f9")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f1f5f9", secondary_y=False)
    fig.update_yaxes(showgrid=False, secondary_y=True)

    return fig

# Backward-compatibility alias
create_body_comp_chart = build_body_comp_chart

def generate_athlete_excel(athlete_data):
    """Generates an aesthetic, multi-tabbed Excel workbook for coaching & medical staff."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Athlete Summary Profile
        profile = athlete_data["profile"]
        profile_dict = {
            "Parameter": [
                "Full Name", "Sport Discipline", "Gender", "Height (cm)",
                "Target Competition", "Target Competition Date",
                "Urgent Clinical Flag", "Urgent Reason"
            ],
            "Value": [
                profile["full_name"], profile["sport_discipline"], profile["gender"], profile["height_cm"],
                profile["target_competition_name"], profile["target_competition_date"],
                "YES" if profile["is_urgent"] else "NO", profile["urgent_reason"] or "None"
            ]
        }
        pd.DataFrame(profile_dict).to_excel(writer, sheet_name="Profile Summary", index=False)

        # Sheet 2: Anthropometrics History
        if not athlete_data["anthro"].empty:
            anthro_export = athlete_data["anthro"][[
                "recorded_at", "weight_kg", "fat_percentage_caliper", 
                "caliper_skinfold_sum", "fat_percentage_dexa", "lean_mass_kg", "measurement_notes"
            ]].rename(columns={
                "recorded_at": "Date",
                "weight_kg": "Weight (kg)",
                "fat_percentage_caliper": "Caliper Body Fat %",
                "caliper_skinfold_sum": "Skinfold Sum (mm)",
                "fat_percentage_dexa": "DEXA Body Fat %",
                "lean_mass_kg": "Lean Mass (kg)",
                "measurement_notes": "Clinical Notes"
            })
            anthro_export.to_excel(writer, sheet_name="Body Composition", index=False)

        # Sheet 3: Blood Biomarkers
        if not athlete_data["blood"].empty:
            blood_export = athlete_data["blood"][[
                "test_date", "hemoglobin", "ferritin", "vitamin_d", 
                "vitamin_b12", "folic_acid", "cpk", "flags_summary"
            ]].rename(columns={
                "test_date": "Date",
                "hemoglobin": "Hemoglobin (g/dL)",
                "ferritin": "Ferritin (ng/mL)",
                "vitamin_d": "Vitamin D (ng/mL)",
                "vitamin_b12": "Vitamin B12 (pg/mL)",
                "folic_acid": "Folic Acid (ng/mL)",
                "cpk": "CPK (U/L)",
                "flags_summary": "Pathology Highlights"
            })
            blood_export.to_excel(writer, sheet_name="Blood Chemistry", index=False)

        # Sheet 4: Supplements Protocol
        if not athlete_data["supps"].empty:
            supps_export = athlete_data["supps"][[
                "category", "supplement_name", "dosage", "timing_and_instructions", "is_active"
            ]].rename(columns={
                "category": "Protocol Category",
                "supplement_name": "Product / Compound",
                "dosage": "Prescribed Dosage",
                "timing_and_instructions": "Timing & Co-ingestion Guidelines",
                "is_active": "Currently Active"
            })
            supps_export.to_excel(writer, sheet_name="Supplement Protocols", index=False)

    output.seek(0)
    return output