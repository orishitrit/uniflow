FROM python:3.11-slim

WORKDIR /app

# התקנת סביבת הידור בסיסית הנדרשת עבור חבילות C
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# העתקה והתקנה של כל החבילות שחולצו
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת קבצי הקוד של הפרויקט
COPY . .