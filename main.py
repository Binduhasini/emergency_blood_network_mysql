from db import init_db
from filter_donor import filter_donors
from distance_calc import rank_by_distance
from notify_and_track import notify_donors, update_response, get_response_summary

init_db()  # creates database + tables and imports donors.csv on first run

required_blood_group = input("Enter required blood group (e.g. O+, A-, AB+): ").strip().upper()

city_coords = {
    "SYDNEY": (-33.8688, 151.2093),
    "MELBOURNE": (-37.8136, 144.9631),
    "BRISBANE": (-27.4698, 153.0251),
    "PERTH": (-31.9505, 115.8605),
    "ADELAIDE": (-34.9285, 138.6007),
    "CANBERRA": (-35.2809, 149.1300),
    "HOBART": (-42.8821, 147.3272),
    "DARWIN": (-12.4634, 130.8456),
}

hospital_city = input("Enter hospital city (Sydney, Melbourne, Brisbane, Perth, Adelaide, Canberra, Hobart, Darwin): ").strip().upper()

if hospital_city not in city_coords:
    print("City not recognized. Defaulting to Sydney.")
    hospital_city = "SYDNEY"

hospital_lat, hospital_long = city_coords[hospital_city]

eligible = filter_donors(required_blood_group)
ranked = rank_by_distance(eligible, hospital_lat, hospital_long)

if not ranked:
    print(f"\nNo eligible {required_blood_group} donors found near {hospital_city.title()}.")
else:
    message = f"Urgent: {required_blood_group} blood needed at {hospital_city.title()} Hospital"
    notified = notify_donors(ranked, message)

    print(f"\nNearest Donor: {notified[0]['name']} \nDistance: {notified[0]['distance_km']} km away "
          f"\nLast Donated : {notified[0]['estimated_avg_gap_months']} months")

    for donor in notified:
        response = input(f"Did {donor['name']} respond yes/no/no response? ").strip().lower()
        timestamp = update_response(donor["donor_id"], response)
        print(f"Recorded: {response} at {timestamp}\n")

        if response == "yes":
            print(f"{donor['name']} confirmed. Request fulfilled — stopping search.")
            break
        else:
            print(f"{donor['name']} declined or didn't respond. Trying next nearest donor...\n")

    print("Response summary (all requests):")
    for status, total in get_response_summary():
        print(f"  {status}: {total}")
