import re
import yaml
import json

def extract_yaml_from_md(md_text):
    # 正则匹配 ```yaml ... ```
    pattern = r"```yaml(.*?)```"
    matches = re.findall(pattern, md_text, re.DOTALL)
    return matches[0].strip() if matches else None

def yaml_to_json(yaml_str):
    data = yaml.safe_load(yaml_str)
    return json.dumps(data, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    with open("267659047e0.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    yaml_str = extract_yaml_from_md(md_text)
    if yaml_str:
        json_str = yaml_to_json(yaml_str)
        print(json_str)
        # 如果想保存到文件：
        with open("openapi.json", "w", encoding="utf-8") as f_out:
            f_out.write(json_str)
    else:
        print("没找到yaml代码块")
