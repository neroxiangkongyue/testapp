import logging
from app.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class SMSService:
    """短信发送服务类（以阿里云为例）"""

    def __init__(self):
        self.access_key = settings.SMS_ACCESS_KEY
        self.access_secret = settings.SMS_ACCESS_SECRET
        self.sign_name = settings.SMS_SIGN_NAME
        self.template_code = settings.SMS_TEMPLATE_CODE
        self.endpoint = "dysmsapi.aliyuncs.com"

    def send_verification_sms(self, phone: str, code: str, purpose: str) -> bool:
        """
        发送验证码短信

        Args:
            phone: 手机号
            code: 验证码
            purpose: 验证码用途

        Returns:
            bool: 发送是否成功
        """
        # 如果禁用了短信发送，直接返回成功（用于测试环境）
        if settings.DISABLE_SMS_SENDING:
            logger.info(f"短信发送已禁用，跳过发送验证码到 {phone}")
            return True

        # 根据用途选择模板参数
        template_param = {
            "code": code,
            "purpose": {
                "register": "注册",
                "login": "登录",
                "reset_password": "重置密码"
            }.get(purpose, "验证")
        }

        return self._send_sms(phone, template_param)

    def _send_sms(self, phone: str, template_param: dict) -> bool:
        """
        发送短信内部实现（阿里云短信服务）

        Args:
            phone: 手机号
            template_param: 模板参数

        Returns:
            bool: 发送是否成功
        """
        try:
            # 这里应该是实际的短信服务商API调用
            # 以下为示例代码，实际使用时需要根据短信服务商文档实现

            # 示例：阿里云短信服务调用
            # 实际项目中需要安装阿里云SDK: pip install alibabacloud_dysmsapi20170525
            """
            from alibabacloud_dysmsapi20170525.client import Client
            from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
            from alibabacloud_tea_openapi import models as open_api_models

            config = open_api_models.Config(
                access_key_id=self.access_key,
                access_key_secret=self.access_secret
            )
            config.endpoint = self.endpoint

            client = Client(config)

            request = dysmsapi_models.SendSmsRequest(
                phone_numbers=phone,
                sign_name=self.sign_name,
                template_code=self.template_code,
                template_param=json.dumps(template_param)
            )

            response = client.send_sms(request)
            return response.body.code == "OK"
            """

            # 由于短信服务需要付费和配置，这里先模拟成功
            logger.info(f"模拟发送短信到 {phone}: 验证码 {template_param.get('code')}")
            return True

        except Exception as e:
            logger.error(f"短信发送失败: {phone}, 错误: {str(e)}")
            return False


# 创建全局短信服务实例
sms_service = SMSService()