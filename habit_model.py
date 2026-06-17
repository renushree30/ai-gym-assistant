from datetime import datetime, timedelta

def predict_skip(workout_log):
    """
    workout_log = list of dates user worked out
    Example: ["2025-06-10", "2025-06-11", "2025-06-13"]
    """
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

if __name__ == "__main__":
    log = ["2025-06-10", "2025-06-11", "2025-06-12"]
    print(predict_skip(log))
    print("Current streak:", get_streak(log))