# Emergency Blood Availability Network

Finds eligible blood donors near a hospital, ranks them by distance, notifies them, and tracks their responses. Data is stored in a MySQL database.

## Requirements
- Python 3.12+
- MySQL Server (running locally)
- `pip install mysql-connector-python`

## Setup
1. Keep `donors.csv` in the same folder as the code.
2. Create a file named `db_config.py` with your own MySQL login (this file is in `.gitignore`, so it is never pushed):
   ```python
   HOST = "localhost"
   USER = "root"
   PASSWORD = "your_mysql_password"
   DB_NAME = "blood_network"
   ```
3. Run: `python main.py`

The database `blood_network` and its tables are created automatically on the first run, and `donors.csv` is imported once.

## How it works
1. Enter the required blood group and the hospital city.
2. Eligible donors are found with an SQL query (right blood group, available, avg. gap between donations of at least 3 months).
3. Donors are ranked by distance (haversine formula).
4. All ranked donors are notified and logged as `pending`.
5. Each donor's response (yes / no / no response) is recorded, starting from the nearest, until one says yes.

## Files
- `db_config.py`: MySQL login details (local only)
- `db.py`: creates the database and tables, imports `donors.csv`
- `filter_donor.py`: SQL query for eligible donors
- `distance_calc.py`: ranks donors by distance
- `notify_and_track.py`: notifies donors, logs responses, response summary
- `main.py`: runs the whole flow

## Database tables
- `donors`: donor details, location, availability
- `notifications`: which donor was notified, their response, and the time (linked to `donors` by `donor_id`)