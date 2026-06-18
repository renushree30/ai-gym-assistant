import os
import sqlite3
import hashlib
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from diet_model import get_diet_plan, get_bmi
from habit_model import predict_skip, get_streak, behavior_prediction
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = "aigym2026secretkey"
CORS(app)

# ─── DATABASE SETUP ───────────────────────────────────────────
def init_db():
    conn = sqlite3.connect('gym_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        weight REAL,
        height REAL,
        bmi REAL,
        bmi_category TEXT,
        goal TEXT,
        diet TEXT,
        health_conditions TEXT,
        registered_on TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS workout_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        workout_date TEXT,
        exercise TEXT,
        reps INTEGER,
        duration INTEGER,
        performance_score INTEGER,
        FOREIGN KEY (user_email) REFERENCES users(email)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS diet_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        log_date TEXT,
        weight REAL,
        calories INTEGER,
        meal_plan TEXT,
        goal TEXT,
        FOREIGN KEY (user_email) REFERENCES users(email)
    )''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect('gym_users.db')
    conn.row_factory = sqlite3.Row
    return conn

# ─── AUTH ROUTES ──────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    age = data.get('age')
    gender = data.get('gender')
    weight = data.get('weight')
    height = data.get('height')
    goal = data.get('goal')
    diet = data.get('diet')
    conditions = ','.join(data.get('health_conditions', []))

    if not all([name, email, password, age, gender, weight, height]):
        return jsonify({"status": "error", "message": "All fields are required!"})

    bmi = round(float(weight) / ((float(height)/100) ** 2), 1)
    if bmi < 18.5:
        bmi_cat = "Underweight"
    elif bmi < 25:
        bmi_cat = "Normal"
    elif bmi < 30:
        bmi_cat = "Overweight"
    else:
        bmi_cat = "Obese"

    try:
        conn = get_db()
        conn.execute('''INSERT INTO users
            (name, email, password, age, gender, weight, height,
             bmi, bmi_category, goal, diet, health_conditions, registered_on)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,date('now'))''',
            (name, email, hash_password(password), age, gender,
             weight, height, bmi, bmi_cat, goal, diet, conditions))
        conn.commit()
        conn.close()
        session['user_email'] = email
        return jsonify({"status": "success", "message": "Account created!"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Email already registered!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email=? AND password=?',
                        (email, hash_password(password))).fetchone()
    conn.close()

    if user:
        session['user_email'] = email
        return jsonify({
            "status": "success",
            "user": {
                "name": user['name'],
                "email": user['email'],
                "bmi": user['bmi'],
                "bmi_category": user['bmi_category'],
                "goal": user['goal'],
                "diet": user['diet'],
                "weight": user['weight'],
                "height": user['height'],
                "age": user['age'],
                "gender": user['gender'],
                "health_conditions": user['health_conditions'].split(',') if user['health_conditions'] else [],
                "registered_on": user['registered_on']
            }
        })
    return jsonify({"status": "error", "message": "Invalid email or password!"})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success"})

@app.route('/get_user', methods=['GET'])
def get_user():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "error", "message": "No email"})
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    conn.close()
    if user:
        return jsonify({
            "status": "success",
            "user": {
                "name": user['name'],
                "email": user['email'],
                "bmi": user['bmi'],
                "bmi_category": user['bmi_category'],
                "goal": user['goal'],
                "diet": user['diet'],
                "weight": user['weight'],
                "height": user['height'],
                "age": user['age'],
                "gender": user['gender'],
                "health_conditions": user['health_conditions'].split(',') if user['health_conditions'] else [],
                "registered_on": user['registered_on']
            }
        })
    return jsonify({"status": "error", "message": "User not found"})

@app.route('/save_workout', methods=['POST'])
def save_workout():
    data = request.get_json()
    email = data.get('email')
    exercise = data.get('exercise', 'General')
    reps = data.get('reps', 0)
    duration = data.get('duration', 0)
    score = data.get('score', 0)

    if not email:
        return jsonify({"status": "error"})

    conn = get_db()
    conn.execute('''INSERT INTO workout_history
        (user_email, workout_date, exercise, reps, duration, performance_score)
        VALUES (?, date('now'), ?, ?, ?, ?)''',
        (email, exercise, reps, duration, score))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/get_workout_history', methods=['GET'])
def get_workout_history():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "error"})
    conn = get_db()
    rows = conn.execute('''SELECT * FROM workout_history
        WHERE user_email=? ORDER BY workout_date DESC LIMIT 10''',
        (email,)).fetchall()
    conn.close()
    history = [dict(row) for row in rows]
    return jsonify({"status": "success", "history": history})

