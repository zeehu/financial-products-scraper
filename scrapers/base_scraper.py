import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import datetime

from ..utils.parser import fetch_page, parse_html, normalize_url


class BaseScraper(ABC):
    """基础爬虫类，所有具体爬虫类都应继承此类"""
    
    def __init__(self, company_name: str, company_url: str):
        self.company_name = company_name
        self.company_url = normalize_url(company_url)
        self.base_url = self.company_url
        
    def get_page(self, url):
        """获取页面内容"""
        html = fetch_page(url)
        if not html:
            return None
        soup = parse_html(html)
        return soup
    
    @abstractmethod
    def get_product_list(self) -> List[Dict[str, Any]]:
        """
        获取产品列表
        返回产品信息字典的列表
        """
        pass
    
    @abstractmethod
    def get_product_details(self, product_url: str) -> Dict[str, Any]:
        """
        获取产品详情
        返回单个产品的详细信息
        """
        pass
    
    @abstractmethod
    def get_product_returns(self, product_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取产品收益信息
        返回产品收益信息字典的列表
        """
        pass
    
    def run(self, max_products: Optional[int] = None) -> Dict[str, Any]:
        """
        运行爬虫，获取所有产品及其收益信息
        返回所有数据
        """
        print(f"开始抓取 {self.company_name} 的数据...")
        
        # 获取产品列表
        products = self.get_product_list()
        if max_products:
            products = products[:max_products]
        
        result = {
            "company_name": self.company_name,
            "company_url": self.company_url,
            "crawl_time": datetime.datetime.now().isoformat(),
            "products": [],
            "daily_returns": []
        }
        
        # 遍历产品列表，获取详情和收益信息
        for i, product in enumerate(products):
            print(f"正在处理第 {i+1}/{len(products)} 个产品: {product.get('product_name', '')}...")
            
            # 获取产品详情
            if product.get('details_url'):
                details = self.get_product_details(product['details_url'])
                if details:
                    product.update(details)
            
            # 获取产品收益信息
            if product.get('product_code'):
                returns = self.get_product_returns(product['product_code'])
                if returns:
                    result["daily_returns"].extend(returns)
            
            result["products"].append(product)
            
            # 随机延时，避免被反爬
            time.sleep(random.uniform(1, 3))
        
        print(f"完成抓取 {self.company_name} 的数据，共 {len(result['products'])} 个产品，{len(result['daily_returns'])} 条收益记录")
        return result 