import os
import shutil
import sqlite3
import datetime
import json
import pandas as pd

# Default fallback path
DEFAULT_BASE_DIR = r"C:\Ilai\fun_analysis\nutrition_athletes_managment"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def get_base_dir() -> str:
    """Reads configured base directory from config.json, or falls back to default."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                configured_path = cfg.get("base_dir", "").strip()
                if configured_path:
                    return configured_path
        except Exception:
            pass
    return DEFAULT_BASE_DIR

def update_paths(base_path: str):
    """Updates module-level directory paths and ensures folders exist."""
    global BASE_DIR, DATA_DIR, UPLOADS_DIR, BACKUPS_DIR, DB_PATH
    BASE_DIR = os.path.abspath(base_path)
    DATA_DIR = os.path.join(BASE_DIR, "data")
    UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
    BACKUPS_DIR = os.path.join(DATA_DIR, "backups")
    DB_PATH = os.path.join(DATA_DIR, "sports_nutrition.db")

    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        os.makedirs(BACKUPS_DIR, exist_ok=True)
    except Exception:
        # Fallback to local script working directory if restricted
        BASE_DIR = os.path.abspath("./nutrition_management")
        DATA_DIR = os.path.join(BASE_DIR, "data")
        UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
        BACKUPS_DIR = os.path.join(DATA_DIR, "backups")
        DB_PATH = os.path.join(DATA_DIR, "sports_nutrition.db")
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        os.makedirs(BACKUPS_DIR, exist_ok=True)

# Initialize paths on module load
update_paths(get_base_dir())

def set_base_dir(new_path: str):
    """Saves new custom path to config.json, updates system paths, and initializes database schema."""
    cleaned_path = new_path.strip()
    if not cleaned_path:
        return False, "Folder path cannot be empty."

    try:
        os.makedirs(cleaned_path, exist_ok=True)
        test_file = os.path.join(cleaned_path, ".perm_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
    except Exception as e:
        return False, f"Cannot write to specified directory: {str(e)}"

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"base_dir": cleaned_path}, f, indent=4)
        update_paths(cleaned_path)
        init_db()
        perform_daily_backup()
        return True, "Storage directory successfully updated!"
    except Exception as e:
        return False, f"Failed to save settings: {str(e)}"

def reset_base_dir():
    """Resets path back to default and cleans up config.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
        except Exception:
            pass
    update_paths(DEFAULT_BASE_DIR)
    init_db()

