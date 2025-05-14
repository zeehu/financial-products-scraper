from typing import Dict, List, Any
import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from .database import get_db
from .product import Product
from .daily_return import DailyReturn
from ..utils.date_utils import parse_date, get_today


class DataProcessor:
    """数据处理器，负责将爬取的数据保存到数据库"""
    
    def __init__(self):
        self.db = get_db()
    
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理爬虫抓取的数据"""
        results = {
            "company_name": data.get("company_name", ""),
            "products_count": 0,
            "products_updated": 0,
            "products_new": 0,
            "returns_count": 0,
            "returns_new": 0
        }
        
        # 处理产品数据
        if "products" in data and data["products"]:
            products_count = len(data["products"])
            results["products_count"] = products_count
            
            for product_data in data["products"]:
                product_result = self.save_product(product_data)
                if product_result["is_new"]:
                    results["products_new"] += 1
                else:
                    results["products_updated"] += 1
        
        # 处理收益数据
        if "daily_returns" in data and data["daily_returns"]:
            returns_count = len(data["daily_returns"])
            results["returns_count"] = returns_count
            
            for return_data in data["daily_returns"]:
                return_result = self.save_daily_return(return_data)
                if return_result["is_new"]:
                    results["returns_new"] += 1
        
        return results
    
    def save_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存产品数据到数据库"""
        result = {"is_new": False, "id": None}
        
        # 检查必要字段
        if "product_code" not in product_data or not product_data["product_code"]:
            print("产品数据缺少产品代码，无法保存")
            return result
        
        # 查询是否存在该产品
        existing_product = self.db.query(Product).filter(
            Product.product_code == product_data["product_code"]
        ).first()
        
        if existing_product:
            # 更新现有产品
            for key, value in product_data.items():
                # 跳过id和空值
                if key == "id" or value is None:
                    continue
                
                # 处理日期类型字段
                if key in ["establishment_date", "maturity_date", "last_update"] and isinstance(value, str):
                    value = parse_date(value)
                
                setattr(existing_product, key, value)
            
            # 设置最后更新日期
            existing_product.last_update = get_today()
            
            result["id"] = existing_product.id
        else:
            # 创建新产品
            product = Product()
            
            for key, value in product_data.items():
                # 跳过id和空值
                if key == "id" or value is None:
                    continue
                
                # 处理日期类型字段
                if key in ["establishment_date", "maturity_date", "last_update"] and isinstance(value, str):
                    value = parse_date(value)
                
                setattr(product, key, value)
            
            # 设置最后更新日期
            if not product.last_update:
                product.last_update = get_today()
            
            self.db.add(product)
            result["is_new"] = True
        
        try:
            self.db.commit()
            
            # 如果是新产品，获取新插入的ID
            if result["is_new"] and not result["id"]:
                result["id"] = self.db.query(Product).filter(
                    Product.product_code == product_data["product_code"]
                ).first().id
                
        except IntegrityError as e:
            self.db.rollback()
            print(f"保存产品 {product_data.get('product_code')} 时发生错误: {str(e)}")
        
        return result
    
    def save_daily_return(self, return_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存每日收益数据到数据库"""
        result = {"is_new": False, "id": None}
        
        # 检查必要字段
        if "product_code" not in return_data or not return_data["product_code"]:
            print("收益数据缺少产品代码，无法保存")
            return result
            
        if "date" not in return_data or not return_data["date"]:
            print("收益数据缺少日期，无法保存")
            return result
        
        # 将字符串日期转换为日期对象
        if isinstance(return_data["date"], str):
            return_data["date"] = parse_date(return_data["date"])
        
        # 查询产品ID
        product = self.db.query(Product).filter(
            Product.product_code == return_data["product_code"]
        ).first()
        
        if not product:
            print(f"找不到产品代码 {return_data['product_code']} 对应的产品，无法保存收益数据")
            return result
        
        # 设置产品ID
        return_data["product_id"] = product.id
        
        # 查询是否存在该收益记录
        existing_return = self.db.query(DailyReturn).filter(
            and_(
                DailyReturn.product_id == return_data["product_id"],
                DailyReturn.date == return_data["date"]
            )
        ).first()
        
        if existing_return:
            # 更新现有收益记录
            for key, value in return_data.items():
                # 跳过id和空值
                if key == "id" or value is None:
                    continue
                
                setattr(existing_return, key, value)
            
            result["id"] = existing_return.id
        else:
            # 创建新收益记录
            daily_return = DailyReturn()
            
            for key, value in return_data.items():
                # 跳过id和空值
                if key == "id" or value is None:
                    continue
                
                setattr(daily_return, key, value)
            
            self.db.add(daily_return)
            result["is_new"] = True
        
        try:
            self.db.commit()
            
            # 如果是新收益记录，获取新插入的ID
            if result["is_new"] and not result["id"]:
                result["id"] = self.db.query(DailyReturn).filter(
                    and_(
                        DailyReturn.product_id == return_data["product_id"],
                        DailyReturn.date == return_data["date"]
                    )
                ).first().id
                
        except IntegrityError as e:
            self.db.rollback()
            print(f"保存产品 {return_data.get('product_code')} 的收益数据时发生错误: {str(e)}")
        
        return result
    
    def close(self):
        """关闭数据库连接"""
        self.db.close() 