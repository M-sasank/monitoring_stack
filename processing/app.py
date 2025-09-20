import os
import time
import random
import json
import threading
import psutil
from collections import deque
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

from utils.resource_monitor import create_global_monitor
from utils.workload_simulator import create_workload_simulator

# OpenTelemetry setup
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "processing-service",
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
    'orders',
    bootstrap_servers=bootstrap_servers,
    group_id='processing-service',
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

# Global resource monitor instance
resource_monitor = create_global_monitor(sample_interval=0.1)

# Global workload simulator
workload_simulator = create_workload_simulator(redis_client)

def process_order(order_data, headers):
    tracer = trace.get_tracer(__name__)
    
    # Extract trace context from Kafka message headers
    header_dict = {k: v.decode() if isinstance(v, bytes) else v for k, v in headers}
    parent_context = extract(header_dict)
    
    with tracer.start_as_current_span("process_order", context=parent_context) as process_order_span:
        start_time = time.time()
        order_id = order_data['orderId']
        
        # Realistic data transformation workload
        with tracer.start_as_current_span("data_transformation") as transformation_span:
            transformation_start = time.time()
            workload_type, intensity = workload_simulator.get_random_workload("processing")
            transformation_result = workload_simulator.execute_workload(
                workload_type, intensity, transformation_span
            )
            transformation_end = time.time()
            resource_monitor.attach_to_span(transformation_span, transformation_start, transformation_end)
        
        # Realistic business logic processing workload
        with tracer.start_as_current_span("business_logic") as logic_span:
            logic_start = time.time()
            workload_type, intensity = workload_simulator.get_random_workload("processing")
            logic_result = workload_simulator.execute_workload(
                workload_type, intensity, logic_span
            )
            logic_end = time.time()
            resource_monitor.attach_to_span(logic_span, logic_start, logic_end)
        
        # Update order data
        processed_order = {
            **order_data,
            'status': 'processed',
            'processed_timestamp': time.time(),
            'transformation_result': transformation_result,
            'logic_result': logic_result
        }
        
        # Store processing status in Redis
        redis_client.set(f"processing:{order_id}", json.dumps({
            'status': 'processed',
            'transformation_operation': transformation_result["operation"],
            'logic_operation': logic_result["operation"],
            'timestamp': time.time()
        }))
        
        end_time = time.time()
        
        # Add resource stats to main span
        resource_monitor.attach_to_span(process_order_span, start_time, end_time,
                                      cpu_threshold=85, memory_threshold_mb=250)
        
        # Add span attributes
        process_order_span.set_attribute("order.id", order_id)
        process_order_span.set_attribute("order.status", "processed")
        process_order_span.set_attribute("transformation.operation", transformation_result["operation"])
        process_order_span.set_attribute("logic.operation", logic_result["operation"])
        
        # Inject trace context into next message
        next_headers = {}
        inject(next_headers)
        
        # Send to next service with trace context
        producer.send('processed-orders', value=processed_order, headers=[(k, v.encode() if isinstance(v, str) else v) for k, v in next_headers.items()])
        producer.flush()
        
        print(f"Processed order {order_id} (transformation: {transformation_result['operation']}, logic: {logic_result['operation']})")

def main():
    print("Processing Service started. Waiting for orders...")
    
    for message in consumer:
        try:
            order_data = message.value
            headers = message.headers or []
            process_order(order_data, headers)
        except Exception as e:
            print(f"Error processing order: {e}")

if __name__ == '__main__':
    main()