def get_db_connection():
    """Returns a thread-safe connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def perform_daily_backup():
    """Creates a timestamped snapshot of the local database."""
    if os.path.exists(DB_PATH):
        today_str = datetime.date.today().strftime("%Y%m%d")
        backup_file = os.path.join(BACKUPS_DIR, f"sports_nutrition_backup_{today_str}.db")
        if not os.path.exists(backup_file):
            try:
                shutil.copy2(DB_PATH, backup_file)
            except Exception:
                pass

def init_db():
    """Initializes tables matching the clinical specifications."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Athletes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS athletes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        sport_discipline TEXT NOT NULL,
        gender TEXT DEFAULT 'Female',
        birth_date TEXT,
        height_cm REAL,
        is_urgent INTEGER DEFAULT 0,
        urgent_reason TEXT,
        target_competition_name TEXT,
        target_competition_date TEXT,
        email TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Automatic migration for existing databases lacking email or phone
    cursor.execute("PRAGMA table_info(athletes)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    if "email" not in existing_cols:
        cursor.execute("ALTER TABLE athletes ADD COLUMN email TEXT")
    if "phone" not in existing_cols:
        cursor.execute("ALTER TABLE athletes ADD COLUMN phone TEXT")

    # Anthropometrics Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anthropometrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        athlete_id INTEGER NOT NULL,
        recorded_at TEXT NOT NULL,
        weight_kg REAL NOT NULL,
        fat_percentage_caliper REAL,
        caliper_skinfold_sum REAL,
        fat_percentage_dexa REAL,
        lean_mass_kg REAL,
        measurement_notes TEXT,
        FOREIGN KEY (athlete_id) REFERENCES athletes (id) ON DELETE CASCADE
    );
    """)

    # Blood Tests Table (Spotlighting key biomarkers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blood_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        athlete_id INTEGER NOT NULL,
        test_date TEXT NOT NULL,
        hemoglobin REAL,
        ferritin REAL,
        vitamin_d REAL,
        vitamin_b12 REAL,
        folic_acid REAL,
        cpk REAL,
        flags_summary TEXT,
        raw_file_name TEXT,
        FOREIGN KEY (athlete_id) REFERENCES athletes (id) ON DELETE CASCADE
    );
    """)

    # Supplement Protocols Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS supplements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        athlete_id INTEGER NOT NULL,
        category TEXT NOT NULL, -- 'CLINICAL' or 'ERGOGENIC'
        supplement_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        timing_and_instructions TEXT,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (athlete_id) REFERENCES athletes (id) ON DELETE CASCADE
    );
    """)

    # Consultations and Clinical Notes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        athlete_id INTEGER NOT NULL,
        session_date TEXT NOT NULL,
        summary_and_conclusions TEXT,
        athlete_recommendations TEXT,
        menu_file_name TEXT,
        FOREIGN KEY (athlete_id) REFERENCES athletes (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def seed_mock_data():
    """Populates realistic test cases for Olympic & elite athletes on first boot."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM athletes")
    if cursor.fetchone()[0] == 0:
        athletes = [
            ("Maya Ronen", "Open Water Swimming", "Female", "2001-04-12", 174.0, 1,
             "Critical Ferritin (22 ng/mL) & 2.4% rapid weight loss before trials",
             "Olympic Open Water Trials", (datetime.date.today() + datetime.timedelta(days=16)).strftime("%Y-%m-%d"),
             "maya.ronen@swim.org.il", "+972-52-4567890"),
            ("Daniel Levin", "Windsurfing (iQFOiL)", "Male", "1998-08-25", 186.0, 1,
             "Acute muscle breakdown (CPK 920 U/L) following high-volume loading cycle",
             "iQFOiL World Championships", (datetime.date.today() + datetime.timedelta(days=42)).strftime("%Y-%m-%d"),
             "daniel.levin@windsurf.org", "+972-54-9876543"),
            ("Noam Cohen", "Triathlon (Olympic Distance)", "Male", "1996-01-15", 179.0, 0,
             "", "European Triathlon Cup", (datetime.date.today() + datetime.timedelta(days=58)).strftime("%Y-%m-%d"),
             "noam.triathlon@gmail.com", "+972-50-1234567"),
            ("Eden Ben-David", "Track & Field (1500m)", "Female", "2003-11-03", 168.0, 0,
             "", "National Championships", (datetime.date.today() + datetime.timedelta(days=75)).strftime("%Y-%m-%d"),
             "eden.track@athletics.org", "+972-53-3344556"),
            ("Tomer Gal", "Basketball (Guard)", "Male", "1999-06-20", 192.0, 0,
             "", "Playoff Finals", (datetime.date.today() + datetime.timedelta(days=28)).strftime("%Y-%m-%d"),
             "tomer.gal@hoops.club", "+972-58-7788990")
        ]
        cursor.executemany("""
            INSERT INTO athletes (full_name, sport_discipline, gender, birth_date, height_cm, is_urgent, urgent_reason, target_competition_name, target_competition_date, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, athletes)
        conn.commit()

        # Seed Anthropometrics
        anthro = [
            (1, "2026-06-15", 62.5, 17.2, 68.0, 18.0, 51.2, "Baseline conditioning block"),
            (1, "2026-07-28", 61.8, 16.5, 63.0, 17.3, 51.1, "Altitude training camp"),
            (1, "2026-09-02", 60.3, 15.1, 56.0, 15.8, 50.8, "Rapid mass drop noticed - RED-S screening"),

            (2, "2026-05-10", 87.5, 12.8, 52.0, 13.5, 75.8, "Pre-season calibration"),
            (2, "2026-07-20", 88.0, 12.2, 49.0, 12.9, 76.6, "Hypertrophy and harness power test"),
            (2, "2026-08-30", 88.2, 12.0, 48.0, 12.6, 77.0, "Stable body composition"),

            (3, "2026-06-01", 69.5, 9.8, 38.0, 10.4, 62.2, "Aerobic base peak"),
            (3, "2026-08-15", 68.8, 9.2, 35.0, 9.9, 62.0, "Race readiness check"),

            (4, "2026-05-18", 53.0, 14.2, 54.0, 14.8, 45.1, "Track season opener"),
            (4, "2026-08-22", 52.6, 13.8, 51.0, 14.2, 45.0, "Mid-season assessment"),

            (5, "2026-06-10", 86.0, 11.5, 45.0, 12.1, 75.6, "Post-rehab clearance"),
            (5, "2026-08-25", 86.5, 11.2, 43.0, 11.8, 76.3, "On-court conditioning")
        ]
        cursor.executemany("""
            INSERT INTO anthropometrics (athlete_id, recorded_at, weight_kg, fat_percentage_caliper, caliper_skinfold_sum, fat_percentage_dexa, lean_mass_kg, measurement_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, anthro)

        # Seed Blood Tests
        blood = [
            (1, "2026-03-10", 13.2, 44.0, 48.0, 520.0, 8.5, 180.0, "Normal baseline", None),
            (1, "2026-08-28", 12.1, 22.0, 39.0, 440.0, 6.8, 290.0, "Low Ferritin (<30 threshold), Hb drop", None),

            (2, "2026-04-12", 15.6, 75.0, 54.0, 680.0, 11.2, 210.0, "Normal profiles", None),
            (2, "2026-08-29", 15.2, 68.0, 48.0, 590.0, 9.5, 920.0, "Acute muscle breakdown (High CPK)", None),

            (3, "2026-07-15", 14.9, 58.0, 52.0, 620.0, 10.4, 240.0, "Solid physiological parameters", None),

            (4, "2026-01-20", 12.8, 38.0, 24.0, 380.0, 7.1, 160.0, "Low Vitamin D; supplement prescribed", None),

            (5, "2025-11-14", 15.4, 82.0, 42.0, 510.0, 8.9, 195.0, "Old baseline", None)
        ]
        cursor.executemany("""
            INSERT INTO blood_tests (athlete_id, test_date, hemoglobin, ferritin, vitamin_d, vitamin_b12, folic_acid, cpk, flags_summary, raw_file_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, blood)

        # Seed Supplements
        supps = [
            (1, "CLINICAL", "Liposomal Iron Bisglycinate", "30 mg elemental iron daily", "In the morning on empty stomach with Vitamin C (fresh orange juice). Strict avoidance of dairy, tea, and coffee for 2 hours.", 1),
            (1, "CLINICAL", "Vitamin D3 + K2 Liquid Drops", "3,000 IU daily", "Take with main meal containing dietary fats (avocado or olive oil).", 1),
            (1, "ERGOGENIC", "Sodium Bicarbonate (Enteric Coated)", "0.3 g/kg body weight (~18g)", "Take 120-150 minutes prior to race start with 1L water + 50g simple carbs. Test in high-intensity simulation first.", 1),
            (1, "ERGOGENIC", "Concentrated Beetroot Juice (Nitrates)", "400 mg dietary nitrates", "Take 2.5 to 3 hours before start to enhance endurance economy and peripheral vasodilation.", 1),

            (2, "CLINICAL", "Omega-3 Triglyceride", "2,000 mg (1,200 EPA / 600 DHA)", "Take with dinner to modulate systemic inflammatory cascade post foil pumping.", 1),
            (2, "ERGOGENIC", "Creatine Monohydrate (Creapure)", "5 g daily maintenance", "Post-workout blended into recovery shake with 30g protein + 60g carbohydrates.", 1),
            (2, "ERGOGENIC", "Anhydrous Caffeine", "3 mg/kg (~265 mg)", "Take 45-60 minutes prior to medal race heats.", 1),

            (3, "ERGOGENIC", "Beta-Alanine", "4.8 g daily (split 4 x 1.2g)", "Consistent daily dosing with meals to elevate intramuscular carnosine buffering capacity.", 1),
            (3, "ERGOGENIC", "Caffeine Gels Protocol", "100 mg at T2 transition", "Immediate central fatigue offset for final 10km run leg.", 1)
        ]
        cursor.executemany("""
            INSERT INTO supplements (athlete_id, category, supplement_name, dosage, timing_and_instructions, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, supps)

        # Seed Consultations
        consultations = [
            (1, "2026-09-02",
             "Athlete reports persistent heavy legs and disrupted sleep. Weight dropped 1.5kg in 2 weeks. Suspected low energy availability (RED-S risk). Blood work confirmed ferritin drop to 22 ng/mL.",
             "1. Immediately initiate liposomal iron supplementation.\n2. Add 400 kcal liquid recovery smoothie immediately post-swim session.\n3. Increase carbohydrate availability to 8g/kg on hard training days.\n4. Re-weigh twice weekly under standardized morning conditions.",
             "Maya_Olympic_Trials_Carb_Loading_Protocol.pdf"),
            (2, "2026-08-30",
             "CPK peaked at 920 U/L following consecutive 4-hour foil pumping sessions in choppy water. Hydration markers indicate mild hypohydration.",
             "1. Implement high-sodium rehydration protocol (800mg Na+/L).\n2. Maintain 2g protein/kg body weight.\n3. Tart cherry juice concentrate 30ml twice daily for muscle recovery.",
             "Daniel_Windsurfing_Offshore_Hydration.pdf"),
            (3, "2026-08-16",
             "Race weight right on target. Excellent gastrointestinal tolerance during 90g/hr carbohydrate gut-training trial.",
             "1. Maintain current race fueling blueprint.\n2. Sodium loading 24h prior to event.",
             "Noam_Triathlon_Race_Nutrition_Strategy.pdf")
        ]
        cursor.executemany("""
            INSERT INTO consultations (athlete_id, session_date, summary_and_conclusions, athlete_recommendations, menu_file_name)
            VALUES (?, ?, ?, ?, ?)
        """, consultations)

        conn.commit()
    conn.close()

def get_all_athletes_summary():
    """Retrieves full list of athletes merged with their latest stats and consultation."""
    conn = get_db_connection()
    query = """
    WITH LatestAnthro AS (
        SELECT athlete_id, weight_kg, fat_percentage_caliper, fat_percentage_dexa, recorded_at,
               ROW_NUMBER() OVER(PARTITION BY athlete_id ORDER BY recorded_at DESC) as rn
        FROM anthropometrics
    ),
    LatestBlood AS (
        SELECT athlete_id, test_date,
               ROW_NUMBER() OVER(PARTITION BY athlete_id ORDER BY test_date DESC) as rn
        FROM blood_tests
    ),
    LatestConsult AS (
        SELECT athlete_id, session_date,
               ROW_NUMBER() OVER(PARTITION BY athlete_id ORDER BY session_date DESC) as rn
        FROM consultations
    )
    SELECT 
        a.id,
        a.full_name,
        a.sport_discipline,
        a.gender,
        a.birth_date,
        a.height_cm,
        a.is_urgent,
        a.urgent_reason,
        a.target_competition_name,
        a.target_competition_date,
        la.weight_kg as latest_weight,
        la.fat_percentage_caliper,
        la.fat_percentage_dexa,
        la.recorded_at as latest_weigh_date,
        lb.test_date as latest_blood_date,
        lc.session_date as latest_consult_date
    FROM athletes a
    LEFT JOIN LatestAnthro la ON a.id = la.athlete_id AND la.rn = 1
    LEFT JOIN LatestBlood lb ON a.id = lb.athlete_id AND lb.rn = 1
    LEFT JOIN LatestConsult lc ON a.id = lc.athlete_id AND lc.rn = 1
    ORDER BY a.is_urgent DESC, a.full_name ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_athlete_full_profile(athlete_id):
    """Fetches all records for a selected athlete."""
    conn = get_db_connection()
    athlete = pd.read_sql_query("SELECT * FROM athletes WHERE id = ?", conn, params=(athlete_id,))
    anthro = pd.read_sql_query("SELECT * FROM anthropometrics WHERE athlete_id = ? ORDER BY recorded_at ASC", conn, params=(athlete_id,))
    blood = pd.read_sql_query("SELECT * FROM blood_tests WHERE athlete_id = ? ORDER BY test_date DESC", conn, params=(athlete_id,))
    supps = pd.read_sql_query("SELECT * FROM supplements WHERE athlete_id = ? ORDER BY category, supplement_name", conn, params=(athlete_id,))
    consults = pd.read_sql_query("SELECT * FROM consultations WHERE athlete_id = ? ORDER BY session_date DESC", conn, params=(athlete_id,))
    conn.close()
    return {
        "profile": athlete.iloc[0] if not athlete.empty else None,
        "anthro": anthro,
        "blood": blood,
        "supps": supps,
        "consults": consults
    }

def insert_athlete(full_name, sport_discipline, gender, height_cm, is_urgent, urgent_reason, target_name, target_date, email="", phone=""):
    """Registers a new athlete into the system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO athletes (full_name, sport_discipline, gender, height_cm, is_urgent, urgent_reason, target_competition_name, target_competition_date, email, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (full_name, sport_discipline, gender, height_cm, 1 if is_urgent else 0, urgent_reason, target_name, target_date, email, phone))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_athlete_urgent(athlete_id, is_urgent, urgent_reason):
    """Updates urgent status flag and reasoning for an athlete."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE athletes 
        SET is_urgent = ?, urgent_reason = ?
        WHERE id = ?
    """, (1 if is_urgent else 0, urgent_reason, athlete_id))
    conn.commit()
    conn.close()

def update_athlete_height(athlete_id, height_cm):
    """Updates the height record for an athlete as they grow."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE athletes 
        SET height_cm = ?
        WHERE id = ?
    """, (height_cm, athlete_id))
    conn.commit()
    conn.close()

