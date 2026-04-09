# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import os
import csv
import pymysql



class HrinfoPipeline:
    def __init__(self):
        self.csv_file = None
        self.csv_writer = None
        self.db = None
        self.cursor = None

    def open_spider(self, spider):
        if spider.name != "HrinfoDataSpider":
            return
        self.download_path  = os.getcwd()+'/downloads'
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        csv_path =os.path.join(self.download_path, 'HrinfoDataSpider.csv')
        self.csv_file = open(csv_path, 'w', newline='',encoding='utf-8')
        #self.csv_file = os.path.join(self.download_path, "HrinfoDataSpider.csv")
        self.csv_writer = csv.DictWriter(self.csv_file,fieldnames=['职位ID','职位名称','部门','产品线','工作地点','学历要求','工作经验','招聘人数','职位类型','岗位职责','任职要求'])
        self.csv_writer.writeheader()
        self.db = pymysql.connect(
            host='localhost',
            user='root',
            password='a2832988438',
            db='Hrinfo',
            charset='utf8mb4'
        )
        self.cursor = self.db.cursor()
        create_sql = '''
                        CREATE TABLE IF NOT EXISTS jobs (
                            id INT PRIMARY KEY AUTO_INCREMENT,
                            job_id VARCHAR(50),
                            name VARCHAR(255),
                            department VARCHAR(255),
                            product VARCHAR(255),
                            location VARCHAR(100),
                            education VARCHAR(50),
                            experience VARCHAR(50),
                            recruit_num INT,
                            post_type VARCHAR(100),
                            description TEXT,
                            requirement TEXT
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    '''


    def process_item(self, item, spider):
        if spider.name != "HrinfoDataSpider":
            return item
        try:
            self.csv_writer.writerow(item)
        except Exception as e:
            print("写入csv失败",e)
        try:
            sql = '''
                    INSERT INTO jobs (
                    job_id, name, department, product, location,
                    education, experience, recruit_num, post_type,
                    description, requirement
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            
            '''
            self.cursor.execute(sql, (
                item.get('职位ID'),
                item.get('职位名称'),
                item.get('部门'),
                item.get('产品线'),
                item.get('工作地点'),
                item.get('学历要求'),
                item.get('工作经验'),
                item.get('招聘人数'),
                item.get('职位类型'),
                item.get('岗位职责'),
                item.get('任职要求')
            ))
            self.db.commit()
            print(f"✅ 已保存：{item.get('职位名称')}")


        except Exception as e:

            print("❌ 保存失败：", e)

            self.db.rollback()

        return item
    def close_spider(self, spider):
        if self.csv_file:
            self.csv_file.close()
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()
        print("✅ 爬虫结束 → 文件与数据库已关闭")
