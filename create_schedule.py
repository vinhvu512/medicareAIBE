import requests
import random
from datetime import datetime

def setup_doctor_schedules():
    base_url = "http://localhost:8000/api/doctor/schedule"
    
    # Days of the week (Monday to Saturday)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    # Schedule patterns
    MORNING_SHIFTS = list(range(0, 10))  # 0-9 for morning
    AFTERNOON_SHIFTS = list(range(10, 20))  # 10-19 for afternoon
    
    # Schedule patterns
    PATTERNS = [
        "morning",    # Morning only
        "afternoon", # Afternoon only
        "full_day"   # Both morning and afternoon
    ]

    for doctor_id in range(83, 103):  # 83 to 102
        room_id = doctor_id - 49  # Calculate room_id based on doctor_id
        pattern = random.choice(PATTERNS)  # Randomly choose a schedule pattern
        
        # Initialize schedule
        schedule = {}
        
        # Create shifts based on pattern
        for day in days:
            shifts = []
            if pattern == "morning" or pattern == "full_day":
                shifts.extend([{"shift_id": shift, "room_id": room_id} for shift in MORNING_SHIFTS])
            if pattern == "afternoon" or pattern == "full_day":
                shifts.extend([{"shift_id": shift, "room_id": room_id} for shift in AFTERNOON_SHIFTS])
            schedule[day] = shifts

        # Prepare request
        url = f"{base_url}/{doctor_id}"
        payload = schedule

        try:
            response = requests.put(url, json=payload)
            print(f"Doctor {doctor_id} schedule set up:")
            print(f"Status Code: {response.status_code}")
            print(f"Pattern: {pattern}")
            if response.status_code != 200:
                print(f"Error: {response.json()}")
            print("-------------------")
        except Exception as e:
            print(f"Error setting up schedule for doctor {doctor_id}: {str(e)}")
            print("-------------------")

if __name__ == "__main__":
    setup_doctor_schedules()