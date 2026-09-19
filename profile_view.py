import os
import datetime
import pandas as pd
import streamlit as st
import database as db
import utils

def make_dialog(title):
    """Provides a seamless modal popup using @st.dialog with fallback for all versions."""
    if hasattr(st, "dialog"):
        return st.dialog(title)
    def fallback_decorator(func):
        def wrapper(*args, **kwargs):
            with st.expander(f"⚙️ {title}", expanded=True):
                return func(*args, **kwargs)
        return wrapper
    return fallback_decorator

@make_dialog("🩸 Log Blood Chemistry Test")
def dialog_add_blood_test(athlete_id, athlete_name):
    st.caption(f"Recording lab results for **{athlete_name}**")
    with st.form("form_dialog_blood", clear_on_submit=True):
        b_date = st.date_input("Blood Draw Date:", value=datetime.date.today())
        
        # Row 1 of lab biomarkers: Equal horizontal baseline
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            val_ferritin = st.number_input("Ferritin (ng/mL):", min_value=0.0, max_value=1000.0, value=35.0, step=1.0)
        with r1_c2:
            val_vitd = st.number_input("25-OH Vitamin D (ng/mL):", min_value=0.0, max_value=200.0, value=45.0, step=1.0)
        with r1_c3:
            val_b12 = st.number_input("Vitamin B12 (pg/mL):", min_value=0.0, max_value=2500.0, value=500.0, step=10.0)

        # Row 2 of lab biomarkers: Equal horizontal baseline
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1:
            val_hb = st.number_input("Hemoglobin (g/dL):", min_value=5.0, max_value=25.0, value=14.0, step=0.1)
        with r2_c2:
            val_cpk = st.number_input("CPK / Creatine Kinase (U/L):", min_value=0.0, max_value=15000.0, value=180.0, step=10.0)
        with r2_c3:
            val_folic = st.number_input("Folic Acid (ng/mL):", min_value=0.0, max_value=100.0, value=10.0, step=0.5)

        b_notes = st.text_area("Pathology Highlights / Flagged Items:", placeholder="e.g. Ferritin depletion noticed; iron replenishment indicated.")
        
        submitted = st.form_submit_button("Save Blood Test Record", use_container_width=True)
        if submitted:
            db.insert_blood_test(athlete_id, b_date.strftime("%Y-%m-%d"), val_hb, val_ferritin, val_vitd, val_b12, val_folic, val_cpk, b_notes)
            st.success("Blood test successfully recorded!")
            st.rerun()

@make_dialog("⚖️ Log Anthropometrics & Weigh-in")
def dialog_add_anthro(athlete_id, athlete_name):
    st.caption(f"Recording body composition for **{athlete_name}**")
    with st.form("form_dialog_anthro", clear_on_submit=True):
        a_date = st.date_input("Date of Assessment:", value=datetime.date.today())
        
        # Row 1 of body comp: Equal horizontal baseline
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            weight = st.number_input("Body Weight (kg):", min_value=30.0, max_value=220.0, value=65.0, step=0.1)
        with r1_c2:
            fat_caliper = st.number_input("Caliper Body Fat (%):", min_value=0.0, max_value=60.0, value=12.5, step=0.1)
        with r1_c3:
            fat_dexa = st.number_input("DEXA Body Fat (%):", min_value=0.0, max_value=60.0, value=13.0, step=0.1)

        # Row 2 of body comp: Equal horizontal baseline
        r2_c1, r2_c2 = st.columns([1, 2])
        with r2_c1:
            lean_mass = st.number_input("Lean Body Mass (FFM kg):", min_value=0.0, max_value=150.0, value=52.0, step=0.1)
        with r2_c2:
            skinfolds = st.number_input("Skinfold Sum (mm, 7-site):", min_value=0.0, max_value=350.0, value=48.0, step=1.0)

        notes = st.text_input("Session Notes:", placeholder="e.g. Standard morning pre-training weigh-in; hydration verified.")

        submitted = st.form_submit_button("Save Assessment Record", use_container_width=True)
        if submitted:
            db.insert_anthropometrics(athlete_id, a_date.strftime("%Y-%m-%d"), weight, fat_caliper, skinfolds, fat_dexa, lean_mass, notes)
            st.success("Anthropometrics saved!")
            st.rerun()

