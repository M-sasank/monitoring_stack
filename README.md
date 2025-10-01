# Distributed Tracing & Performance Monitoring Learning Guide

This repository demonstrates a comprehensive distributed tracing and performance monitoring system using **Jaeger**, **OpenTelemetry**, and **realistic workload simulation**. It's designed to teach fundamental concepts of microservices observability, performance bottleneck identification, and system architecture analysis.

## 🎯 What You'll Learn

### Core Concepts
- **Distributed Tracing**: End-to-end request flow across microservices
- **OpenTelemetry Instrumentation**: Auto vs manual trace instrumentation
- **Resource Monitoring**: Real-time CPU/memory correlation with operations
- **Performance Bottleneck Identification**: Using traces to find system limitations
- **Workload Simulation**: Realistic vs artificial performance testing

### Advanced Insights
- **Head-of-line Blocking**: How single-threaded processing affects entire systems
- **Resource Correlation**: Linking CPU/memory usage to specific operations
- **Trace Context Propagation**: Maintaining trace continuity across async boundaries
- **Performance Scaling Patterns**: Identifying when and how to scale services

---

## 🏗️ System Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐
│             │    │              │    │                 │    │                 │
│ API Service │───▶│ Processing   │───▶│ Notification    │───▶│ Analytics       │
│             │    │ Service      │    │ Service         │    │ Service         │
│ (Port 8080) │    │              │    │                 │    │                 │
└─────────────┘    └──────────────┘    └─────────────────┘    └─────────────────┘
        │                   │                    │                        │
        │                   │                    │                        │
        ▼                   ▼                    ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Kafka Message Bus                                   │
│                         (orders → processed-orders → notified-orders)           │
└─────────────────────────────────────────────────────────────────────────────────┘
        │                   │                    │                        │
        ▼                   ▼                    ▼                        ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐
│             │    │              │    │                 │    │                 │
│    Redis    │    │   Jaeger     │    │   Zookeeper     │    │   Resource      │
│  (Storage)  │    │ (Tracing UI) │    │  (Kafka Coord)  │    │  Monitoring     │
│             │    │              │    │                 │    │                 │
└─────────────┘    └──────────────┘    └─────────────────┘    └─────────────────┘
```

### Service Communication Flow
1. **HTTP Request** → API Service (REST endpoint)
2. **Kafka Message** → Processing Service (async processing)
3. **Kafka Message** → Notification Service (async notification)
4. **Kafka Message** → Analytics Service (async analytics)

Each service performs **realistic workloads** and exports **detailed traces** to Jaeger.

---

## 🔬 Workload Simulation System

### Workload Types

#### **CPU-Intensive Operations**
- **Light**: JSON processing, simple calculations (100 items)
- **Medium**: Hash computation, data transformations (1k-5k items)
- **Heavy**: Prime computation + factorization + multi-round hashing (50k-100k items)
- **Severe**: Extreme prime computation + memory stress (100k-200k items)

#### **I/O-Intensive Operations**
- **Light**: Basic Redis operations (5-15 ops)
- **Medium**: File operations + Redis queries (100-500 lines)
- **Heavy**: Large file processing + intensive Redis operations (5k-15k lines)
- **Severe**: Massive file processing + extreme Redis operations (30k-60k lines)

### Service-Specific Configurations

| Service      | CPU Heavy | I/O Heavy | Intensities Available    | Use Case                     |
|--------------|-----------|-----------|--------------------------|------------------------------|
| API          | 40%       | 60%       | light, medium            | Input validation, audit logs |
| Processing   | 70%       | 30%       | medium, heavy, **severe**| Data transformation, business logic |
| Notification | 30%       | 70%       | light, medium, heavy     | Message formatting, delivery |
| Analytics    | 50%       | 50%       | medium, heavy, **severe**| Data analysis, aggregation   |

### Workload Operations You'll See in Jaeger

**CPU Operations**:
- `json_processing` - Light JSON manipulation
- `hash_computation` - SHA256 hash calculations  
- `intensive_prime_computation` - Enhanced prime finding + factorization
- `extreme_cpu_computation` - Severe CPU stress (double heavy intensity)

**I/O Operations**:
- `redis_basic` - Simple Redis get/set operations
- `file_and_redis` - File processing + Redis operations
- `intensive_io_operations` - Large file processing + complex Redis ops
- `extreme_io_operations` - Massive file processing (4 passes, double intensity)

---

## 📊 Resource Monitoring & Correlation

### Real-Time Resource Tracking

The system includes **continuous resource monitoring** that samples CPU and memory every 100ms and correlates usage with specific operations:

```json
{
  "resource.cpu.avg": 156.8,
  "resource.cpu.max": 196.0,
  "resource.cpu.min": 117.6,
  "resource.cpu_bound": true,
  "resource.memory.avg_mb": 67.73,
  "resource.memory.max_mb": 68.29,
  "resource.memory.min_mb": 67.16,
  "resource.samples": 2
}
```

### Understanding CPU Values > 100%

**Why you see 196% CPU**:
- 100% = 1 full CPU core utilized
- 196% = Nearly 2 full CPU cores utilized
- This indicates **multi-core utilization** by intensive workloads

### Resource Flags

- `resource.cpu_bound: true` - Operation is CPU-intensive
- `resource.memory_threshold_exceeded: true` - Memory usage exceeded threshold
- Higher `resource.samples` - Longer-running operations

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- 4+ CPU cores recommended
- 8GB+ RAM recommended

### Quick Start

1. **Clone and Start Services**:
```bash
git clone <repository>
cd monitoring
docker-compose up --build -d
```

2. **Verify Services**:
```bash
docker-compose ps
# All services should be "Up"
```

3. **Access Interfaces**:
- **Jaeger UI**: http://localhost:16686
- **API Service**: http://localhost:8080
- **Redis**: localhost:6379

### Generate Test Data

**Basic Request**:
```bash
curl -X POST http://localhost:8080/order \
  -H "Content-Type: application/json" \
  -d '{"item": "test-product", "quantity": 1}'
