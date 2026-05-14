from database import CalendarDB
from datetime import datetime

db = CalendarDB()

# COMMENTED OUT clear_all so we can keep Google data
# db.clear_all() 

print("Starting sync and test...")

# 1. This will trigger the sync from Google
# (It won't ask for permission again, it uses token.json)
db.sync_with_google()

# 2. Check a specific time (Change this to match your Google event!)
test_time = datetime(2026, 5, 14, 14, 32) 
result = db.get_event_at(test_time)

print("\n--- Final Results ---")
print(f"Checking schedule for: {test_time.strftime('%Y-%m-%d %H:%M')}")
print(f"Status: {result}")