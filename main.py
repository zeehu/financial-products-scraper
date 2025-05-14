#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import time
from typing import List, Dict

from models.database import init_db
from models.data_processor import DataProcessor
from scrapers.webank_scraper import WeBankScraper
from scrapers.icbc_scraper import ICBCScraper


def get_partners():
    """获取合作伙伴列表"""
    webank_scraper = WeBankScraper()
    partners = webank_scraper.get_partners()
    return partners


def init_scrapers():
    """初始化所有爬虫"""
    scrapers = [
        ICBCScraper(),
        # 添加更多爬虫...
    ]
    return scrapers


def run_specific_scraper(scraper_name: str, max_products: int = None):
    """运行指定名称的爬虫"""
    scrapers = init_scrapers()
    found = False
    
    for scraper in scrapers:
        if scraper.company_name == scraper_name:
            print(f"开始运行 {scraper_name} 爬虫...")
            data = scraper.run(max_products)
            
            # 保存数据到数据库
            processor = DataProcessor()
            results = processor.process_data(data)
            processor.close()
            
            print_results(results)
            found = True
            break
    
    if not found:
        print(f"未找到名为 {scraper_name} 的爬虫")


def run_all_scrapers(max_products: int = None):
    """运行所有爬虫"""
    scrapers = init_scrapers()
    all_results = []
    
    for scraper in scrapers:
        print(f"开始运行 {scraper.company_name} 爬虫...")
        data = scraper.run(max_products)
        
        # 保存数据到数据库
        processor = DataProcessor()
        results = processor.process_data(data)
        processor.close()
        
        all_results.append(results)
    
    # 打印总结果
    print("\n所有爬虫运行完成，总结:")
    for result in all_results:
        print_results(result)


def print_results(results: Dict):
    """打印爬虫结果"""
    print(f"\n{results['company_name']} 爬虫结果:")
    print(f"  产品总数: {results['products_count']}")
    print(f"  新增产品: {results['products_new']}")
    print(f"  更新产品: {results['products_updated']}")
    print(f"  收益记录总数: {results['returns_count']}")
    print(f"  新增收益记录: {results['returns_new']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='理财产品信息抓取系统')
    parser.add_argument('--list-partners', action='store_true', help='列出所有合作伙伴')
    parser.add_argument('--company', help='指定要抓取的理财公司名称')
    parser.add_argument('--all', action='store_true', help='抓取所有已实现爬虫的理财公司数据')
    parser.add_argument('--max-products', type=int, help='每个公司最多抓取的产品数量')
    parser.add_argument('--init-db', action='store_true', help='初始化数据库')
    
    args = parser.parse_args()
    
    # 初始化数据库
    if args.init_db:
        print("正在初始化数据库...")
        init_db()
        print("数据库初始化完成")
        return
    
    # 列出合作伙伴
    if args.list_partners:
        partners = get_partners()
        print(f"共找到 {len(partners)} 个合作伙伴:")
        for i, partner in enumerate(partners):
            print(f"{i+1}. {partner['name']} - {partner['url']}")
        return
    
    # 运行指定公司爬虫
    if args.company:
        run_specific_scraper(args.company, args.max_products)
        return
    
    # 运行所有爬虫
    if args.all:
        run_all_scrapers(args.max_products)
        return
    
    # 如果没有指定任何操作，显示帮助信息
    parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序发生错误: {str(e)}")
        sys.exit(1)
