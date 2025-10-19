#!/usr/bin/env python3
"""
QQ邮箱SMTP完整测试脚本
"""

import smtplib
import ssl
import os
from dotenv import load_dotenv

load_dotenv()


def full_smtp_test():
    smtp_server = os.getenv("SMTP_SERVER", "smtp.qq.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "770782393@qq.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "cqvniouyrgtibeab")

    print("=" * 50)
    print("QQ邮箱SMTP完整测试")
    print("=" * 50)
    print(f"SMTP服务器: {smtp_server}")
    print(f"SMTP端口: {smtp_port}")
    print(f"用户名: {smtp_username}")
    print(f"密码: {'*' * len(smtp_password) if smtp_password else '<未设置>'}")

    try:
        # 测试1: 基本连接
        print("\n1. 测试基本连接...")
        context = ssl.create_default_context()

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()

        print("基本连接测试成功！")

        # 测试2: 认证
        print("\n2. 测试认证...")
        server.login(smtp_username, smtp_password)
        print("认证测试成功！")

        # 测试3: 发送简单邮件
        print("\n3. 测试发送简单邮件...")
        from email.mime.text import MIMEText
        from email.utils import formataddr

        msg = MIMEText("这是一封测试邮件")
        msg['From'] = formataddr(("测试发件人", smtp_username))
        msg['To'] = "test@example.com"  # 替换为你的测试邮箱
        msg['Subject'] = "SMTP测试邮件"

        server.sendmail(smtp_username, "baal@hunnu.edu.cn", msg.as_string())
        print("发送测试邮件成功！")

        server.quit()
        print("\n所有测试通过！QQ邮箱配置正确")
        return True

    except smtplib.SMTPAuthenticationError:
        print("\n错误：认证失败")
        print("请检查用户名和授权码是否正确")
        return False
    except smtplib.SMTPException as e:
        print(f"\nSMTP错误: {str(e)}")
        return False
    except Exception as e:
        print(f"\n错误: {str(e)}")
        return False


if __name__ == "__main__":
    full_smtp_test()