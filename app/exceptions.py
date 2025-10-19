# app/exceptions.py
class NotFoundException(Exception):
    """资源未找到异常"""
    def __init__(self, message: str = "资源未找到"):
        self.message = message
        super().__init__(self.message)


class ValidationException(Exception):
    """验证失败异常"""
    def __init__(self, message: str = "验证失败"):
        self.message = message
        super().__init__(self.message)