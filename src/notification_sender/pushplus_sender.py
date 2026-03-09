# -*- coding: utf-8 -*-
"""
PushPlus 发送提醒服务

职责：
1. 通过 PushPlus API 发送 PushPlus 消息
"""
import logging
from typing import Optional
from datetime import datetime
import requests

from src.config import Config


logger = logging.getLogger(__name__)


class PushplusSender:
    
    def __init__(self, config: Config):
        """
        初始化 PushPlus 配置

        Args:
            config: 配置对象
        """
        self._pushplus_token = getattr(config, 'pushplus_token', None)
        self._pushplus_topic = getattr(config, 'pushplus_topic', None)
        
    def send_to_pushplus(self, content: str, title: Optional[str] = None) -> bool:
        """
        推送消息到 PushPlus

        PushPlus API 格式：
        POST http://www.pushplus.plus/send
        {
            "token": "用户令牌",
            "title": "訊息標題",
            "content": "消息内容",
            "template": "html/txt/json/markdown"
        }

        PushPlus 特点：
        - 国内推送服务，免费额度充足
        - 支持微信公众号推送
        - 支持多种消息格式

        Args:
            content: 消息内容（Markdown 格式）
            title: 訊息標題（可选）

        Returns:
            是否发送成功
        """
        if not self._pushplus_token:
            logger.warning("PushPlus Token 未配置，跳过推送")
            return False

        # PushPlus API 端点
        api_url = "http://www.pushplus.plus/send"

        # 处理訊息標題
        if title is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            title = f"📈 股票分析報告 - {date_str}"

        try:
            payload = {
                "token": self._pushplus_token,
                "title": title,
                "content": content,
                "template": "markdown"  # 使用 Markdown 格式
            }

            # 群组推送（配置了 PUSHPLUS_TOPIC 时推给群组所有人）
            if self._pushplus_topic:
                payload["topic"] = self._pushplus_topic

            response = requests.post(api_url, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    logger.info("PushPlus 消息發送成功")
                    return True
                else:
                    error_msg = result.get('msg', '未知錯誤')
                    logger.error(f"PushPlus 返回錯誤: {error_msg}")
                    return False
            else:
                logger.error(f"PushPlus 請求失敗: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"發送 PushPlus 消息失敗: {e}")
            return False
   