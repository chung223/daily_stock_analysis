# -*- coding: utf-8 -*-
"""
Discord 發送提醒服务

职责：
1. 通过 webhook 或 Discord bot API 發送 Discord 訊息
"""
import logging
import requests

from src.config import Config
from src.formatters import chunk_content_by_max_words


logger = logging.getLogger(__name__)


class DiscordSender:
    
    def __init__(self, config: Config):
        """
        初始化 Discord 設定

        Args:
            config: 設定对象
        """
        self._discord_config = {
            'bot_token': getattr(config, 'discord_bot_token', None),
            'channel_id': getattr(config, 'discord_main_channel_id', None),
            'webhook_url': getattr(config, 'discord_webhook_url', None),
        }
        self._discord_max_words = getattr(config, 'discord_max_words', 2000)
        self._webhook_verify_ssl = getattr(config, 'webhook_verify_ssl', True)
    
    def _is_discord_configured(self) -> bool:
        """检查 Discord 設定是否完整（支持 Bot 或 Webhook）"""
        # 只要設定了 Webhook 或完整的 Bot Token+Channel，即视为可用
        bot_ok = bool(self._discord_config['bot_token'] and self._discord_config['channel_id'])
        webhook_ok = bool(self._discord_config['webhook_url'])
        return bot_ok or webhook_ok
    
    def send_to_discord(self, content: str) -> bool:
        """
        推播訊息到 Discord（支持 Webhook 和 Bot API）
        
        Args:
            content: Markdown 格式的訊息内容
            
        Returns:
            是否發送成功
        """
        # 分割内容，避免单条訊息超过 Discord 限制
        try:
            chunks = chunk_content_by_max_words(content, self._discord_max_words)
        except ValueError as e:
            logger.error(f"分割 Discord 訊息失敗: {e}, 尝试整段發送。")
            chunks = [content]

        # 优先使用 Webhook（設定简单，权限低）
        if self._discord_config['webhook_url']:
            return all(self._send_discord_webhook(chunk) for chunk in chunks)

        # 其次使用 Bot API（权限高，需要 channel_id）
        if self._discord_config['bot_token'] and self._discord_config['channel_id']:
            return all(self._send_discord_bot(chunk) for chunk in chunks)

        logger.warning("Discord 設定不完整，跳过推播")
        return False

  
    def _send_discord_webhook(self, content: str) -> bool:
        """
        使用 Webhook 發送訊息到 Discord
        
        Discord Webhook 支持 Markdown 格式
        
        Args:
            content: Markdown 格式的訊息内容
            
        Returns:
            是否發送成功
        """
        try:
            payload = {
                'content': content,
                'username': 'A股分析機器人',
                'avatar_url': 'https://picsum.photos/200'
            }
            
            response = requests.post(
                self._discord_config['webhook_url'],
                json=payload,
                timeout=10,
                verify=self._webhook_verify_ssl
            )
            
            if response.status_code in [200, 204]:
                logger.info("Discord Webhook 訊息發送成功")
                return True
            else:
                logger.error(f"Discord Webhook 發送失敗: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Discord Webhook 發送异常: {e}")
            return False
    
    def _send_discord_bot(self, content: str) -> bool:
        """
        使用 Bot API 發送訊息到 Discord
        
        Args:
            content: Markdown 格式的訊息内容
            
        Returns:
            是否發送成功
        """
        try:
            headers = {
                'Authorization': f'Bot {self._discord_config["bot_token"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'content': content
            }
            
            url = f'https://discord.com/api/v10/channels/{self._discord_config["channel_id"]}/messages'
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("Discord Bot 訊息發送成功")
                return True
            else:
                logger.error(f"Discord Bot 發送失敗: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Discord Bot 發送异常: {e}")
            return False
