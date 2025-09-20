import os
import time
import random
import json
from kafka import KafkaConsumer
import redis
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.propagate import extract
from opentelemetry import context

# OpenTelemetry setup
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "analytics-service",
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
    'notified-orders',
    bootstrap_servers=bootstrap_servers,
    group_id='analytics-service',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest'
)

# Redis client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)

def analyze_order(order_data, headers):
    tracer = trace.get_tracer(__name__)
    
    # Extract trace context from Kafka message headers
    header_dict = {k: v.decode() if isinstance(v, bytes) else v for k, v in headers}
    parent_context = extract(header_dict)
    
    with tracer.start_as_current_span("analyze_order", context=parent_context) as span:
        order_id = order_data['orderId']
        
        # Simulate database write delay
        analytics_delay = random.uniform(0.1, 0.4)
        time.sleep(analytics_delay)
        
        # Calculate total processing time
        start_time = order_data.get('timestamp')
        end_time = time.time()
        total_processing_time = end_time - start_time if start_time else 0
        
        # Create analytics record
        analytics_record = {
            'order_id': order_id,
            'status': 'completed',
            'total_processing_time': total_processing_time,
            'validation_delay': order_data.get('validation_delay', 0),
            'processing_delay': order_data.get('processing_delay', 0),
            'notification_delay': order_data.get('notification_delay', 0),
            'analytics_delay': analytics_delay,
            'completed_timestamp': end_time
        }
        
        # Store final analytics in Redis
        redis_client.set(f"analytics:{order_id}", json.dumps(analytics_record))
        
        # Increment order counter
        redis_client.incr("total_orders_processed")
        
        # Add span attributes
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.status", "completed")
        span.set_attribute("analytics.delay", analytics_delay)
        span.set_attribute("total.processing.time", total_processing_time)
        
        print(f"Analytics completed for order {order_id}")
        print(f"  Total processing time: {total_processing_time:.2f}s")
        print(f"  Validation delay: {analytics_record['validation_delay']:.2f}s")
        print(f"  Processing delay: {analytics_record['processing_delay']:.2f}s")
        print(f"  Notification delay: {analytics_record['notification_delay']:.2f}s")
        print(f"  Analytics delay: {analytics_delay:.2f}s")
        print("---")

def main():
    print("Analytics Service started. Waiting for notified orders...")
    
    for message in consumer:
        try:
            order_data = message.value
            headers = message.headers or []
            analyze_order(order_data, headers)
        except Exception as e:
            print(f"Error analyzing order: {e}")

if __name__ == '__main__':
    main()