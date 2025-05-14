import json
import re
import time
import random
from typing import List, Dict, Any
from urllib.parse import urljoin
import datetime

from ..utils.parser import fetch_page, parse_html, clean_text
from ..utils.date_utils import parse_date, get_today
from .base_scraper import BaseScraper

# 工商银行融e行网站URL
ICBC_BASE_URL = "https://elife.icbc.com.cn"
ICBC_PRODUCT_LIST_URL = "https://elife.icbc.com.cn/ICBC/newperbank/perbank3/wealth/financing/financing_index.jsp"
ICBC_PRODUCT_DETAIL_API = "https://elife.icbc.com.cn/ICBC/newperbank/perbank3/wealth/financing/queryFinacingDetail.do"
ICBC_PRODUCT_RETURN_API = "https://elife.icbc.com.cn/ICBC/newperbank/perbank3/wealth/financing/queryLingqianyieldList.do"


class ICBCScraper(BaseScraper):
    """工商银行融e行爬虫"""
    
    def __init__(self):
        super().__init__("工商银行融e行", ICBC_BASE_URL)
        self.product_list_url = ICBC_PRODUCT_LIST_URL
    
    def get_product_list(self) -> List[Dict[str, Any]]:
        """获取产品列表"""
        print(f"开始获取工商银行融e行产品列表...")
        
        products = []
        page = 1
        has_more = True
        
        while has_more:
            # 构造请求参数
            params = {
                "page": page,
                "pageSize": 10,
                "productType": "ALL"  # 所有产品
            }
            
            # 请求产品列表
            url = f"{self.product_list_url}?page={page}"
            soup = self.get_page(url)
            
            if not soup:
                print(f"获取第 {page} 页产品列表失败")
                break
            
            # 查找产品列表
            product_items = soup.select('.product-list .product-item')
            
            if not product_items:
                print(f"第 {page} 页没有找到产品")
                break
                
            for item in product_items:
                product = {}
                
                # 产品名称
                name_tag = item.select_one('.product-name')
                if name_tag:
                    product['product_name'] = clean_text(name_tag.text)
                
                # 产品代码
                code_tag = item.select_one('.product-code')
                if code_tag:
                    code_text = clean_text(code_tag.text)
                    code_match = re.search(r'(\w+)', code_text)
                    if code_match:
                        product['product_code'] = code_match.group(1)
                
                # 产品类型
                type_tag = item.select_one('.product-type')
                if type_tag:
                    product['product_type'] = clean_text(type_tag.text)
                
                # 风险等级
                risk_tag = item.select_one('.risk-level')
                if risk_tag:
                    product['risk_level'] = clean_text(risk_tag.text)
                
                # 预期收益率
                return_tag = item.select_one('.expected-return')
                if return_tag:
                    return_text = clean_text(return_tag.text)
                    return_match = re.search(r'(\d+\.\d+)%', return_text)
                    if return_match:
                        product['expected_return'] = float(return_match.group(1))
                
                # 投资期限
                period_tag = item.select_one('.investment-period')
                if period_tag:
                    product['investment_horizon'] = clean_text(period_tag.text)
                
                # 产品详情链接
                detail_tag = item.select_one('a.detail-link')
                if detail_tag and 'href' in detail_tag.attrs:
                    detail_url = detail_tag['href']
                    if not detail_url.startswith('http'):
                        detail_url = urljoin(self.base_url, detail_url)
                    product['details_url'] = detail_url
                
                # 设置公司信息
                product['company_name'] = self.company_name
                product['company_url'] = self.company_url
                
                if 'product_code' in product and 'product_name' in product:
                    products.append(product)
            
            # 判断是否有下一页
            next_page = soup.select_one('.pagination .next:not(.disabled)')
            if not next_page:
                has_more = False
            else:
                page += 1
                # 添加延时避免频繁请求
                time.sleep(random.uniform(1, 3))
        
        print(f"共获取到 {len(products)} 个产品")
        return products
    
    def get_product_details(self, product_url: str) -> Dict[str, Any]:
        """获取产品详情"""
        print(f"获取产品详情: {product_url}")
        
        soup = self.get_page(product_url)
        if not soup:
            print(f"获取产品详情页面失败: {product_url}")
            return {}
        
        details = {}
        
        # 起投金额
        min_invest_tag = soup.select_one('.min-investment')
        if min_invest_tag:
            min_invest_text = clean_text(min_invest_tag.text)
            min_invest_match = re.search(r'(\d+(?:\.\d+)?)', min_invest_text)
            if min_invest_match:
                details['min_investment'] = float(min_invest_match.group(1))
        
        # 产品状态
        status_tag = soup.select_one('.product-status')
        if status_tag:
            details['status'] = clean_text(status_tag.text)
        
        # 成立日期
        establish_tag = soup.select_one('.establishment-date')
        if establish_tag:
            establish_text = clean_text(establish_tag.text)
            details['establishment_date'] = parse_date(establish_text)
        
        # 到期日期
        maturity_tag = soup.select_one('.maturity-date')
        if maturity_tag:
            maturity_text = clean_text(maturity_tag.text)
            details['maturity_date'] = parse_date(maturity_text)
        
        # 产品描述
        desc_tag = soup.select_one('.product-description')
        if desc_tag:
            details['description'] = clean_text(desc_tag.text)
        
        # 实际收益率
        actual_return_tag = soup.select_one('.actual-return')
        if actual_return_tag:
            actual_return_text = clean_text(actual_return_tag.text)
            actual_return_match = re.search(r'(\d+\.\d+)%', actual_return_text)
            if actual_return_match:
                details['actual_return'] = float(actual_return_match.group(1))
        
        # 记录最后更新日期
        details['last_update'] = get_today()
        
        return details
    
    def get_product_returns(self, product_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """获取产品收益信息"""
        print(f"获取产品 {product_code} 的收益信息...")
        
        # 构造API请求参数
        today = get_today()
        start_date = today - datetime.timedelta(days=days)
        
        # 构造请求URL
        params = {
            "productCode": product_code,
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": today.strftime("%Y-%m-%d")
        }
        
        # 格式化为查询字符串
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{ICBC_PRODUCT_RETURN_API}?{query_string}"
        
        html = fetch_page(url)
        if not html:
            print(f"获取产品 {product_code} 收益信息失败")
            return []
        
        try:
            # 尝试解析JSON响应
            data = json.loads(html)
            
            if not data or 'data' not in data or not data['data']:
                print(f"产品 {product_code} 收益数据为空")
                return []
            
            returns = []
            
            for item in data['data']:
                return_info = {
                    'product_code': product_code,
                    'date': parse_date(item.get('date', '')),
                    'unit_net_value': float(item.get('unitNetValue', 0)),
                    'cumulative_net_value': float(item.get('cumulativeNetValue', 0)),
                    'daily_return_rate': float(item.get('dailyReturn', 0)),
                    'seven_day_annualized': float(item.get('sevenDayAnnualized', 0))
                }
                
                if return_info['date']:  # 确保日期有效
                    returns.append(return_info)
            
            print(f"获取到产品 {product_code} 的 {len(returns)} 条收益记录")
            return returns
            
        except json.JSONDecodeError:
            print(f"解析产品 {product_code} 收益数据失败，尝试解析HTML")
            
            # 如果不是JSON，尝试解析HTML
            soup = parse_html(html)
            if not soup:
                return []
            
            returns = []
            
            # 查找表格数据
            table = soup.select_one('.return-table')
            if not table:
                return []
            
            rows = table.select('tr')
            for row in rows[1:]:  # 跳过表头
                cols = row.select('td')
                if len(cols) >= 5:
                    try:
                        return_info = {
                            'product_code': product_code,
                            'date': parse_date(cols[0].text),
                            'unit_net_value': float(cols[1].text),
                            'cumulative_net_value': float(cols[2].text),
                            'daily_return_rate': float(cols[3].text.strip('%')),
                            'seven_day_annualized': float(cols[4].text.strip('%'))
                        }
                        
                        if return_info['date']:  # 确保日期有效
                            returns.append(return_info)
                    except (ValueError, AttributeError):
                        continue
            
            print(f"从HTML中获取到产品 {product_code} 的 {len(returns)} 条收益记录")
            return returns