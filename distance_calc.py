import math
import filter_donor


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def rank_by_distance(donor_list, requester_lat, requester_long):
    for donor in donor_list:
        d_lat = float(donor["lat"])
        d_lon = float(donor["long"])
        donor["distance_km"] = round(haversine(requester_lat, requester_long, d_lat, d_lon), 2)
    donor_list.sort(key=lambda donor: donor["distance_km"])
    return donor_list


if __name__ == "__main__":
    from db import init_db
    init_db()

    dataset = filter_donor.load_donors()
    blood_groups = sorted(set(donor["blood_group"].strip().upper() for donor in dataset))

    requester_lat = -33.8688
    requester_long = 151.2093

    for blood_group in blood_groups:
        ranked = rank_by_distance(filter_donor.filter_donors(blood_group), requester_lat, requester_long)
        print(f"\n{blood_group} - {len(ranked)} eligible donor(s):")
        for donor in ranked:
            print(f"  {donor['name']} - {donor['city']} - {donor['distance_km']} km away")