```

**Load Testing**:
```bash
# Generate multiple requests
for i in {1..10}; do
  curl -X POST http://localhost:8080/order \
    -H "Content-Type: application/json" \
    -d '{"item": "product-'$i'", "quantity": '$i'}'
  sleep 1
done
```

---

## 🔍 What to Observe in Jaeger

### 1. End-to-End Trace Flow

**Complete Request Journey**:
```
API Service (create_order)
├── input_validation (CPU/I/O workload)
├── audit_logging (CPU/I/O workload)
└── → Kafka publish

Processing Service (process_order)  
├── data_transformation (CPU/I/O workload)
├── business_logic (CPU/I/O workload)
└── → Kafka publish

Notification Service (notify_order)
└── message_formatting (CPU/I/O workload)

Analytics Service (analyze_order)
└── data_analysis (CPU/I/O workload)
```

### 2. Performance Patterns to Identify

#### **Head-of-Line Blocking**
Look at span start times:
```
API Span:        [----] 10:30:00 → 10:30:01 (order 1)
Processing Span: [--------] 10:30:01 → 10:30:15 (heavy: 14s)

API Span:        [----] 10:30:02 → 10:30:03 (order 2)  
Processing Span:        [waiting...] → 10:30:15 → 10:30:20 (delayed!)
```

**Observation**: Later requests wait for heavy operations to complete.

#### **Resource Utilization Patterns**
- **Light workloads**: 20-40% CPU, <50MB memory
- **Heavy workloads**: 90-100% CPU, 100-200MB memory  
- **Severe workloads**: 150-200% CPU (multi-core), 200MB+ memory

#### **Workload Distribution**
Check span attributes:
- `workload.type`: cpu_heavy vs io_heavy
- `workload.intensity`: light → medium → heavy → severe
- `workload.operation`: Specific operation performed

### 3. Trace Context Propagation

**Successful Propagation**: All spans connected in single trace
**Failed Propagation**: Separate traces per service (broken flow)

Look for consistent `trace_id` across all services in a single request.

### 4. Error Patterns

**Service Crashes** (with severe workloads):
- Incomplete spans (start but no finish)
- Container restarts in docker logs
- Consumer lag in Kafka

**Resource Exhaustion**:
- Memory thresholds exceeded
- Very high CPU utilization (>200%)
- Long operation durations

---

## 📈 Performance Analysis Techniques

### 1. Identifying Bottlenecks

**Single Point of Failure**:
```bash
# Check consumer lag
docker exec monitoring-kafka-1 kafka-consumer-groups \
  --bootstrap-server localhost:29092 \
  --describe --group processing-service
