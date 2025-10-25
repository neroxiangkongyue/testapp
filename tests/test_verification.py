from unittest.mock import patch
from fastapi.testclient import TestClient


def test_send_verification_code_email(client: TestClient):
    """
    测试发送邮箱验证码
    """
    # 模拟邮件发送成功
    with patch('app.services.email_service.EmailService.send_verification_email') as mock_send:
        mock_send.return_value = True

        data = {
            "identifier": "test@example.com",
            "purpose": "register"
        }

        response = client.post("/auth/send-verification-code", json=data)

        assert response.status_code == 200
        assert "验证码已发送" in response.json()["message"]


def test_send_verification_code_phone(client: TestClient):
    """
    测试发送手机验证码
    """
    # 模拟短信发送成功
    with patch('app.services.sms_service.SMSService.send_verification_sms') as mock_send:
        mock_send.return_value = True

        data = {
            "identifier": "+8613800138000",
            "purpose": "login"
        }

        response = client.post("/auth/send-verification-code", json=data)

        assert response.status_code == 200
        assert "验证码已发送" in response.json()["message"]


def test_send_verification_code_invalid_email(client: TestClient):
    """
    测试发送验证码到无效邮箱
    """
    data = {
        "identifier": "invalid-email",
        "purpose": "register"
    }

    response = client.post("/auth/send-verification-code", json=data)

    assert response.status_code == 400
    assert "邮箱格式无效" in response.json()["detail"]


def test_send_verification_code_existing_email(client: TestClient, test_user):
    """
    测试向已注册邮箱发送注册验证码
    """
    data = {
        "identifier": "test@example.com",  # 已存在的邮箱
        "purpose": "register"
    }

    response = client.post("/auth/send-verification-code", json=data)

    assert response.status_code == 400
    assert "已被注册" in response.json()["detail"]