@app.route('/save_diet', methods=['POST'])
def save_diet():
    data = request.get_json()
    email = data.get('email')
    weight = data.get('weight')
    calories = data.get('calories')
    meal_plan = data.get('meal_plan')
    goal = data.get('goal')

    if not email:
        return jsonify({"status": "error"})

    conn = get_db()
    conn.execute('''INSERT INTO diet_logs
        (user_email, log_date, weight, calories, meal_plan, goal)
        VALUES (?, date('now'), ?, ?, ?, ?)''',
        (email, weight, calories, meal_plan, goal))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/admin_users', methods=['GET'])
def admin_users():
    conn = get_db()
    users = conn.execute('SELECT name, email, age, gender, bmi, bmi_category, goal, health_conditions, registered_on FROM users').fetchall()
    total = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    workouts = conn.execute('SELECT COUNT(*) as count FROM workout_history').fetchone()['count']
    conn.close()
    return jsonify({
        "status": "success",
        "total_users": total,
        "total_workouts": workouts,
        "users": [dict(u) for u in users]
    })

# ─── EXISTING ROUTES ──────────────────────────────────────────
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
    return jsonify({"status": "success", "prediction": prediction, "streak": streak})

@app.route('/behavior', methods=['POST'])
def behavior():
    data = request.get_json()
    workout_log = data.get('workout_log', [])
    result = behavior_prediction(workout_log)
    return jsonify({"status": "success", "data": result})

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
            "🔥 You got this! Every champion was once a beginner. Just show up today — that is all that matters!",
        'weight|fat|lose|loss|slim|thin|obese':
            "⚖️ Weight loss = calories out > calories in. Combine cardio with strength training. Stay consistent!",
        'water|hydrat|drink':
            "💧 Drink at least 8 glasses (2 litres) of water daily. Drink one glass before every meal!",
        'sleep|rest|recover|recovery':
            "😴 Sleep is when your muscles actually grow! Aim for 7-8 hours every night.",
        'squat|pushup|plank|lunge|deadlift|bench|situp':
            "🏋️ Great exercise! For beginners do 3 sets of 10-12 reps with 60 seconds rest between sets.",
        'vegetarian|vegan|plant|no meat':
            "🌱 Great plant based protein: Lentils, Chickpeas, Tofu, Tempeh, Quinoa, Edamame and Paneer!",
        'breakfast|morning|wake up':
            "🌅 Best breakfast: Oats with banana, Eggs with whole wheat toast, or Poha with sprouts!",
        'supplement|whey|creatine|bcaa':
            "💊 Supplements are optional — real food comes first! Whey protein, Creatine, Multivitamin.",
        'bmi|body mass|overweight|underweight':
            "📊 BMI: Under 18.5 = Underweight, 18.5-25 = Normal, 25-30 = Overweight, above 30 = Obese.",
        'chest|shoulder|back|arm|leg|abs|core':
            "💪 Focus on compound movements — Bench Press, Rows, Squats, Overhead Press for maximum results!",
        'heart|cardiac|cardiovascular':
            "❤️ For heart patients: Always consult your doctor before exercising! Stick to light walking, yoga and breathing exercises. Avoid heavy lifting!",
        'diabetes|sugar|blood sugar':
            "🩸 For diabetics: Monitor blood sugar before and after workouts. Carry glucose tablets. Avoid fasted exercise!",
        'thank|thanks|great|awesome|good':
            "😊 You are welcome! Keep pushing and stay consistent. You got this! 💪",
        'hello|hi|hey|start|help':
            "👋 Hey! I am your AI Fitness Assistant. Ask me about diet, workout, protein, calories or motivation! 💪"
    }
    for keywords, reply in responses.items():
        if any(word in message for word in keywords.split('|')):
            return jsonify({"status": "success", "reply": reply})
    return jsonify({"status": "success", "reply": "🤔 Try asking about diet, protein, workout tips, weight loss or motivation 💪"})

