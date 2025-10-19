import requests
from typing import Optional, Dict
import os


class WechatAuthService:
    @staticmethod
    def get_access_token(code: str) -> Optional[Dict]:
        """获取微信access_token（含openid）"""
        appid = os.getenv("WECHAT_APPID")
        secret = os.getenv("WECHAT_SECRET")
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        params = {
            "appid": appid,
            "secret": secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if 'errcode' in data:
                logger.error(f"微信Token获取失败: {data}")
                return None
            return data
        except Exception as e:
            logger.error(f"微信Token请求异常: {e}")
            return None

    @staticmethod
    def get_user_info(access_token: str, openid: str) -> Optional[Dict]:
        """获取微信用户信息（需scope为snsapi_userinfo）"""
        url = "https://api.weixin.qq.com/sns/userinfo"
        params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if 'errcode' in data:
                logger.error(f"微信用户信息获取失败: {data}")
                return None
            return data
        except Exception as e:
            logger.error(f"微信用户信息请求异常: {e}")
            return None

class QQAuthService:
    @staticmethod
    def get_access_token(code: str, redirect_uri: str) -> Optional[Dict]:
        """获取QQ access_token"""
        appid = os.getenv("QQ_APPID")
        secret = os.getenv("QQ_SECRET")
        url = "https://graph.qq.com/oauth2.0/token"
        params = {
            "grant_type": "authorization_code",
            "client_id": appid,
            "client_secret": secret,
            "code": code,
            "redirect_uri": redirect_uri
        }
        try:
            response = requests.get(url, params=params)
            # 处理QQ的字符串响应（如 "access_token=XXX&expires_in=7776000"）
            data = {}
            for item in response.text.split('&'):
                key, value = item.split('=')
                data[key] = value
            return data if 'access_token' in data else None
        except Exception as e:
            logger.error(f"QQ Token请求异常: {e}")
            return None

    @staticmethod
    def get_openid(access_token: str) -> Optional[Dict]:
        """解析QQ OpenID（返回格式如 callback({"openid":"XXX"}); ）"""
        url = "https://graph.qq.com/oauth2.0/me"
        params = {"access_token": access_token}
        try:
            response = requests.get(url, params=params)
            text = response.text
            # 去除回调函数包裹
            json_str = text[9:-3]  # 去掉 "callback(" 和 ");"
            import json
            data = json.loads(json_str)
            if 'openid' not in data:
                logger.error(f"QQ OpenID解析失败: {data}")
                return None
            return data
        except Exception as e:
            logger.error(f"QQ OpenID请求异常: {e}")
            return None