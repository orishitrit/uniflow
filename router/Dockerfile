FROM python:3.11-slim

WORKDIR /app

# העתקת תיקיית הראוטר כולה כדי לאפשר ריצה כמודול
COPY . ./router

# ריצה כמודול עם הפניה ל-rx ברשת הפנימית
ENTRYPOINT ["python3", "-u", "-m", "router.main", "--target-host", "rx"]