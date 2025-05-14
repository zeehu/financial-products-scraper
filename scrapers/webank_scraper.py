import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from ..utils.parser import fetch_page, parse_html, clean_text, normalize_url

WEBANK_PARTNER_URL = "https://www.webank.com/inquiryCenter/financepartner"

class WeBankScraper:
    """微众银行合作伙伴爬虫"""
    
    def __init__(self):
        self.partner_url = WEBANK_PARTNER_URL
        
    def get_partners(self) -> List[Dict[str, Any]]:
        """
        获取微众银行金融合作伙伴列表
        返回合作伙伴信息字典的列表
        """
        print(f"开始抓取微众银行合作伙伴信息...")
        
        # 获取页面内容
        html = fetch_page(self.partner_url)
        if not html:
            print("获取微众银行合作伙伴页面失败")
            return []
        
        soup = parse_html(html)
        if not soup:
            print("解析微众银行合作伙伴页面失败")
            return []
        
        partners = []
        
        # 查找合作伙伴区域
        partner_section = soup.find('div', class_='tablewrap')
        if not partner_section:
            print("未找到合作伙伴区域")
            return []
        
        # 获取所有合作伙伴条目
        partner_items = partner_section.find_all('dl', class_='tablelist')
        
        for item in partner_items:
            partner_info = {}
            
            # 获取合作伙伴名称
            name_tag = item.find('dt')
            if name_tag:
                partner_info['name'] = clean_text(name_tag.text)
            
            # 获取链接
            link_tag = item.find('a', href=True)
            if link_tag:
                url = link_tag.get('href')
                if url:
                    # 规范化URL
                    url = normalize_url(url)
                    partner_info['url'] = url
            
            if partner_info.get('name') and partner_info.get('url'):
                partners.append(partner_info)
                print(f"找到合作伙伴: {partner_info['name']} - {partner_info['url']}")
        
        print(f"共找到 {len(partners)} 个合作伙伴")
        return partners 