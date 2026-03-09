from schemas import UserProfileRequest, YesNoEnum, DietPreferenceEnum
from pydantic import ValidationError

payload = {
  "name": "Yug",
  "gender": "Male",
  "age": 22,
  "height_cm": 178,
  "weight_kg": 85,
  "family_history_obesity": "No",
  "high_caloric_food": "No",
  "vegetable_frequency": 1,
  "main_meals_per_day": 2,
  "snacking": "No",
  "smoker": "no",
  "water_intake_litres": 2,
  "calorie_monitoring": "no",
  "physical_activity_days": 1,
  "tech_device_hours": 4,
  "alcohol_frequency": "No",
  "transport_mode": "Walking",
  "diet_preference": "veg",
  "allergies": [],
  "health_goal": "lose_weight",
  "activity_level": "sedentary"
}

print("Testing model validation...")
try:
    user = UserProfileRequest(**payload)
    print("SUCCESS: Model created!")
    print(f"Gender: {user.gender}")
    print(f"Family History: {user.family_history_obesity}")
    print(f"Diet: {user.diet_preference}")
except ValidationError as e:
    print("FAILED: Validation Error")
    print(e.json(indent=2))
except Exception as e:
    print(f"ERROR: {e}")
