import scrapy
import json
import brotli

class HrinfodataspiderSpider(scrapy.Spider):
    name = "HrinfoDataSpider"
    allowed_domains = ["hr.163.com"]
    start_urls = ["https://hr.163.com/job-list.html"]






    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.post_query,
            dont_filter=True
    )

    def post_query(self, response):
        url = "https://hr.163.com/api/hr163/position/queryPage"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "authtype": "ursAuth",
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "hr.163.com",
            "language": "zh",
            "Origin": "https://hr.163.com",
            "Referer": "https://hr.163.com/job-list.html",
            "x-ehr-uuid": "9c3cd241-878a-476a-986e-759d8ec5b8",
        }
        for i in range(2,5):
            body = json.dumps({
                "currentPage": i    ,
                "pageSize": 10
            })

            yield scrapy.Request(
                url=url,
                method="POST",
                headers=headers,
                body=body,
                callback=self.parse_result,
                meta = {"page": i}

            )

    def parse_result(self, response):
        try:
            # 关键修复：解压 br 压缩内容
            if response.headers.get('Content-Encoding') == b'br':
                decompressed = brotli.decompress(response.body)
                data = json.loads(decompressed)
            else:
                data = json.loads(response.text)

            self.logger.info(f"✅ 接口返回成功：code={data.get('code')}")

            job_list = data.get("data", {}).get("list", [])
            self.logger.info(f"✅ 成功获取到 {len(job_list)} 条岗位数据")

            for job in job_list:
                yield {
                    "职位ID": job.get("id"),
                    "职位名称": job.get("name"),
                    "部门": job.get("firstDepName"),
                    "产品线": job.get("productName"),
                    "工作地点": job.get("workPlaceNameList", [None])[0],
                    "学历要求": job.get("reqEducationName"),
                    "工作经验": job.get("reqWorkYearsName"),
                    "招聘人数": job.get("recruitNum"),
                    "职位类型": job.get("firstPostTypeName"),
                    "岗位职责": job.get("description"),
                    "任职要求": job.get("requirement"),
                }

        except Exception as e:
            self.logger.error(f"解析失败：{str(e)}")
            self.logger.error(f"返回内容：{response.body[:200]}")


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute("scrapy crawl HrinfoDataSpider".split())