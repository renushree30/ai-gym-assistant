import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from diet_model import get_diet_plan, get_bmi
from habit_model import predict_skip, get_streak

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/workout', methods=['GET'])
def workout():
    return jsonify({
        "status": "success",
        "message": "AI Gym Trainer is running",
        "exercises": ["Squats", "Pushups", "Lunges", "Plank"],
        "tip": "Keep your back straight during squats!"
    })

@app.route('/diet', methods=['POST'])
def diet():
    data = request.get_json()
    weight = data.get('weight', 70)
    height = data.get('height', 165)
    goal = data.get('goal', 'maintain')
    preference = data.get('preference', 'vegetarian')
    result = get_diet_plan(weight, height, goal, preference)
    return jsonify({"status": "success", "data": result})

@app.route('/habit', methods=['POST'])
def habit():
    data = request.get_json()
    workout_log = data.get('workout_log', [])
    prediction = predict_skip(workout_log)
    streak = get_streak(workout_log)
    return jsonify({
        "status": "success",
        "prediction": prediction,
        "streak": streak
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()

    responses = {
        'protein|protien|muscle|strength|gain|build':
            "🥩 Top protein rich foods: Eggs, Paneer, Chicken, Lentils, Chickpeas, Greek Yogurt, Tofu, Milk and Peanut Butter. Aim for 1.6g protein per kg of your bodyweight daily!",
        'calorie|calories|kcal|how much|intake|good calorie':
            "🔥 Calorie rich healthy foods: Nuts, Avocado, Banana, Sweet Potato, Brown Rice, Oats, Paneer, Eggs and Whole Milk. These give energy without junk!",
        'diet|food|eat|eating|meal|nutrition':
            "🥗 For a healthy diet focus on proteins, complex carbs and avoid processed food. Want me to generate a full diet plan from the Diet Planner tab?",
        'workout|exercise|gym|training|cardio':
            "💪 Start with 3 sets of Squats, Pushups and Planks daily. Consistency beats intensity — show up every day!",
        'motivat|tired|lazy|demotivat|give up|cant|stress':
            "🔥 You got this! Every champion was once a beginner. Just show up today — that is all that matters! Progress not perfection!",
        'weight|fat|lose|loss|slim|thin|obese':
            "⚖️ Weight loss = calories out > calories in. Combine cardio with strength training. Avoid sugar and fried food. Stay consistent!",
        'water|hydrat|drink':
            "💧 Drink at least 8 glasses (2 litres) of water daily. Drink one glass before every meal — it helps digestion and reduces overeating!",
        'sleep|rest|recover|recovery':
            "😴 Sleep is when your muscles actually grow! Aim for 7-8 hours every night. Poor sleep increases hunger hormones and slows fat loss.",
        'squat|pushup|plank|lunge|deadlift|bench|situp|sit up':
            "🏋️ Great exercise! For beginners do 3 sets of 10-12 reps with 60 seconds rest between sets. Focus on form before adding weight!",
        'vegetarian|vegan|plant|no meat':
            "🌱 Great plant based protein: Lentils, Chickpeas, Tofu, Tempeh, Quinoa, Edamame and Paneer. You can easily hit protein goals without meat!",
        'breakfast|morning|wake up':
            "🌅 Best breakfast for fitness: Oats with banana, Eggs with whole wheat toast, or Poha with sprouts. Never skip breakfast — it kickstarts your metabolism!",
        'supplement|whey|creatine|bcaa|protein powder':
            "💊 Supplements are optional — real food comes first! Whey protein for convenience, Creatine for strength, Multivitamin for overall health.",
        'bmi|body mass|overweight|underweight':
            "📊 BMI tells your body status. Under 18.5 = Underweight, 18.5-25 = Normal, 25-30 = Overweight, above 30 = Obese. Check your BMI in the Diet Planner tab!",
        'chest|shoulder|back|arm|leg|abs|core':
            "💪 Focus on compound movements first — Bench Press for chest, Rows for back, Squats for legs, Overhead Press for shoulders. These give maximum results!",
        'how many|how much|how long|how often':
            "📋 General guidelines: Workout 4-5 days per week, 45-60 mins per session. Eat every 3-4 hours. Sleep 7-8 hours. Drink 2L water daily!",
        'thank|thanks|great|awesome|good|nice|helpful':
            "😊 You are welcome! Keep pushing and stay consistent. Small daily improvements lead to big results. You got this! 💪",
        'hello|hi|hey|start|help|what can':
            "👋 Hey! I am your AI Fitness Assistant. Ask me anything about diet, workout, protein, calories, weight loss or motivation! I am here to help 💪"
    }

    for keywords, reply in responses.items():
        if any(word in message for word in keywords.split('|')):
            return jsonify({"status": "success", "reply": reply})

    return jsonify({
        "status": "success",
        "reply": "🤔 I am not sure about that! Try asking about diet, protein foods, workout tips, weight loss, calories or motivation 💪"
    })

@app.route('/analytics', methods=['GET'])
def analytics():
    return jsonify({
        "status": "success",
        "data": {
            "total_users": 124,
            "active_today": 38,
            "avg_streak": 4.2,
            "top_exercise": "Squats",
            "weekly_workouts": [3, 5, 4, 6, 5, 7, 4]
        }
    })
@app.route('/performance', methods=['POST'])
def performance():
    data = request.get_json()
    reps = data.get('reps', 0)
    duration = data.get('duration', 0)
    exercise = data.get('exercise', 'squat')

    if reps == 0:
        score = 0
    elif duration == 0:
        score = 50
    else:
        reps_per_min = (reps / duration) * 60
        if reps_per_min >= 20:
            score = 95
        elif reps_per_min >= 15:
            score = 85
        elif reps_per_min >= 10:
            score = 70
        elif reps_per_min >= 5:
            score = 55
        else:
            score = 40

    if score >= 90:
        grade = "Excellent 🏆"
    elif score >= 75:
        grade = "Good 💪"
    elif score >= 60:
        grade = "Average 👍"
    else:
        grade = "Need Improvement 📈"

    return jsonify({
        "status": "success",
        "data": {
            "exercise": exercise,
            "reps": reps,
            "performance_score": score,
            "grade": grade,
            "weekly_report": {
                "Mon": 72, "Tue": 78, "Wed": 65,
                "Thu": 80, "Fri": 85, "Sat": 90, "Sun": score
            }
        }
    })
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    goal = data.get('goal', 'weight loss')
    level = data.get('level', 'beginner')
    days = data.get('days', 3)

    plans = {
        'weight loss': {
            'beginner': ['30 min walking', 'Basic cardio', 'Light stretching'],
            'intermediate': ['HIIT 20 min', 'Jump rope', 'Cycling 30 min'],
            'advanced': ['Running 5km', 'Burpees', 'Circuit training']
        },
        'muscle gain': {
            'beginner': ['Bodyweight squats', 'Pushups', 'Dumbbell curls'],
            'intermediate': ['Bench press', 'Deadlift', 'Pull ups'],
            'advanced': ['Heavy compound lifts', 'Progressive overload', 'Supersets']
        },
        'maintain': {
            'beginner': ['Yoga', 'Walking', 'Light stretching'],
            'intermediate': ['Mixed cardio', 'Bodyweight training', 'Swimming'],
            'advanced': ['CrossFit', 'Sport specific training', 'Functional fitness']
        }
    }

    nearby_gyms = [
        {"name": "FitLife Gym", "distance": "0.5 km", "rating": "4.5"},
        {"name": "PowerZone Fitness", "distance": "1.2 km", "rating": "4.3"},
        {"name": "HealthFirst Club", "distance": "2.0 km", "rating": "4.7"}
    ]

    workout_plan = plans.get(goal, plans['maintain']).get(level, ['Basic workout'])

    return jsonify({
        "status": "success",
        "data": {
            "goal": goal,
            "level": level,
            "days_per_week": days,
            "recommended_exercises": workout_plan,
            "nearby_gyms": nearby_gyms,
            "challenge": f"Complete {days} workouts this week — you got this! 💪"
        }
    })
@app.route('/iot', methods=['POST'])
def iot():
    data = request.get_json()
    heart_rate = data.get('heart_rate', 75)
    reps = data.get('reps', 0)
    fatigue = data.get('fatigue', 'low')

    if heart_rate > 150:
        resistance = "Decrease resistance by 20%"
        rest = "Take 2 minute rest now!"
        intensity = "High"
    elif heart_rate > 120:
        resistance = "Maintain current resistance"
        rest = "Rest after 2 more sets"
        intensity = "Medium"
    else:
        resistance = "Increase resistance by 10%"
        rest = "Keep going — you are doing great!"
        intensity = "Low"

    if fatigue == 'high':
        recommendation = "Stop workout — rest for today!"
    elif fatigue == 'medium':
        recommendation = "Slow down and focus on form"
    else:
        recommendation = "Great energy — push harder!"

    return jsonify({
        "status": "success",
        "data": {
            "heart_rate": heart_rate,
            "intensity_level": intensity,
            "resistance_adjustment": resistance,
            "rest_recommendation": rest,
            "ai_recommendation": recommendation,
            "calories_burned": round(heart_rate * 0.15 * (reps or 10), 1)
        }
    })

if __name__ == '__main__':
    app.run(debug=True)