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

if __name__ == '__main__':
    app.run(debug=True)