@make_dialog("💊 Prescribe Supplement Protocol")
def dialog_add_supplement(athlete_id, athlete_name):
    st.caption(f"Configuring supplement strategy for **{athlete_name}**")
    with st.form("form_dialog_supp", clear_on_submit=True):
        category = st.radio("Category:", ["CLINICAL", "ERGOGENIC"], horizontal=True, 
                            help="Clinical = Deficiency correction (e.g. Iron, Vit D). Ergogenic = Event performance aids (e.g. Caffeine, Beta-Alanine, Nitrates).")
        name = st.text_input("Product / Compound Name:", placeholder="e.g. Liposomal Iron, Beta-Alanine, Caffeine")
        dosage = st.text_input("Prescribed Dosage:", placeholder="e.g. 30mg daily / 0.3g/kg / 5g daily")
        timing = st.text_area("Timing and Co-ingestion Guidelines:", placeholder="e.g. In the morning with orange juice on an empty stomach; avoid dairy for 2 hours.")

        submitted = st.form_submit_button("Add to Active Protocol", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("Please enter the supplement name.")
            else:
                db.insert_supplement(athlete_id, category, name.strip(), dosage.strip(), timing.strip())
                st.success(f"{name} added to {category.title()} protocols!")
                st.rerun()

@make_dialog("📝 New Consultation & Menu Upload")
def dialog_add_consultation(athlete_id, athlete_name):
    st.caption(f"Logging consultation notes & nutrition plan for **{athlete_name}**")
    with st.form("form_dialog_consult", clear_on_submit=True):
        c_date = st.date_input("Session Date:", value=datetime.date.today())
        c_notes = st.text_area("Internal Dietitian Case Notes:", placeholder="Clinical assessment, gastrointestinal tolerance, training load review...")
        c_actions = st.text_area("Action Items for Athlete:", placeholder="1. 400 kcal liquid recovery smoothie immediately post-workout...\n2. Increase hydration...")
        uploaded_menu = st.file_uploader("Attach Active Nutrition Menu (PDF / Image / Doc):", type=["pdf", "png", "jpg", "docx"])

        submitted = st.form_submit_button("Save Consultation & Plan", use_container_width=True)
        if submitted:
            menu_filename = None
            if uploaded_menu is not None:
                menu_filename = f"{athlete_id}_{datetime.date.today().strftime('%Y%m%d')}_{uploaded_menu.name}"
                save_path = os.path.join(db.UPLOADS_DIR, menu_filename)
                with open(save_path, "wb") as f:
                    f.write(uploaded_menu.getbuffer())

            db.insert_consultation(athlete_id, c_date.strftime("%Y-%m-%d"), c_notes, c_actions, menu_filename)
            st.success("Consultation notes & menu plan saved successfully!")
            st.rerun()

@make_dialog("⚠️ Update Urgent Alert Status")
def dialog_edit_urgent_flag(athlete_id, current_status, current_reason):
    with st.form("form_dialog_urgent", clear_on_submit=True):
        is_urgent = st.checkbox("Mark as High-Priority / Urgent Clinical Attention (⚠️)", value=bool(current_status))
        reason = st.text_area("Urgent Alert Reason / Trigger:", value=str(current_reason or ""), placeholder="e.g. Acute weight reduction, severe ferritin drop, RED-S warning...")

        submitted = st.form_submit_button("Update Alert Status", use_container_width=True)
        if submitted:
            db.update_athlete_urgent(athlete_id, is_urgent, reason)
            st.success("Athlete status updated!")
            st.rerun()

@make_dialog("📏 Update Athlete Height")
def dialog_edit_height(athlete_id, athlete_name, current_height):
    st.caption(f"Adjusting height record for **{athlete_name}** (track growth in developing athletes).")
    with st.form("form_dialog_height", clear_on_submit=True):
        new_height = st.number_input(
            "Current Height (cm):",
            min_value=120.0,
            max_value=240.0,
            value=float(current_height) if current_height else 175.0,
            step=0.5
        )
        submitted = st.form_submit_button("Save Height Update", use_container_width=True)
        if submitted:
            db.update_athlete_height(athlete_id, new_height)
            st.success(f"Height updated to {new_height} cm!")
            st.rerun()

@make_dialog("🎯 Update Target Competition")
def dialog_edit_target_competition(athlete_id, athlete_name, current_name, current_date):
    st.caption(f"Setting peak target competition & date for **{athlete_name}**")
    with st.form("form_dialog_target_comp", clear_on_submit=True):
        new_name = st.text_input(
            "Competition / Championship Name:",
            value=str(current_name or ""),
            placeholder="e.g. Olympic Qualifying Trials / World Championships"
        )
        
        default_date = datetime.date.today() + datetime.timedelta(days=60)
        if current_date:
            try:
                default_date = datetime.datetime.strptime(str(current_date), "%Y-%m-%d").date()
            except Exception:
                pass
                
        new_date = st.date_input("Scheduled Competition Date:", value=default_date)
        
        clear_target = st.checkbox("Clear target competition (no upcoming event scheduled)", value=False)
        
        submitted = st.form_submit_button("Save Target Competition", use_container_width=True)
        if submitted:
            if clear_target:
                db.update_athlete_target_competition(athlete_id, "", "")
                st.success("Target competition cleared!")
            else:
                db.update_athlete_target_competition(athlete_id, new_name.strip(), new_date.strftime("%Y-%m-%d"))
                st.success("Target competition updated!")
            st.rerun()

@make_dialog("📞 Edit Athlete Contact Information")
def dialog_edit_contact(athlete_id, athlete_name, current_email, current_phone):
    st.caption(f"Updating direct communication details for **{athlete_name}**")
    with st.form("form_dialog_contact", clear_on_submit=True):
        new_email = st.text_input(
            "Email Address:",
            value=str(current_email) if (current_email and pd.notna(current_email)) else "",
            placeholder="e.g. athlete@sports.com"
        )
        new_phone = st.text_input(
            "Phone Number:",
            value=str(current_phone) if (current_phone and pd.notna(current_phone)) else "",
            placeholder="e.g. +972-52-1234567"
        )
        submitted = st.form_submit_button("Save Contact Information", use_container_width=True)
        if submitted:
            db.update_athlete_contact(athlete_id, new_email.strip(), new_phone.strip())
            st.success("Contact information successfully updated!")
            st.rerun()

@make_dialog("🗑️ Delete Athlete Profile")
def dialog_confirm_delete(athlete_id, athlete_name):
    st.markdown(f"""
    <div style="background-color: #fff1f2; border: 1.5px solid #fecdd3; border-radius: 8px; padding: 14px; margin-bottom: 14px;">
        <strong style="color: #be123c; font-size: 1.05rem;">Permanent Deletion Warning</strong>
        <p style="color: #881337; margin-top: 6px; font-size: 0.9rem; line-height: 1.4;">
            Are you sure you want to delete <strong>{athlete_name}</strong>? This action will permanently remove:
        </p>
        <ul style="color: #9f1239; font-size: 0.85rem; margin-bottom: 0;">
            <li>All anthropometric and body composition entries</li>
            <li>All recorded blood chemistry tests</li>
            <li>All clinical & ergogenic supplement protocols</li>
            <li>All consultation notes and uploaded menus</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_dialog_delete", clear_on_submit=True):
        confirmed = st.checkbox("I confirm that I want to delete this athlete permanently.", value=False)
        submitted = st.form_submit_button("🚨 Yes, Delete Athlete Permanently", use_container_width=True)
        if submitted:
            if not confirmed:
                st.error("Please mark the confirmation checkbox before deleting.")
            else:
                db.delete_athlete(athlete_id)
                st.session_state["selected_athlete_id"] = None
                st.session_state["current_page"] = "Dashboard"
                st.rerun()

def render_athlete_profile(chosen_id):
    """Renders the comprehensive, modular 360-degree Athlete Profile view with direct action buttons."""
    data = db.get_athlete_full_profile(chosen_id)
    profile = data["profile"]
    anthro_df = data["anthro"]
    blood_df = data["blood"]
    supps_df = data["supps"]
    consults_df = data["consults"]

    if profile is None:
        st.error("Athlete profile could not be found.")
        return

    # Extract clean contact details
    email_val = str(profile["email"]).strip() if ("email" in profile and pd.notna(profile["email"]) and str(profile["email"]).strip()) else "Not provided"
    phone_val = str(profile["phone"]).strip() if ("phone" in profile and pd.notna(profile["phone"]) and str(profile["phone"]).strip()) else "Not provided"

    # Top Navigation Row
    top_col1, top_col2 = st.columns([2.9, 1.5])
    with top_col1:
        st.title(f"{profile['full_name']}")
        st.markdown(f"""
        <div style="font-size: 1.05rem; color: #334155; margin-top: -10px; margin-bottom: 6px; font-weight: 500; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span><strong style="color: #0f172a;">Discipline:</strong> {profile['sport_discipline']}</span>
            <span style="color: #cbd5e1;">|</span>
            <span><strong style="color: #0f172a;">Gender:</strong> {profile['gender']}</span>
            <span style="color: #cbd5e1;">|</span>
            <span><strong style="color: #0f172a;">Height:</strong> {profile['height_cm']} cm</span>
        </div>
        <div style="font-size: 0.88rem; color: #475569; margin-bottom: 14px; display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
            <span>📧 <b>Email:</b> {email_val}</span>
            <span style="color: #cbd5e1;">|</span>
            <span>📱 <b>Phone:</b> {phone_val}</span>
        </div>
        """, unsafe_allow_html=True)
    with top_col2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        h_btn1, h_btn2, h_btn3 = st.columns([1.2, 1.1, 0.9])
        with h_btn1:
            if st.button("← Dashboard", use_container_width=True):
                st.session_state["current_page"] = "Dashboard"
                st.rerun()
        with h_btn2:
            if st.button("📞 Contact", use_container_width=True, help="Edit email and phone"):
                dialog_edit_contact(
                    chosen_id,
                    profile["full_name"],
                    profile["email"] if "email" in profile else "",
                    profile["phone"] if "phone" in profile else ""
                )
        with h_btn3:
            if st.button("🗑️ Delete", use_container_width=True, help="Permanently delete this athlete file"):
                dialog_confirm_delete(chosen_id, profile["full_name"])

    # Target Competition Countdown Banner & In-Context Edit Action
    today = datetime.date.today()
    has_target = bool(profile["target_competition_name"] and profile["target_competition_date"])

    t_col1, t_col2 = st.columns([4.8, 1.2])
    with t_col1:
        if has_target:
            try:
                target_date = datetime.datetime.strptime(profile["target_competition_date"], "%Y-%m-%d").date()
                days_left = (target_date - today).days
                countdown_msg = f"{days_left} Days Remaining" if days_left >= 0 else "Event Completed"
                st.markdown(f"""
                <div class="target-badge">
                    <div>
                        <span style="text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.08em; opacity: 0.9;">Target Competition</span>
                        <div style="font-size: 1.3rem; font-weight: 700; margin-top: 2px;">{profile['target_competition_name']}</div>
                        <span style="font-size: 0.85rem; opacity: 0.9;">Scheduled Date: {profile['target_competition_date']}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.6rem; font-weight: 800;">{countdown_msg}</div>
                        <span style="font-size: 0.8rem; opacity: 0.85;">High Priority Race Phase</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                has_target = False

        if not has_target:
            st.markdown("""
            <div style="border: 1.5px dashed #cbd5e1; border-radius: 12px; padding: 16px 20px; color: #64748b; display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; background: #f8fafc;">
                <div>
                    <strong style="color: #334155; font-size: 1.05rem;">🎯 No Target Competition Scheduled</strong>
                    <div style="font-size: 0.82rem; margin-top: 2px;">Set a primary competition to enable countdown and timeline tracking.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with t_col2:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        btn_label = "🎯 Edit Target" if has_target else "🎯 Set Target"
        if st.button(btn_label, use_container_width=True, help="Update or schedule target competition"):
            dialog_edit_target_competition(
                chosen_id, 
                profile["full_name"], 
                profile["target_competition_name"], 
                profile["target_competition_date"]
            )

    # Urgent Banner (if flagged)
    if profile["is_urgent"]:
        st.markdown(f"""
        <div class="urgent-banner">
            <strong>⚠️ URGENT CLINICAL ATTENTION REQUIRED:</strong><br>
            {profile['urgent_reason'] or 'Clinically flagged for immediate review.'}
        </div>
        """, unsafe_allow_html=True)

    # In-Context Quick Action Bar directly on the Athlete's Profile
    st.markdown("##### ⚡ Quick Clinical Actions")
    act1, act2, act3, act4, act5, act6 = st.columns(6)
    with act1:
        if st.button("🩸 Add Blood Test", use_container_width=True):
            dialog_add_blood_test(chosen_id, profile["full_name"])
    with act2:
        if st.button("⚖️ Log Weigh-in", use_container_width=True):
            dialog_add_anthro(chosen_id, profile["full_name"])
    with act3:
        if st.button("📏 Edit Height", use_container_width=True):
            dialog_edit_height(chosen_id, profile["full_name"], profile["height_cm"])
    with act4:
        if st.button("💊 Add Supplement", use_container_width=True):
            dialog_add_supplement(chosen_id, profile["full_name"])
    with act5:
        if st.button("📝 Add Menu / Consult", use_container_width=True):
            dialog_add_consultation(chosen_id, profile["full_name"])
    with act6:
        if st.button("⚠️ Edit Alert", use_container_width=True):
            dialog_edit_urgent_flag(chosen_id, profile["is_urgent"], profile["urgent_reason"])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # KPI Metric Cards
    latest_weight = f"{anthro_df.iloc[-1]['weight_kg']:.1f}" if not anthro_df.empty else "-"
    latest_caliper = f"{anthro_df.iloc[-1]['fat_percentage_caliper']:.1f}%" if (not anthro_df.empty and pd.notna(anthro_df.iloc[-1]["fat_percentage_caliper"])) else "-"
    latest_dexa = f"{anthro_df.iloc[-1]['fat_percentage_dexa']:.1f}%" if (not anthro_df.empty and pd.notna(anthro_df.iloc[-1]["fat_percentage_dexa"])) else "-"
    latest_lean = f"{anthro_df.iloc[-1]['lean_mass_kg']:.1f} kg" if (not anthro_df.empty and pd.notna(anthro_df.iloc[-1]["lean_mass_kg"])) else "-"
    last_consult_str = consults_df.iloc[0]["session_date"] if not consults_df.empty else "None"

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Current Weight</div>
            <div class="metric-value">{latest_weight} <span style="font-size: 1rem; font-weight: 500;">kg</span></div>
            <div class="metric-sub">Height: {profile['height_cm']} cm</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Caliper Fat %</div>
            <div class="metric-value">{latest_caliper}</div>
            <div class="metric-sub">Skinfold Protocol</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">DEXA Fat %</div>
            <div class="metric-value">{latest_dexa}</div>
            <div class="metric-sub">Dual-Energy Scan</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Lean Body Mass</div>
            <div class="metric-value">{latest_lean}</div>
            <div class="metric-sub">FFM Target</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Last Consultation</div>
            <div class="metric-value" style="font-size: 1.15rem;">{last_consult_str}</div>
            <div class="metric-sub">{profile['sport_discipline']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🔬 Biomarker Spotlight (Clinical Blood Work)")
    st.caption("Surveillance of key biomarkers critical for elite endurance, oxygen carrying capacity, and tissue integrity.")

    if not blood_df.empty:
        latest_b = blood_df.iloc[0]
        test_dt = latest_b["test_date"]
        st.markdown(f"**Latest Blood Test Recorded:** `{test_dt}`")

        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            st1, lbl1, cls1, tgt1 = utils.evaluate_biomarker("Ferritin", latest_b["ferritin"], profile["gender"])
            st.markdown(f"""
            <div class="{cls1}">
                <div style="font-weight: 700; color: #0f172a;">Ferritin (Iron Reserve)</div>
                <div style="font-size: 1.35rem; font-weight: 800; margin: 4px 0;">{lbl1}</div>
                <div style="font-size: 0.78rem; color: #64748b;">{tgt1}</div>
            </div>
            """, unsafe_allow_html=True)

            st2, lbl2, cls2, tgt2 = utils.evaluate_biomarker("Hemoglobin", latest_b["hemoglobin"], profile["gender"])
            st.markdown(f"""
            <div class="{cls2}">
                <div style="font-weight: 700; color: #0f172a;">Hemoglobin</div>
                <div style="font-size: 1.35rem; font-weight: 800; margin: 4px 0;">{lbl2}</div>
                <div style="font-size: 0.78rem; color: #64748b;">{tgt2}</div>
            </div>
            """, unsafe_allow_html=True)

        with b_col2:
            st3, lbl3, cls3, tgt3 = utils.evaluate_biomarker("Vitamin D", latest_b["vitamin_d"], profile["gender"])
            st.markdown(f"""
            <div class="{cls3}">
                <div style="font-weight: 700; color: #0f172a;">25-OH Vitamin D</div>
                <div style="font-size: 1.35rem; font-weight: 800; margin: 4px 0;">{lbl3}</div>
                <div style="font-size: 0.78rem; color: #64748b;">{tgt3}</div>
            </div>
            """, unsafe_allow_html=True)

            st4, lbl4, cls4, tgt4 = utils.evaluate_biomarker("CPK", latest_b["cpk"], profile["gender"])
            st.markdown(f"""
            <div class="{cls4}">
                <div style="font-weight: 700; color: #0f172a;">Creatine Kinase (CPK)</div>
                <div style="font-size: 1.35rem; font-weight: 800; margin: 4px 0;">{lbl4}</div>
                <div style="font-size: 0.78rem; color: #64748b;">{tgt4}</div>
            </div>
            """, unsafe_allow_html=True)

        with b_col3:
            st5, lbl5, cls5, tgt5 = utils.evaluate_biomarker("Vitamin B12", latest_b["vitamin_b12"], profile["gender"])
            st.markdown(f"""
            <div class="{cls5}">
                <div style="font-weight: 700; color: #0f172a;">Vitamin B12</div>
                <div style="font-size: 1.35rem; font-weight: 800; margin: 4px 0;">{lbl5}</div>
                <div style="font-size: 0.78rem; color: #64748b;">{tgt5}</div>
            </div>
            """, unsafe_allow_html=True)

            st6, lbl6, cls6, tgt6 = utils.evaluate_biomarker("Folic Acid", latest_b["folic_acid"], profile["gender"])
            st.markdown(f"""
            <div class="{cls6}">
                <div style="font-weight: 700; color: #0f172a;">Folic Acid</div>
                <div style="font-size: 1.35rem; font-weight: 800; margin: 4px 0;">{lbl6}</div>
                <div style="font-size: 0.78rem; color: #64748b;">{tgt6}</div>
            </div>
            """, unsafe_allow_html=True)

        if pd.notna(latest_b.get("flags_summary")) and str(latest_b["flags_summary"]).strip():
            st.info(f"**Clinical Lab Notes:** {latest_b['flags_summary']}")
    else:
        st.info("No blood lab tests logged yet for this athlete. Click **'🩸 Add Blood Test'** above to enter results.")

    st.markdown("### 💊 Structured Supplementation Protocols")
    st.caption("Clinical distinction between medical deficiency corrections and event ergogenic performance aids.")

    tab_clinical, tab_ergogenic = st.tabs(["🏥 Medical / Clinical Supplements", "⚡ Ergogenic Performance Aids"])

    with tab_clinical:
        clin_supps = supps_df[supps_df["category"] == "CLINICAL"] if not supps_df.empty else pd.DataFrame()
        if not clin_supps.empty:
            for _, s in clin_supps.iterrows():
                col_c1, col_c2 = st.columns([5, 1])
                with col_c1:
                    st.markdown(f"""
                    <div class="supplement-card clinical">
                        <div style="font-size: 1.05rem; font-weight: 700; color: #0e7490;">{s['supplement_name']}</div>
                        <div style="font-weight: 600; color: #1e293b; margin: 2px 0;">Dosage: {s['dosage']}</div>
                        <div style="font-size: 0.88rem; color: #475569; margin-top: 4px;"><b>Clinical Protocol:</b> {s['timing_and_instructions']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_c2:
                    if st.button("Remove", key=f"del_supp_{s['id']}"):
                        db.delete_supplement(s['id'])
                        st.rerun()
        else:
            st.write("No active medical supplements prescribed.")

    with tab_ergogenic:
        ergo_supps = supps_df[supps_df["category"] == "ERGOGENIC"] if not supps_df.empty else pd.DataFrame()
        if not ergo_supps.empty:
            for _, s in ergo_supps.iterrows():
                col_e1, col_e2 = st.columns([5, 1])
                with col_e1:
                    st.markdown(f"""
                    <div class="supplement-card ergogenic">
                        <div style="font-size: 1.05rem; font-weight: 700; color: #6d28d9;">{s['supplement_name']}</div>
                        <div style="font-weight: 600; color: #1e293b; margin: 2px 0;">Dosage: {s['dosage']}</div>
                        <div style="font-size: 0.88rem; color: #475569; margin-top: 4px;"><b>Timing & Strategy:</b> {s['timing_and_instructions']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_e2:
                    if st.button("Remove", key=f"del_ergo_{s['id']}"):
                        db.delete_supplement(s['id'])
                        st.rerun()
        else:
            st.write("No ergogenic aid protocols currently active.")

    st.markdown("### 📈 Body Composition & Mass Trajectory")
    if not anthro_df.empty:
        fig = utils.build_body_comp_chart(
            anthro_df,
            profile["target_competition_name"],
            profile["target_competition_date"]
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No anthropometric records logged yet. Click **'⚖️ Log Weigh-in'** above to begin tracking.")

    st.markdown("### 📋 Clinical Notes & Action Plan")
    col_notes, col_actions = st.columns(2)

    latest_consult = consults_df.iloc[0] if not consults_df.empty else None

    with col_notes:
        st.markdown("**Internal Dietitian Case Notes**")
        if latest_consult is not None and pd.notna(latest_consult["summary_and_conclusions"]) and str(latest_consult["summary_and_conclusions"]).strip():
            st.markdown(f"""
            <div class="action-box">
                {latest_consult['summary_and_conclusions']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write("No case notes recorded.")

    with col_actions:
        st.markdown("**Action Items for Athlete (Printable)**")
        if latest_consult is not None and pd.notna(latest_consult["athlete_recommendations"]) and str(latest_consult["athlete_recommendations"]).strip():
            st.markdown(f"""
            <div class="action-box" style="border-left: 4px solid #16a34a; background: #f0fdf4;">
                {latest_consult['athlete_recommendations']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write("No direct action items assigned.")

    # Menu Download if available
    if latest_consult is not None and pd.notna(latest_consult["menu_file_name"]) and str(latest_consult["menu_file_name"]).strip():
        file_path = os.path.join(db.UPLOADS_DIR, str(latest_consult["menu_file_name"]))
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"📄 Download Current Active Nutrition Plan ({latest_consult['menu_file_name']})",
                    data=f.read(),
                    file_name=str(latest_consult["menu_file_name"]),
                    mime="application/pdf"
                )

    st.markdown("---")
    st.markdown("### 📤 Export & Sharing")
    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        excel_data = utils.generate_athlete_excel(data)
        st.download_button(
            label="📊 Download Formatted Excel Report",
            data=excel_data,
            file_name=f"{profile['full_name'].replace(' ', '_')}_Nutrition_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with exp_col2:
        if st.button("🖨️ Printable Summary View", use_container_width=True):
            st.markdown("""
            <script>
                window.print();
            </script>
            """, unsafe_allow_html=True)
            st.success("Use your browser's Print Dialog (Ctrl+P or Cmd+P) to save this page as a clean PDF.")