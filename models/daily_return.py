from sqlalchemy import Column, Integer, Float, Date, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class DailyReturn(Base):
    """理财产品每日收益模型"""
    __tablename__ = "daily_returns"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    product_code = Column(String(50), index=True)
    date = Column(Date, index=True, comment="收益日期")
    unit_net_value = Column(Float, comment="单位净值")
    cumulative_net_value = Column(Float, comment="累计净值")
    daily_return_rate = Column(Float, comment="日收益率(%)")
    seven_day_annualized = Column(Float, comment="7日年化收益率(%)")
    
    # 建立与产品表的关系
    product = relationship("Product", back_populates="daily_returns")
    
    def __repr__(self):
        return f"<DailyReturn {self.product_code}: {self.date} - {self.daily_return_rate}%>"