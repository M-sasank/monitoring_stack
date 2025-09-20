import os
import time
import random
import json
from kafka import KafkaProducer, KafkaConsumer
import redis
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.propagate import extract, inject
from opentelemetry import context

# OpenTelemetry setup
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "notification-service",
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
KafkaInstrumentor().instrument()
RedisInstrumentor().instrument()

# Kafka setup
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

consumer = KafkaConsumer(
    'processed-orders',
    bootstrap_servers=bootstrap_servers,
    group_id='notification-service',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest'
)

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Redis client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)

def send_notification(order_data, headers):
    tracer = trace.get_tracer(__name__)
    
    # Extract trace context from Kafka message headers
    header_dict = {k: v.decode() if isinstance(v, bytes) else v for k, v in headers}
    parent_context = extract(header_dict)
    
    with tracer.start_as_current_span("send_notification", context=parent_context) as span:
        order_id = order_data['orderId']
        
        # Simulate email send delay
        notification_delay = random.uniform(0.2, 0.8)
        time.sleep(notification_delay)
        
        # Update order data
        notified_order = {
            **order_data,
            'status': 'notified',
            'notified_timestamp': time.time(),
            'notification_delay': notification_delay
        }
        
        # Store notification status in Redis
        redis_client.set(f"notification:{order_id}", json.dumps({
            'status': 'notified',
            'notification_delay': notification_delay,
            'timestamp': time.time()
        }))
        
        # Add span attributes
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.status", "notified")
        span.set_attribute("notification.delay", notification_delay)
        
        # Inject trace context into next message
        next_headers = {}
        inject(next_headers)
        
        # Send to analytics service with trace context
        producer.send('notified-orders', value=notified_order, headers=[(k, v.encode() if isinstance(v, str) else v) for k, v in next_headers.items()])
        producer.flush()
        
        print(f"Sent notification for order {order_id} (delay: {notification_delay:.2f}s)")

def main():
    print("Notification Service started. Waiting for processed orders...")
    
    for message in consumer:
        try:
            order_data = message.value
            headers = message.headers or []
            send_notification(order_data, headers)
        except Exception as e:
            print(f"Error sending notification: {e}")

if __name__ == '__main__':
    main()