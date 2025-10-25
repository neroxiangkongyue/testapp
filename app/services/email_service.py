import smtplib
import ssl
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import logging

from fastapi import HTTPException

from app.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务类"""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER  # 服务器
        self.smtp_port = settings.SMTP_PORT  # 端口
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_name = settings.EMAIL_FROM_NAME

    def send_verification_email(self, to_email: str, code: str, purpose: str) -> bool:
        """
        发送验证码邮件

        Args:
            to_email: 收件人邮箱
            code: 验证码
            purpose: 验证码用途（register/login/reset_password）

        Returns:
            bool: 发送是否成功
        """
        if purpose == "register":
            subject = "注册验证码"
            template = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2563eb;">欢迎注册单词图学习系统</h2>
                    <p>您的注册验证码是：</p>
                    <div style="background: #f3f4f6; padding: 10px 15px; border-radius: 5px; 
                                font-size: 24px; font-weight: bold; color: #2563eb; 
                                display: inline-block; margin: 15px 0;">
                        {code}
                    </div>
                    <p style="color: #6b7280; font-size: 14px;">
                        此验证码将在5分钟后失效，请尽快完成注册。
                    </p>
                </div>
                """
        elif purpose == "reset_password":
            subject = "密码重置验证码"
            template = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2563eb;">密码重置</h2>
                    <p>您正在尝试重置密码，验证码是：</p>
                    <div style="background: #f3f4f6; padding: 10px 15px; border-radius: 5px; 
                                font-size: 24px; font-weight: bold; color: #2563eb; 
                                display: inline-block; margin: 15px 0;">
                        {code}
                    </div>
                    <p style="color: #6b7280; font-size: 14px;">
                        如果您没有请求重置密码，请忽略此邮件。
                    </p>
                </div>
                """
        else:
            subject = "验证码"
            template = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2563eb;">您的验证码</h2>
                    <p>验证码是：</p>
                    <div style="background: #f3f4f6; padding: 10px 15px; border-radius: 5px; 
                                font-size: 24px; font-weight: bold; color: #2563eb; 
                                display: inline-block; margin: 15px 0;">
                        {code}
                    </div>
                    <p style="color: #6b7280; font-size: 14px;">
                        此验证码将在5分钟后失效，请尽快使用。
                    </p>
                </div>
                """

        try:
            # 使用改进的邮件发送方法
            return self._send_email(to_email, subject, template)
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="邮件发送失败，请稍后重试"
            )

    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        发送邮件内部实现（修复From头格式问题）

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容

        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()

            # 修复From头格式 - 使用formataddr而不是字符串拼接
            # 这是关键修复：QQ邮箱要求From头符合RFC标准
            msg['From'] = formataddr((Header(self.from_name, 'utf-8').encode(), self.smtp_username))
            msg['To'] = to_email
            msg['Subject'] = Header(subject, 'utf-8').encode()

            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # 创建SSL上下文
            context = ssl.create_default_context()

            # 根据端口选择连接方式
            if self.smtp_port == 465:
                # 使用SSL连接
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context)
            else:
                # 使用TLS连接
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.ehlo()  # 向服务器标识用户身份
                server.starttls(context=context)  # 安全传输模式
                server.ehlo()  # 再次向服务器标识用户身份

            # 登录QQ邮箱
            server.login(self.smtp_username, self.smtp_password)

            # 发送邮件
            server.sendmail(self.smtp_username, to_email, msg.as_string())
            server.quit()

            logger.info(f"邮件发送成功: {to_email}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {to_email}, 错误: {str(e)}")
            return False

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """
        发送欢迎邮件（用户注册成功后）

        Args:
            to_email: 收件人邮箱
            username: 用户名

        Returns:
            bool: 发送是否成功
        """
        subject = "欢迎加入单词图学习系统"
        html_content = f"""
        <h2>欢迎加入单词图学习系统！</h2>
        <p>亲爱的 {username}，</p>
        <p>感谢您注册单词图学习系统，我们很高兴您的加入！</p>
        <p>在单词图中，您可以：</p>
        <ul>
            <li>📚 学习海量单词和例句</li>
            <li>🔗 探索单词之间的关联关系</li>
            <li>📊 跟踪个人学习进度</li>
            <li>👥 与其他学习者交流</li>
        </ul>
        <p>立即开始您的单词学习之旅吧！</p>
        <p>祝您学习愉快！</p>
        <br>
        <p>单词图团队敬上</p>
        """

        return self._send_email(to_email, subject, html_content)


# 创建全局邮件服务实例
email_service = EmailService()