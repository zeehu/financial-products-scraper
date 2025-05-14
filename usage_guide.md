# 理财产品信息抓取系统使用指南

## 安装

1. 克隆项目
```bash
git clone https://your-repository-url/financial_products_scraper.git
cd financial_products_scraper
```

2. 安装依赖包
```bash
pip install -r requirements.txt
```

## 使用方法

### 初始化数据库

在首次使用前，需要初始化数据库：

```bash
python -m financial_products_scraper.main --init-db
```

### 列出微众银行合作伙伴

查看所有可用的理财公司合作伙伴：

```bash
python -m financial_products_scraper.main --list-partners
```

### 抓取指定公司的数据

指定要抓取的理财公司名称：

```bash
python -m financial_products_scraper.main --company "工商银行融e行"
```

限制最多抓取的产品数量（如仅抓取5个产品用于测试）：

```bash
python -m financial_products_scraper.main --company "工商银行融e行" --max-products 5
```

### 抓取所有已实现爬虫的公司数据

```bash
python -m financial_products_scraper.main --all
```

限制每个公司最多抓取的产品数量：

```bash
python -m financial_products_scraper.main --all --max-products 10
```

## 数据库查询示例

以下是一些SQLite查询示例，可以通过SQLite命令行工具或图形界面工具（如DB Browser for SQLite）执行：

### 查询所有产品

```sql
SELECT * FROM products;
```

### 查询某公司的所有产品

```sql
SELECT * FROM products WHERE company_name = '工商银行融e行';
```

### 查询某产品的所有收益记录

```sql
SELECT * FROM daily_returns WHERE product_code = 'PRODUCT_CODE';
```

### 查询最近7天的平均收益率排名前10的产品

```sql
SELECT p.product_name, p.company_name, AVG(d.daily_return_rate) as avg_return
FROM daily_returns d
JOIN products p ON d.product_id = p.id
WHERE d.date >= date('now', '-7 days')
GROUP BY d.product_id
ORDER BY avg_return DESC
LIMIT 10;
```

## 添加新的理财公司爬虫

若要添加新的理财公司爬虫，需要执行以下步骤：

1. 在`scrapers`目录下创建新的爬虫类文件，例如`xyz_scraper.py`
2. 继承`BaseScraper`类并实现所需的方法
3. 在`main.py`的`init_scrapers`函数中添加新爬虫的实例

示例：

```python
# 在 xyz_scraper.py 中
from .base_scraper import BaseScraper

class XYZScraper(BaseScraper):
    def __init__(self):
        super().__init__("XYZ理财", "https://xyz.com")
        
    def get_product_list(self):
        # 实现获取产品列表的代码
        pass
        
    def get_product_details(self, product_url):
        # 实现获取产品详情的代码
        pass
        
    def get_product_returns(self, product_code, days=30):
        # 实现获取产品收益信息的代码
        pass
```

```python
# 在 main.py 的 init_scrapers 函数中添加
from scrapers.xyz_scraper import XYZScraper

def init_scrapers():
    scrapers = [
        ICBCScraper(),
        XYZScraper(),  # 添加新的爬虫
        # 添加更多爬虫...
    ]
    return scrapers
```

## 注意事项

- 爬取数据时请遵守网站的robots.txt协议
- 适当控制爬取频率，避免对目标网站造成压力
- 某些理财公司网站可能需要登录才能访问数据，需要额外处理
- 网站结构可能随时变化，爬虫代码可能需要相应更新 