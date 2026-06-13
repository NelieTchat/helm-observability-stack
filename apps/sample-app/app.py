import os
import time
import random
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "sample_app_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "sample_app_request_latency_seconds",
    "HTTP request latency",
    ["endpoint"]
)

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/ready")
def ready():
    return jsonify({"status": "ready"}), 200

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.route("/api/work")
def work():
    start = time.time()
    if random.random() < 0.05:
        REQUEST_COUNT.labels(
            method="GET", endpoint="/api/work", status="500"
        ).inc()
        return jsonify({"error": "internal error"}), 500

    time.sleep(random.uniform(0.01, 0.1))
    latency = time.time() - start

    REQUEST_LATENCY.labels(endpoint="/api/work").observe(latency)
    REQUEST_COUNT.labels(
        method="GET", endpoint="/api/work", status="200"
    ).inc()

    return jsonify({"processed": True}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)