from datetime import datetime
from db import get_connection


def notify_donors(ranked_donors, message):
    """Print the notification and log one 'pending' row per donor in the notifications table."""
    conn = get_connection()
    cur = conn.cursor()
    for donor in ranked_donors:
        print(f"Notifying {donor['name']} at {donor['email']} / {donor['contact_number']} "
              f"({donor.get('distance_km', '?')} km away): {message}")
        cur.execute(
            "INSERT INTO notifications (donor_id, message, sent_at) VALUES (%s, %s, %s)",
            (donor["donor_id"], message, datetime.now().replace(microsecond=0)),
        )
    conn.commit()
    conn.close()
    return ranked_donors


def update_response(donor_id, response):
    """Record the response on the donor's latest notification. Returns the timestamp, or None."""
    timestamp = datetime.now().replace(microsecond=0)
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT MAX(id) AS last_id FROM notifications WHERE donor_id = %s", (donor_id,))
    last_id = cur.fetchone()["last_id"]
    if last_id is None:
        print(f"No notification found for donor ID {donor_id}")
        conn.close()
        return None

    cur.execute(
        "UPDATE notifications SET response = %s, responded_at = %s WHERE id = %s",
        (response, timestamp, last_id),
    )
    conn.commit()

    cur.execute("SELECT name FROM donors WHERE donor_id = %s", (donor_id,))
    name = cur.fetchone()["name"]
    conn.close()
    print(f"Logged response for {name}: {response}")
    return timestamp


def get_response_summary():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT response, COUNT(*) AS total FROM notifications GROUP BY response ORDER BY total DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return [(r["response"], r["total"]) for r in rows]


if __name__ == "__main__":
    from db import init_db
    from filter_donor import filter_donors
    from distance_calc import rank_by_distance

    init_db()
    ranked = rank_by_distance(filter_donors("O-"), -33.8688, 151.2093)
    notified = notify_donors(ranked, "Urgent: O- blood needed at City Hospital")

    if notified:
        update_response(notified[0]["donor_id"], "yes")
