from db import get_connection


def load_donors():
    """Return every donor as a list of dicts."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM donors")
    rows = cur.fetchall()
    conn.close()
    return rows


def filter_donors(required_blood_group, min_gap_months=3):
    """Eligible = right blood group, available, avg gap between donations >= min_gap_months."""
    required_blood_group = required_blood_group.strip().upper()
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM (
            SELECT *,
                   months_since_first_donation /
                   CASE WHEN number_of_donation = 0 THEN 1 ELSE number_of_donation END
                   AS raw_gap
            FROM donors
            WHERE UPPER(TRIM(blood_group)) = %s
              AND LOWER(TRIM(availability)) = 'yes'
        ) AS t
        WHERE raw_gap >= %s
    """, (required_blood_group, min_gap_months))
    rows = cur.fetchall()
    conn.close()

    eligible = []
    for donor in rows:
        donor["estimated_avg_gap_months"] = round(float(donor.pop("raw_gap")), 1)
        eligible.append(donor)
    return eligible


def months_and_days(avg_gap):
    whole_months = int(avg_gap)
    remaining_fraction = avg_gap - whole_months
    days = round(remaining_fraction * 30)
    return whole_months, days


if __name__ == "__main__":
    from db import init_db
    init_db()

    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

    for blood_group in blood_groups:
        result = filter_donors(blood_group)
        print(f"\n{blood_group} - Found {len(result)} donor(s):")
        for donor in result:
            months, days = months_and_days(donor["estimated_avg_gap_months"])
            time_ago = f"{months} months" if days == 0 else f"{months} months {days} days"
            print(f"Name: {donor['name']} - City: {donor['city']} - "
                  f"Mobile Number: {donor['contact_number']} - Avg. Gap Between Donations: {time_ago} ago")
