#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自定义时间节点功能
"""

import os
import time
import datetime
from datetime import datetime as dt

def create_test_files_with_specific_times():
    """创建具有特定时间的测试文件"""
    print("=== 创建测试文件 ===")
    
    test_dir = "test_custom_time"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # 定义特定的时间节点
    time_nodes = [
        ("2024-01-01 00:00:00", "2024年元旦文件.txt"),
        ("2024-06-15 12:30:45", "2024年中期文件.txt"),
        ("2024-12-31 23:59:59", "2024年末文件.txt"),
        ("2023-06-01 10:30:00", "2023年文件.txt"),
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "当前时间文件.txt"),
    ]
    
    for time_str, filename in time_nodes:
        try:
            # 解析时间字符串
            file_time = dt.strptime(time_str, '%Y-%m-%d %H:%M:%S').timestamp()
            
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"测试文件 - {filename} - 创建时间: {time_str}")
            
            # 修改文件时间
            os.utime(filepath, (file_time, file_time))
            
            print(f"创建文件: {filename} - 时间: {time_str}")
        except Exception as e:
            print(f"创建文件 {filename} 失败: {e}")
    
    print(f"测试文件已创建在: {test_dir}")
    return test_dir

def test_custom_time_filtering(test_dir, custom_time_str):
    """测试自定义时间节点过滤"""
    print(f"\n=== 测试自定义时间节点: {custom_time_str} ===")
    
    try:
        # 解析自定义时间节点
        custom_dt = dt.strptime(custom_time_str, '%Y-%m-%d %H:%M:%S')
        cutoff_time = custom_dt.timestamp()
        
        print(f"时间节点: {custom_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"将删除该时间节点之前修改的文件")
        print("-" * 50)
        
        files_to_delete = []
        files_to_keep = []
        
        for filename in os.listdir(test_dir):
            filepath = os.path.join(test_dir, filename)
            if os.path.isfile(filepath):
                file_mtime = os.path.getmtime(filepath)
                file_dt = dt.fromtimestamp(file_mtime)
                
                if file_mtime < cutoff_time:
                    files_to_delete.append((filename, file_dt))
                    print(f"  [需要删除] {filename} - 修改时间: {file_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    files_to_keep.append((filename, file_dt))
                    print(f"  [保留] {filename} - 修改时间: {file_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n统计:")
        print(f"  需要删除的文件: {len(files_to_delete)} 个")
        print(f"  保留的文件: {len(files_to_keep)} 个")
        
        return files_to_delete, files_to_keep
        
    except ValueError as e:
        print(f"时间格式错误: {e}")
        return [], []

def test_relative_time_filtering(test_dir, time_value, time_unit):
    """测试相对时间过滤"""
    print(f"\n=== 测试相对时间: {time_value}{time_unit}前 ===")
    
    # 计算时间阈值
    seconds_per_unit = {
        '分钟': 60,
        '小时': 60 * 60,
        '天': 24 * 60 * 60,
        '月': 30 * 24 * 60 * 60,  # 近似值
        '年': 365 * 24 * 60 * 60  # 近似值
    }
    
    cutoff_time = time.time() - (time_value * seconds_per_unit[time_unit])
    cutoff_date = dt.fromtimestamp(cutoff_time)
    
    print(f"时间阈值: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"将删除{time_value}{time_unit}前修改的文件")
    print("-" * 50)
    
    files_to_delete = []
    files_to_keep = []
    
    for filename in os.listdir(test_dir):
        filepath = os.path.join(test_dir, filename)
        if os.path.isfile(filepath):
            file_mtime = os.path.getmtime(filepath)
            file_dt = dt.fromtimestamp(file_mtime)
            
            if file_mtime < cutoff_time:
                files_to_delete.append((filename, file_dt))
                print(f"  [需要删除] {filename} - 修改时间: {file_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                files_to_keep.append((filename, file_dt))
                print(f"  [保留] {filename} - 修改时间: {file_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n统计:")
    print(f"  需要删除的文件: {len(files_to_delete)} 个")
    print(f"  保留的文件: {len(files_to_keep)} 个")
    
    return files_to_delete, files_to_keep

def test_time_format_validation():
    """测试时间格式验证"""
    print("\n=== 测试时间格式验证 ===")
    
    test_formats = [
        "2024-01-01 00:00:00",  # 正确格式
        "2024-12-31 23:59:59",  # 正确格式
        "2024-06-15 12:30:45",  # 正确格式
        "2024-01-01",           # 错误格式 - 缺少时间
        "01-01-2024 00:00:00",   # 错误格式 - 日期格式错误
        "2024-01-01 25:00:00",  # 错误格式 - 小时数错误
        "2024-13-01 00:00:00",   # 错误格式 - 月份错误
        "invalid-date",          # 错误格式 - 完全无效
    ]
    
    for time_str in test_formats:
        try:
            dt.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            print(f"  ✓ 有效格式: '{time_str}'")
        except ValueError as e:
            print(f"  ✗ 无效格式: '{time_str}' - {e}")

if __name__ == "__main__":
    print("自定义时间节点功能测试")
    print("=" * 60)
    
    # 创建测试文件
    test_dir = create_test_files_with_specific_times()
    
    # 测试自定义时间节点
    test_custom_time_filtering(test_dir, "2024-06-01 00:00:00")
    test_custom_time_filtering(test_dir, "2024-01-01 00:00:00")
    
    # 测试相对时间
    test_relative_time_filtering(test_dir, 6, '月')
    test_relative_time_filtering(test_dir, 1, '年')
    
    # 测试时间格式验证
    test_time_format_validation()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("注意: 测试文件位于 'test_custom_time' 文件夹中，可手动清理")