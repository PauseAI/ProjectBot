from scripts.joining_chart import plot_arrivals
from airtable_client import TABLES
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    records = TABLES.onboarding_events.get_all()
    plot_arrivals(records, "Discord Server")
    records = TABLES.members.get_all()
    plot_arrivals(records, "Website", "Joined Time")
    records = TABLES.volunteers.get_all()
    plot_arrivals(records, "Volunteers", "Created", per_week=True)