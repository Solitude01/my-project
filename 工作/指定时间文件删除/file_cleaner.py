#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文件夹清理器 - 根据修改时间删除文件
作者: Claude Code
功能: 可视化界面选择文件夹，根据时间条件删除旧文件
"""

import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime, timedelta
from pathlib import Path
import fnmatch

# 尝试导入send2trash库，用于安全删除（移动到回收站）
try:
    from send2trash import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False


class FileCleanerApp:
    """智能文件夹清理器主应用类"""

    def __init__(self, root):
        """初始化应用程序"""
        self.root = root
        self.root.title("智能文件夹清理器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 应用程序变量
        self.folder_path = tk.StringVar()  # 选择的文件夹路径
        self.time_value = tk.IntVar(value=30)  # 时间值（默认30）
        self.time_unit = tk.StringVar(value='天')  # 时间单位（默认天）
        self.time_mode = tk.StringVar(value="relative")  # 时间模式: relative 或 custom
        self.custom_timestamp = tk.StringVar(value="")  # 自定义时间节点
        self.include_subfolders = tk.BooleanVar(value=False)  # 是否包含子文件夹
        self.use_recycle_bin = tk.BooleanVar(value=True)  # 是否移动到回收站
        self.file_filter = tk.StringVar(value="*.*")  # 文件类型过滤

        # 创建界面
        self.create_widgets()
        self.update_status("准备就绪")

        # 如果send2trash不可用，警告用户
        if not SEND2TRASH_AVAILABLE:
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 警告：未安装send2trash库，将无法使用回收站功能。")
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 提示：运行 'pip install send2trash' 安装此库。")
            self.use_recycle_bin.set(False)
        
        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 智能文件夹清理器初始化完成")

    def create_widgets(self):
        """创建所有GUI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重，使界面可以自适应调整大小
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        current_row = 0

        # ========== 文件夹选择区域 ==========
        ttk.Label(main_frame, text="目标文件夹:", font=('Arial', 10, 'bold')).grid(
            row=current_row, column=0, sticky=tk.W, pady=5
        )
        current_row += 1

        # 文件夹路径显示框
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)

        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, state='readonly')
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(folder_frame, text="浏览...", command=self.browse_folder).grid(row=0, column=1)
        current_row += 1

        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )
        current_row += 1

        # ========== 时间条件设置区域 ==========
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=current_row, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Label(time_frame, text="删除", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))

        # 时间值输入框（使用Spinbox）
        self.time_value_spinbox = ttk.Spinbox(
            time_frame,
            from_=1,
            to=3650,
            textvariable=self.time_value,
            width=10
        )
        self.time_value_spinbox.pack(side=tk.LEFT, padx=(0, 5))

        # 时间单位选择
        self.time_unit_combo = ttk.Combobox(
            time_frame,
            textvariable=self.time_unit,
            values=['天', '小时', '分钟', '月', '年'],
            width=8,
            state='readonly'
        )
        self.time_unit_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.time_unit_combo.bind('<<ComboboxSelected>>', self.on_time_unit_change)

        ttk.Label(time_frame, text="前修改过的文件", font=('Arial', 10)).pack(side=tk.LEFT)
        current_row += 1

        # 时间模式选择
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=current_row, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(mode_frame, text="时间模式:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.time_mode = tk.StringVar(value="relative")  # relative 或 custom
        
        # 相对时间模式
        self.relative_radio = ttk.Radiobutton(
            mode_frame,
            text="相对时间",
            variable=self.time_mode,
            value="relative",
            command=self.on_time_mode_change
        )
        self.relative_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        # 自定义时间节点模式
        self.custom_radio = ttk.Radiobutton(
            mode_frame,
            text="自定义时间节点",
            variable=self.time_mode,
            value="custom",
            command=self.on_time_mode_change
        )
        self.custom_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        current_row += 1

        # 自定义时间节点输入区域
        custom_time_frame = ttk.Frame(main_frame)
        custom_time_frame.grid(row=current_row, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Label(custom_time_frame, text="时间节点:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.custom_time_entry = ttk.Entry(custom_time_frame, textvariable=self.custom_timestamp, width=25)
        self.custom_time_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            custom_time_frame,
            text="当前时间",
            command=self.set_current_time,
            width=10
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(custom_time_frame, text="(格式: YYYY-MM-DD HH:MM:SS)").pack(side=tk.LEFT)
        current_row += 1

        # ========== 配置选项区域 ==========
        options_frame = ttk.LabelFrame(main_frame, text="配置选项", padding="10")
        options_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        current_row += 1

        # 包含子文件夹选项
        ttk.Checkbutton(
            options_frame,
            text="包含子文件夹",
            variable=self.include_subfolders
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

        # 移动到回收站选项
        self.recycle_checkbox = ttk.Checkbutton(
            options_frame,
            text="移动到回收站（取消选中将永久删除）",
            variable=self.use_recycle_bin,
            command=self.toggle_recycle_bin
        )
        self.recycle_checkbox.grid(row=1, column=0, sticky=tk.W, pady=2)

        if not SEND2TRASH_AVAILABLE:
            self.recycle_checkbox.config(state='disabled')

        # 文件类型过滤
        filter_frame = ttk.Frame(options_frame)
        filter_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(filter_frame, text="文件类型过滤:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(filter_frame, textvariable=self.file_filter, width=20).pack(side=tk.LEFT)
        ttk.Label(filter_frame, text="(例如: *.log, *.tmp, 留空表示 *.*)").pack(side=tk.LEFT, padx=(5, 0))

        # ========== 操作按钮区域 ==========
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=0, columnspan=3, pady=10)
        current_row += 1

        self.preview_button = ttk.Button(
            button_frame,
            text="预览",
            command=self.preview_files,
            width=15
        )
        self.preview_button.pack(side=tk.LEFT, padx=5)

        self.execute_button = ttk.Button(
            button_frame,
            text="执行清理",
            command=self.execute_cleanup,
            width=15
        )
        self.execute_button.pack(side=tk.LEFT, padx=5)

        # ========== 日志区域 ==========
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="5")
        log_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(current_row, weight=1)
        current_row += 1

        # 使用ScrolledText控件显示日志
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=80,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 清空日志按钮
        ttk.Button(log_frame, text="清空日志", command=self.clear_log).grid(
            row=1, column=0, sticky=tk.E, pady=(5, 0)
        )

        # ========== 状态栏 ==========
        self.status_label = ttk.Label(
            main_frame,
            text="准备就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

    def on_time_unit_change(self, event=None):
        """时间单位改变时的处理"""
        unit = self.time_unit.get()
        # 根据单位调整输入范围
        if unit == '分钟':
            self.time_value_spinbox.config(from_=1, to=525600)  # 最多1年分钟数
        elif unit == '小时':
            self.time_value_spinbox.config(from_=1, to=8760)   # 最多1年小时数
        elif unit == '天':
            self.time_value_spinbox.config(from_=1, to=3650)   # 最多10年天数
        elif unit == '月':
            self.time_value_spinbox.config(from_=1, to=120)    # 最多10年月数
        elif unit == '年':
            self.time_value_spinbox.config(from_=1, to=10)     # 最多10年

    def on_time_mode_change(self):
        """时间模式改变时的处理"""
        if self.time_mode.get() == "custom":
            # 自定义时间节点模式
            self.time_value_spinbox.config(state='disabled')
            self.time_unit_combo.config(state='disabled')
            self.custom_time_entry.config(state='normal')
            if not self.custom_timestamp.get():
                self.custom_timestamp.set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            # 相对时间模式
            self.time_value_spinbox.config(state='normal')
            self.time_unit_combo.config(state='readonly')
            self.custom_time_entry.config(state='disabled')

    def set_current_time(self):
        """设置当前时间为自定义时间节点"""
        self.custom_timestamp.set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def browse_folder(self):
        """浏览并选择文件夹"""
        folder = filedialog.askdirectory(title="选择要清理的文件夹")
        if folder:
            self.folder_path.set(folder)
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 已选择文件夹: {folder}")

    def toggle_recycle_bin(self):
        """切换回收站选项时的处理"""
        if not self.use_recycle_bin.get():
            # 警告用户永久删除的风险
            response = messagebox.askokcancel(
                "警告",
                "取消选中此选项将执行永久删除，无法恢复！\n\n确定要继续吗？",
                icon='warning'
            )
            if not response:
                self.use_recycle_bin.set(True)

    def get_files_to_delete(self):
        """
        获取符合条件的文件列表
        返回: 文件路径列表
        """
        start_time = time.time()
        folder = self.folder_path.get()

        # 验证文件夹路径
        if not folder:
            messagebox.showerror("错误", "请先选择一个文件夹！")
            return None

        if not os.path.exists(folder):
            messagebox.showerror("错误", f"文件夹不存在: {folder}")
            return None

        if not os.path.isdir(folder):
            messagebox.showerror("错误", f"选择的路径不是文件夹: {folder}")
            return None

        # 计算时间阈值
        try:
            if self.time_mode.get() == "custom":
                # 自定义时间节点模式 - 删除该时间节点之前的文件
                custom_time_str = self.custom_timestamp.get().strip()
                if not custom_time_str:
                    messagebox.showerror("错误", "请输入自定义时间节点！")
                    return None
                try:
                    custom_dt = datetime.strptime(custom_time_str, '%Y-%m-%d %H:%M:%S')
                    cutoff_time = custom_dt.timestamp()
                    cutoff_date = custom_dt
                except ValueError:
                    messagebox.showerror("错误", "自定义时间节点格式错误！\n正确格式: YYYY-MM-DD HH:MM:SS")
                    return None
            else:
                # 相对时间模式 - 删除N个时间单位前的文件
                time_value = self.time_value.get()
                if time_value < 1:
                    messagebox.showerror("错误", "时间值必须大于0！")
                    return None
                
                unit = self.time_unit.get()
                seconds_per_unit = {
                    '分钟': 60,
                    '小时': 60 * 60,
                    '天': 24 * 60 * 60,
                    '月': 30 * 24 * 60 * 60,  # 近似值
                    '年': 365 * 24 * 60 * 60  # 近似值
                }
                
                cutoff_time = time.time() - (time_value * seconds_per_unit[unit])
                cutoff_date = datetime.fromtimestamp(cutoff_time)
                
        except tk.TclError:
            messagebox.showerror("错误", "请输入有效的时间值！")
            return None

        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始扫描文件夹: {folder}")
        if self.time_mode.get() == "custom":
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 使用自定义时间节点: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 将删除该时间节点之前修改的文件")
        else:
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 时间阈值: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} ({time_value}{unit}前)")
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 将删除{time_value}{unit}前修改的文件")
        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 包含子文件夹: {'是' if self.include_subfolders.get() else '否'}")

        # 获取文件过滤模式
        filter_patterns = self.file_filter.get().strip()
        if not filter_patterns or filter_patterns == "":
            filter_patterns = "*.*"

        patterns = [p.strip() for p in filter_patterns.split(',')]
        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 文件过滤: {', '.join(patterns)}")

        files_to_delete = []

        try:
            # 遍历文件夹
            if self.include_subfolders.get():
                # 递归遍历所有子文件夹
                scan_start = time.time()
                for root, dirs, files in os.walk(folder):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        if self._should_delete_file(file_path, cutoff_time, patterns):
                            files_to_delete.append(file_path)
                scan_end = time.time()
                self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 扫描完成，耗时: {scan_end - scan_start:.2f}秒")
            else:
                # 只遍历当前文件夹
                scan_start = time.time()
                try:
                    for item in os.listdir(folder):
                        file_path = os.path.join(folder, item)
                        if os.path.isfile(file_path):
                            if self._should_delete_file(file_path, cutoff_time, patterns):
                                files_to_delete.append(file_path)
                    scan_end = time.time()
                    self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 扫描完成，耗时: {scan_end - scan_start:.2f}秒")
                except PermissionError as e:
                    self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 错误：无权限访问文件夹 {folder}: {e}")
                    messagebox.showerror("权限错误", f"无法访问文件夹: {e}")
                    return None

        except Exception as e:
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 扫描文件时发生错误: {e}")
            messagebox.showerror("错误", f"扫描文件时发生错误: {e}")
            return None

        total_time = time.time() - start_time
        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 文件扫描总耗时: {total_time:.2f}秒，找到 {len(files_to_delete)} 个文件")
        return files_to_delete

    def _should_delete_file(self, file_path, cutoff_time, patterns):
        """
        判断文件是否应该被删除
        参数:
            file_path: 文件路径
            cutoff_time: 时间阈值（时间戳）
            patterns: 文件名匹配模式列表
        返回: True/False
        """
        try:
            # 检查文件修改时间
            mtime = os.path.getmtime(file_path)
            if mtime >= cutoff_time:
                return False

            # 检查文件名是否匹配过滤模式
            filename = os.path.basename(file_path)
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern):
                    return True

            return False

        except PermissionError:
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 警告：无权限访问文件 {file_path}")
            return False
        except Exception as e:
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 警告：检查文件时出错 {file_path}: {e}")
            return False

    def preview_files(self):
        """预览将要删除的文件（不执行删除）"""
        preview_start = time.time()
        self.clear_log()
        self.update_status("预览中...")
        self.log_message("=" * 80)
        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始预览...")
        self.log_message("=" * 80)

        # 暂时禁用按钮
        self.preview_button.config(state='disabled')
        self.execute_button.config(state='disabled')
        self.root.update()

        try:
            files_to_delete = self.get_files_to_delete()

            if files_to_delete is None:
                return

            if len(files_to_delete) == 0:
                self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] \n没有找到符合条件的文件。")
                self.update_status("预览完成 - 无文件")
            else:
                self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] \n找到 {len(files_to_delete)} 个符合条件的文件:\n")

                # 计算总大小
                total_size = 0
                for i, file_path in enumerate(files_to_delete, 1):
                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        mtime = os.path.getmtime(file_path)
                        mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                        size_str = self._format_size(file_size)

                        self.log_message(f"{i}. [{mtime_str}] [{size_str}] {file_path}")
                    except Exception as e:
                        self.log_message(f"{i}. [错误] {file_path} - {e}")

                preview_end = time.time()
                self.log_message(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 总计: {len(files_to_delete)} 个文件, 总大小: {self._format_size(total_size)}")
                self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 预览完成，耗时: {preview_end - preview_start:.2f}秒")
                self.update_status(f"预览完成 - 找到 {len(files_to_delete)} 个文件")

        finally:
            # 重新启用按钮
            self.preview_button.config(state='normal')
            self.execute_button.config(state='normal')

    def execute_cleanup(self):
        """执行文件清理操作"""
        cleanup_start = time.time()
        self.clear_log()
        self.update_status("准备执行清理...")
        self.log_message("=" * 80)
        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行清理...")
        self.log_message("=" * 80)

        # 获取要删除的文件列表
        files_to_delete = self.get_files_to_delete()

        if files_to_delete is None:
            return

        if len(files_to_delete) == 0:
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] \n没有找到符合条件的文件。")
            messagebox.showinfo("提示", "没有找到符合条件的文件。")
            self.update_status("就绪")
            return

        # 确认对话框
        use_recycle = self.use_recycle_bin.get() and SEND2TRASH_AVAILABLE
        deletion_type = "移动到回收站" if use_recycle else "永久删除"

        confirm_message = (
            f"您确定要{deletion_type} {len(files_to_delete)} 个文件吗？\n\n"
            f"{'文件将被移动到回收站，可以恢复。' if use_recycle else '警告：此操作将永久删除文件，无法恢复！'}"
        )

        response = messagebox.askyesno(
            "确认删除",
            confirm_message,
            icon='warning' if not use_recycle else 'question'
        )

        if not response:
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] \n用户取消了操作。")
            self.update_status("操作已取消")
            return

        # 执行删除
        self.log_message(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始{deletion_type}...\n")

        # 禁用按钮
        self.preview_button.config(state='disabled')
        self.execute_button.config(state='disabled')

        success_count = 0
        error_count = 0
        delete_start = time.time()

        try:
            for i, file_path in enumerate(files_to_delete, 1):
                try:
                    if use_recycle:
                        # 移动到回收站
                        send2trash(file_path)
                        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [✓] 已移动到回收站: {file_path}")
                    else:
                        # 永久删除
                        os.remove(file_path)
                        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [✓] 已永久删除: {file_path}")

                    success_count += 1

                except PermissionError:
                    self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [✗] 权限不足，无法删除: {file_path}")
                    error_count += 1

                except Exception as e:
                    self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [✗] 删除失败: {file_path} - {e}")
                    error_count += 1

                # 更新状态
                self.update_status(f"正在处理... ({i}/{len(files_to_delete)})")
                self.root.update()

        finally:
            # 重新启用按钮
            self.preview_button.config(state='normal')
            self.execute_button.config(state='normal')

        delete_end = time.time()
        # 显示结果
        self.log_message("\n" + "=" * 80)
        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 清理完成！")
        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 成功: {success_count} 个文件")
        if error_count > 0:
            self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 失败: {error_count} 个文件")
        self.log_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 删除操作耗时: {delete_end - delete_start:.2f}秒")
        self.log_message("=" * 80)

        total_time = time.time() - cleanup_start
        self.update_status(f"清理完成 - 成功: {success_count}, 失败: {error_count}, 总耗时: {total_time:.2f}秒")

        # 显示完成消息
        messagebox.showinfo(
            "完成",
            f"清理完成！\n\n成功: {success_count} 个文件\n失败: {error_count} 个文件\n总耗时: {total_time:.2f}秒"
        )

    def _format_size(self, size_bytes):
        """格式化文件大小显示"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def log_message(self, message):
        """在日志区域添加消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 自动滚动到底部
        self.root.update()

    def clear_log(self):
        """清空日志区域"""
        self.log_text.delete(1.0, tk.END)

    def update_status(self, status):
        """更新状态栏"""
        self.status_label.config(text=status)
        self.root.update()

    def get_processing_summary(self):
        """获取处理时间汇总信息"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{current_time}] 处理时间戳已记录"


def main():
    """主函数"""
    root = tk.Tk()
    app = FileCleanerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
