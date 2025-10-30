#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TXT转JSON格式化工具 - 高对比度优化版本
解决显示问题，确保所有元素清晰可见
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from pathlib import Path
import threading
import time
import math
from typing import Dict, List, Tuple, Optional


class HighContrastTheme:
    """高对比度主题系统"""

    # 高对比度色彩方案
    COLORS = {
        # 背景色 - 确保清晰对比
        'background': '#FFFFFF',      # 纯白背景
        'surface': '#F8F9FA',         # 浅灰表面
        'surface_variant': '#E9ECEF', # 更深的表面变体

        # 主色调 - 高饱和度确保可见性
        'primary': '#0066CC',         # 鲜艳蓝色
        'primary_container': '#E6F0FF', # 浅蓝容器
        'on_primary': '#FFFFFF',      # 蓝色上的白色文字

        # 次要色调
        'secondary': '#6C757D',       # 灰色
        'secondary_container': '#F1F3F4', # 浅灰容器
        'on_secondary': '#000000',    # 深色文字

        # 状态色 - 高对比度
        'success': '#28A745',         # 绿色
        'error': '#DC3545',           # 红色
        'warning': '#FFC107',         # 黄色（深色文字）
        'info': '#17A2B8',            # 青色

        # 文字颜色 - 确保可读性
        'on_background': '#212529',   # 深灰文字
        'on_surface': '#212529',      # 深灰文字
        'on_surface_variant': '#495057', # 中等灰文字
        'text_secondary': '#6C757D',  # 次要文字

        # 边框和分隔线
        'outline': '#DEE2E6',         # 浅灰边框
        'outline_variant': '#CED4DA', # 中等灰边框

        # 卡片阴影
        'card_shadow': '#E9ECEF',     # 浅灰阴影
        'card_shadow_dark': '#ADB5BD', # 中等灰阴影

        # 进度条
        'progress_track': '#E9ECEF',   # 进度轨道
        'progress_fill': '#0066CC',   # 进度填充

        # 按钮状态
        'button_hover': '#0056B3',    # 悬停状态
        'button_pressed': '#004494',  # 按下状态
    }

    def get_colors(self) -> Dict[str, str]:
        """获取颜色配置"""
        return self.COLORS.copy()


class HighContrastButton(tk.Button):
    """高对比度按钮"""

    def __init__(self, parent, theme: HighContrastTheme, **kwargs):
        self.theme = theme
        self.colors = theme.get_colors()

        # 默认样式
        default_style = {
            'bg': self.colors['primary'],
            'fg': self.colors['on_primary'],
            'activebackground': self.colors['button_hover'],
            'activeforeground': self.colors['on_primary'],
            'bd': 0,
            'relief': 'flat',
            'padx': 15,
            'pady': 8,
            'font': ('Segoe UI', 10, 'bold')
        }

        super().__init__(parent, **default_style, **kwargs)

        # 绑定事件
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, event):
        """悬停效果"""
        self.config(bg=self.colors['button_hover'])

    def on_leave(self, event):
        """离开效果"""
        self.config(bg=self.colors['primary'])


class HighContrastCard(tk.Frame):
    """高对比度卡片"""

    def __init__(self, parent, theme: HighContrastTheme, padding: int = 20, **kwargs):
        self.theme = theme
        self.colors = theme.get_colors()

        # 卡片样式
        super().__init__(
            parent,
            bg=self.colors['surface'],
            highlightbackground=self.colors['outline'],
            highlightthickness=1,
            **kwargs
        )

        self.grid_propagate(False)
        self.config(padx=padding, pady=padding)


