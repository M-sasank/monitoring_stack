"""
Continuous Resource Monitoring for Distributed Tracing

A lightweight approach to correlate CPU and memory usage with specific operations
in distributed tracing systems. Uses background sampling to capture resource 
utilization during span execution.
"""

import time
import threading
import psutil
from collections import deque


class ResourceMonitor:
    """
    Background resource monitor that continuously samples CPU and memory usage.
    
    Provides correlation between resource consumption and span execution timeframes.
    Designed to be lightweight with bounded memory usage.
    """
    
    def __init__(self, sample_interval=0.1, max_samples=100):
        """
        Initialize the resource monitor.
        
        Args:
            sample_interval (float): Seconds between samples (default: 0.1 = 100ms)
            max_samples (int): Maximum samples to keep in memory (default: 100)
        """
        self.samples = deque(maxlen=max_samples)
        self.sample_interval = sample_interval
        self.process = psutil.Process()
        self._running = False
        self._thread = None
    
    def start(self):
        """Start background resource sampling in a daemon thread."""
        if self._running:
            return  # Already running
            
        self._running = True
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop background sampling and wait for thread to finish."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
    
    def _sample_loop(self):
        """
        Continuous sampling loop running in background thread.
        Gracefully handles exceptions to prevent monitoring from breaking the app.
        """
        while self._running:
            try:
                sample = {
                    'timestamp': time.time(),
                    'cpu': self.process.cpu_percent(interval=0.01),
                    'memory_mb': self.process.memory_info().rss / 1024 / 1024
                }
                self.samples.append(sample)
            except Exception:
                # Graceful degradation - continue sampling even if one sample fails
                pass
            
            time.sleep(self.sample_interval)
    
    def get_stats_during_span(self, start_time, end_time):
        """
        Calculate resource statistics for a specific time window.
        
        Args:
            start_time (float): Start timestamp of the span
            end_time (float): End timestamp of the span
            
        Returns:
            dict: Resource statistics including avg/max/min CPU and memory,
                  or None if no samples available for the time window
        """
        if start_time >= end_time:
            return None
            
        # Filter samples within the span timeframe
        relevant_samples = [
            s for s in self.samples 
            if start_time <= s['timestamp'] <= end_time
        ]
        
        if not relevant_samples:
            return None
        
        # Extract CPU and memory values
        cpus = [s['cpu'] for s in relevant_samples]
        mems = [s['memory_mb'] for s in relevant_samples]
        
        return {
            'cpu_avg': sum(cpus) / len(cpus),
            'cpu_max': max(cpus),
            'cpu_min': min(cpus),
            'memory_avg': sum(mems) / len(mems),
            'memory_max': max(mems),
            'memory_min': min(mems),
            'sample_count': len(relevant_samples)
        }
    
    def attach_to_span(self, span, start_time, end_time, 
                      cpu_threshold=80, memory_threshold_mb=200):
        """
        Convenience method to attach resource stats to an OpenTelemetry span.
        
        Args:
            span: OpenTelemetry span object
            start_time (float): Span start timestamp
            end_time (float): Span end timestamp  
            cpu_threshold (float): CPU percentage threshold for cpu_bound flag
            memory_threshold_mb (float): Memory MB threshold for memory_high flag
        """
        stats = self.get_stats_during_span(start_time, end_time)
        if not stats:
            return
        
        # Attach resource metrics as span attributes
        span.set_attribute("resource.cpu.avg", round(stats['cpu_avg'], 2))
        span.set_attribute("resource.cpu.max", round(stats['cpu_max'], 2))
        span.set_attribute("resource.cpu.min", round(stats['cpu_min'], 2))
        span.set_attribute("resource.memory.avg_mb", round(stats['memory_avg'], 2))
        span.set_attribute("resource.memory.max_mb", round(stats['memory_max'], 2))
        span.set_attribute("resource.memory.min_mb", round(stats['memory_min'], 2))
        span.set_attribute("resource.samples", stats['sample_count'])
        
        # Performance flags for easy filtering in Jaeger
        if stats['cpu_max'] > cpu_threshold:
            span.set_attribute("resource.cpu_bound", True)
        if stats['memory_max'] > memory_threshold_mb:
            span.set_attribute("resource.memory_high", True)


def create_global_monitor(sample_interval=0.1, max_samples=100):
    """
    Factory function to create and start a global ResourceMonitor instance.
    
    Args:
        sample_interval (float): Seconds between samples
        max_samples (int): Maximum samples to keep in memory
        
    Returns:
        ResourceMonitor: Started monitor instance
    """
    monitor = ResourceMonitor(sample_interval, max_samples)
    monitor.start()
    return monitor