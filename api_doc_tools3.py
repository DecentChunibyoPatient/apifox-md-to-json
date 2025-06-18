import json
import os

openapi_json = '''
{
  "openapi": "3.0.1",
  "info": {
    "title": "",
    "description": "",
    "version": "1.0.0"
  },
  "paths": {
    "/circle/index/release": {
      "post": {
        "summary": "发布动态",
        "deprecated": false,
        "description": "",
        "tags": ["动态"],
        "parameters": [
          {
            "name": "pet_client_type",
            "in": "header",
            "description": "",
            "example": "PET_APP_CLIENT",
            "schema": {
              "type": "string",
              "default": "PET_APP_CLIENT"
            }
          },
          {
            "name": "Authorization",
            "in": "header",
            "description": "",
            "example": "{{Authorization}}",
            "schema": {
              "type": "string",
              "default": "{{Authorization}}"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "fileUrl": {"type": "string", "description": "上传的文件"},
                  "content": {"type": "string", "description": "内容"},
                  "coverUrl": {"type": "string", "description": "封面图"},
                  "cityId": {"type": "integer"},
                  "petTypeId": {"type": "integer", "description": "宠物类型id"}
                },
                "required": [
                  "petTypeId",
                  "fileUrl",
                  "content",
                  "coverUrl",
                  "cityId"
                ]
              }
            }
          }
        }
      }
    }
  }
}
'''


def to_camel_case(s):
    parts = s.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def java_type(openapi_type):
    mapping = {
        "string": "String",
        "integer": "int",
        "boolean": "boolean",
        "number": "double",
        "array": "List",
        "object": "Object"
    }
    return mapping.get(openapi_type, "String")

def generate_java_method(path, method, info):
    method_name = info.get("summary", "api").replace(" ", "")
    method_name = method_name[0].lower() + method_name[1:]

    # 请求头参数
    headers = info.get("parameters", [])
    header_params = [h for h in headers if h.get("in") == "header"]

    # 请求体参数
    request_body = info.get("requestBody", {})
    body_props = {}
    if request_body:
        content = request_body.get("content", {})
        app_json = content.get("application/json", {})
        schema = app_json.get("schema", {})
        body_props = schema.get("properties", {})

    params = []
    for h in header_params:
        param_name = to_camel_case(h["name"])
        params.append(f'String {param_name}')
    for prop, detail in body_props.items():
        jtype = java_type(detail.get("type", "string"))
        param_name = to_camel_case(prop)
        params.append(f'{jtype} {param_name}')

    param_str = ", ".join(params)

    json_body_lines = []
    for prop in body_props.keys():
        camel = to_camel_case(prop)
        json_body_lines.append(f'        "\\"{prop}\\": \\"" + {camel} + "\\","')

    # 最后一行不需要逗号
    if json_body_lines:
        json_body_lines[-1] = json_body_lines[-1].rstrip(',')

    json_body_str = '\n'.join(json_body_lines)

    code = f'''public void {method_name}({param_str}) throws IOException {{
    OkHttpClient client = new OkHttpClient();

    String jsonBody = "{{" + 
{json_body_str}
    + "}}";

    Request request = new Request.Builder()
        .url("https://xxxxxxxxxxxxx/prod-api{path}")
'''

    for h in header_params:
        name = h["name"]
        param_name = to_camel_case(name)
        code += f'        .addHeader("{name}", {param_name})\n'

    code += f'''        .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
        .build();

    Response response = client.newCall(request).execute();
    if (!response.isSuccessful()) throw new IOException("Unexpected code " + response);

    System.out.println(response.body().string());
}}
'''

    return code

if __name__ == "__main__":
    api = json.loads(openapi_json)
    for path, methods in api["paths"].items():
        for method, info in methods.items():
            java_code = generate_java_method(path, method, info)
            # 取第一个tag作为分类
            category = info.get("tags", ["default"])[0]
            method_name = info.get("summary", "api").replace(" ", "")
            # 创建目录
            dir_path = os.path.join("output", category)
            os.makedirs(dir_path, exist_ok=True)
            # 写文件
            file_path = os.path.join(dir_path, f"{method_name}.java")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(java_code)
            print(f"已保存：{file_path}")
