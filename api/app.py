import os
import time
import random
import json
from uuid import uuid4
from flask import Flask, request, jsonify
from kafka import KafkaProducer
import redis
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.propagate import inject
from opentelemetry import context

app = Flask(__name__)

# OpenTelemetry setup
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "api-service",
    "service.version": "1.0.0"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint=os.getenv('JAEGER_ENDPOINT', 'http://jaeger:4318/v1/traces')
    )
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Auto-instrument
FlaskInstrumentor().instrument_app(app)
KafkaInstrumentor().instrument()
RedisInstrumentor().instrument()

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Redis client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "api"})

@app.route('/order', methods=['POST'])
def create_order():
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("create_order") as create_order_span:
        # Simulate validation delay
        validation_delay = random.uniform(0.1, 0.3)
        time.sleep(validation_delay)

        # simulate random delay
        with tracer.start_as_current_span("random_delay") as random_delay_span:
            random_delay = random.uniform(0.2, 0.3)
            time.sleep(random_delay)
            random_delay_span.set_attribute("random.delay", random_delay)
        
        order_id = str(uuid4())
        timestamp = time.time()
        
        order_data = {
            'orderId': order_id,
            'status': 'received',
            'timestamp': timestamp,
            'validation_delay': validation_delay
        }
        
        # Store in Redis
        redis_client.set(f"order:{order_id}", json.dumps(order_data))
        
        # Add span attributes
        create_order_span.set_attribute("order.id", order_id)
        create_order_span.set_attribute("order.status", "received")
        create_order_span.set_attribute("validation.delay", validation_delay)
        
        # Inject trace context into message headers
        headers = {}
        inject(headers)
        
        # Send to Kafka with trace context
        producer.send('orders', value=order_data, headers=[(k, v.encode() if isinstance(v, str) else v) for k, v in headers.items()])
        producer.flush()
        
        return jsonify({"orderId": order_id, "status": "received"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)