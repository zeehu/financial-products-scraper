import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fake_useragent import UserAgent

def get_random_user_agent():
    """获取随机用户代理"""
    ua = UserAgent()
    return ua.random

def fetch_page(url):
    """获取页面内容"""
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        print(f"获取页面 {url} 失败: {str(e)}")
        return None

def parse_html(html):
    """解析HTML内容"""
    if not html:
        return None
    return BeautifulSoup(html, 'lxml')

def extract_links(soup, base_url=None):
    """提取页面上的所有链接"""
    if not soup:
        return []
    
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if base_url and not href.startswith(('http://', 'https://')):
            href = urljoin(base_url, href)
        links.append({
            'url': href,
            'text': a_tag.text.strip()
        })
    return links

def normalize_url(url):
    """规范化URL"""
    if not url:
        return None
    
    # 确保URL有协议头
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # 移除URL末尾的斜杠
    if url.endswith('/'):
        url = url[:-1]
    
    return url

def clean_text(text):
    """清理文本内容"""
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    # 移除HTML实体
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    return text