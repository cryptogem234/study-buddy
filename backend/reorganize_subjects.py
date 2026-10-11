"""
reorganize_subjects.py
One-time cleanup of the subject list (safe to re-run):
- 8th Grade Science topics that belong to Physics or Chemistry move there.
- 8th Grade Science topics that duplicate a Physics or Chemistry topic are hidden
  (their quiz history is kept and still shows on the Progress page).
- What remains becomes "Earth & Space Science" with proper units.
- 7th grade subjects are archived (shown under Review on the Home page).
- Subjects get a fixed display order.

Quiz attempts and lesson progress point at topic ids, which never change here,
so Aashi's history stays attached to every topic.

Run from the backend folder:
    python reorganize_subjects.py
"""
import sqlite3
from pathlib import Path

from database import ensure_schema
import models  # noqa: F401

DB_PATH = Path(__file__).parent / "study_buddy.db"

EARTH_SPACE_UNITS = {
    "Science Skills": ["Scientific Method", "Graphing and Data Analysis", "Metric System"],
    "Weather & Climate": [
        "Water Cycle and the Hydrosphere", "Global Wind Patterns",
        "Atmospheric Pressure and Weather Fronts", "Weather Instruments",
        "Ocean Currents", "Climate Change and Human Activity",
    ],
    "Earth, Moon & Sun": ["Seasons", "Tides"],
    "Space": [
        "Gravity and Formation of the Universe", "Kepler's Laws of Planetary Motion",
        "Inner and Outer Planets", "Stars and the HR Diagram", "Galaxies",
    ],
}

DUPLICATES = [
    "Mass, Volume, and Density", "Changes in States of Matter",
    "Speed, Velocity, and Acceleration", "Newton's Three Laws of Motion",
    "Electromagnetic Forces and Fields", "Conservation of Energy",
    "Potential and Kinetic Energy", "Heat Transfer: Conduction, Convection, Radiation",
    "Energy Conversions", "Parts of an Atom", "The Periodic Table",
    "Chemical and Physical Properties and Changes", "Mixtures vs. Pure Substances",
    "Conservation of Mass and Balancing Equations",
]

# Final topic order per subject: (unit, term, [topic names in order])
PHYSICS_LAYOUT = [
    ("Motion & Forces", 1, [
        "Describing Motion: Speed, Velocity & Acceleration", "Weight vs. Mass",
        "Balanced and Unbalanced Forces", "Friction", "Newton's First Law: Inertia",
        "Newton's Second Law: Force, Mass & Acceleration",
        "Newton's Third Law: Action & Reaction", "Momentum",
    ]),
    ("Energy", 1, [
        "Kinetic & Potential Energy", "Conservation of Energy", "Work, Power & Simple Machines",
        "Thermal Energy & Heat Transfer", "Specific Heat",
    ]),
    ("Electricity & Magnetism", 2, [
        "Electric Charge & Static Electricity", "Electric Circuits & Current", "Magnetism & Electromagnets",
    ]),
    ("Waves, Sound & Light", 2, [
        "Wave Properties: Amplitude, Wavelength & Frequency", "Sound Waves & How We Hear",
        "Light, Reflection & Refraction", "The Electromagnetic Spectrum",
    ]),
]
CHEMISTRY_LAYOUT = [
    ("Atomic Structure & Elements", 1, [
        "Atoms: Structure & Subatomic Particles", "The Periodic Table: Organization & Trends",
        "Elements, Compounds & Mixtures", "Chemical Symbols & Formulas",
        "Chemical Bonding: Ionic and Covalent Bonds",
    ]),
    ("States & Properties of Matter", 1, [
        "States of Matter & the Particle Model", "Phase Changes & Energy",
        "Physical vs. Chemical Properties", "Density & Buoyancy",
    ]),
    ("Chemical Reactions", 2, [
        "Signs of a Chemical Reaction", "Conservation of Mass in Reactions",
        "Balancing Chemical Equations", "Types of Chemical Reactions",
        "Exothermic & Endothermic Reactions",
    ]),
    ("Solutions, Acids & Bases", 2, [
        "Solutions, Solubility & Concentration", "Acids, Bases & pH",
    ]),
]

SUBJECT_ORDER = [  # (name, grade, position, archived)
    ("ELA", 8, 1, 0), ("Physics", 8, 2, 0), ("Chemistry", 8, 3, 0), ("Biology", 8, 4, 0),
    ("Earth & Space Science", 8, 5, 0), ("ELA", 7, 10, 1), ("7th Grade Science", 7, 11, 1),
]


def subject_id(conn, name, grade):
    row = conn.execute("select id from subjects where name = ? and grade = ?", (name, grade)).fetchone()
    return row[0] if row else None


def apply_layout(conn, subj_id, layout, source_ids):
    order = 1
    for unit, term, names in layout:
        for name in names:
            row = conn.execute(
                f"select id from topics where name = ? and subject_id in ({','.join('?' * len(source_ids))}) "
                "order by subject_id = ? desc",  # prefer the copy already in the target subject
                (name, *source_ids, subj_id),
            ).fetchone()
            if not row:
                raise SystemExit(f"Topic not found: {name}")
            conn.execute(
                'update topics set subject_id = ?, unit = ?, term = ?, "order" = ?, hidden = 0 where id = ?',
                (subj_id, unit, term, order, row[0]),
            )
            order += 1


def main():
    ensure_schema()
    conn = sqlite3.connect(DB_PATH)
    with conn:
        science8 = subject_id(conn, "8th Grade Science", 8) or subject_id(conn, "Earth & Space Science", 8)
        physics = subject_id(conn, "Physics", 8)
        chemistry = subject_id(conn, "Chemistry", 8)

        apply_layout(conn, physics, PHYSICS_LAYOUT, [physics, science8])
        apply_layout(conn, chemistry, CHEMISTRY_LAYOUT, [chemistry, science8])

        order = 1
        for unit, names in EARTH_SPACE_UNITS.items():
            for name in names:
                n = conn.execute(
                    'update topics set unit = ?, "order" = ?, hidden = 0 where subject_id = ? and name = ?',
                    (unit, order, science8, name),
                ).rowcount
                if n != 1:
                    raise SystemExit(f"Earth & Space topic not found: {name}")
                order += 1
        for name in DUPLICATES:
            n = conn.execute(
                'update topics set hidden = 1, unit = ?, "order" = ? where subject_id = ? and name = ?',
                ("Covered in Physics & Chemistry", 100 + order, science8, name),
            ).rowcount
            if n != 1:
                raise SystemExit(f"Duplicate topic not found: {name}")
            order += 1

        conn.execute(
            "update subjects set name = ?, icon = ?, description = ? where id = ?",
            ("Earth & Space Science", "🌍",
             "Weather, Climate, Oceans, Earth & Sun, Space — plus Science Skills", science8),
        )
        for name, grade, position, archived in SUBJECT_ORDER:
            conn.execute(
                "update subjects set position = ?, archived = ? where name = ? and grade = ?",
                (position, archived, name, grade),
            )

    for row in conn.execute(
        "select s.position, s.name, s.grade, s.archived, "
        "sum(t.hidden = 0), sum(t.hidden = 1) from subjects s join topics t on t.subject_id = s.id "
        "group by s.id order by s.position"
    ):
        print(row)
    conn.close()


if __name__ == "__main__":
    main()
