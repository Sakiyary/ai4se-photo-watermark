#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板管理对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class TemplateDialog:
    """模板管理对话框"""
    
    def __init__(self, parent: tk.Widget, config_manager, title: str = "模板管理"):
        """
        初始化模板对话框
        
        Args:
            parent: 父窗口
            config_manager: 配置管理器
            title: 对话框标题
        """
        self.parent = parent
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.result = None
        
        # 创建对话框
        self._create_dialog(title)
    
    def _create_dialog(self, title: str):
        """创建对话框界面"""
        try:
            # 创建顶级窗口
            self.dialog = tk.Toplevel(self.parent)
            self.dialog.title(title)
            self.dialog.geometry("400x300")
            self.dialog.resizable(False, False)
            self.dialog.grab_set()  # 模态对话框
            
            # 居中显示
            self._center_dialog()
            
            # 创建界面
            self._create_widgets()
            
        except Exception as e:
            self.logger.error(f"创建模板对话框失败: {str(e)}")
    
    def _center_dialog(self):
        """居中显示对话框"""
        try:
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
            self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        except Exception as e:
            self.logger.error(f"居中对话框失败: {str(e)}")
    
    def _create_widgets(self):
        """创建界面组件"""
        try:
            # 主框架
            main_frame = ttk.Frame(self.dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 模板列表
            list_frame = ttk.LabelFrame(main_frame, text="已保存的模板")
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # 列表框和滚动条
            list_container = ttk.Frame(list_frame)
            list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self.template_listbox = tk.Listbox(list_container)
            scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.template_listbox.yview)
            self.template_listbox.config(yscrollcommand=scrollbar.set)
            
            self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 绑定选择事件
            self.template_listbox.bind('<<ListboxSelect>>', self._on_template_select)
            self.template_listbox.bind('<Double-Button-1>', self._on_template_double_click)
            
            # 按钮框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            # 左侧按钮
            left_buttons = ttk.Frame(button_frame)
            left_buttons.pack(side=tk.LEFT)
            
            ttk.Button(left_buttons, text="加载", command=self._load_template).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(left_buttons, text="删除", command=self._delete_template).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(left_buttons, text="重命名", command=self._rename_template).pack(side=tk.LEFT)
            
            # 右侧按钮
            right_buttons = ttk.Frame(button_frame)
            right_buttons.pack(side=tk.RIGHT)
            
            ttk.Button(right_buttons, text="取消", command=self._cancel).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(right_buttons, text="确定", command=self._ok).pack(side=tk.LEFT)
            
            # 加载模板列表
            self._load_template_list()
            
        except Exception as e:
            self.logger.error(f"创建模板对话框界面失败: {str(e)}")
    
    def _load_template_list(self):
        """加载模板列表"""
        try:
            self.template_listbox.delete(0, tk.END)
            templates = self.config_manager.get_all_templates()
            for name in templates:
                self.template_listbox.insert(tk.END, name)
        except Exception as e:
            self.logger.error(f"加载模板列表失败: {str(e)}")
    
    def _on_template_select(self, event):
        """模板选择事件"""
        pass
    
    def _on_template_double_click(self, event):
        """模板双击事件"""
        self._load_template()
    
    def _load_template(self):
        """加载选中的模板"""
        try:
            selection = self.template_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请选择一个模板")
                return
            
            template_name = self.template_listbox.get(selection[0])
            template_config = self.config_manager.get_template(template_name)
            
            if template_config:
                self.result = ('load', template_name, template_config)
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "加载模板失败")
                
        except Exception as e:
            self.logger.error(f"加载模板失败: {str(e)}")
            messagebox.showerror("错误", f"加载模板失败: {str(e)}")
    
    def _delete_template(self):
        """删除选中的模板"""
        try:
            selection = self.template_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请选择一个模板")
                return
            
            template_name = self.template_listbox.get(selection[0])
            if messagebox.askyesno("确认", f"确定要删除模板 '{template_name}' 吗？"):
                if self.config_manager.delete_template(template_name):
                    self._load_template_list()
                    messagebox.showinfo("成功", "模板删除成功")
                else:
                    messagebox.showerror("错误", "删除模板失败")
                    
        except Exception as e:
            self.logger.error(f"删除模板失败: {str(e)}")
            messagebox.showerror("错误", f"删除模板失败: {str(e)}")
    
    def _rename_template(self):
        """重命名选中的模板"""
        try:
            selection = self.template_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请选择一个模板")
                return
            
            old_name = self.template_listbox.get(selection[0])
            new_name = tk.simpledialog.askstring("重命名模板", f"请输入新名称:", initialvalue=old_name)
            
            if new_name and new_name != old_name:
                template_config = self.config_manager.get_template(old_name)
                if template_config:
                    if self.config_manager.save_template(new_name, template_config):
                        self.config_manager.delete_template(old_name)
                        self._load_template_list()
                        messagebox.showinfo("成功", "模板重命名成功")
                    else:
                        messagebox.showerror("错误", "重命名模板失败")
                        
        except Exception as e:
            self.logger.error(f"重命名模板失败: {str(e)}")
            messagebox.showerror("错误", f"重命名模板失败: {str(e)}")
    
    def _ok(self):
        """确定按钮"""
        self._load_template()
    
    def _cancel(self):
        """取消按钮"""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[tuple]:
        """显示对话框并返回结果"""
        try:
            self.dialog.wait_window()
            return self.result
        except Exception as e:
            self.logger.error(f"显示模板对话框失败: {str(e)}")
            return None