class HighContrastProgressBar(tk.Canvas):
    """高对比度进度条"""

    def __init__(self, parent, theme: HighContrastTheme, height: int = 10, **kwargs):
        self.theme = theme
        self.colors = theme.get_colors()
        self.progress = 0

        super().__init__(
            parent,
            height=height,
            bg=self.colors['progress_track'],
            highlightthickness=0,
            **kwargs
        )

        self.draw_progress()

    def draw_progress(self):
        """绘制进度"""
        self.delete('all')
        width = self.winfo_width()
        height = self.winfo_height()

        if width < 10:  # 最小宽度
            width = 200

        # 绘制轨道
        self.create_rectangle(
            0, 0, width, height,
            fill=self.colors['progress_track'],
            outline=''
        )

        # 绘制进度
        progress_width = width * self.progress
        self.create_rectangle(
            0, 0, progress_width, height,
            fill=self.colors['progress_fill'],
            outline=''
        )

    def set_progress(self, value: float):
        """设置进度"""
        self.progress = max(0, min(1, value))
        self.draw_progress()


class HighContrastConverter:
    """高对比度转换器"""

    def __init__(self, root):
        self.root = root
        self.root.title("TXT转JSON格式化工具")
        self.root.geometry("850x650")
        self.root.minsize(750, 550)

        # 初始化主题
        self.theme = HighContrastTheme()
        self.colors = self.theme.get_colors()

        # 应用主题
        self.root.configure(bg=self.colors['background'])

        # 变量
        self.output_path_var = tk.StringVar()
        self.use_custom_output = tk.BooleanVar(value=False)
        self.check_folder_path_var = tk.StringVar()

        # 存储上一次的输出目录
        self.last_output_path = None

        # 设置界面
        self.setup_layout()
        self.setup_ui()

    def setup_layout(self):
        """设置布局"""
        # 主框架
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # 网格配置
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

    def setup_ui(self):
        """设置用户界面"""
        # 标题区域
        self.create_header()

        # 输出设置
        self.create_output_settings()

        # 功能区域
        self.create_function_area()

        # 进度和结果
        self.create_progress_area()

    def create_header(self):
        """创建标题"""
        header_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        header_frame.pack(fill='x', pady=(0, 20))

        # 主标题
        title = tk.Label(
            header_frame,
            text="TXT转JSON格式化工具",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['background'],
            fg=self.colors['on_background']
        )
        title.pack(side='left')

        # 副标题
        subtitle = tk.Label(
            header_frame,
            text="将TXT文件中的JSON字符串转换为格式化JSON文件",
            font=('Segoe UI', 11),
            bg=self.colors['background'],
            fg=self.colors['text_secondary']
        )
        subtitle.pack(side='left', padx=(10, 0))

        # 版本标签
        version = tk.Label(
            header_frame,
            text="",
            font=('Segoe UI', 9, 'bold'),
            bg=self.colors['background'],
            fg=self.colors['primary']
        )
        version.pack(side='right')

        # 水印
        watermark = tk.Label(
            header_frame,
            text="智能制造推进部|2025",
            font=('Segoe UI', 8, 'italic'),
            bg=self.colors['background'],
            fg=self.colors['text_secondary'],
            padx=10,
            pady=5
        )
        watermark.pack(side='left', padx=(10, 0), pady=(10, 0))

    def create_output_settings(self):
        """创建输出设置区域"""
        card = HighContrastCard(self.main_frame, self.theme, padding=25)
        card.pack(fill='x', pady=(0, 20))

        # 标题
        title = tk.Label(
            card,
            text="📁 输出路径设置",
            font=('Segoe UI', 16, 'bold'),
            bg=card.colors['surface'],
            fg=card.colors['on_surface']
        )
        title.pack(anchor='w', pady=(0, 10))

        # 说明
        desc = tk.Label(
            card,
            text="选择输出文件的保存位置",
            font=('Segoe UI', 10),
            bg=card.colors['surface'],
            fg=card.colors['text_secondary']
        )
        desc.pack(anchor='w', pady=(0, 15))

        # 选项框架
        options_frame = tk.Frame(card, bg=card.colors['surface'])
        options_frame.pack(fill='x', pady=(0, 15))

        # 默认路径选项
        default_radio = tk.Radiobutton(
            options_frame,
            text="默认路径（在源文件夹父目录创建副本）",
            variable=self.use_custom_output,
            value=False,
            bg=card.colors['surface'],
            fg=card.colors['on_surface'],
            font=('Segoe UI', 10),
            command=self.toggle_output_widgets
        )
        default_radio.grid(row=0, column=0, sticky='w')

        # 自定义路径选项
        custom_radio = tk.Radiobutton(
            options_frame,
            text="自定义路径",
            variable=self.use_custom_output,
            value=True,
            bg=card.colors['surface'],
            fg=card.colors['on_surface'],
            font=('Segoe UI', 10),
            command=self.toggle_output_widgets
        )
        custom_radio.grid(row=1, column=0, sticky='w', pady=(5, 0))

        # 自定义路径输入区
        self.custom_frame = tk.Frame(card, bg=card.colors['surface'])
        self.custom_frame.pack(fill='x', pady=(10, 0))
        self.custom_frame.columnconfigure(0, weight=1)

        self.custom_entry = tk.Entry(
            self.custom_frame,
            textvariable=self.output_path_var,
            state='disabled',
            font=('Segoe UI', 10),
            bg=card.colors['surface_variant'],
            fg=card.colors['on_surface'],
            relief='flat',
            highlightbackground=card.colors['outline'],
            highlightthickness=1
        )
        self.custom_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        self.browse_btn = HighContrastButton(
            self.custom_frame,
            self.theme,
            text="📁 选择文件夹",
            command=self.select_output_folder,
            width=15
        )
        self.browse_btn.grid(row=0, column=1)

        # 初始化状态
        self.toggle_output_widgets()

    def create_function_area(self):
        """创建功能区域"""
        # 功能卡片容器
        func_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        func_frame.pack(fill='x', pady=(0, 15))
        func_frame.columnconfigure(0, weight=1)
        func_frame.columnconfigure(1, weight=1)
        func_frame.columnconfigure(2, weight=1)

        # 单个文件处理
        self.create_single_file_card(func_frame)

        # 批量处理
        self.create_batch_card(func_frame)

        # 格式核查
        self.create_check_card(func_frame)

    def create_single_file_card(self, parent):
        """创建单个文件卡片"""
        card = HighContrastCard(parent, self.theme, padding=20)
        card.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

        title = tk.Label(
            card,
            text="📄 单个文件处理",
            font=('Segoe UI', 14, 'bold'),
            bg=card.colors['surface'],
            fg=card.colors['on_surface']
        )
        title.pack(anchor='w', pady=(0, 10))

        desc = tk.Label(
            card,
            text="选择单个TXT文件进行转换",
            font=('Segoe UI', 9),
            bg=card.colors['surface'],
            fg=card.colors['text_secondary']
        )
        desc.pack(anchor='w', pady=(0, 15))

        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(
            card,
            textvariable=self.file_path_var,
            state='readonly',
            font=('Segoe UI', 9),
            bg=card.colors['surface_variant'],
            fg=card.colors['on_surface'],
            relief='flat',
            highlightbackground=card.colors['outline'],
            highlightthickness=1
        )
        file_entry.pack(fill='x', pady=(0, 15))

        btn_frame = tk.Frame(card, bg=card.colors['surface'])
        btn_frame.pack(fill='x')

        select_btn = HighContrastButton(
            btn_frame,
            self.theme,
            text="📁 选择文件",
            command=self.select_single_file,
            width=12
        )
        select_btn.pack(side='left', padx=(0, 5))

        convert_btn = HighContrastButton(
            btn_frame,
            self.theme,
            text="⚡ 转换",
            command=self.convert_single_file,
            width=12
        )
        convert_btn.pack(side='right')

    def create_batch_card(self, parent):
        """创建批量处理卡片"""
        card = HighContrastCard(parent, self.theme, padding=20)
        card.grid(row=0, column=1, sticky='nsew', padx=(5, 10))

        title = tk.Label(
            card,
            text="📦 批量文件夹处理",
            font=('Segoe UI', 14, 'bold'),
            bg=card.colors['surface'],
            fg=card.colors['on_surface']
        )
        title.pack(anchor='w', pady=(0, 10))

        desc = tk.Label(
            card,
            text="选择包含TXT文件的文件夹进行批量处理",
            font=('Segoe UI', 9),
            bg=card.colors['surface'],
            fg=card.colors['text_secondary']
        )
        desc.pack(anchor='w', pady=(0, 15))

        self.folder_path_var = tk.StringVar()
        folder_entry = tk.Entry(
            card,
            textvariable=self.folder_path_var,
            state='readonly',
            font=('Segoe UI', 9),
            bg=card.colors['surface_variant'],
            fg=card.colors['on_surface'],
            relief='flat',
            highlightbackground=card.colors['outline'],
            highlightthickness=1
        )
        folder_entry.pack(fill='x', pady=(0, 15))

        btn_frame = tk.Frame(card, bg=card.colors['surface'])
        btn_frame.pack(fill='x')

        select_btn = HighContrastButton(
            btn_frame,
            self.theme,
            text="📁 选择文件夹",
            command=self.select_folder,
            width=12
        )
        select_btn.pack(side='left', padx=(0, 5))

        convert_btn = HighContrastButton(
            btn_frame,
            self.theme,
            text="⚡ 批量转换",
            command=self.convert_folder_files,
            width=12
        )
        convert_btn.pack(side='right')

    def create_check_card(self, parent):
        """创建格式核查卡片"""
        card = HighContrastCard(parent, self.theme, padding=20)
        card.grid(row=0, column=2, sticky='nsew', padx=(5, 0))

        title = tk.Label(
            card,
            text="🔍 格式核查",
            font=('Segoe UI', 14, 'bold'),
            bg=card.colors['surface'],
            fg=card.colors['on_surface']
        )
        title.pack(anchor='w', pady=(0, 10))

        desc = tk.Label(
            card,
            text="检查JSON文件的格式是否正确",
            font=('Segoe UI', 9),
            bg=card.colors['surface'],
            fg=card.colors['text_secondary']
        )
        desc.pack(anchor='w', pady=(0, 15))

        self.check_path_var = tk.StringVar()
        check_entry = tk.Entry(
            card,
            textvariable=self.check_path_var,
            state='readonly',
            font=('Segoe UI', 9),
            bg=card.colors['surface_variant'],
            fg=card.colors['on_surface'],
            relief='flat',
            highlightbackground=card.colors['outline'],
            highlightthickness=1
        )
        check_entry.pack(fill='x', pady=(0, 15))

        btn_frame = tk.Frame(card, bg=card.colors['surface'])
        btn_frame.pack(fill='x')

        select_btn = HighContrastButton(
            btn_frame,
            self.theme,
            text="📁 选择文件夹",
            command=self.select_check_folder,
            width=12
        )
        select_btn.pack(side='left', padx=(0, 5))

        check_btn = HighContrastButton(
            btn_frame,
            self.theme,
            text="🔍 开始核查",
            command=self.check_json_format,
            width=12
        )
        check_btn.pack(side='right')

    def create_progress_area(self):
        """创建进度区域"""
        # 进度卡片
        progress_card = HighContrastCard(self.main_frame, self.theme, padding=20)
        progress_card.pack(fill='x', pady=(0, 15))

        title = tk.Label(
            progress_card,
            text="📊 处理进度",
            font=('Segoe UI', 14, 'bold'),
            bg=progress_card.colors['surface'],
            fg=progress_card.colors['on_surface']
        )
        title.pack(anchor='w', pady=(0, 10))

        # 进度条
        self.progress_bar = HighContrastProgressBar(progress_card, self.theme)
        self.progress_bar.pack(fill='x', pady=(0, 10))

        # 状态显示
        self.status_var = tk.StringVar()
        self.status_var.set("等待选择文件或文件夹...")
        status_label = tk.Label(
            progress_card,
            textvariable=self.status_var,
            font=('Segoe UI', 11),
            bg=progress_card.colors['surface'],
            fg=progress_card.colors['info']
        )
        status_label.pack(anchor='w', pady=(0, 5))

        # 结果区域
        result_card = HighContrastCard(self.main_frame, self.theme, padding=20)
        result_card.pack(fill='both', expand=True)

        result_title = tk.Label(
            result_card,
            text="📋 处理结果",
            font=('Segoe UI', 14, 'bold'),
            bg=result_card.colors['surface'],
            fg=result_card.colors['on_surface']
        )
        result_title.pack(anchor='w', pady=(0, 10))

        # 结果文本框
        self.result_text = tk.Text(
            result_card,
            height=6,
            font=('Consolas', 10),
            bg=result_card.colors['surface_variant'],
            fg=result_card.colors['on_surface'],
            relief='flat',
            highlightbackground=result_card.colors['outline'],
            highlightthickness=1,
            state='disabled',
            wrap='word'
        )
        self.result_text.pack(fill='both', pady=(0, 10), expand=True)

        # 滚动条
        scrollbar = ttk.Scrollbar(result_card, orient='vertical', command=self.result_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.result_text.configure(yscrollcommand=scrollbar.set)

        # 清空按钮
        clear_btn = HighContrastButton(
            result_card,
            self.theme,
            text="🗑️ 清空结果",
            command=self.clear_results,
            width=15
        )
        clear_btn.pack(anchor='e', pady=(5, 0))

    # 事件处理方法
    def toggle_output_widgets(self):
        """切换输出控件状态"""
        if self.use_custom_output.get():
            self.custom_entry.config(state='normal')
            self.browse_btn.config(state='normal')
        else:
            self.custom_entry.config(state='disabled')
            self.browse_btn.config(state='disabled')

    def select_output_folder(self):
        """选择输出文件夹"""
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.output_path_var.set(folder_path)

    def select_single_file(self):
        """选择单个文件"""
        file_path = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("TXT文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.status_var.set(f"已选择文件: {os.path.basename(file_path)}")
            self.update_results(f"📁 已选择文件: {file_path}")

    def select_folder(self):
        """选择文件夹"""
        folder_path = filedialog.askdirectory(title="选择文件夹")
        if folder_path:
            self.folder_path_var.set(folder_path)
            txt_files = list(Path(folder_path).glob("*.txt"))
            file_count = len(txt_files)
            self.status_var.set(f"已选择文件夹: {os.path.basename(folder_path)} (包含{file_count}个TXT文件)")
            self.update_results(f"📁 已选择文件夹: {folder_path}\n包含{file_count}个TXT文件")

    def select_check_folder(self):
        """选择核查文件夹"""
        # 默认使用上一次的输出目录
        initial_dir = self.last_output_path or ""

        folder_path = filedialog.askdirectory(
            title="选择JSON文件夹进行格式核查",
            initialdir=initial_dir if initial_dir and os.path.exists(initial_dir) else None
        )
        if folder_path:
            self.check_path_var.set(folder_path)
            json_files = list(Path(folder_path).glob("*.json"))
            file_count = len(json_files)
            self.update_results(f"已选择JSON文件夹: {folder_path}\n包含{file_count}个JSON文件")

    def get_output_path(self, input_path):
        """获取输出路径"""
        if self.use_custom_output.get():
            custom_path = self.output_path_var.get()
            if custom_path:
                return Path(custom_path)
            else:
                return self._get_default_output_path(input_path)
        else:
            return self._get_default_output_path(input_path)

    def _get_default_output_path(self, input_path):
        """获取默认输出路径"""
        input_path = Path(input_path)
        if input_path.is_file():
            parent_dir = input_path.parent
            output_folder = parent_dir / f"{parent_dir.name}_JSON"
        else:
            parent_dir = input_path.parent
            output_folder = parent_dir / f"{input_path.name}_JSON"

        output_folder.mkdir(exist_ok=True)
        return output_folder

    def parse_json_from_text(self, text_content):
        """解析JSON"""
        try:
            return json.loads(text_content)
        except json.JSONDecodeError:
            cleaned_text = text_content.strip()
            if not cleaned_text:
                raise ValueError("文本内容为空")

            if cleaned_text.startswith('\ufeff'):
                cleaned_text = cleaned_text[1:]

            if (cleaned_text.startswith('"') and cleaned_text.endswith('"') and
                cleaned_text.count('"') == 2):
                cleaned_text = cleaned_text[1:-1]

            cleaned_text = cleaned_text.replace('\\n', '\n').replace('\\t', '\t')

            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON解析失败: {e}")

    def format_and_save_json(self, input_path, output_path):
        """格式化并保存JSON"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()

            parsed_data = self.parse_json_from_text(content)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2, separators=(',', ': '))

            return True, "成功"
        except Exception as e:
            return False, str(e)

    def update_status(self, message, progress=None):
        """更新状态"""
        self.status_var.set(message)
        if progress is not None:
            self.progress_bar.set_progress(progress)
        self.root.update_idletasks()

    def update_results(self, message):
        """更新结果"""
        self.result_text.config(state='normal')
        current_time = time.strftime("%H:%M:%S", time.localtime())
        formatted_message = f"[{current_time}] {message}\n"
        self.result_text.insert('end', formatted_message)
        self.result_text.see('end')
        self.result_text.config(state='disabled')

    def clear_results(self):
        """清空结果"""
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, 'end')
        self.result_text.config(state='disabled')
        self.progress_bar.set_progress(0)
        self.status_var.set("等待选择文件或文件夹...")

    def convert_single_file(self):
        """转换单个文件"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择一个TXT文件")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在")
            return

        if not file_path.lower().endswith('.txt'):
            messagebox.showwarning("警告", "请选择TXT文件")
            return

        output_folder = self.get_output_path(file_path)
        output_path = output_folder / Path(file_path).with_suffix('.json').name

        if output_path.exists():
            if not messagebox.askyesno("确认", f"文件 {output_path.name} 已存在，是否覆盖？"):
                return

        # 更新上一次的输出目录
        self.last_output_path = str(output_folder)

        self.update_status("正在处理单个文件...", 0)
        self.root.update_idletasks()

        try:
            success, message = self.format_and_save_json(file_path, str(output_path))
            if success:
                output_info = str(output_path) if self.use_custom_output.get() else f"{output_folder.name}/{output_path.name}"
                self.update_status("单个文件处理完成！", 100)
                self.update_results(f"✓ 成功转换: {os.path.basename(file_path)} -> {output_info}")
                messagebox.showinfo("成功", f"文件转换成功！\n输出路径: {output_path}")
            else:
                self.update_status(f"处理失败: {message}", 0)
                self.update_results(f"✗ 转换失败 {os.path.basename(file_path)}: {message}")
                messagebox.showerror("错误", f"转换失败: {message}")
        except Exception as e:
            self.update_status(f"处理异常: {str(e)}", 0)
            self.update_results(f"✗ 处理异常 {os.path.basename(file_path)}: {str(e)}")
            messagebox.showerror("错误", f"处理异常: {str(e)}")

    def convert_folder_files(self):
        """批量转换"""
        folder_path = self.folder_path_var.get()
        if not folder_path:
            messagebox.showwarning("警告", "请先选择一个文件夹")
            return

        if not os.path.exists(folder_path):
            messagebox.showerror("错误", "文件夹不存在")
            return

        txt_files = list(Path(folder_path).glob("*.txt"))
        if not txt_files:
            messagebox.showwarning("警告", "文件夹中没有找到TXT文件")
            return

        output_folder = self.get_output_path(folder_path)
        output_location = str(output_folder) if self.use_custom_output.get() else f"{output_folder.name}文件夹"

        if not messagebox.askyesno("确认", f"将处理 {len(txt_files)} 个TXT文件，输出到 {output_location}，是否继续？"):
            return

        # 更新上一次的输出目录
        self.last_output_path = str(output_folder)

        self.update_status("开始批量处理...", 0)
        self.root.update_idletasks()

        def process_files():
            success_count = 0
            fail_count = 0
            total_files = len(txt_files)

            for i, txt_file in enumerate(txt_files):
                try:
                    output_path = output_folder / txt_file.with_suffix('.json').name
                    success, message = self.format_and_save_json(str(txt_file), str(output_path))

                    if success:
                        success_count += 1
                        self.update_results(f"✓ {txt_file.name} -> {output_path.name}")
                    else:
                        fail_count += 1
                        self.update_results(f"✗ {txt_file.name}: {message}")

                    progress = ((i + 1) / total_files) * 100
                    self.update_status(f"处理进度: {i + 1}/{total_files}", progress)

                except Exception as e:
                    fail_count += 1
                    self.update_results(f"✗ {txt_file.name}: 处理异常 - {str(e)}")

            output_location = str(output_folder) if self.use_custom_output.get() else f"{output_folder.name}文件夹"
            final_message = f"批量处理完成！成功: {success_count}, 失败: {fail_count}\n输出位置: {output_location}"
            self.update_status(final_message, 100)
            self.update_results(final_message)
            messagebox.showinfo("完成", final_message)

        processing_thread = threading.Thread(target=process_files, daemon=True)
        processing_thread.start()

    def check_json_format(self):
        """格式核查"""
        folder_path = self.check_path_var.get()
        if not folder_path:
            messagebox.showwarning("警告", "请先选择一个JSON文件夹")
            return

        if not os.path.exists(folder_path):
            messagebox.showerror("错误", "文件夹不存在")
            return

        json_files = list(Path(folder_path).glob("*.json"))
        if not json_files:
            messagebox.showwarning("警告", "文件夹中没有找到JSON文件")
            return

        self.update_status("开始核查JSON格式...", 0)
        self.root.update_idletasks()

        def check_files():
            valid_count = 0
            invalid_count = 0
            total_files = len(json_files)

            for i, json_file in enumerate(json_files):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    parsed_data = json.loads(content)
                    formatted_content = json.dumps(parsed_data, ensure_ascii=False, indent=2, separators=(',', ': '))
                    is_formatted = content.strip() == formatted_content

                    if is_formatted:
                        valid_count += 1
                        self.update_results(f"✓ {json_file.name} - 格式正确")
                    else:
                        invalid_count += 1
                        self.update_results(f"✗ {json_file.name} - 格式不正确")

                except json.JSONDecodeError as e:
                    invalid_count += 1
                    self.update_results(f"✗ {json_file.name} - JSON语法错误: {e}")
                except Exception as e:
                    invalid_count += 1
                    self.update_results(f"✗ {json_file.name} - 读取错误: {e}")

                progress = ((i + 1) / total_files) * 100
                self.update_status(f"核查进度: {i + 1}/{total_files}", progress)

            final_message = f"格式核查完成！格式正确: {valid_count}, 格式错误: {invalid_count}"
            self.update_status(final_message, 100)
            self.update_results(final_message)
            messagebox.showinfo("核查完成", final_message)

        checking_thread = threading.Thread(target=check_files, daemon=True)
        checking_thread.start()


def main():
    """主函数"""
    root = tk.Tk()
    app = HighContrastConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()