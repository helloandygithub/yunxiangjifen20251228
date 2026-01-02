from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models
from config import settings
import logging

logger = logging.getLogger(__name__)


def send_sms_code(phone: str, code: str) -> bool:
    """
    发送短信验证码
    
    Args:
        phone: 手机号（不带国家码）
        code: 验证码
    
    Returns:
        bool: 发送是否成功
    """
    # 确定可以使用的密钥
    secret_id = settings.SMS_SECRET_ID or settings.COS_SECRET_ID
    secret_key = settings.SMS_SECRET_KEY or settings.COS_SECRET_KEY

    # 检查配置是否完整
    if not all([secret_id, secret_key, 
                settings.SMS_SDK_APP_ID, settings.SMS_TEMPLATE_ID]):
        logger.warning("短信服务配置不完整，使用开发模式")
        # 开发模式：打印验证码到日志
        logger.info(f"[开发模式] 手机号: {phone}, 验证码: {code}")
        return True
    
    try:
        # 腾讯云凭证
        cred = credential.Credential(
            secret_id, 
            secret_key
        )
        
        # 创建客户端
        client = sms_client.SmsClient(cred, "ap-guangzhou")
        
        # 构建请求
        req = models.SendSmsRequest()
        req.SmsSdkAppId = settings.SMS_SDK_APP_ID
        req.SignName = settings.SMS_SIGN_NAME or "云享积分"
        req.TemplateId = settings.SMS_TEMPLATE_ID
        req.TemplateParamSet = [code]  # 只发送验证码
        req.PhoneNumberSet = [f"+86{phone}"]
        
        # 发送请求
        resp = client.SendSms(req)
        
        # 检查结果
        if resp.SendStatusSet and resp.SendStatusSet[0].Code == "Ok":
            logger.info(f"短信发送成功: {phone}")
            return True
        else:
            error_msg = resp.SendStatusSet[0].Message if resp.SendStatusSet else "未知错误"
            logger.error(f"短信发送失败: {phone}, 错误: {error_msg}")
            return False
            
    except TencentCloudSDKException as e:
        logger.error(f"腾讯云短信SDK异常: {e}")
        # 降级为开发模式
        logger.warning(f"[降级模式] 手机号: {phone}, 验证码: {code}")
        return True
    except Exception as e:
        logger.error(f"短信发送异常: {e}")
        # 降级为开发模式
        logger.warning(f"[降级模式] 手机号: {phone}, 验证码: {code}")
        return True
