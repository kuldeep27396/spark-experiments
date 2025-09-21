#!/usr/bin/env python3
"""
Apache Spark Memory Management - Practical Configuration Examples

This script provides practical examples of Spark memory configuration
for different workload types. It demonstrates how to calculate and
configure memory settings based on the concepts covered in the video.

Usage:
    python memory_config_examples.py

This will show different memory configurations and their calculations.
"""

from pyspark.sql import SparkSession
import time

def create_spark_session(config_name, executor_memory, memory_fraction=0.6,
                          storage_fraction=0.5, off_heap_enabled=False,
                          off_heap_size="0g"):
    """
    Create a Spark session with specific memory configuration.

    Args:
        config_name: Name of the configuration for display
        executor_memory: Total executor memory (e.g., "10g")
        memory_fraction: Fraction for unified memory (default: 0.6)
        storage_fraction: Fraction for storage within unified memory (default: 0.5)
        off_heap_enabled: Whether to enable off-heap memory
        off_heap_size: Size of off-heap memory (e.g., "2g")

    Returns:
        SparkSession with specified configuration
    """
    builder = SparkSession.builder \
        .appName(f"Memory_Management_{config_name}") \
        .master("local[*]") \
        .config("spark.executor.memory", executor_memory) \
        .config("spark.memory.fraction", memory_fraction) \
        .config("spark.memory.storageFraction", storage_fraction) \
        .config("spark.memory.offHeap.enabled", str(off_heap_enabled).lower()) \
        .config("spark.memory.offHeap.size", off_heap_size) \
        .config("spark.ui.port", "4050")

    spark = builder.getOrCreate()
    return spark

def calculate_memory_layout(executor_memory_gb, memory_fraction=0.6,
                            storage_fraction=0.5, off_heap_size_gb=0):
    """
    Calculate memory layout based on configuration parameters.

    Args:
        executor_memory_gb: Total executor memory in GB
        memory_fraction: Fraction for unified memory
        storage_fraction: Fraction for storage within unified memory
        off_heap_size_gb: Off-heap memory size in GB

    Returns:
        Dictionary with memory calculations
    """
    # Convert to GB for calculations
    exec_mem = executor_memory_gb

    # Unified memory calculations
    unified_mem = exec_mem * memory_fraction
    storage_mem = unified_mem * storage_fraction
    execution_mem = unified_mem - storage_mem

    # Non-unified memory calculations
    non_unified_mem = exec_mem - unified_mem
    reserved_mem = 0.3  # 300MB reserved
    user_mem = non_unified_mem - reserved_mem

    # Overhead memory calculation
    overhead_mem = max(0.384, exec_mem * 0.1)  # max(384MB, 10% of executor)

    # Total container memory
    total_container_mem = exec_mem + overhead_mem + off_heap_size_gb

    return {
        'executor_memory': exec_mem,
        'unified_memory': unified_mem,
        'storage_memory': storage_mem,
        'execution_memory': execution_mem,
        'user_memory': user_mem,
        'reserved_memory': reserved_mem,
        'overhead_memory': overhead_mem,
        'off_heap_memory': off_heap_size_gb,
        'total_container_memory': total_container_mem
    }

def print_memory_calculations(config_name, calculations):
    """Print memory calculations in a formatted way."""
    print(f"\n{'='*60}")
    print(f"Memory Configuration: {config_name}")
    print(f"{'='*60}")

    print(f"Executor Memory: {calculations['executor_memory']:.1f} GB")
    print(f"  ├── Unified Memory ({calculations['unified_memory']/calculations['executor_memory']*100:.0f}%): {calculations['unified_memory']:.1f} GB")
    print(f"  │   ├── Storage Memory ({calculations['storage_memory']/calculations['unified_memory']*100:.0f}%): {calculations['storage_memory']:.1f} GB")
    print(f"  │   └── Execution Memory ({calculations['execution_memory']/calculations['unified_memory']*100:.0f}%): {calculations['execution_memory']:.1f} GB")
    print(f"  └── Non-Unified Memory ({calculations['user_memory']/calculations['executor_memory']*100:.0f}%): {calculations['executor_memory'] - calculations['unified_memory']:.1f} GB")
    print(f"      ├── User Memory: {calculations['user_memory']:.1f} GB")
    print(f"      └── Reserved Memory: {calculations['reserved_memory']:.1f} GB")

    print(f"\nAdditional Memory:")
    print(f"  Overhead Memory: {calculations['overhead_memory']:.1f} GB")
    print(f"  Off-Heap Memory: {calculations['off_heap_memory']:.1f} GB")
    print(f"  Total Container Memory: {calculations['total_container_memory']:.1f} GB")

