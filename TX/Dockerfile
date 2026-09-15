FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build_src

COPY TX/sender/ .
RUN mkdir -p build && cd build && cmake .. && cmake --build .

FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir protobuf zfec watchdog

COPY --from=builder /build_src/build/sender ./sender_bin


COPY TX/file_monitor/ ./TX/file_monitor/
COPY Schemas/ ./Schemas/
COPY fec/ ./fec/
COPY TX/entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN mkdir -p /app/watch_dir

CMD ["./entrypoint.sh"]