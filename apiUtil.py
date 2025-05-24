import hmac
import hashlib
import base64
import time
import json
from typing import Dict, List, Any, Optional
import requests

class SignUtil:
    """
    签名工具类，提供HMAC和SHA256加密功能以及签名生成
    """
    @staticmethod
    def hmac256(key: bytes, msg: str) -> bytes:
        """
        执行HMAC-SHA256运算
        
        Args:
            key: 加密密钥字节数组
            msg: 待加密消息字符串
            
        Returns:
            加密后的字节数组
        """
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    
    @staticmethod
    def sha256_hex(s: str) -> str:
        """
        计算字符串的SHA-256哈希值并转换为小写十六进制字符串
        
        Args:
            s: 待计算哈希值的字符串
            
        Returns:
            小写十六进制格式的SHA-256哈希值
        """
        return hashlib.sha256(s.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_sign(secret_key: str, timestamp: str, data_str: Optional[str] = "") -> str:
        """
        生成签名
        
        Args:
            secret_key: 秘钥字符串
            timestamp: 时间戳字符串
            data_str: 可选的额外数据字符串
            
        Returns:
            Base64编码的签名字符串
        """
        # 组合时间戳和额外数据并计算SHA-256哈希
        content = SignUtil.sha256_hex(timestamp + data_str)
        # 使用HMAC-SHA256算法生成签名并进行Base64编码
        return base64.b64encode(SignUtil.hmac256(secret_key.encode('utf-8'), content)).decode('utf-8')

    @staticmethod
    def dataSend(api_uri: str, datalist: list, wrapWithItems: bool = True):
        # 请替换为实际的密钥对和API地址
        secret_id = "AKIDcKmO0D36wIAS86eW3kj0bySERBHiTM74"
        secret_key = "46388f1865c4b79a6e20ec954c814da5"
        
        # 检查必要参数是否已设置
        if not secret_id or not secret_key or not api_uri:
            print("请设置secret_id、secret_key和api_uri")
            exit(1)
        
        headers = {}
        timestamp = str(int(time.time() * 1000))  # 毫秒级时间戳
                
        if wrapWithItems:
            request_data = {
                'items': datalist
            }
        else:
            request_data = {
                'data': datalist
            }    
        
        json_data = json.dumps(request_data, ensure_ascii=False)
        data = json_data.encode()
        try:
            # 生成签名（使用带额外数据的版本）
            # sign = SignUtil.generate_sign(secret_key, timestamp, json_data)
            sign = SignUtil.generate_sign(secret_key, timestamp)
            
            # 设置请求头
            headers["secretId"] = secret_id
            headers["timestamp"] = timestamp
            headers["sign"] = sign
            headers["Content-Type"] = "application/json"
            
            print(f"生成的签名: {sign}")
            print(f"时间戳: {timestamp}")
            
            # 发送HTTP请求
            response = requests.post(
                api_uri,
                headers=headers,
                # data=json_data.encode('utf-8')
                data=data
            )
            
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应内容: {response.text}")
            print(f"提交数据：{json_data}")
            return {"code":response.status_code, "message":response.text}
        except Exception as e:
            print(f"请求过程中发生错误: {str(e)}")
            return {'code': -1, 'message': {str(e)}}
        

if __name__ == "__main__":
    # 请替换为实际的密钥对和API地址
    secret_id = "AKIDcKmO0D36wIAS86eW3kj0bySERBHiTM74"
    secret_key = "46388f1865c4b79a6e20ec954c814da5"
    api_uri = "http://58.48.136.183:19090/hbyjbg-api/model/v2/mmsPriceRptTest"
    
    # 检查必要参数是否已设置
    if not secret_id or not secret_key or not api_uri:
        print("请设置secret_id、secret_key和api_uri")
        exit(1)
    
    headers = {}
    timestamp = str(int(time.time() * 1000))  # 毫秒级时间戳
    
    # 构建请求数据
    data = {
        "linkman": "test apt",
        "telephone": "13912345678"
    }
    
    request_data = {
        "items": [data]
    }
    
    json_data = json.dumps(request_data, ensure_ascii=False)
    
    try:
        # 生成签名（使用带额外数据的版本）
        # sign = SignUtil.generate_sign(secret_key, timestamp, json_data)
        sign = SignUtil.generate_sign(secret_key, timestamp)
        
        # 设置请求头
        headers["secretId"] = secret_id
        headers["timestamp"] = timestamp
        headers["sign"] = sign
        headers["Content-Type"] = "application/json"
        
        print(f"生成的签名: {sign}")
        print(f"时间戳: {timestamp}")
        
        # 发送HTTP请求
        response = requests.post(
            api_uri,
            headers=headers,
            data=json_data.encode('utf-8')
        )
        
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
    except Exception as e:
        print(f"请求过程中发生错误: {str(e)}")