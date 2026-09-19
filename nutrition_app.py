import datetime
import pandas as pd
import streamlit as st
import database as db
import utils
import profile_view


# Initialize database schema, backup snapshot, seed data, and styling
db.init_db()
db.perform_daily_backup()
db.seed_mock_data()
utils.inject_custom_css()

@profile_view.make_dialog("👤 Register New Elite Athlete")
def dialog_register_athlete():
    st.caption("Create a new athlete record in the clinic database.")
    with st.form("form_register_athlete", clear_on_submit=True):
        f_name = st.text_input("Full Name:", placeholder="e.g. Alex Morgan")
        col_sp1, col_sp2, col_sp3 = st.columns(3)
        with col_sp1:
            sport = st.text_input("Sport Discipline:", placeholder="e.g. 200m Freestyle Swimming")
        with col_sp2:
            gender = st.selectbox("Gender:", ["Female", "Male", "Other"])
        with col_sp3:
            height = st.number_input("Height (cm):", min_value=120.0, max_value=240.0, value=175.0, step=0.5)

        col_ct1, col_ct2 = st.columns(2)
        with col_ct1:
            email_input = st.text_input("Email Address:", placeholder="e.g. athlete@sports.com")
        with col_ct2:
            phone_input = st.text_input("Phone Number:", placeholder="e.g. +972-52-1234567")

        col_cp1, col_cp2 = st.columns(2)
        with col_cp1:
            comp_name = st.text_input("Target Peak Competition:", placeholder="e.g. Olympic Qualifying Trials")
        with col_cp2:
            comp_date = st.date_input("Target Competition Date:", value=datetime.date.today() + datetime.timedelta(days=60))

        is_urgent = st.checkbox("Trigger Urgent Red Flag Alert (⚠️)", value=False)
        urgent_reason = st.text_area("Urgent Alert Reason (if flagged):", placeholder="e.g. Rapid weight drop noticed; low ferritin.")

        submitted = st.form_submit_button("Register Athlete", use_container_width=True)
        if submitted:
            if not f_name.strip():
                st.error("Athlete name is required.")
            else:
                new_id = db.insert_athlete(
                    f_name.strip(), sport.strip(), gender, height, is_urgent,
                    urgent_reason.strip(), comp_name.strip(), comp_date.strftime("%Y-%m-%d"),
                    email_input.strip(), phone_input.strip()
                )
                st.session_state["selected_athlete_id"] = new_id
                st.session_state["current_page"] = "Athlete Profile"
                st.success(f"Athlete '{f_name}' registered successfully!")
                st.rerun()

