# שלב 1: הידור ה-Receiver ב-C++
FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build_src

COPY RX/receiver/ .
RUN mkdir -p build && cd build && cmake .. && cmake --build .

# שלב 2: סביבת ריצה משותפת
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir protobuf zfec

COPY --from=builder /build_src/build/receiver ./receiver_bin

# העתקה בתוך תיקיית RX כדי לתמוך ב-import RX...
COPY RX/session_manager/ ./RX/session_manager/
COPY Schemas/ ./Schemas/
COPY RX/entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]