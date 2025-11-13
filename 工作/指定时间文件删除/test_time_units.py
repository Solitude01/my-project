#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时间单位和自定义时间戳功能
"""

import os
import time
import datetime
from datetime import datetime as dt

def test_time_calculation():
    """测试时间计算逻辑"""
    print("=== 测试时间计算逻辑 ===")
    
    # 测试不同时间单位
    seconds_per_unit = {
        '分钟': 60,
        '小时': 60 * 60,
        '天': 24 * 60 * 60,
        '月': 30 * 24 * 60 * 60,  # 近似值
        '年': 365 * 24 * 60 * 60  # 近似值
    }
    
    current_time = time.time()
    
    for unit, seconds in seconds_per_unit.items():
        for value in [1, 5, 10]:
            cutoff_time = current_time - (value * seconds)
            cutoff_date = dt.fromtimestamp(cutoff_time)
            print(f"{value}{unit}前: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print()

def test_custom_timestamp():
    """测试自定义时间戳"""
    print("=== 测试自定义时间戳 ===")
    
    # 测试不同格式的时间戳
    test_timestamps = [
        "2024-01-01 00:00:00",
        "2024-06-15 12:30:45",
        "2023-12-31 23:59:59",
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ]
    
    for timestamp_str in test_timestamps:
        try:
            custom_dt = dt.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            timestamp = custom_dt.timestamp()
            print(f"时间戳 '{timestamp_str}' -> {timestamp} -> {dt.fromtimestamp(timestamp)}")
        except ValueError as e:
            print(f"时间戳 '{timestamp_str}' 格式错误: {e}")
    
    print()

def create_test_files():
    """创建测试文件用于验证"""
    print("=== 创建测试文件 ===")
    
    test_dir = "test_files"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    current_time = time.time()
    
    # 创建不同时间的文件
    file_times = [
        ("1小时前.txt", current_time - 3600),
        ("1天前.txt", current_time - 86400),
        ("1周前.txt", current_time - 604800),
        ("1个月前.txt", current_time - 2592000),  # 30天
        ("1年前.txt", current_time - 31536000),   # 365天
    ]
    
    for filename, file_time in file_times:
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"测试文件 - {filename}")
        
        # 修改文件时间
        os.utime(filepath, (file_time, file_time))
        
        file_dt = dt.fromtimestamp(file_time)
        print(f"创建文件: {filename} - 时间: {file_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"测试文件已创建在: {test_dir}")
    print()

def test_file_filtering():
    """测试文件过滤逻辑"""
    print("=== 测试文件过滤逻辑 ===")
    
    test_dir = "test_files"
    if not os.path.exists(test_dir):
        print("请先运行 create_test_files() 创建测试文件")
        return
    
    # 测试不同的时间阈值
    current_time = time.time()
    test_thresholds = [
        ("1小时前", current_time - 3600),
        ("1天前", current_time - 86400),
        ("1周前", current_time - 604800),
        ("自定义时间戳", dt.strptime("2024-01-01 00:00:00", '%Y-%m-%d %H:%M:%S').timestamp())
    ]
    
    for threshold_name, cutoff_time in test_thresholds:
        print(f"\n--- 阈值: {threshold_name} ({dt.fromtimestamp(cutoff_time).strftime('%Y-%m-%d %H:%M:%S')}) ---")
        
        for filename in os.listdir(test_dir):
            filepath = os.path.join(test_dir, filename)
            if os.path.isfile(filepath):
                file_mtime = os.path.getmtime(filepath)
                file_dt = dt.fromtimestamp(file_mtime)
                
                if file_mtime < cutoff_time:
                    print(f"  [需要删除] {filename} - 修改时间: {file_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"  [保留] {filename} - 修改时间: {file_dt.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("时间单位和自定义时间戳功能测试")
    print("=" * 50)
    
    test_time_calculation()
    test_custom_timestamp()
    create_test_files()
    test_file_filtering()
    
    print("测试完成！")