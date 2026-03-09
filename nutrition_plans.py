"""
nutrition_plans.py
All 7 WHO obesity level nutrition plans.
"""

NUTRITION_PLANS = {
    "Insufficient_Weight": {
        "calorie_target"    : "2200–2600 kcal/day",
        "macros"            : "Carbs 50% | Protein 25% | Fat 25%",
        "meal_plan"         : [
            "Breakfast: Oats with banana & peanut butter",
            "Lunch: Brown rice + grilled chicken + avocado",
            "Snack: Greek yogurt with nuts & honey",
            "Dinner: Whole wheat pasta with lean meat sauce",
        ],
        "foods_to_increase" : ["Whole grains","Lean proteins","Healthy fats","Dairy","Nuts & seeds"],
        "foods_to_avoid"    : ["Empty calorie snacks","Excessive sugar","Junk food"],
        "hydration"         : "2.0 litres/day",
        "exercise"          : "Light strength training 3x/week + 20 min daily walks",
        "priority"          : "Increase caloric intake with nutritious, whole foods",
        "bmi_range"         : "< 18.5",
        "supplements"       : ["Vitamin D","Iron","B12","Calcium"],
    },
    "Normal_Weight": {
        "calorie_target"    : "1800–2200 kcal/day",
        "macros"            : "Carbs 45% | Protein 25% | Fat 30%",
        "meal_plan"         : [
            "Breakfast: Whole grain toast + eggs + seasonal fruit",
            "Lunch: Grilled fish + quinoa + steamed vegetables",
            "Snack: Mixed salad with olive oil dressing",
            "Dinner: Lentil soup + whole grain bread",
        ],
        "foods_to_increase" : ["Vegetables","Fruits","Whole grains","Lean protein","Legumes"],
        "foods_to_avoid"    : ["Processed foods","Excessive sugar","Trans fats","Alcohol"],
        "hydration"         : "2.0–2.5 litres/day",
        "exercise"          : "Mixed cardio + strength training 4x/week",
        "priority"          : "Maintain healthy weight with a balanced, varied diet",
        "bmi_range"         : "18.5 – 24.9",
        "supplements"       : ["Vitamin D","Omega-3","Multivitamin"],
    },
    "Overweight_Level_I": {
        "calorie_target"    : "1600–1900 kcal/day",
        "macros"            : "Carbs 40% | Protein 30% | Fat 30%",
        "meal_plan"         : [
            "Breakfast: Vegetable omelette + whole grain toast",
            "Lunch: Grilled chicken salad with lemon dressing",
            "Snack: Apple slices with almond butter",
            "Dinner: Steamed vegetables + baked salmon",
        ],
        "foods_to_increase" : ["Non-starchy vegetables","Lean protein","Fibre-rich foods","Water"],
        "foods_to_avoid"    : ["High-calorie snacks","Refined carbs","Sugary drinks","Fried foods"],
        "hydration"         : "2.5 litres/day",
        "exercise"          : "Cardio 4x/week (30 min) + light strength training",
        "priority"          : "Moderate calorie reduction, increase fibre & protein",
        "bmi_range"         : "25.0 – 27.4",
        "supplements"       : ["Vitamin D","Fibre supplement","Green tea extract"],
    },
    "Overweight_Level_II": {
        "calorie_target"    : "1400–1700 kcal/day",
        "macros"            : "Carbs 35% | Protein 35% | Fat 30%",
        "meal_plan"         : [
            "Breakfast: Low-fat yogurt + berries + chia seeds",
            "Lunch: Tuna salad wrap (whole wheat tortilla)",
            "Snack: Cucumber + hummus",
            "Dinner: Vegetable stir-fry + tofu",
        ],
        "foods_to_increase" : ["High-fibre vegetables","Lean protein","Low-GI foods","Herbal teas"],
        "foods_to_avoid"    : ["White bread","Fast food","Alcohol","Processed meats","Cheese"],
        "hydration"         : "2.5–3.0 litres/day",
        "exercise"          : "Brisk walking 45 min/day + swimming or cycling",
        "priority"          : "Consistent calorie deficit, eliminate processed foods",
        "bmi_range"         : "27.5 – 29.9",
        "supplements"       : ["Vitamin D","Magnesium","CLA","Green tea extract"],
    },
    "Obesity_Type_I": {
        "calorie_target"    : "1200–1500 kcal/day",
        "macros"            : "Carbs 30% | Protein 40% | Fat 30%",
        "meal_plan"         : [
            "Breakfast: Protein smoothie with spinach & chia seeds",
            "Lunch: Grilled turkey breast + roasted vegetables",
            "Snack: Boiled eggs + celery sticks",
            "Dinner: Large mixed salad + lentil soup",
        ],
        "foods_to_increase" : ["Leafy greens","High-protein foods","Fibre","Water","Broth soups"],
        "foods_to_avoid"    : ["Sugar","Alcohol","Refined carbs","High-fat dairy","Fast food","Processed snacks"],
        "hydration"         : "3.0 litres/day",
        "exercise"          : "Low-impact cardio 45 min/day — consult physiotherapist",
        "priority"          : "⚠️ Consult a dietitian. Strict calorie control + high protein",
        "bmi_range"         : "30.0 – 34.9",
        "supplements"       : ["Vitamin D","B12","Iron","Protein powder","Omega-3"],
    },
    "Obesity_Type_II": {
        "calorie_target"    : "1100–1400 kcal/day (medical supervision recommended)",
        "macros"            : "Carbs 25% | Protein 45% | Fat 30%",
        "meal_plan"         : [
            "Breakfast: Egg whites + steamed spinach",
            "Lunch: Grilled fish + large salad (no dressing)",
            "Snack: Cottage cheese + cucumber slices",
            "Dinner: Low-sodium vegetable soup",
        ],
        "foods_to_increase" : ["Non-starchy vegetables","Lean protein","Green tea","Low-sugar fruits"],
        "foods_to_avoid"    : ["All added sugar","Alcohol","Starchy foods","Fatty meats","Full-fat dairy","Oils"],
        "hydration"         : "3.0–3.5 litres/day",
        "exercise"          : "Chair exercises, water aerobics, supervised walking",
        "priority"          : "🚨 Medical supervision required. Structured diet + behavioral therapy",
        "bmi_range"         : "35.0 – 39.9",
        "supplements"       : ["Multivitamin","Vitamin D","B12","Magnesium","Zinc"],
    },
    "Obesity_Type_III": {
        "calorie_target"    : "800–1100 kcal/day (strict medical supervision only)",
        "macros"            : "Carbs 20% | Protein 50% | Fat 30%",
        "meal_plan"         : [
            "Breakfast: Protein shake + multivitamin",
            "Lunch: Steamed broccoli + grilled chicken (no oil)",
            "Snack: Cucumber + boiled egg white",
            "Dinner: Clear vegetable broth",
        ],
        "foods_to_increase" : ["Lean proteins","Non-starchy vegetables","Fibre","Water","Vitamins & minerals"],
        "foods_to_avoid"    : ["All processed food","Refined carbs","Alcohol","Sugar","Oils","Sauces"],
        "hydration"         : "3.5+ litres/day",
        "exercise"          : "Bed/chair exercises only — supervised by medical team",
        "priority"          : "🚨🚨 URGENT: Bariatric specialist + nutritionist + psychologist required",
        "bmi_range"         : "≥ 40.0",
        "supplements"       : ["Bariatric multivitamin","Vitamin D","B12","Iron","Calcium","Zinc"],
    },
}

