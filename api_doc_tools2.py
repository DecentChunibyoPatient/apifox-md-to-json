import re
import requests
import yaml
import json
import os
from urllib.parse import urlparse

def download_text(url):
    resp = requests.get(url, proxies={})  # proxies={} 禁用代理
    resp.raise_for_status()
    return resp.text

def extract_urls(markdown_text):
    pattern = r'\[.*?\]\((https?://[^\s)]+\.md)\)'
    return re.findall(pattern, markdown_text)
def extract_name_and_url(markdown_text):
    # 匹配类似：- 用户 [用户登录](https://apifox.com/...)
    pattern = r'-\s*[^[]*\[([^\]]+)\]\((https?://[^\s)]+\.md)\)'
    return re.findall(pattern, markdown_text)
def extract_category_and_name(markdown_text):
    # 匹配格式：- 分类 [接口名](URL)
    pattern = r'-\s*([^ ]+)\s*\[([^\]]+)\]\((https?://[^\s)]+\.md)\)'
    matches = re.findall(pattern, markdown_text)
    # 返回： [(分类, 接口名, URL), ...]
    return matches
def extract_yaml_from_md(md_text):
    pattern = r"```yaml(.*?)```"
    matches = re.findall(pattern, md_text, re.DOTALL)
    return matches[0].strip() if matches else None

def yaml_to_json(yaml_str):
    data = yaml.safe_load(yaml_str)
    return json.dumps(data, indent=2, ensure_ascii=False)

def guess_filename(url):
    path = urlparse(url).path
    fname = os.path.basename(path)
    if fname.endswith(".md"):
        fname = fname[:-3]
    return fname + ".json"

def main(markdown_index_url):
    print(f"开始下载索引文件：{markdown_index_url}")
    index_md = download_text(markdown_index_url)
    urls = extract_category_and_name(index_md)
    print(f"提取到 {len(urls)} 个接口文档链接")

    os.makedirs("output", exist_ok=True)

    for category,name, url in urls:
        print(f"下载并解析接口文档：{url}")
        try:
            md = download_text(url)
            yaml_str = extract_yaml_from_md(md)
            if not yaml_str:
                print(f"⚠️ 未找到yaml代码块，跳过：{url}")
                continue
            json_str = yaml_to_json(yaml_str)
            filename = guess_filename(url)
            filepath = os.path.join(f"output/{category}",f"{name}_{filename}" )
            # 先构造目录路径
            dir_path = os.path.join("output", category)
            # 判断目录是否存在，不存在就创建
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"✅ 保存成功：{filepath}")
        except Exception as e:
            print(f"❌ 失败：{url}，错误：{e}")

if __name__ == "__main__":
    # 这里填入你的索引Markdown URL
    markdown_index_url = "https://apifox.com/xxxxxxxxxxxx/llms.txt"
    main(markdown_index_url)
