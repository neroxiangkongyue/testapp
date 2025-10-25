#!/usr/bin/env python3
"""
测试QQ邮箱SMTP连接
"""

# !/usr/bin/env python3
"""
QQ邮箱SMTP连接测试脚本
"""

import smtplib
import ssl
import os
from dotenv import load_dotenv

load_dotenv()


def test_qq_smtp():
    smtp_server = os.getenv("SMTP_SERVER", "smtp.qq.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "770782393@qq.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "cqvniouyrgtibeab")

    print("=" * 50)
    print("QQ邮箱SMTP配置测试")
    print("=" * 50)
    print(f"SMTP服务器: {smtp_server}")
    print(f"SMTP端口: {smtp_port}")
    print(f"用户名: {smtp_username}")
    print(f"密码: {'*' * len(smtp_password) if smtp_password else '<未设置>'}")

    try:
        print("\n尝试连接服务器...")
        context = ssl.create_default_context()

        if smtp_port == 465:
            print("使用SSL连接(端口465)")
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        else:
            print("使用TLS连接(端口587)")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls(context=context)

        print("连接成功！")

        print("\n尝试登录...")
        server.login(smtp_username, smtp_password)
        print("登录成功！QQ邮箱配置正确")

        server.quit()
        return True

    except smtplib.SMTPAuthenticationError:
        print("\n错误：认证失败")
        print("可能原因：")
        print("1. 用户名或密码错误")
        print("2. 使用了QQ登录密码而不是授权码")
        print("3. SMTP服务未开启")
        return False
    except smtplib.SMTPException as e:
        print(f"\nSMTP错误: {str(e)}")
        return False
    except Exception as e:
        print(f"\n连接失败: {str(e)}")
        return False


if __name__ == "__main__":
    test_qq_smtp()