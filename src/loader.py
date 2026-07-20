import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.config import DATABASE_PATH

def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # to access columns by name
    return conn

def close_connection(conn):
    """Close the database connection."""
    if conn:
        conn.close()

def load_all_scenarios() -> List[Dict[str, Any]]:
    """Load all scenarios from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.scenario_id, s.scenario_text, s.difficulty, 
                   s.image_path, s.image_description, s.kural_id,
                   k.tamil_kural, k.english_kural,
                   c.concept_id, c.concept_name,
                   p.paal_id, p.paal_name
            FROM scenario s
            LEFT JOIN kural k ON s.kural_id = k.kural_id
            LEFT JOIN concept c ON k.concept_id = c.concept_id
            LEFT JOIN paal p ON c.paal_id = p.paal_id
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        close_connection(conn)

def load_scenario_by_id(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Load a single scenario by its ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.scenario_id, s.scenario_text, s.difficulty, 
                   s.image_path, s.image_description, s.kural_id,
                   k.tamil_kural, k.english_kural,
                   c.concept_id, c.concept_name,
                   p.paal_id, p.paal_name
            FROM scenario s
            LEFT JOIN kural k ON s.kural_id = k.kural_id
            LEFT JOIN concept c ON k.concept_id = c.concept_id
            LEFT JOIN paal p ON c.paal_id = p.paal_id
            WHERE s.scenario_id = ?
        """, (scenario_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        close_connection(conn)

def load_all_questions() -> List[Dict[str, Any]]:
    """Load all questions from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.question_id, q.scenario_id, q.kural_id,
                   q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
                   q.correct_option, q.explanation
            FROM question q
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        close_connection(conn)

def load_all_kurals() -> List[Dict[str, Any]]:
    """Load all kurals from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT k.kural_id, k.tamil_kural, k.transliteration, 
                   k.english_kural, k.vilakam, k.adhigaram_id, k.adhigaram,
                   c.concept_id, c.concept_name,
                   p.paal_id, p.paal_name
            FROM kural k
            LEFT JOIN concept c ON k.concept_id = c.concept_id
            LEFT JOIN paal p ON c.paal_id = p.paal_id
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        close_connection(conn)

def load_all_concepts() -> List[Dict[str, Any]]:
    """Load all concepts from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.concept_id, c.concept_name, c.description,
                   p.paal_id, p.paal_name
            FROM concept c
            LEFT JOIN paal p ON c.paal_id = p.paal_id
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        close_connection(conn)

def load_all_paals() -> List[Dict[str, Any]]:
    """Load all paal (sections) from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.paal_id, p.paal_name, p.description
            FROM paal p
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        close_connection(conn)