# Diet preference food overrides
DIET_OVERRIDES = {
    "vegan": {
        "replace": {
            "Grilled chicken": "Grilled tofu",
            "Grilled turkey breast": "Tempeh",
            "Grilled fish": "Marinated jackfruit",
            "Egg whites": "Chickpea scramble",
            "Tuna salad": "Chickpea salad",
            "Cottage cheese": "Cashew ricotta",
            "Protein shake": "Pea protein shake",
        },
        "add_foods": ["Legumes","Tofu","Tempeh","Nutritional yeast","Plant-based protein"],
        "avoid_additional": ["All animal products","Dairy","Eggs","Honey"],
        "supplements_extra": ["B12","Iron","Zinc","Omega-3 algae oil","Iodine"],
    },
    "vegetarian": {
        "replace": {
            "Grilled chicken": "Paneer tikka",
            "Grilled turkey breast": "Cottage cheese patty",
            "Grilled fish": "Tofu steak",
            "Tuna salad": "Chickpea salad",
        },
        "add_foods": ["Paneer","Legumes","Eggs","Dairy","Tofu"],
        "avoid_additional": ["Meat","Poultry","Fish","Seafood"],
        "supplements_extra": ["B12","Iron","Omega-3"],
    },
    "keto": {
        "replace": {
            "Brown rice": "Cauliflower rice",
            "Whole wheat pasta": "Zucchini noodles",
            "Oats": "Chia seed pudding",
            "Whole grain bread": "Almond flour bread",
        },
        "add_foods": ["Avocado","Nuts","Seeds","Fatty fish","Olive oil","Cheese"],
        "avoid_additional": ["All grains","Starchy vegetables","Fruit (except berries)","Legumes"],
        "supplements_extra": ["Electrolytes","Magnesium","MCT oil"],
    },
    "diabetic": {
        "replace": {
            "Banana": "Berries",
            "Brown rice": "Barley or quinoa",
            "Honey": "Stevia",
        },
        "add_foods": ["Low-GI vegetables","Bitter gourd","Cinnamon","Fenugreek"],
        "avoid_additional": ["All sugars","White rice","Potatoes","Sweet fruits","Fruit juice"],
        "supplements_extra": ["Chromium","Magnesium","Berberine","Vitamin D"],
    },
    "gluten_free": {
        "replace": {
            "Whole grain toast": "Rice cake",
            "Whole wheat pasta": "Rice pasta",
            "Whole grain bread": "Gluten-free bread",
            "Oats": "Certified GF oats",
        },
        "add_foods": ["Quinoa","Rice","Buckwheat","Millet","Amaranth"],
        "avoid_additional": ["Wheat","Barley","Rye","Regular oats","Most processed foods"],
        "supplements_extra": ["B vitamins","Iron","Calcium"],
    },
    "halal": {
        "replace": {},
        "add_foods": ["Halal-certified meats","Legumes","Fish","Eggs"],
        "avoid_additional": ["Pork","Alcohol","Non-halal meat"],
        "supplements_extra": [],
    },
    "none": {
        "replace": {},
        "add_foods": [],
        "avoid_additional": [],
        "supplements_extra": [],
    },
}