def render_dashboard():
    """Renders the master operational roster table with instant clinical alerts."""
    st.title("⚡ Operational Dashboard & Athlete Roster")
    st.caption("Central clinical command center: monitor red flags, consultation cadence, and upcoming peak competitions.")

    df = db.get_all_athletes_summary()

    if df.empty:
        st.info("No athletes currently in the database.")
        if st.button("➕ Register First Athlete"):
            dialog_register_athlete()
        return

    # Top KPI Quick Tiles
    total_athletes = len(df)
    urgent_count = df["is_urgent"].sum()

    today = datetime.date.today()
    expired_blood_count = 0
    for dt in df["latest_blood_date"]:
        if pd.isna(dt):
            expired_blood_count += 1
        else:
            try:
                days = (today - datetime.datetime.strptime(dt, "%Y-%m-%d").date()).days
                if days > 180:
                    expired_blood_count += 1
            except Exception:
                expired_blood_count += 1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Roster</div>
            <div class="metric-value">{total_athletes}</div>
            <div class="metric-sub">Elite Athletes Tracked</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #e11d48;">
            <div class="metric-title" style="color: #e11d48;">Urgent Alerts</div>
            <div class="metric-value" style="color: #e11d48;">{urgent_count}</div>
            <div class="metric-sub">Require Clinical Action</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Overdue Labs (>6m)</div>
            <div class="metric-value" style="color: #d97706;">{expired_blood_count}</div>
            <div class="metric-sub">Need Blood Test Renewal</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Next Major Peak</div>
            <div class="metric-value" style="font-size: 1.25rem;">Olympic Trials</div>
            <div class="metric-sub">16 Days Remaining</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Search and Filter Toolbar
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1, 1, 1])
    with f_col1:
        search_query = st.text_input("🔍 Search athlete or sport:", placeholder="e.g. Maya, Swimming, Windsurfing...")
    with f_col2:
        sport_options = ["All Sports"] + sorted(list(df["sport_discipline"].unique()))
        selected_sport = st.selectbox("Filter by Sport:", sport_options)
    with f_col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        urgent_filter = st.checkbox("Urgent Only (⚠️)", value=False)
    with f_col4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ Add Athlete", use_container_width=True):
            dialog_register_athlete()

    # Apply filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["full_name"].str.contains(search_query, case=False, na=False) |
            filtered_df["sport_discipline"].str.contains(search_query, case=False, na=False)
        ]
    if selected_sport != "All Sports":
        filtered_df = filtered_df[filtered_df["sport_discipline"] == selected_sport]
    if urgent_filter:
        filtered_df = filtered_df[filtered_df["is_urgent"] == 1]

    # Master Athlete Roster Cards
    st.markdown("### Master Athlete Roster")

    for _, row in filtered_df.iterrows():
        # Clean Blood date & expired status
        blood_date_display = row["latest_blood_date"] if pd.notna(row["latest_blood_date"]) else "None"
        blood_is_expired = False
        if pd.notna(row["latest_blood_date"]):
            try:
                days_since_blood = (today - datetime.datetime.strptime(str(row["latest_blood_date"]), "%Y-%m-%d").date()).days
                if days_since_blood > 180:
                    blood_is_expired = True
            except Exception:
                pass

        # Clean Body composition strings
        fat_str = "-"
        if pd.notna(row["fat_percentage_caliper"]):
            fat_str = f"{row['fat_percentage_caliper']:.1f}% (Caliper)"
        elif pd.notna(row["fat_percentage_dexa"]):
            fat_str = f"{row['fat_percentage_dexa']:.1f}% (DEXA)"

        weight_display = f"{row['latest_weight']:.1f} kg" if pd.notna(row['latest_weight']) else "-"
        height_display = f"{row['height_cm']:.1f} cm" if pd.notna(row['height_cm']) else "-"

        # Clean Last Consultation display
        consult_raw = row["latest_consult_date"]
        if pd.notna(consult_raw) and str(consult_raw).strip() != "" and str(consult_raw).lower() != "nan":
            consult_display = str(consult_raw)
        else:
            consult_display = "None"

        # Target competition formatting (Line 3 of Col 2)
        comp_display_text = "🎯 No Target Scheduled"
        if pd.notna(row["target_competition_date"]) and str(row["target_competition_date"]).strip():
            try:
                days_left = (datetime.datetime.strptime(str(row["target_competition_date"]), "%Y-%m-%d").date() - today).days
                c_name = str(row["target_competition_name"] or "Competition")
                if len(c_name) > 22:
                    c_name = c_name[:20] + "..."
                if days_left >= 0:
                    comp_display_text = f"🎯 {c_name} ({days_left}d)"
                else:
                    comp_display_text = f"🎯 {c_name} (Past)"
            except Exception:
                pass

        # Badges for Sport & Gender
        sport_badge = utils.get_sport_badge(row["sport_discipline"])
        gender_badge = utils.get_gender_badge(row["gender"])

        # Individual Athlete Card Container (Guaranteed uniform 3-row layout with generous vertical height)
        with st.container(border=True):
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            card_col1, card_col2, card_col3, card_col4 = st.columns([3.1, 2.7, 2.5, 1.45])

            with card_col1:
                # Row 1: Name + Urgent indicator
                urgent_icon = "⚠️ " if row["is_urgent"] else ""
                st.markdown(f"<div style='font-size: 1.22rem; font-weight: 700; color: #0f172a; line-height: 1.2;'>{urgent_icon}{row['full_name']}</div>", unsafe_allow_html=True)
                
                # Row 2: Badges (Sport discipline + Gender)
                st.markdown(f"<div style='display: flex; gap: 8px; align-items: center; margin: 20px 0;'>{sport_badge} {gender_badge}</div>", unsafe_allow_html=True)
                
                # Row 3: Alert status or stable profile confirmation
                if row["is_urgent"] and row["urgent_reason"]:
                    reason_safe = str(row['urgent_reason'])
                    reason_short = (reason_safe[:42] + '...') if len(reason_safe) > 45 else reason_safe
                    st.markdown(f"<div style='color: #be123c; font-size: 0.84rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{reason_safe}'>🚨 {reason_short}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color: #16a34a; font-size: 0.84rem; font-weight: 600;'>🟢 Stable Profile • In Target</div>", unsafe_allow_html=True)

            with card_col2:
                # Row 1: Weight & Body Fat
                st.markdown(f"<div style='font-size: 0.95rem; color: #1e293b; line-height: 1.2;'><b>Weight:</b> {weight_display} &nbsp;|&nbsp; <b>Fat:</b> {fat_str}</div>", unsafe_allow_html=True)
                
                # Row 2: Height
                st.markdown(f"<div style='font-size: 0.88rem; color: #64748b; margin: 20px 0;'>Height: {height_display}</div>", unsafe_allow_html=True)
                
                # Row 3: Target competition badge
                st.markdown(f"<div style='font-size: 0.84rem; color: #475569; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{comp_display_text}</div>", unsafe_allow_html=True)

            with card_col3:
                # Row 1: Consultation
                st.markdown(f"<div style='font-size: 0.95rem; color: #1e293b; line-height: 1.2;'><b>Consult:</b> {consult_display}</div>", unsafe_allow_html=True)
                
                # Row 2: Blood draw date
                st.markdown(f"<div style='font-size: 0.88rem; color: #64748b; margin: 20px 0;'>Blood: {blood_date_display}</div>", unsafe_allow_html=True)
                
                # Row 3: Blood renewal alert status
                if blood_is_expired:
                    st.markdown("<div style='color: #dc2626; font-size: 0.84rem; font-weight: 700;'>⚠️ Renewal Needed (>6m)</div>", unsafe_allow_html=True)
                elif pd.notna(row["latest_blood_date"]):
                    st.markdown("<div style='color: #16a34a; font-size: 0.84rem; font-weight: 600;'>🟢 Labs Up to Date</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color: #94a3b8; font-size: 0.84rem;'>No Labs on File</div>", unsafe_allow_html=True)

            with card_col4:
                # Compact button centered vertically inside taller card
                st.markdown("<div style='height: 42px;'></div>", unsafe_allow_html=True)
                st.markdown("<div class='roster-btn-container'>", unsafe_allow_html=True)
                if st.button("Open Card →", key=f"btn_athlete_{row['id']}", use_container_width=True):
                    st.session_state["selected_athlete_id"] = int(row['id'])
                    st.session_state["current_page"] = "Athlete Profile"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