def demonstrate_memory_usage(spark, config_name):
    """
    Demonstrate memory usage with sample operations.
    """
    print(f"\n{'='*40}")
    print(f"Demonstrating {config_name}")
    print(f"{'='*40}")

    # Create sample data
    data = [(i, f"value_{i}", i * 100) for i in range(10000)]

    # Create DataFrame
    df = spark.createDataFrame(data, ["id", "name", "value"])

    print("Created DataFrame with 10,000 records")

    # Show memory configuration
    config = spark.sparkContext.getConf()
    print(f"Executor Memory: {config.get('spark.executor.memory')}")
    print(f"Memory Fraction: {config.get('spark.memory.fraction')}")
    print(f"Storage Fraction: {config.get('spark.memory.storageFraction')}")
    print(f"Off-Heap Enabled: {config.get('spark.memory.offHeap.enabled')}")
    print(f"Off-Heap Size: {config.get('spark.memory.offHeap.size')}")

    # Demonstrate caching (storage memory usage)
    print("\nCaching DataFrame (uses Storage Memory)...")
    start_time = time.time()
    df.cache().count()  # Cache and count to force execution
    cache_time = time.time() - start_time
    print(f"Cached in {cache_time:.2f} seconds")

    # Demonstrate aggregation (execution memory usage)
    print("\nPerforming aggregation (uses Execution Memory)...")
    start_time = time.time()
    result = df.groupBy("value % 10").count().collect()
    agg_time = time.time() - start_time
    print(f"Aggregation completed in {agg_time:.2f} seconds")
    print(f"Result: {result}")

    # Unpersist to free memory
    df.unpersist()
    print("DataFrame unpersisted")

def main():
    """Main function to demonstrate different memory configurations."""

    print("Apache Spark Memory Management - Practical Examples")
    print("=" * 60)
    print("This script demonstrates different memory configurations")
    print("based on the concepts covered in the video tutorial.")

    configurations = [
        {
            'name': 'General Purpose (Default)',
            'executor_memory': '10g',
            'memory_fraction': 0.6,
            'storage_fraction': 0.5,
            'off_heap_enabled': False,
            'off_heap_size': '0g'
        },
        {
            'name': 'Shuffle-Heavy Workload',
            'executor_memory': '16g',
            'memory_fraction': 0.7,
            'storage_fraction': 0.3,
            'off_heap_enabled': False,
            'off_heap_size': '0g'
        },
        {
            'name': 'Cache-Heavy Workload',
            'executor_memory': '16g',
            'memory_fraction': 0.6,
            'storage_fraction': 0.7,
            'off_heap_enabled': False,
            'off_heap_size': '0g'
        },
        {
            'name': 'GC-Sensitive Workload',
            'executor_memory': '10g',
            'memory_fraction': 0.6,
            'storage_fraction': 0.5,
            'off_heap_enabled': True,
            'off_heap_size': '2g'
        }
    ]

    for i, config in enumerate(configurations):
        print(f"\n{'='*80}")
        print(f"Configuration {i+1}: {config['name']}")
        print(f"{'='*80}")

        # Calculate memory layout
        calculations = calculate_memory_layout(
            executor_memory_gb=float(config['executor_memory'].replace('g', '')),
            memory_fraction=config['memory_fraction'],
            storage_fraction=config['storage_fraction'],
            off_heap_size_gb=float(config['off_heap_size'].replace('g', ''))
        )

        # Print calculations
        print_memory_calculations(config['name'], calculations)

        # Create Spark session and demonstrate
        spark = create_spark_session(**config)

        try:
            demonstrate_memory_usage(spark, config['name'])
        except Exception as e:
            print(f"Error during demonstration: {e}")
        finally:
            spark.stop()
            print("Spark session stopped")

    print(f"\n{'='*80}")
    print("Summary of Memory Configurations")
    print(f"{'='*80}")

    print("\nBest Practices:")
    print("1. Start with default configuration and monitor performance")
    print("2. Adjust based on workload type (shuffle-heavy vs cache-heavy)")
    print("3. Use off-heap memory for GC-sensitive applications")
    print("4. Monitor Spark UI for memory usage and GC time")
    print("5. Only cache DataFrames that will be reused multiple times")

    print("\nCommon Mistakes to Avoid:")
    print("1. Caching DataFrames that are never reused")
    print("2. Using default configuration for all workload types")
    print("3. Ignoring memory pressure and GC pauses")
    print("4. Enabling off-heap memory without proper need")

    print(f"\n{'='*80}")
    print("For detailed explanations, see: Spark_Memory_Management_Complete_Guide.md")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()