def get_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)

def get_diet_plan(weight, height, goal, preference):
    bmi = get_bmi(weight, height)

    if bmi < 18.5:
        category = "Underweight"
        calories = 2500
        plan = "High protein meals - eggs, paneer, milk, nuts, banana"
    elif bmi < 25:
        category = "Normal"
        calories = 2000
        plan = "Balanced diet - rice, dal, vegetables, fruits, curd"
    elif bmi < 30:
        category = "Overweight"
        calories = 1600
        plan = "Low carb - salads, grilled chicken/tofu, oats, green tea"
    else:
        category = "Obese"
        calories = 1300
        plan = "Very low calorie - soups, steamed veggies, no sugar/fried food"

    return {
        "bmi": bmi,
        "category": category,
        "daily_calories": calories,
        "meal_plan": plan,
        "goal": goal
    }

if __name__ == "__main__":
    result = get_diet_plan(70, 165, "weight loss", "vegetarian")
    print(result)