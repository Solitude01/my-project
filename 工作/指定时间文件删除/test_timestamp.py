#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时间戳功能
"""

import os
import time
from datetime import datetime
import tempfile
import shutil

# 创建测试文件夹和文件
def create_test_files():
    """创建测试文件用于验证时间戳功能"""
    test_dir = tempfile.mkdtemp(prefix="file_cleaner_test_")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 创建测试文件夹: {test_dir}")
    
    # 创建一些旧文件（模拟30天前的文件）
    old_time = time.time() - (30 * 24 * 60 * 60)
    
    for i in range(5):
        file_path = os.path.join(test_dir, f"old_file_{i}.log")
        with open(file_path, 'w') as f:
            f.write(f"这是测试文件 {i}，模拟30天前的文件")
        
        # 修改文件时间戳
        os.utime(file_path, (old_time, old_time))
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 创建旧文件: {file_path}")
    
    # 创建一些新文件（当前时间）
    for i in range(3):
        file_path = os.path.join(test_dir, f"new_file_{i}.txt")
        with open(file_path, 'w') as f:
            f.write(f"这是测试文件 {i}，当前时间的文件")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 创建新文件: {file_path}")
    
    return test_dir

def test_timestamp_functionality():
    """测试时间戳功能"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始测试时间戳功能")
    
    start_time = time.time()
    
    # 创建测试文件
    test_dir = create_test_files()
    
    # 模拟文件扫描过程
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始扫描文件夹...")
    scan_start = time.time()
    
    files_found = []
    for item in os.listdir(test_dir):
        file_path = os.path.join(test_dir, item)
        if os.path.isfile(file_path):
            files_found.append(file_path)
            mtime = os.path.getmtime(file_path)
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 发现文件: {item} (修改时间: {mtime_str})")
    
    scan_end = time.time()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 扫描完成，耗时: {scan_end - scan_start:.2f}秒")
    
    # 模拟文件过滤过程
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始过滤文件...")
    filter_start = time.time()
    
    old_files = []
    cutoff_time = time.time() - (30 * 24 * 60 * 60)
    
    for file_path in files_found:
        if os.path.getmtime(file_path) < cutoff_time:
            old_files.append(file_path)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 标记为旧文件: {os.path.basename(file_path)}")
    
    filter_end = time.time()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 过滤完成，耗时: {filter_end - filter_start:.2f}秒")
    
    # 模拟删除过程
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始删除文件...")
    delete_start = time.time()
    
    for file_path in old_files:
        try:
            os.remove(file_path)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 已删除: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 删除失败: {os.path.basename(file_path)} - {e}")
    
    delete_end = time.time()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 删除完成，耗时: {delete_end - delete_start:.2f}秒")
    
    # 清理测试文件夹
    try:
        shutil.rmtree(test_dir)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 清理测试文件夹: {test_dir}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 清理测试文件夹失败: {e}")
    
    total_time = time.time() - start_time
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 测试完成，总耗时: {total_time:.2f}秒")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 时间戳功能测试成功！")

if __name__ == "__main__":
    test_timestamp_functionality()