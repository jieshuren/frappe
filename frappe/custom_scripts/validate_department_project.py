#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
凭证保存时验证部门和项目是否匹配
"""
import frappe
from frappe import _

def validate_department_project(doc, method):
    """
    验证凭证中的部门和项目是否匹配
    在 Journal Entry 保存前触发
    """
    for row in doc.accounts:
        # 如果同时填了部门和项目
        if row.department and row.project:
            # 获取项目归属的部门
            project_department = frappe.db.get_value('Project', row.project, 'department')

            if project_department and project_department != row.department:
                frappe.throw(
                    _('第 {0} 行：项目 {1} 归属于 {2}，但选择的部门是 {3}，请修改！').format(
                        row.idx,
                        row.project,
                        project_department,
                        row.department
                    )
                )

# 注册钩子
# 在 hooks.py 中添加：
# doc_events = {
#     "Journal Entry": {
#         "validate": "frappe.custom_scripts.validate_department_project.validate_department_project"
#     }
# }
