"""
微信小程序登录工具
"""
import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)


async def get_wx_session(code: str) -> dict:
    """
    通过code换取微信session_key和openid
    
    Args:
        code: 小程序wx.login获取的code
        
    Returns:
        dict: 包含openid和session_key
    """
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        
    if "errcode" in data and data["errcode"] != 0:
        logger.error(f"微信登录失败: {data}")
        raise Exception(f"微信登录失败: {data.get('errmsg', '未知错误')}")
    
    return data


async def get_phone_number(code: str) -> str:
    """
    通过getPhoneNumber的code获取手机号
    
    Args:
        code: 小程序getPhoneNumber获取的code
        
    Returns:
        str: 手机号
    """
    # 先获取access_token
    token_url = "https://api.weixin.qq.com/cgi-bin/token"
    token_params = {
        "grant_type": "client_credential",
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET
    }
    
    async with httpx.AsyncClient() as client:
        token_resp = await client.get(token_url, params=token_params)
        token_data = token_resp.json()
        
    if "access_token" not in token_data:
        logger.error(f"获取access_token失败: {token_data}")
        raise Exception("获取access_token失败")
    
    access_token = token_data["access_token"]
    
    # 用access_token和code获取手机号
    phone_url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}"
    
    async with httpx.AsyncClient() as client:
        phone_resp = await client.post(phone_url, json={"code": code})
        phone_data = phone_resp.json()
    
    if phone_data.get("errcode") != 0:
        logger.error(f"获取手机号失败: {phone_data}")
        raise Exception(f"获取手机号失败: {phone_data.get('errmsg', '未知错误')}")
    
    phone_info = phone_data.get("phone_info", {})
    phone_number = phone_info.get("purePhoneNumber") or phone_info.get("phoneNumber", "")
    
    if not phone_number:
        raise Exception("未获取到手机号")
    
    # 去掉可能的国家码前缀
    if phone_number.startswith("86"):
        phone_number = phone_number[2:]
    elif phone_number.startswith("+86"):
        phone_number = phone_number[3:]
    
    return phone_number
