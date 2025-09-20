"""
Realistic Workload Simulator for Performance Testing

Provides CPU-intensive and I/O-intensive operations to replace artificial delays
with realistic workloads that show meaningful resource usage patterns.
"""

import time
import random
import json
import hashlib
import tempfile
import os
import requests
from io import StringIO


class WorkloadSimulator:
    """
    Simulates realistic CPU and I/O intensive workloads for performance testing.
    """
    
    def __init__(self, redis_client=None):
        """
        Initialize workload simulator.
        
        Args:
            redis_client: Optional Redis client for I/O operations
        """
        self.redis_client = redis_client
    
    def get_random_workload(self, service_type="general"):
        """
        Get a random workload configuration based on service type.
        
        Args:
            service_type (str): Service type - api, processing, notification, analytics
            
        Returns:
            tuple: (workload_type, intensity, operation_name)
        """
        workload_configs = {
            "api": {
                "cpu_heavy": 0.4,
                "io_heavy": 0.6,
                "intensities": ["light", "medium"]
            },
            "processing": {
                "cpu_heavy": 0.7,
                "io_heavy": 0.3,
                "intensities": ["medium", "heavy", "severe"]
            },
            "notification": {
                "cpu_heavy": 0.3,
                "io_heavy": 0.7,
                "intensities": ["light", "medium", "heavy"]
            },
            "analytics": {
                "cpu_heavy": 0.5,
                "io_heavy": 0.5,
                "intensities": ["medium", "heavy", "severe"]
            },
            "general": {
                "cpu_heavy": 0.5,
                "io_heavy": 0.5,
                "intensities": ["light", "medium"]
            }
        }
        
        config = workload_configs.get(service_type, workload_configs["general"])
        
        # Randomly choose workload type based on service characteristics
        workload_type = random.choices(
            ["cpu_heavy", "io_heavy"],
            weights=[config["cpu_heavy"], config["io_heavy"]]
        )[0]
        
        intensity = random.choice(config["intensities"])
        
        return workload_type, intensity
    
    def execute_workload(self, workload_type, intensity, span=None):
        """
        Execute a workload and optionally attach metadata to span.
        
        Args:
            workload_type (str): cpu_heavy or io_heavy
            intensity (str): light, medium, or heavy
            span: Optional OpenTelemetry span to attach metadata
            
        Returns:
            dict: Workload execution metadata
        """
        start_time = time.time()
        
        if workload_type == "cpu_heavy":
            operation, result = self._execute_cpu_workload(intensity)
        else:
            operation, result = self._execute_io_workload(intensity)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        metadata = {
            "workload_type": workload_type,
            "intensity": intensity,
            "operation": operation,
            "duration_ms": round(duration_ms, 2),
            "result": result
        }
        
        # Attach to span if provided
        if span:
            span.set_attribute("workload.type", workload_type)
            span.set_attribute("workload.intensity", intensity)
            span.set_attribute("workload.operation", operation)
            span.set_attribute("workload.duration_ms", duration_ms)
            if result.get("items_processed"):
                span.set_attribute("workload.items_processed", result["items_processed"])
        
        return metadata
    
    def _execute_cpu_workload(self, intensity):
        """Execute CPU-intensive operations."""
        
        if intensity == "light":
            return self._light_cpu_work()
        elif intensity == "medium":
            return self._medium_cpu_work()
        elif intensity == "heavy":
            return self._heavy_cpu_work()
        else:  # severe
            return self._severe_cpu_work()
    
    def _execute_io_workload(self, intensity):
        """Execute I/O-intensive operations."""
        
        if intensity == "light":
            return self._light_io_work()
        elif intensity == "medium":
            return self._medium_io_work()
        elif intensity == "heavy":
            return self._heavy_io_work()
        else:  # severe
            return self._severe_io_work()
    
    def _light_cpu_work(self):
        """Light CPU work: Simple calculations and small data processing."""
        operation = "json_processing"
        
        # Generate and process small JSON data
        data = {"items": [{"id": i, "value": random.randint(1, 1000)} for i in range(100)]}
        
        # Process data with calculations
        total = 0
        for item in data["items"]:
            total += item["value"] * 2 + item["id"]
        
        # Some string operations
        result_string = json.dumps(data)
        hash_result = hashlib.md5(result_string.encode()).hexdigest()
        
        return operation, {"total": total, "hash": hash_result, "items_processed": 100}
    
    def _medium_cpu_work(self):
        """Medium CPU work: Hash computations and data transformations."""
        operation = "hash_computation"
        
        # Generate larger dataset
        data_size = random.randint(1000, 5000)
        processed_hashes = []
        
        for i in range(data_size):
            # Create data to hash
            data_item = f"item_{i}_{random.randint(1, 10000)}_{time.time()}"
            
            # Multiple hash rounds for CPU work
            hash_result = data_item
            for _ in range(3):
                hash_result = hashlib.sha256(hash_result.encode()).hexdigest()
            
            processed_hashes.append(hash_result)
        
        # Final aggregation
        final_hash = hashlib.sha256(''.join(processed_hashes[:10]).encode()).hexdigest()
        
        return operation, {
            "items_processed": data_size,
            "final_hash": final_hash,
            "hash_count": len(processed_hashes)
        }
    
    def _heavy_cpu_work(self):
        """Heavy CPU work: Complex algorithms targeting 95% CPU usage."""
        operation = "intensive_prime_computation"
        
        # Much larger prime computation to reach 95% CPU
        start_num = random.randint(10000, 20000)
        end_num = start_num + random.randint(50000, 100000)
        
        primes = []
        composite_factors = {}
        
        # More intensive computation - find primes and factor composites
        for num in range(start_num, end_num):
            if self._is_prime(num):
                primes.append(num)
            else:
                # Factor composite numbers (CPU intensive)
                factors = self._factor_number(num)
                if len(factors) > 2:  # Non-trivial factors
                    composite_factors[num] = factors
        
        # Additional heavy computations
        prime_sum = sum(primes)
        
        # Expensive hash computations on results
        hash_rounds = []
        for i in range(min(1000, len(primes))):
            data = f"{primes[i]}_{prime_sum}_{i}"
            hash_result = data
            # Multiple SHA256 rounds for CPU burn
            for _ in range(10):
                hash_result = hashlib.sha256(hash_result.encode()).hexdigest()
            hash_rounds.append(hash_result)
        
        # Final intensive computation
        final_computation = 0
        for i in range(len(hash_rounds)):
            final_computation += hash(hash_rounds[i]) % 1000000
        
        return operation, {
            "range_start": start_num,
            "range_end": end_num,
            "primes_found": len(primes),
            "composites_factored": len(composite_factors),
            "hash_rounds": len(hash_rounds),
            "final_computation": final_computation,
            "items_processed": end_num - start_num
        }
    
    def _light_io_work(self):
        """Light I/O work: Simple Redis operations."""
        operation = "redis_basic"
        
        if not self.redis_client:
            # Fallback to file I/O
            return self._file_io_work("light")
        
        # Simple Redis operations
        key_prefix = f"test_{int(time.time())}_{random.randint(1, 1000)}"
        operations_count = random.randint(5, 15)
        
        for i in range(operations_count):
            key = f"{key_prefix}:{i}"
            value = {"id": i, "timestamp": time.time(), "data": f"value_{i}"}
            self.redis_client.set(key, json.dumps(value), ex=60)  # 60 sec expiry
        
        # Read back some values
        retrieved_count = 0
        for i in range(min(operations_count, 5)):
            key = f"{key_prefix}:{i}"
            if self.redis_client.get(key):
                retrieved_count += 1
        
        return operation, {
            "operations_count": operations_count,
            "retrieved_count": retrieved_count,
            "items_processed": operations_count
        }
    
    def _medium_io_work(self):
        """Medium I/O work: File operations and multiple Redis queries."""
        operation = "file_and_redis"
        
        # File I/O component
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            data_lines = random.randint(100, 500)
            for i in range(data_lines):
                line_data = {
                    "line": i,
                    "timestamp": time.time(),
                    "random_data": random.randint(1, 10000)
                }
                f.write(json.dumps(line_data) + "\n")
            temp_file = f.name
        
        # Read back and process
        processed_lines = 0
        total_value = 0
        try:
            with open(temp_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    total_value += data["random_data"]
                    processed_lines += 1
        finally:
            os.unlink(temp_file)
        
        # Redis component if available
        redis_ops = 0
        if self.redis_client:
            key_prefix = f"medium_work_{int(time.time())}"
            for i in range(random.randint(10, 30)):
                key = f"{key_prefix}:{i}"
                self.redis_client.hset(key, mapping={
                    "id": i,
                    "total": total_value + i,
                    "processed": processed_lines
                })
                redis_ops += 1
        
        return operation, {
            "file_lines": data_lines,
            "processed_lines": processed_lines,
            "redis_operations": redis_ops,
            "total_value": total_value,
            "items_processed": processed_lines + redis_ops
        }
    
    def _heavy_io_work(self):
        """Heavy I/O work: Intensive Redis and file operations targeting 95% CPU."""
        operation = "intensive_io_operations"
        
        # Much larger file processing to reach 95% CPU
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            data_lines = random.randint(5000, 15000)  # Much larger files
            for i in range(data_lines):
                # Create much larger data objects with complex structures
                line_data = {
                    "id": i,
                    "timestamp": time.time(),
                    "payload": "x" * random.randint(500, 2000),  # Larger payloads
                    "complex_data": {
                        "nested_array": [random.randint(1, 1000) for _ in range(50)],
                        "nested_dict": {f"key_{j}": f"value_{j}_{random.randint(1, 10000)}" 
                                      for j in range(20)},
                        "hash_data": hashlib.md5(f"data_{i}_{time.time()}".encode()).hexdigest()
                    },
                    "metadata": {
                        "source": f"source_{i % 20}",
                        "tags": [f"tag_{j}" for j in range(random.randint(5, 15))],
                        "computed_values": [i * j for j in range(10)]
                    }
                }
                f.write(json.dumps(line_data) + "\n")
            temp_file = f.name
        
        # Process file with multiple passes
        file_stats = {"total_size": 0, "line_count": 0, "avg_payload_size": 0}
        total_payload_size = 0
        
        try:
            # First pass: intensive statistics and validation
            with open(temp_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    file_stats["line_count"] += 1
                    payload_size = len(data["payload"])
                    total_payload_size += payload_size
                    file_stats["total_size"] += len(line)
                    
                    # Additional CPU-intensive validation
                    for i in range(5):  # Multiple hash validations
                        hashlib.sha256(data["payload"].encode()).hexdigest()
            
            file_stats["avg_payload_size"] = total_payload_size / file_stats["line_count"]
            
            # Second pass: intensive filtering and complex aggregation
            processed_items = []
            complex_computations = []
            with open(temp_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    
                    # Complex filtering with CPU-intensive operations
                    computed_value = sum(data["complex_data"]["nested_array"])
                    hash_validation = hashlib.md5(
                        f"{data['id']}_{computed_value}".encode()
                    ).hexdigest()
                    
                    if len(data["payload"]) > 500:  # Higher threshold for heavy work
                        processed_items.append({
                            "id": data["id"],
                            "size": len(data["payload"]),
                            "tag_count": len(data["metadata"]["tags"]),
                            "computed_value": computed_value,
                            "hash_validation": hash_validation
                        })
                        complex_computations.append(computed_value)
            
            # Third pass: additional CPU-intensive analysis
            analysis_results = []
            with open(temp_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    # Complex string operations and transformations
                    for key, value in data["complex_data"]["nested_dict"].items():
                        result = hashlib.sha1(f"{key}_{value}".encode()).hexdigest()
                        analysis_results.append(len(result))
                        
        finally:
            os.unlink(temp_file)
        
        # Heavy Redis operations if available
        redis_ops = 0
        if self.redis_client:
            # Simulate batch processing
            pipeline = self.redis_client.pipeline()
            batch_key = f"heavy_batch_{int(time.time())}"
            
            for item in processed_items[:50]:  # Limit to prevent overwhelming
                pipeline.zadd(f"{batch_key}:sizes", {f"item_{item['id']}": item["size"]})
                pipeline.sadd(f"{batch_key}:processed", item["id"])
                redis_ops += 2
            
            pipeline.execute()
        
        return operation, {
            "file_lines": data_lines,
            "file_size_bytes": file_stats["total_size"],
            "filtered_items": len(processed_items),
            "complex_computations": len(complex_computations),
            "analysis_results": len(analysis_results),
            "avg_payload_size": round(file_stats["avg_payload_size"], 2),
            "redis_operations": redis_ops,
            "items_processed": len(processed_items)
        }
    
    def _severe_cpu_work(self):
        """SEVERE CPU work: Double the intensity of heavy workloads for extreme stress testing."""
        operation = "extreme_cpu_computation"
        
        # Much more intensive than heavy workloads (roughly double)
        start_num = random.randint(20000, 40000)  # Double the range of heavy
        end_num = start_num + random.randint(100000, 200000)  # Double the range
        
        primes = []
        composite_factors = {}
        
        # Double the intensive computation of heavy workloads
        for num in range(start_num, end_num):
            if self._is_prime(num):
                primes.append(num)
            else:
                # Factor composite numbers (CPU intensive)
                factors = self._factor_number(num)
                if len(factors) > 2:  # Non-trivial factors
                    composite_factors[num] = factors
        
        # Additional heavy computations - double the hash rounds
        prime_sum = sum(primes)
        
        # More expensive hash computations than heavy (double the rounds)
        hash_rounds = []
        for i in range(min(2000, len(primes))):  # Double the iteration count
            data = f"{primes[i]}_{prime_sum}_{i}"
            hash_result = data
            # Double the SHA256 rounds compared to heavy (20 vs 10)
            for _ in range(20):
                hash_result = hashlib.sha256(hash_result.encode()).hexdigest()
            hash_rounds.append(hash_result)
        
        # Final intensive computation - double the complexity
        final_computation = 0
        for i in range(len(hash_rounds)):
            # More complex computation than heavy
            final_computation += (hash(hash_rounds[i]) * i) % 10000000
            
        # Additional memory stress (but not infinite)
        memory_stress = []
        for i in range(100):  # Limited memory allocation
            large_data = [random.randint(1, 1000000) for _ in range(50000)]
            memory_stress.append(large_data)
        
        return operation, {
            "range_start": start_num,
            "range_end": end_num,
            "primes_found": len(primes),
            "composites_factored": len(composite_factors),
            "hash_rounds": len(hash_rounds),
            "memory_objects_created": len(memory_stress),
            "final_computation": final_computation,
            "items_processed": end_num - start_num
        }
    
    def _severe_io_work(self):
        """SEVERE I/O work: Double the intensity of heavy I/O operations for extreme stress testing."""
        operation = "extreme_io_operations"
        
        # Much larger file processing than heavy (double the intensity)
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            data_lines = random.randint(30000, 60000)  # Double the heavy workload (was 5k-15k)
            for i in range(data_lines):
                # Create even larger data objects with more complex structures
                line_data = {
                    "id": i,
                    "timestamp": time.time(),
                    "payload": "x" * random.randint(1000, 4000),  # Double the payload size
                    "complex_data": {
                        "nested_array": [random.randint(1, 1000) for _ in range(100)],  # Double the array size
                        "nested_dict": {f"key_{j}": f"value_{j}_{random.randint(1, 10000)}" 
                                      for j in range(40)},  # Double the dict size
                        "hash_data": hashlib.md5(f"data_{i}_{time.time()}".encode()).hexdigest(),
                        "additional_arrays": [[random.random() for _ in range(20)] for _ in range(10)]
                    },
                    "metadata": {
                        "source": f"source_{i % 40}",
                        "tags": [f"tag_{j}" for j in range(random.randint(10, 30))],  # Double the tags
                        "computed_values": [i * j for j in range(20)],  # Double the computed values
                        "extra_data": "Z" * 1000  # Additional data
                    }
                }
                f.write(json.dumps(line_data) + "\n")
            temp_file = f.name
        
        # Process file with even more intensive passes (4 passes instead of 3)
        file_stats = {"total_size": 0, "line_count": 0, "avg_payload_size": 0}
        total_payload_size = 0
        
        try:
            # First pass: intensive statistics and validation (double the hash rounds)
            with open(temp_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    file_stats["line_count"] += 1
                    payload_size = len(data["payload"])
                    total_payload_size += payload_size
                    file_stats["total_size"] += len(line)
                    
                    # Double the CPU-intensive validation (10 hash rounds vs 5)
                    for i in range(10):
                        hashlib.sha256(data["payload"].encode()).hexdigest()
            
            file_stats["avg_payload_size"] = total_payload_size / file_stats["line_count"]
            
            # Second pass: even more intensive filtering and complex aggregation
            processed_items = []
            complex_computations = []
            with open(temp_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    
                    # More complex filtering with double the CPU-intensive operations
                    computed_value = sum(data["complex_data"]["nested_array"])
                    for arr in data["complex_data"]["additional_arrays"]:
                        computed_value += sum(arr)
                    
                    # Double the hash validations
                    hash_validation = hashlib.md5(f"{data['id']}_{computed_value}".encode()).hexdigest()
                    hash_validation2 = hashlib.sha1(f"{hash_validation}_{computed_value}".encode()).hexdigest()
                    
                    if len(data["payload"]) > 1000:  # Lower threshold due to larger payloads
                        processed_items.append({
                            "id": data["id"],
                            "size": len(data["payload"]),
                            "tag_count": len(data["metadata"]["tags"]),
                            "computed_value": computed_value,
                            "hash_validation": hash_validation,
                            "hash_validation2": hash_validation2
                        })
                        complex_computations.append(computed_value)
            
            # Third pass: double the CPU-intensive analysis
            analysis_results = []
            with open(temp_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    # Double the complex string operations and transformations
                    for key, value in data["complex_data"]["nested_dict"].items():
                        result1 = hashlib.sha1(f"{key}_{value}".encode()).hexdigest()
                        result2 = hashlib.md5(f"{result1}_{key}".encode()).hexdigest()
                        analysis_results.append(len(result1) + len(result2))
            
            # Fourth pass: additional extreme processing
            final_analysis = []
            with open(temp_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    # Complex mathematical operations on nested arrays
                    for arr in data["complex_data"]["additional_arrays"]:
                        result = sum(x * i for i, x in enumerate(arr))
                        final_analysis.append(result)
                        
        finally:
            os.unlink(temp_file)
        
        # Extreme Redis operations if available (double the intensity)
        redis_ops = 0
        if self.redis_client:
            # Double the batch processing intensity
            pipeline = self.redis_client.pipeline()
            batch_key = f"extreme_batch_{int(time.time())}"
            
            for item in processed_items[:100]:  # Double the limit (was 50)
                pipeline.zadd(f"{batch_key}:sizes", {f"item_{item['id']}": item["size"]})
                pipeline.sadd(f"{batch_key}:processed", item["id"])
                pipeline.hset(f"{batch_key}:data", item["id"], item["computed_value"])
                pipeline.lpush(f"{batch_key}:queue", f"processed_{item['id']}")
                redis_ops += 4  # 4 operations per item (double the complexity)
            
            pipeline.execute()
        
        return operation, {
            "file_lines": data_lines,
            "file_size_bytes": file_stats["total_size"],
            "filtered_items": len(processed_items),
            "complex_computations": len(complex_computations),
            "analysis_results": len(analysis_results),
            "final_analysis": len(final_analysis),
            "avg_payload_size": round(file_stats["avg_payload_size"], 2),
            "redis_operations": redis_ops,
            "items_processed": len(processed_items)
        }
    
    def _file_io_work(self, intensity):
        """Fallback file I/O work when Redis not available."""
        operation = f"file_io_{intensity}"
        
        size_map = {"light": (10, 50), "medium": (100, 300), "heavy": (500, 1500)}
        min_lines, max_lines = size_map[intensity]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            data_lines = random.randint(min_lines, max_lines)
            for i in range(data_lines):
                f.write(f"line_{i}_{random.randint(1, 10000)}_{time.time()}\n")
            temp_file = f.name
        
        # Read and count
        line_count = 0
        try:
            with open(temp_file, 'r') as f:
                for line in f:
                    line_count += 1
                    if intensity == "heavy":
                        # Additional processing for heavy workload
                        hashlib.md5(line.encode()).hexdigest()
        finally:
            os.unlink(temp_file)
        
        return operation, {"lines_written": data_lines, "lines_read": line_count, "items_processed": line_count}
    
    def _is_prime(self, n):
        """Check if a number is prime (CPU intensive for larger numbers)."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def _factor_number(self, n):
        """Factor a number into its prime factors (CPU intensive)."""
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors


def create_workload_simulator(redis_client=None):
    """
    Factory function to create a WorkloadSimulator instance.
    
    Args:
        redis_client: Optional Redis client for I/O operations
        
    Returns:
        WorkloadSimulator: Configured simulator instance
    """
    return WorkloadSimulator(redis_client)