ALLERGY_RESTRICTIONS = {
    "nuts"       : ["Peanut butter","Nuts","Almonds","Cashews","Walnuts"],
    "dairy"      : ["Yogurt","Milk","Cheese","Cottage cheese","Paneer","Whey protein"],
    "gluten"     : ["Whole grain toast","Pasta","Bread","Oats","Wheat"],
    "eggs"       : ["Egg whites","Eggs","Omelette"],
    "soy"        : ["Tofu","Tempeh","Soy sauce","Edamame"],
    "fish"       : ["Fish","Salmon","Tuna","Seafood"],
    "shellfish"  : ["Shrimp","Crab","Lobster","Prawns"],
    "none"       : [],
}

BMI_THRESHOLDS = [
    ("Insufficient_Weight",        0.0,   18.5),
    ("Normal_Weight",             18.5,   25.0),
    ("Overweight_Level_I",        25.0,   27.5),
    ("Overweight_Level_II",       27.5,   30.0),
    ("Obesity_Type_I",            30.0,   35.0),
    ("Obesity_Type_II",           35.0,   40.0),
    ("Obesity_Type_III",          40.0,  999.0),
]

def classify_bmi(bmi: float) -> str:
    for key, lo, hi in BMI_THRESHOLDS:
        if lo <= bmi < hi:
            return key
    return "Obesity_Type_III"