def update_athlete_target_competition(athlete_id, target_name, target_date):
    """Updates the target competition name and scheduled date for an athlete."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE athletes 
        SET target_competition_name = ?, target_competition_date = ?
        WHERE id = ?
    """, (target_name, target_date, athlete_id))
    conn.commit()
    conn.close()

def update_athlete_contact(athlete_id, email, phone):
    """Updates the contact details (email and phone) for an athlete."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE athletes 
        SET email = ?, phone = ?
        WHERE id = ?
    """, (email, phone, athlete_id))
    conn.commit()
    conn.close()

def delete_athlete(athlete_id):
    """Permanently removes an athlete and all their linked clinical records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM anthropometrics WHERE athlete_id = ?", (athlete_id,))
    cursor.execute("DELETE FROM blood_tests WHERE athlete_id = ?", (athlete_id,))
    cursor.execute("DELETE FROM supplements WHERE athlete_id = ?", (athlete_id,))
    cursor.execute("DELETE FROM consultations WHERE athlete_id = ?", (athlete_id,))
    cursor.execute("DELETE FROM athletes WHERE id = ?", (athlete_id,))
    conn.commit()
    conn.close()

def insert_blood_test(athlete_id, test_date, hb, ferritin, vit_d, b12, folic, cpk, flags_summary):
    """Saves a new blood test entry for an athlete."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO blood_tests (athlete_id, test_date, hemoglobin, ferritin, vitamin_d, vitamin_b12, folic_acid, cpk, flags_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (athlete_id, test_date, hb, ferritin, vit_d, b12, folic, cpk, flags_summary))
    conn.commit()
    conn.close()