def main():
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Dashboard"

    # Sidebar Branding
    st.sidebar.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <div style="
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(2, 132, 199, 0.25);
            flex-shrink: 0;
        ">
            <span style="font-size: 24px; line-height: 1;">⚡</span>
        </div>
        <div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #0f172a; line-height: 1.15; letter-spacing: -0.02em;">ApexNutri</div>
            <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #0284c7; font-weight: 700;">Clinical Portal</div>
        </div>
    </div>
    <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 14px; line-height: 1.35;">
        High-Performance Nutrition & Clinical Management
    </div>
    """, unsafe_allow_html=True)

    df_athletes = db.get_all_athletes_summary()
    athlete_map = dict(zip(df_athletes["id"], df_athletes["full_name"])) if not df_athletes.empty else {}

    # Sidebar Athlete Switcher
    if not df_athletes.empty:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Quick Athlete Switcher:**")
        athlete_ids = list(athlete_map.keys())
        current_idx = 0
        if "selected_athlete_id" in st.session_state and st.session_state["selected_athlete_id"] in athlete_ids:
            current_idx = athlete_ids.index(st.session_state["selected_athlete_id"])

        selected_id = st.sidebar.selectbox(
            "Select Profile:",
            options=athlete_ids,
            index=current_idx,
            format_func=lambda x: athlete_map.get(x, f"Athlete #{x}")
        )
        if st.sidebar.button("Go to Athlete Profile ➔", use_container_width=True):
            st.session_state["selected_athlete_id"] = selected_id
            st.session_state["current_page"] = "Athlete Profile"
            st.rerun()

    # Interactive Storage Directory Settings
    st.sidebar.markdown("---")
    with st.sidebar.expander("📁 Storage Settings", expanded=False):
        st.caption("Customize where this clinic's athlete records, blood tests, and uploaded menus are saved.")
        current_path = db.get_base_dir()
        custom_path_input = st.text_input("Data Folder Path:", value=current_path, help="Paste any folder path on your computer")

        btn_c1, btn_c2 = st.columns([1.2, 1])
        with btn_c1:
            if st.button("💾 Save Path", use_container_width=True):
                if custom_path_input.strip() != current_path:
                    ok, msg = db.set_base_dir(custom_path_input)
                    if ok:
                        st.sidebar.success(msg)
                        st.rerun()
                    else:
                        st.sidebar.error(msg)
                else:
                    st.sidebar.info("Path is already active.")
        with btn_c2:
            if st.button("↺ Reset", use_container_width=True, help="Reset to system default"):
                db.reset_base_dir()
                st.sidebar.info("Reset to default path.")
                st.rerun()

        st.caption(f"**Current:** `{db.BASE_DIR}`")

    # Navigation Routing
    if st.session_state["current_page"] == "Dashboard":
        render_dashboard()
    elif st.session_state["current_page"] == "Athlete Profile":
        athlete_id = st.session_state.get("selected_athlete_id")
        if athlete_id is None and not df_athletes.empty:
            athlete_id = df_athletes.iloc[0]["id"]
            st.session_state["selected_athlete_id"] = athlete_id
        
        if athlete_id:
            profile_view.render_athlete_profile(athlete_id)
        else:
            st.warning("No athlete selected. Returning to dashboard.")
            st.session_state["current_page"] = "Dashboard"
            st.rerun()

if __name__ == "__main__":
    main()