# Continuous Resource Monitoring with Distributed Tracing

## Overview

A lightweight approach to correlate CPU and memory usage with specific operations in distributed tracing systems. Uses background sampling to capture resource utilization during span execution and attaches metrics as span attributes.

## How It Works

### Core Concept
- **Background Thread**: Continuously samples CPU/memory every 100ms
- **Span Correlation**: Maps resource usage to specific operation timeframes  
- **Trace Integration**: Attaches resource metrics as span attributes in Jaeger/OpenTelemetry

### Architecture
```
[Business Logic] ←→ [Tracing Span]
                         ↑
                   [Resource Stats]
                         ↑
                  [Background Sampler]
                         ↑
                   [System Resources]
```

### Implementation Pattern
```python
# 1. Background sampling
resource_monitor.start()  # Samples every 100ms

# 2. Span execution with timing
with tracer.start_span("operation") as span:
    start_time = time.time()
    # ... business logic ...
    end_time = time.time()
    
    # 3. Correlate and attach
    stats = monitor.get_stats_during_span(start_time, end_time)
    span.set_attribute("cpu.avg", stats['cpu_avg'])
```

## Advantages

### 🎯 **Spike Detection**
- Captures resource spikes that point-in-time sampling misses
- 100ms granularity reveals transient bottlenecks

### 🔗 **Operation Correlation** 
- Direct mapping: "Which operation caused high CPU?"
- Visible in existing Jaeger UI without additional tooling

### ⚡ **Lightweight Design**
- Bounded memory usage (circular buffer)
- Independent of request rate
- No external dependencies

### 📊 **Actionable Insights**
- Identify resource-bound vs I/O-bound operations
- Performance flags for easy filtering
- Statistical aggregation (avg/max/min)

## Disadvantages

### 🔧 **Application Code Changes**
- Requires modifications to each service
- Additional complexity in business logic

### 📈 **Limited Granularity**
- 100ms sampling may miss microsecond spikes
- Statistical approximation, not exact measurements

### 🏗️ **Single-Process Scope**
- Monitors individual service resources only
- No cluster-wide or node-level visibility

### 🎛️ **No Historical Aggregation**
- Per-trace data only, no time-series analysis
- Can't calculate P95/P99 across multiple requests

## Scale Characteristics

### **Light Scale (1K-50K requests/month)**
- **Memory**: ~5KB per service (negligible)
- **CPU**: <0.1% overhead per service
- **Storage**: +150KB/month in traces
- **Status**: ✅ **Optimal**

### **Medium Scale (50K-1M requests/month)**  
- **Memory**: ~5KB per service (unchanged)
- **CPU**: <0.1% overhead per service
- **Storage**: +3MB/month in traces
- **Status**: ✅ **Excellent**

### **High Scale (1M-100M requests/month)**
- **Memory**: ~5KB per service (unchanged)
- **CPU**: <0.1% overhead per service  
- **Storage**: +300MB/month in traces
- **Status**: ⚠️ **Good** (consider sampling)

### **Very High Scale (100M+ requests/month)**
- **Storage**: +30GB/month in traces
- **Trace volume**: May overwhelm Jaeger
- **Status**: ❌ **Consider alternatives**

## When to Use This Approach

### ✅ **Ideal Scenarios**
- **Learning/Development**: Understanding resource patterns
- **Debugging**: Correlating performance issues with resource usage
- **Small-Medium Scale**: <10M requests/month
- **Microservices**: Need per-service resource visibility
- **Existing Tracing**: Already using Jaeger/OpenTelemetry

### ❌ **Consider Alternatives When**
- **High Scale**: >100M requests/month
- **Production Monitoring**: Need alerts and dashboards
- **Historical Analysis**: Require time-series metrics
- **Infrastructure Focus**: Need node/cluster level metrics
- **Complex Aggregations**: P95/P99 across time periods

## Alternative Approaches

### **Prometheus + Grafana**
- **When**: Production monitoring, historical analysis
- **Pros**: Time-series, alerting, dashboards
- **Cons**: Additional infrastructure complexity

### **APM Solutions** (New Relic, DataDog)
- **When**: Comprehensive observability, minimal setup
- **Pros**: Full-stack monitoring, ML insights
- **Cons**: Cost, vendor lock-in

### **Metrics-First Approach**
- **When**: Primarily need aggregated data
- **Pros**: Efficient storage, fast queries
- **Cons**: Less correlation with individual requests

### **Sampling Strategies**
- **When**: High-scale tracing
- **Pros**: Reduced overhead and storage
- **Cons**: May miss important traces

## Implementation Considerations

### **Memory Management**
```python
# Bounded circular buffer prevents memory leaks
samples = deque(maxlen=100)  # Fixed size
```

### **Error Handling**
```python
# Graceful degradation if monitoring fails
try:
    stats = get_resource_stats()
    span.set_attribute("cpu.avg", stats['cpu'])
except:
    # Continue without resource data
    pass
```

### **Performance Flags**
```python
# Easy filtering in Jaeger UI
if cpu_max > 80:
    span.set_attribute("resource.cpu_bound", True)
if memory_max > threshold:
    span.set_attribute("resource.memory_high", True)
```

## Next Steps

### **Phase 1: Basic Implementation**
1. Add ResourceMonitor to one service
2. Test with simple operations
3. Verify span attributes in Jaeger

### **Phase 2: Service Rollout**  
1. Deploy to all microservices
2. Establish resource thresholds
3. Create Jaeger search queries

### **Phase 3: Enhancement**
1. Add custom metrics (disk I/O, network)
2. Implement dynamic sampling rates
3. Consider trace sampling for scale

### **Phase 4: Evolution** 
1. Evaluate Prometheus integration
2. Add alerting on resource patterns
3. Migrate to dedicated metrics stack if needed

## Conclusion

Continuous resource monitoring with span correlation provides excellent visibility for small-to-medium scale applications. It's particularly valuable for:

- **Development teams** learning about resource patterns
- **Debugging scenarios** where you need operation-level resource correlation  
- **Microservices architectures** requiring per-service insights
- **Cost-conscious environments** avoiding additional infrastructure

The approach scales well up to ~10M requests/month before storage and complexity concerns suggest transitioning to dedicated metrics platforms.