@app.route('/analytics', methods=['GET'])
def analytics():
    conn = get_db()
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_workouts = conn.execute('SELECT COUNT(*) as count FROM workout_history').fetchone()['count']
    heart_patients = conn.execute("SELECT COUNT(*) as count FROM users WHERE health_conditions LIKE '%heart%'").fetchone()['count']
    conn.close()
    return jsonify({
        "status": "success",
        "data": {
            "total_users": total_users or 0,
            "active_today": total_workouts or 0,
            "avg_streak": 4.2,
            "top_exercise": "Squats",
            "heart_patients": heart_patients,
            "weekly_workouts": [3, 5, 4, 6, 5, 7, 4],
            "module_usage": {
                "Workout Trainer": 89,
                "Diet Planner": 76,
                "Habit Tracker": 65,
                "AI Chat": 92,
                "Performance": 54,
                "Recommender": 48,
                "IoT Assistant": 41
            },
            "bmi_distribution": {
                "Underweight": 12,
                "Normal": 58,
                "Overweight": 22,
                "Obese": 8
            },
            "skip_risk_today": {
                "Low": 65,
                "Medium": 25,
                "High": 10
            }
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
        if reps_per_min >= 20: score = 95
        elif reps_per_min >= 15: score = 85
        elif reps_per_min >= 10: score = 70
        elif reps_per_min >= 5: score = 55
        else: score = 40
    grade = "Excellent 🏆" if score >= 90 else "Good 💪" if score >= 75 else "Average 👍" if score >= 60 else "Need Improvement 📈"
    return jsonify({"status": "success", "data": {"exercise": exercise, "reps": reps, "performance_score": score, "grade": grade, "weekly_report": {"Mon": 72, "Tue": 78, "Wed": 65, "Thu": 80, "Fri": 85, "Sat": 90, "Sun": score}}})

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    goal = data.get('goal', 'weight loss')
    level = data.get('level', 'beginner')
    days = data.get('days', 3)
    lat = data.get('lat', None)
    lon = data.get('lon', None)
    plans = {
        'weight loss': {'beginner': ['30 min walking', 'Basic cardio', 'Light stretching'], 'intermediate': ['HIIT 20 min', 'Jump rope', 'Cycling 30 min'], 'advanced': ['Running 5km', 'Burpees', 'Circuit training']},
        'muscle gain': {'beginner': ['Bodyweight squats', 'Pushups', 'Dumbbell curls'], 'intermediate': ['Bench press', 'Deadlift', 'Pull ups'], 'advanced': ['Heavy compound lifts', 'Progressive overload', 'Supersets']},
        'maintain': {'beginner': ['Yoga', 'Walking', 'Light stretching'], 'intermediate': ['Mixed cardio', 'Bodyweight training', 'Swimming'], 'advanced': ['CrossFit', 'Sport specific training', 'Functional fitness']}
    }
    workout_plan = plans.get(goal, plans['maintain']).get(level, ['Basic workout'])
    nearby_gyms = []
    if lat and lon:
        try:
            overpass_url = "https://overpass-api.de/api/interpreter"
            overpass_query = f"[out:json][timeout:25];(node[\"leisure\"=\"fitness_centre\"](around:5000,{lat},{lon});node[\"amenity\"=\"gym\"](around:5000,{lat},{lon});way[\"leisure\"=\"fitness_centre\"](around:5000,{lat},{lon}););out center 8;"
            response = requests.post(overpass_url, data={"data": overpass_query}, timeout=25, headers={"User-Agent": "AIGymAssistant/1.0"})
            results = response.json()
            for element in results.get('elements', [])[:5]:
                tags = element.get('tags', {})
                name = tags.get('name', 'Gym / Fitness Centre')
                elem_lat = element.get('lat') or element.get('center', {}).get('lat', lat)
                elem_lon = element.get('lon') or element.get('center', {}).get('lon', lon)
                dist_km = round(((float(elem_lat)-float(lat))**2 + (float(elem_lon)-float(lon))**2)**0.5 * 111, 2)
                nearby_gyms.append({"name": name, "distance": f"{dist_km} km", "maps_url": f"https://www.google.com/maps/search/gym/@{elem_lat},{elem_lon},17z"})
            nearby_gyms.sort(key=lambda x: float(x['distance'].replace(' km', '')))
            if not nearby_gyms:
                nearby_gyms = [{"name": "🔍 Search Gyms Near Me", "distance": "Click", "maps_url": f"https://www.google.com/maps/search/gym+near+me/@{lat},{lon},14z"}]
        except:
            nearby_gyms = [{"name": "🔍 Search Gyms Near Me on Google Maps", "distance": "Click", "maps_url": f"https://www.google.com/maps/search/gym+near+me/@{lat},{lon},14z"}]
    else:
        nearby_gyms = [{"name": "📍 Click Get My Location first!", "distance": "-", "maps_url": "#"}]
    return jsonify({"status": "success", "data": {"goal": goal, "level": level, "days_per_week": days, "recommended_exercises": workout_plan, "nearby_gyms": nearby_gyms, "challenge": f"Complete {days} workouts this week — you got this! 💪"}})

@app.route('/iot', methods=['POST'])
def iot():
    data = request.get_json()
    heart_rate = data.get('heart_rate', 75)
    reps = data.get('reps', 0)
    fatigue = data.get('fatigue', 'low')
    if heart_rate > 150: resistance, rest, intensity = "Decrease resistance by 20%", "Take 2 minute rest now!", "High"
    elif heart_rate > 120: resistance, rest, intensity = "Maintain current resistance", "Rest after 2 more sets", "Medium"
    else: resistance, rest, intensity = "Increase resistance by 10%", "Keep going — you are doing great!", "Low"
    recommendation = "Stop workout — rest for today!" if fatigue == 'high' else "Slow down and focus on form" if fatigue == 'medium' else "Great energy — push harder!"
    return jsonify({"status": "success", "data": {"heart_rate": heart_rate, "intensity_level": intensity, "resistance_adjustment": resistance, "rest_recommendation": rest, "ai_recommendation": recommendation, "calories_burned": round(heart_rate * 0.15 * (reps or 10), 1)}})

if __name__ == '__main__':
    app.run(debug=True)