```

**Resource Correlation**:
- Compare CPU usage between light vs heavy operations
- Identify memory leaks (increasing baseline usage)
- Find I/O-bound vs CPU-bound operations

### 2. Scaling Decisions

**When to Scale Horizontally**:
- Consistent consumer lag
- High CPU utilization across multiple cores
- Queue buildup during peak loads

**When to Optimize Code**:
- Inefficient algorithms (high CPU for simple operations)
- Memory leaks (increasing memory usage)
- Excessive I/O operations

### 3. Workload Characterization

**Understanding Service Profiles**:
- **API Service**: Fast input validation, minimal processing
- **Processing Service**: CPU-intensive transformation algorithms
- **Notification Service**: I/O-heavy message formatting and delivery
- **Analytics Service**: Mixed CPU/I/O for data analysis

---

## 🎓 Learning Exercises

### Exercise 1: Basic Tracing
1. Send 5 requests and find them in Jaeger
2. Identify the complete trace flow for each request
3. Note the different workload types that were executed

### Exercise 2: Performance Comparison
1. Send requests and identify light vs heavy workloads
2. Compare CPU and memory usage between them
3. Calculate the performance difference (duration, resource usage)

### Exercise 3: Bottleneck Identification
1. Send 10 rapid requests (no delay between them)
2. Observe the processing delays in subsequent requests
3. Identify which service creates the bottleneck and why

### Exercise 4: Resource Correlation
1. Find a trace with `intensive_prime_computation`
2. Note the CPU usage (likely >150%)
3. Compare with `json_processing` operation
4. Understand why certain operations use multiple CPU cores

### Exercise 5: Severe Workload Analysis
1. Wait for a severe workload to trigger (processing/analytics services)
2. Observe the extreme resource usage (200%+ CPU, high memory)
3. Note how long other requests are delayed
4. Understand the impact on system throughput

### Exercise 6: System Scaling Design
1. Identify the current throughput limitation
2. Design solutions for:
   - Horizontal scaling (multiple containers)
   - Async processing (non-blocking operations)
   - Load balancing strategies
3. Estimate the performance improvement

---

## 🔧 Advanced Configuration

### Workload Intensity Modification

Edit `utils/workload_simulator.py` to adjust intensities:

```python
# Increase severe workload intensity
"processing": {
    "cpu_heavy": 0.8,  # More CPU-heavy workloads
    "io_heavy": 0.2,
    "intensities": ["heavy", "severe"]  # Only intense workloads
}
```

### Resource Monitoring Tuning

Adjust monitoring sensitivity in `utils/resource_monitor.py`:

```python
# More frequent sampling
resource_monitor = create_global_monitor(sample_interval=0.05)  # 50ms

# Different thresholds
resource_monitor.attach_to_span(span, start, end, 
                               cpu_threshold=70,      # Lower CPU threshold
                               memory_threshold_mb=100) # Lower memory threshold
```

### Docker Resource Limits

Test resource constraints:

```yaml
processing-service:
  deploy:
    resources:
      limits:
        cpus: '2.0'     # Limit to 2 CPU cores
        memory: 1G      # Limit to 1GB RAM
```

---

## 🚨 Common Issues & Solutions

### Issue: No Traces in Jaeger
**Symptoms**: Empty Jaeger UI, no services listed
**Solutions**:
1. Check service health: `docker-compose ps`
2. Verify Jaeger endpoint: `http://localhost:16686`
3. Check for trace export errors in container logs

### Issue: Processing Service Not Consuming
**Symptoms**: Consumer lag increasing, no processing traces
**Solutions**:
1. Check if service is stuck in severe workload
2. Restart processing service: `docker-compose restart processing-service`
3. Verify Kafka connectivity: Check container logs

### Issue: Container Crashes
**Symptoms**: Service restarts frequently, incomplete traces
**Solutions**:
1. Severe workloads may exhaust resources
2. Increase Docker memory limits
3. Monitor with `docker stats` during execution

### Issue: Clock Skew Warnings
**Symptoms**: "invalid parent span IDs" in logs
**Solutions**:
1. This is a timing warning, traces still work
2. Usually occurs with severe workloads
3. Can be ignored for learning purposes

---

## 📚 Key Takeaways

### Distributed Tracing Benefits
- **End-to-End Visibility**: See complete request flow across services
- **Performance Correlation**: Link resource usage to specific operations
- **Bottleneck Identification**: Find architectural limitations
- **Realistic Testing**: Use actual workloads instead of artificial delays

### Real-World Insights
- **Single-threaded processing** creates head-of-line blocking
- **CPU-intensive operations** can utilize multiple cores effectively
- **Resource monitoring** reveals the true cost of operations
- **Async messaging** doesn't guarantee performance isolation

### Architecture Lessons
- **Microservices** require careful performance monitoring
- **Queue-based systems** need proper scaling strategies
- **Resource allocation** affects entire system throughput
- **Observability** is crucial for production systems

---

## 🤝 Contributing

This learning system is designed to be educational. Consider extending it with:

- Additional workload types (network-intensive, database operations)
- More sophisticated scaling patterns (auto-scaling, circuit breakers)
- Different messaging patterns (pub/sub, request/reply)
- Advanced monitoring (custom metrics, alerting)

---

## 📖 Further Reading

- [OpenTelemetry Documentation](https://opentelemetry.io/)
- [Jaeger Documentation](https://www.jaegertracing.io/)
- [Distributed Systems Observability](https://distributed-systems-observability-ebook.humio.com/)
- [Site Reliability Engineering](https://sre.google/books/)

---

**Happy Learning!** 

This system demonstrates real-world distributed tracing concepts that are essential for modern microservices architecture. The realistic workloads and detailed resource monitoring provide insights that you can't get from simple synthetic tests.