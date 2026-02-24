"""
微信小程序认证工具

提供微信用户认证和会话管理功能
"""

import hashlib
import time
import json
from typing import Optional, Dict, Any
import requests


class WeChatAuth:
    """微信小程序认证类"""
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化微信认证
        
        参数:
            app_id: 微信小程序AppID
            app_secret: 微信小程序AppSecret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://api.weixin.qq.com"
        
        # 会话缓存（实际应该使用Redis等）
        self.sessions = {}
    
    def login(self, code: str) -> Dict[str, Any]:
        """
        微信登录
        
        参数:
            code: 微信登录code
            
        返回:
            用户信息字典
        """
        # 调用微信API获取openid和session_key
        url = f"{self.base_url}/sns/jscode2session"
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"微信登录失败: {data.get('errmsg', '未知错误')}")
            
            openid = data.get("openid")
            session_key = data.get("session_key")
            
            if not openid or not session_key:
                raise Exception("微信登录返回数据不完整")
            
            # 生成用户token
            token = self._generate_token(openid, session_key)
            
            # 保存会话信息
            self.sessions[token] = {
                "openid": openid,
                "session_key": session_key,
                "expires_at": time.time() + 7200,  # 2小时过期
                "user_info": {}
            }
            
            return {
                "success": True,
                "openid": openid,
                "session_key": session_key,
                "token": token,
                "expires_in": 7200
            }
            
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析失败: {str(e)}")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证用户token
        
        参数:
            token: 用户token
            
        返回:
            用户信息或None
        """
        if token not in self.sessions:
            return None
        
        session = self.sessions[token]
        
        # 检查是否过期
        if time.time() > session["expires_at"]:
            del self.sessions[token]
            return None
        
        # 更新过期时间
        session["expires_at"] = time.time() + 7200
        
        return {
            "openid": session["openid"],
            "session_key": session["session_key"],
            "user_info": session.get("user_info", {})
        }
    
    def update_user_info(self, token: str, user_info: Dict[str, Any]) -> bool:
        """
        更新用户信息
        
        参数:
            token: 用户token
            user_info: 用户信息
            
        返回:
            是否成功
        """
        if token not in self.sessions:
            return False
        
        self.sessions[token]["user_info"] = user_info
        return True
    
    def logout(self, token: str) -> bool:
        """
        用户登出
        
        参数:
            token: 用户token
            
        返回:
            是否成功
        """
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
    def _generate_token(self, openid: str, session_key: str) -> str:
        """
        生成用户token
        
        参数:
            openid: 用户openid
            session_key: 会话密钥
            
        返回:
            生成的token
        """
        # 使用openid、session_key和时间戳生成token
        raw = f"{openid}:{session_key}:{time.time()}"
        return hashlib.sha256(raw.encode()).hexdigest()
    
    def decrypt_data(self, encrypted_data: str, iv: str, session_key: str) -> Dict[str, Any]:
        """
        解密微信加密数据
        
        参数:
            encrypted_data: 加密数据
            iv: 加密算法的初始向量
            session_key: 会话密钥
            
        返回:
            解密后的数据
        """
        # 这里需要实现微信数据解密算法
        # 实际实现需要使用cryptography等库
        # 这里返回模拟数据
        
        # 模拟解密过程
        try:
            # 实际解密代码：
            # from Crypto.Cipher import AES
            # import base64
            # 
            # aes_key = base64.b64decode(session_key)
            # aes_iv = base64.b64decode(iv)
            # aes_cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
            # 
            # encrypted_bytes = base64.b64decode(encrypted_data)
            # decrypted_bytes = aes_cipher.decrypt(encrypted_bytes)
            # 
            # # 去除填充
            # pad = decrypted_bytes[-1]
            # decrypted_bytes = decrypted_bytes[:-pad]
            # 
            # data_str = decrypted_bytes.decode('utf-8')
            # return json.loads(data_str)
            
            # 简化处理，返回模拟数据
            return {
                "openId": "simulated_openid",
                "nickName": "微信用户",
                "gender": 0,
                "city": "",
                "province": "",
                "country": "",
                "avatarUrl": "https://thirdwx.qlogo.cn/xxx",
                "unionId": "",
                "watermark": {
                    "timestamp": int(time.time()),
                    "appid": self.app_id
                }
            }
            
        except Exception as e:
            raise Exception(f"数据解密失败: {str(e)}")


# 创建全局认证实例（需要配置后使用）
wechat_auth = None

def init_wechat_auth(app_id: str, app_secret: str):
    """
    初始化微信认证
    
    参数:
        app_id: 微信小程序AppID
        app_secret: 微信小程序AppSecret
    """
    global wechat_auth
    wechat_auth = WeChatAuth(app_id, app_secret)


def get_wechat_auth() -> Optional[WeChatAuth]:
    """
    获取微信认证实例
    
    返回:
        WeChatAuth实例或None
    """
    return wechat_auth