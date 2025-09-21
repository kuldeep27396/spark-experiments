# Apache Spark Executor Tuning | Executor Cores & Memory - Complete Guide

![Introduction to Executor Tuning](./screenshots/001_executor_tuning.png)

## Table of Contents
1. [Introduction to Executor Tuning](#introduction-to-executor-tuning)
2. [Understanding YARN Architecture](#understanding-yarn-architecture)
3. [Key Configuration Parameters](#key-configuration-parameters)
4. [Executor Types: Fat vs Thin vs Optimal](#executor-types-fat-vs-thin-vs-optimal)
5. [Memory Allocation Strategies](#memory-allocation-strategies)
6. [Performance Considerations](#performance-considerations)
7. [Practical Examples](#practical-examples)
8. [Best Practices](#best-practices)

---

## Introduction to Executor Tuning

![Executor Overview](./screenshots/002_executor_tuning.png)

Executor tuning is crucial for optimizing Apache Spark performance. This guide covers the essential concepts of executor cores, memory allocation, and how to configure them effectively for your workloads.

**Key Learning Objectives:**
- Understand the relationship between executor cores and memory
- Learn how to calculate optimal executor configurations
- Master YARN resource management for Spark applications
- Avoid common pitfalls in executor tuning

---

## Understanding YARN Architecture

![YARN Architecture Overview](./screenshots/003_executor_tuning.png)

### YARN Components
- **ResourceManager**: Global resource manager
- **NodeManager**: Per-node framework agent
- **ApplicationMaster**: Per-application manager
- **Container**: Resource allocation unit

### Resource Allocation Flow
1. Application requests resources from ResourceManager
2. ResourceManager allocates containers on NodeManagers
3. ApplicationMaster manages container lifecycle
4. Executors run within allocated containers

---

## Key Configuration Parameters

![Configuration Parameters](./screenshots/004_executor_tuning.png)

### Core Spark Parameters

```mermaid
graph TD
    A[Spark Configuration] --> B[Executor Resources]
    A --> C[Dynamic Allocation]
    A --> D[Memory Settings]

    B --> B1[spark.executor.cores]
    B --> B2[spark.executor.memory]
    B --> B3[spark.executor.instances]

    C --> C1[spark.dynamicAllocation.enabled]
    C --> C2[spark.dynamicAllocation.minExecutors]
    C --> C3[spark.dynamicAllocation.maxExecutors]

    D --> D1[spark.memory.fraction]
    D --> D2[spark.memory.storageFraction]
```

### Essential Parameters

| Parameter | Default | Description | Recommendation |
|-----------|---------|-------------|----------------|
| `spark.executor.cores` | 1 | Number of cores per executor | 4-5 cores |
| `spark.executor.memory` | 1g | Memory per executor | Based on workload |
| `spark.executor.instances` | 2 | Number of executors | Calculate based on resources |
| `spark.dynamicAllocation.enabled` | false | Enable dynamic allocation | true for production |
| `spark.shuffle.service.enabled` | false | Enable shuffle service | true for dynamic allocation |

---

## Executor Types: Fat vs Thin vs Optimal

![Executor Types Comparison](./screenshots/005_executor_tuning.png)

### 1. Fat Executors
- **Characteristics**: Many cores, high memory
- **Pros**: Better data locality, reduced network traffic
- **Cons**: Resource fragmentation, longer GC pauses
- **Use Case**: Large-scale batch processing

### 2. Thin Executors
- **Characteristics**: Few cores, low memory
- **Pros**: Better resource utilization, shorter GC pauses
- **Cons**: Increased network traffic, overhead
- **Use Case**: Interactive queries, streaming

### 3. Optimal Executors
- **Characteristics**: Balanced cores and memory
- **Pros**: Best of both worlds
- **Cons**: Requires careful calculation
- **Use Case**: General-purpose workloads

---

## Memory Allocation Strategies

![Memory Allocation](./screenshots/006_executor_tuning.png)

### Memory Components

```mermaid
graph LR
    A[Container Memory] --> B[Executor Memory]
    A --> C[Overhead Memory]

    B --> D[Unified Memory]
    B --> E[Reserved Memory]

    D --> F[Execution Memory]
    D --> G[Storage Memory]

    F --> H[Shuffle Memory]
    F --> I[Computation Memory]

    G --> J[Cache Memory]
    G --> K[Broadcast Memory]
```

### Calculation Formulas

#### 1. Total Container Memory
```bash
Total Container Memory = Executor Memory + Overhead Memory
```

#### 2. Overhead Memory
```bash
Overhead Memory = max(384MB, Executor Memory × 0.1)
```

#### 3. Unified Memory
```bash
Unified Memory = Executor Memory × spark.memory.fraction (default: 0.6)
```

#### 4. Execution Memory
```bash
Execution Memory = Unified Memory × (1 - spark.memory.storageFraction)
```

---

## Performance Considerations

![Performance Factors](./screenshots/007_executor_tuning.png)

### 1. Garbage Collection Impact
- More memory per executor → Longer GC pauses
- Parallel GC helps with large heaps
- Consider G1GC for heaps > 4GB

### 2. Data Locality
- Fat executors improve data locality
- Reduce network shuffling
- Better HDFS throughput

### 3. Resource Utilization
- Avoid resource fragmentation
- Balance core and memory allocation
- Consider cluster size and workload

---

## Practical Examples

![Example Configurations](./screenshots/008_executor_tuning.png)

### Example 1: Small Cluster (16 cores, 64GB RAM)

```bash
# Configuration
--executor-cores 4 \
--executor-memory 8G \
--num-executors 3 \
--conf spark.dynamicAllocation.enabled=false
```

**Calculation:**
- Total executor memory: 3 × 8GB = 24GB
- Overhead memory: 3 × max(384MB, 8GB × 0.1) = 3 × 800MB = 2.4GB
- Total required: 24GB + 2.4GB = 26.4GB
- Cores used: 3 × 4 = 12 cores

### Example 2: Large Cluster (64 cores, 256GB RAM)

```bash
# Configuration
--executor-cores 5 \
--executor-memory 16G \
--num-executors 10 \
--conf spark.dynamicAllocation.enabled=true \
--conf spark.dynamicAllocation.minExecutors=5 \
--conf spark.dynamicAllocation.maxExecutors=15
```

**Calculation:**
- Total executor memory: 10 × 16GB = 160GB
- Overhead memory: 10 × max(384MB, 16GB × 0.1) = 10 × 1.6GB = 16GB
- Total required: 160GB + 16GB = 176GB
- Cores used: 10 × 5 = 50 cores

### Example 3: Streaming Workload

```bash
# Configuration
--executor-cores 2 \
--executor-memory 4G \
--num-executors 8 \
--conf spark.dynamicAllocation.enabled=true \
--conf spark.shuffle.service.enabled=true \
--conf spark.streaming.backpressure.enabled=true
```

---

## Best Practices

![Best Practices Summary](./screenshots/009_executor_tuning.png)

### 1. General Guidelines
- **Start with 4-5 cores per executor**
- **Balance memory and core allocation**
- **Enable dynamic allocation for production**
- **Monitor resource utilization**

### 2. Memory Settings
- **spark.memory.fraction**: 0.6-0.8 (default: 0.6)
- **spark.memory.storageFraction**: 0.4-0.6 (default: 0.5)
- **Leave 10-20% memory for system overhead**

### 3. Dynamic Allocation
- **Enable shuffle service**
- **Set appropriate min/max bounds**
- **Monitor executor allocation patterns**

### 4. Advanced Tuning
```bash
# Garbage Collection Tuning
--conf spark.executor.extraJavaOptions="-XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35"

# Shuffle Optimization
--conf spark.shuffle.file.buffer=64k \
--conf spark.reducer.maxSizeInFlight=96m \
--conf spark.shuffle.io.maxRetries=3
```

### 5. Monitoring and Debugging
- Use Spark UI to monitor executor performance
- Check for GC pauses and memory pressure
- Monitor shuffle spill metrics
- Profile executor resource utilization

---

## Common Pitfalls and Solutions

![Troubleshooting Guide](./screenshots/010_executor_tuning.png)

### 1. Out of Memory Errors
**Symptoms**: Executors dying with OOM
**Solutions**:
- Increase executor memory
- Reduce data partitioning
- Optimize memory settings
- Check for memory leaks

### 2. Resource Fragmentation
**Symptoms**: Poor cluster utilization
**Solutions**:
- Use dynamic allocation
- Optimize executor size
- Balance core/memory ratio

### 3. Long GC Pauses
**Symptoms**: Performance degradation
**Solutions**:
- Reduce executor memory
- Use parallel GC
- Consider G1GC
- Optimize memory settings

### 4. Network Issues
**Symptoms**: High shuffle times
**Solutions**:
- Increase executor cores
- Optimize data locality
- Tune shuffle parameters

---

## Advanced Configuration Examples

### Production-Grade Configuration

```bash
#!/bin/bash

# Production Spark Configuration
spark-submit \
  --class com.example.MySparkJob \
  --master yarn \
  --deploy-mode cluster \
  --executor-cores 4 \
  --executor-memory 12G \
  --num-executors 20 \
  --driver-memory 4G \
  --conf spark.dynamicAllocation.enabled=true \
  --conf spark.dynamicAllocation.minExecutors=10 \
  --conf spark.dynamicAllocation.maxExecutors=30 \
  --conf spark.shuffle.service.enabled=true \
  --conf spark.memory.fraction=0.7 \
  --conf spark.memory.storageFraction=0.4 \
  --conf spark.executor.extraJavaOptions="-XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35" \
  --conf spark.sql.shuffle.partitions=200 \
  --conf spark.default.parallelism=400 \
  --conf spark.shuffle.file.buffer=64k \
  --conf spark.reducer.maxSizeInFlight=96m \
  my-app.jar \
  application-args
```

### Memory-Intensive Workload Configuration

```bash
#!/bin/bash

# Memory-Intensive Configuration
spark-submit \
  --class com.example.MemoryIntensiveJob \
  --master yarn \
  --deploy-mode cluster \
  --executor-cores 3 \
  --executor-memory 24G \
  --num-executors 8 \
  --driver-memory 8G \
  --conf spark.dynamicAllocation.enabled=false \
  --conf spark.memory.fraction=0.8 \
  --conf spark.memory.storageFraction=0.3 \
  --conf spark.executor.extraJavaOptions="-XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35 -XX:MaxGCPauseMillis=200" \
  --conf spark.sql.inMemoryColumnarStorage.compressed=true \
  --conf spark.sql.inMemoryColumnarStorage.batchSize=10000 \
  my-app.jar \
  application-args
```

### Streaming Configuration

```bash
#!/bin/bash

# Streaming Configuration
spark-submit \
  --class com.example.StreamingJob \
  --master yarn \
  --deploy-mode cluster \
  --executor-cores 2 \
  --executor-memory 6G \
  --num-executors 12 \
  --driver-memory 4G \
  --conf spark.dynamicAllocation.enabled=true \
  --conf spark.dynamicAllocation.minExecutors=6 \
  --conf spark.dynamicAllocation.maxExecutors=20 \
  --conf spark.shuffle.service.enabled=true \
  --conf spark.streaming.backpressure.enabled=true \
  --conf spark.streaming.blockInterval=200ms \
  --conf spark.streaming.receiver.maxRate=10000 \
  --conf spark.executor.extraJavaOptions="-XX:+UseG1GC" \
  my-app.jar \
  application-args
```

---

## Performance Monitoring

### Key Metrics to Monitor

![Monitoring Dashboard](./screenshots/011_executor_tuning.png)

1. **Executor Metrics**
   - Active executors
   - Completed tasks
   - Shuffle read/write
   - GC time

2. **Memory Metrics**
   - Used memory
   - Available memory
   - Memory spills
   - Cache usage

3. **Resource Utilization**
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk I/O

### Spark UI Monitoring

![Spark UI Overview](./screenshots/012_executor_tuning.png)

The Spark UI provides comprehensive monitoring capabilities:
- **Executors Tab**: Individual executor performance
- **Storage Tab**: Memory and cache usage
- **SQL Tab**: Query execution details
- **Jobs Tab**: Job progress and metrics

---

## Conclusion

![Summary](./screenshots/013_executor_tuning.png)

### Key Takeaways
1. **Balance is crucial**: Find the right balance between cores and memory
2. **Start conservative**: Begin with recommended settings and optimize
3. **Monitor continuously**: Use Spark UI and metrics for ongoing optimization
4. **Consider workload**: Different workloads require different configurations
5. **Use dynamic allocation**: Enable for production environments

### Final Recommendations
- **For general use**: 4-5 cores, 8-16GB memory per executor
- **For memory-intensive**: 3-4 cores, 16-32GB memory per executor
- **For streaming**: 2-3 cores, 4-8GB memory per executor
- **Always test**: Validate configurations with your specific workload

### Next Steps
1. Review your current Spark applications
2. Calculate optimal executor configurations
3. Implement monitoring and alerting
4. Continuously optimize based on metrics

---

## Additional Resources

### Reference Materials
- [Spark Official Documentation](https://spark.apache.org/docs/latest/)
- [YARN Architecture Guide](https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/YARN.html)
- [Spark Tuning Guide](https://spark.apache.org/docs/latest/tuning.html)

### Tools and Utilities
- Spark UI for monitoring
- YARN ResourceManager UI
- Cluster resource calculators
- Performance benchmarking tools

### Community Resources
- Spark mailing lists
- Stack Overflow
- Apache Spark JIRA
- Performance tuning blogs and articles

---

**Note**: This guide provides comprehensive coverage of Apache Spark executor tuning concepts. Always test configurations in your specific environment and adjust based on your workload characteristics and cluster resources.