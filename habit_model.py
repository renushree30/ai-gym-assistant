from datetime import datetime

def predict_skip(workout_log):
    if not workout_log:
        return {"risk": "High", "message": "No workouts logged yet! Start today."}
    last_date = datetime.strptime(workout_log[-1], "%Y-%m-%d")
    days_since = (datetime.today() - last_date).days
    if days_since == 0:
        return {"risk": "Low", "message": "Great job! You worked out today!"}
    elif days_since == 1:
        return {"risk": "Low", "message": "Keep it up! Don't break the streak."}
    elif days_since == 2:
        return {"risk": "Medium", "message": "2 days gap! Time to get back on track."}
    else:
        return {"risk": "High", "message": f"{days_since} days missed! You need motivation!"}

def get_streak(workout_log):
    streak = 0
    today = datetime.today()
    for i in range(len(workout_log) - 1, -1, -1):
        d = datetime.strptime(workout_log[i], "%Y-%m-%d")
        if (today - d).days == streak:
            streak += 1
        else:
            break
    return streak

def behavior_prediction(workout_log):
    if len(workout_log) < 3:
        return {
            "total_workouts": len(workout_log),
            "pattern": "Insufficient data",
            "consistency_score": "Low",
            "avg_gap_days": 0,
            "skip_probability": "High",
            "behavioral_nudge": "Log at least 3 workouts to get behavior predictions!",
            "prediction": "Need more data to analyze your behavior pattern"
        }
    total = len(workout_log)
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in workout_log]
    gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
    avg_gap = sum(gaps) / len(gaps)
    last_gap = (datetime.today() - dates[-1]).days

    if avg_gap <= 1:
        pattern = "Daily trainer"
        consistency = "Very High"
    elif avg_gap <= 2:
        pattern = "Regular exerciser"
        consistency = "High"
    elif avg_gap <= 4:
        pattern = "Moderate exerciser"
        consistency = "Medium"
    else:
        pattern = "Irregular exerciser"
        consistency = "Low"

    if last_gap > avg_gap * 1.5:
        skip_probability = "High"
        nudge = "You are overdue for a workout! Even 20 mins counts today!"
    elif last_gap > avg_gap:
        skip_probability = "Medium"
        nudge = "Your gap is getting longer than usual. Time to move!"
    else:
        skip_probability = "Low"
        nudge = "Great consistency! Keep the momentum going!"

    return {
        "total_workouts": total,
        "pattern": pattern,
        "consistency_score": consistency,
        "avg_gap_days": round(avg_gap, 1),
        "skip_probability": skip_probability,
        "behavioral_nudge": nudge,
        "prediction": f"Based on your pattern you are a {pattern} with {consistency} consistency"
    }