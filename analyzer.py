import sqlite3
import re
import hashlib
import secrets
import string
from datetime import datetime

# ---------------- DATABASE ----------------

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Table for all entered passwords
cursor.execute("""
CREATE TABLE IF NOT EXISTS entered_passwords(
    password_hash TEXT PRIMARY KEY
)
""")

# Table for accepted/saved passwords
cursor.execute("""
CREATE TABLE IF NOT EXISTS saved_passwords(
    password_hash TEXT PRIMARY KEY,
    strength TEXT,
    created_at TEXT
)
""")

conn.commit()

# ---------------- COMMON PASSWORDS ----------------

common_passwords = {
    "password",
    "123456",
    "12345678",
    "admin",
    "qwerty",
    "welcome",
    "abc123",
    "password123"
}

# ---------------- HASH PASSWORD ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- CHECK ENTERED PASSWORD ----------------

def entered_before(password):

    password_hash = hash_password(password)

    cursor.execute(
        "SELECT 1 FROM entered_passwords WHERE password_hash=?",
        (password_hash,)
    )

    return cursor.fetchone() is not None

# ---------------- CHECK SAVED PASSWORD ----------------

def saved_before(password):

    password_hash = hash_password(password)

    cursor.execute(
        "SELECT 1 FROM saved_passwords WHERE password_hash=?",
        (password_hash,)
    )

    return cursor.fetchone() is not None

# ---------------- STORE ENTERED PASSWORD ----------------

def store_entered(password):

    password_hash = hash_password(password)

    try:
        cursor.execute(
            """
            INSERT INTO entered_passwords
            VALUES (?)
            """,
            (password_hash,)
        )

        conn.commit()

    except sqlite3.IntegrityError:
        pass

# ---------------- STORE SAVED PASSWORD ----------------

def store_saved(password, strength):

    password_hash = hash_password(password)

    cursor.execute(
        """
        INSERT INTO saved_passwords
        (
            password_hash,
            strength,
            created_at
        )
        VALUES (?,?,?)
        """,
        (
            password_hash,
            strength,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    conn.commit()

# ---------------- GENERATE PASSWORD ----------------

def generate_password():

    chars = (
        string.ascii_letters +
        string.digits +
        "!@#$%^&*"
    )

    return ''.join(
        secrets.choice(chars)
        for _ in range(12)
    )

# ---------------- ANALYZE PASSWORD ----------------

def analyze_password(password):

    issues = []

    if password.lower() in common_passwords:
        issues.append(
            "Avoid common passwords"
        )

    if len(password) < 8:
        issues.append(
            "Use at least 8 characters"
        )

    if not re.search(r"[A-Z]", password):
        issues.append(
            "Add an uppercase letter"
        )

    if not re.search(r"[a-z]", password):
        issues.append(
            "Add a lowercase letter"
        )

    if not re.search(r"\d", password):
        issues.append(
            "Add a number"
        )

    if not re.search(r"[^a-zA-Z0-9]", password):
        issues.append(
            "Add a special character"
        )

    if len(issues) == 0:
        return "STRONG", issues

    elif len(issues) <= 2:
        return "MEDIUM", issues

    else:
        return "WEAK", issues

# ---------------- MAIN PROGRAM ----------------

print("\n===== PASSWORD STRENGTH ANALYZER =====")

while True:

    password = input(
        "\nEnter Password: "
    ).strip()

    # Warning if entered before
    if entered_before(password):

        print(
            "\n⚠ WARNING: This password was entered before."
        )

        continue

    # Warning if saved before
    if saved_before(password):

        print(
            "\n⚠ WARNING: This password was already used and saved before."
        )

        continue

    # Store every entered password
    store_entered(password)

    strength, issues = analyze_password(password)

    # Strong password
    if strength == "STRONG":

        store_saved(
            password,
            strength
        )

        print(
            "\n✅ Password accepted and saved successfully."
        )

        break

    # Weak or Medium password
    print(
        f"\nPassword Strength: {strength}"
    )

    print("\nSuggestions:")

    for issue in issues:
        print("-", issue)

    suggested_password = generate_password()

    print(
        "\nSuggested Strong Password:"
    )

    print(suggested_password)

    choice = input(
        "\nUse suggested password? (Y/N): "
    ).strip().upper()

    if choice == "Y":

        if entered_before(suggested_password):

            print(
                "\n⚠ WARNING: Suggested password was entered before."
            )

            continue

        if saved_before(suggested_password):

            print(
                "\n⚠ WARNING: Suggested password was already used before."
            )

            continue

        store_entered(suggested_password)

        store_saved(
            suggested_password,
            "STRONG"
        )

        print(
            "\n✅ Suggested password accepted and saved successfully."
        )

        break

    print(
        "\nPlease enter a new password."
    )

conn.close()