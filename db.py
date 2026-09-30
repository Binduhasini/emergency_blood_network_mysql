import csv
import mysql.connector
from db_config import HOST, USER, PASSWORD, DB_NAME

CSV_PATH = "donors.csv"


def create_database():
    conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.close()


def get_connection():
    return mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DB_NAME)


def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            donor_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150),
            contact_number VARCHAR(30),
            city VARCHAR(50),
            blood_group VARCHAR(5) NOT NULL,
            availability VARCHAR(10),
            months_since_first_donation INT,
            number_of_donation INT,
            pints_donated INT,
            created_at DATE,
            lat DOUBLE,
            `long` DOUBLE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            donor_id VARCHAR(20) NOT NULL,
            message VARCHAR(255),
            sent_at DATETIME,
            response VARCHAR(20) DEFAULT 'pending',
            responded_at DATETIME,
            FOREIGN KEY (donor_id) REFERENCES donors(donor_id)
        )
    """)
    conn.commit()
    conn.close()


def load_donors_from_csv(csv_path=CSV_PATH):
    """One-time import. Skipped if the donors table already has data."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM donors")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    cols = list(rows[0].keys())
    col_sql = ", ".join(f"`{c}`" for c in cols)
    val_sql = ", ".join(f"%({c})s" for c in cols)
    cur.executemany(f"INSERT IGNORE INTO donors ({col_sql}) VALUES ({val_sql})", rows)
    conn.commit()
    conn.close()
    print(f"Imported {len(rows)} donors into MySQL database '{DB_NAME}'")


def init_db():
    create_database()
    create_tables()
    load_donors_from_csv()
