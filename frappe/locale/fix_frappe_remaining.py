#!/usr/bin/env python3
import polib

PO_PATH = '/Users/comfan/Documents/GitHub/AIERP/apps/frappe/frappe/locale/zh.po'
po = polib.pofile(PO_PATH)

for entry in po:
    if not entry.msgstr and entry.msgid:
        raw = entry.msgid
        if 'too guessable' in raw:
            entry.msgstr = "0 - 太容易猜测：危险密码。\n<br>\n1 - 非常容易猜测：仅能防御受限的在线攻击。\n<br>\n2 - 有点容易猜测：仅能防御不受限的在线攻击。\n<br>\n3 - 安全：适度防御离线攻击。\n<br>\n4 - 非常安全：强力防御离线攻击。"
        elif 'Error validating' in raw and 'Ignore User Permissions' in raw:
            entry.msgstr = '验证\u201c忽略用户权限\u201d时出错'
        elif 'Export only customizations' in raw:
            entry.msgstr = "仅导出分配给所选模块的自定义设置。<br><span class='text-muted'><strong>注意：</strong>您必须在文档类型中设置<em>模块（用于导出）</em>字段才能使用此筛选器。</span>"
        elif 'Failed to retrieve the list of IMAP' in raw:
            entry.msgstr = '从服务器获取 IMAP 文件夹列表失败。请确保邮箱可访问且账户有列出文件夹的权限。'
        elif 'only System Managers can upload public' in raw:
            entry.msgstr = "如果启用，只有系统管理员可以上传公共文件。其他用户在上传对话框中看不到<i>是否私有</i>复选框。"
        elif 'mask property for the phone number' in raw:
            entry.msgstr = '如果用户为电话号码字段启用掩码属性，值将以掩码格式显示（例如：811XXXXXXX）。'
        elif 'No IMAP folders were found' in raw:
            entry.msgstr = '在服务器上未找到 IMAP 文件夹。请验证邮箱账户设置并确保邮箱包含文件夹。'
        elif 'Raw HTML emails are rendered' in raw:
            entry.msgstr = '原始 HTML 邮件作为完整的 Jinja 模板渲染。否则，邮件将包装在 standard.html 邮件模板中，该模板插入 brand_logo 等。'
        elif 'configured IMAP folder' in raw and 'not found' in raw:
            entry.msgstr = '以下配置的 IMAP 文件夹在服务器上未找到或不可访问：<br><ul>{0}</ul>请验证文件夹名称与服务器上显示的完全一致，并确保账户有权访问它们。'

po.save(PO_PATH)
po2 = polib.pofile(PO_PATH)
remaining = sum(1 for e in po2 if not e.msgstr and e.msgid)
print(f"Frappe remaining: {remaining}")