def insert_anthropometrics(athlete_id, recorded_at, weight, fat_caliper, skinfolds, fat_dexa, lean_mass, notes):
    """Saves a new body composition assessment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO anthropometrics (athlete_id, recorded_at, weight_kg, fat_percentage_caliper, caliper_skinfold_sum, fat_percentage_dexa, lean_mass_kg, measurement_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (athlete_id, recorded_at, weight, fat_caliper, skinfolds, fat_dexa, lean_mass, notes))
    conn.commit()
    conn.close()

def insert_supplement(athlete_id, category, name, dosage, timing):
    """Adds a supplement protocol for an athlete."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO supplements (athlete_id, category, supplement_name, dosage, timing_and_instructions, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (athlete_id, category, name, dosage, timing))
    conn.commit()
    conn.close()

def delete_supplement(supplement_id):
    """Deletes a supplement protocol record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM supplements WHERE id = ?", (supplement_id,))
    conn.commit()
    conn.close()

def insert_consultation(athlete_id, session_date, case_notes, athlete_actions, menu_filename):
    """Saves a consultation note and menu link."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO consultations (athlete_id, session_date, summary_and_conclusions, athlete_recommendations, menu_file_name)
        VALUES (?, ?, ?, ?, ?)
    """, (athlete_id, session_date, case_notes, athlete_actions, menu_filename))
    conn.commit()
    conn.close()