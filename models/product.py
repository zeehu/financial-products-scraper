from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class Product(Base):
    """理财产品模型"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, index=True, comment="产品代码")
    product_name = Column(String(100), index=True, comment="产品名称")
    company_name = Column(String(100), index=True, comment="理财公司名称")
    company_url = Column(String(255), comment="理财公司官网地址")
    product_type = Column(String(50), comment="产品类型")
    risk_level = Column(String(50), comment="风险等级")
    investment_horizon = Column(String(50), comment="投资期限")
    min_investment = Column(Float, comment="起投金额")
    expected_return = Column(Float, comment="预期收益率")
    actual_return = Column(Float, comment="实际收益率")
    status = Column(String(20), comment="产品状态(在售/停售)")
    establishment_date = Column(Date, comment="成立日期")
    maturity_date = Column(Date, comment="到期日期")
    description = Column(Text, comment="产品描述")
    details_url = Column(String(255), comment="产品详情页URL")
    last_update = Column(Date, comment="最后更新日期")
    
    # 建立与每日收益表的关系
    daily_returns = relationship("DailyReturn", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.product_code}: {self.product_name}>" 