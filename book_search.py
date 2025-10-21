# https://bqg123.net/

import requests
import time
import re
import os
import base64
from urllib.parse import unquote
import json

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
    "accept-language": 'zh-CN,zh;q=0.9',
    "referer": "https://bqg123.net/"
}


def string_to_json(json_string):
    """
    将JSON格式的字符串转换为Python对象（字典/列表）
    :param json_string: 包含JSON数据的字符串
    :return: 转换后的Python对象或错误信息
    """
    try:
        # 使用json.loads解析JSON字符串
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        return f"JSON解析错误: {str(e)}"
    except TypeError as e:
        return f"类型错误: {str(e)} - 请确保输入是字符串类型"


def decode_base64_url(encoded_str):
    try:
        # 先进行Base64解码
        base64_decoded = base64.b64decode(encoded_str)
        # 将Base64解码后的字节数据解码为UTF-8字符串
        base64_str = base64_decoded.decode('utf-8')
        # 再进行URL解码
        url_decoded = unquote(base64_str)
        return url_decoded
    except Exception as e:
        return f"解码失败: {str(e)}"

    # 测试用例


# 获取搜索小说的接口
def search_book(search_name):
    search_url = f"https://dmit.xsjs.cc/v3/search1?ws=2741536&pf=win32&keyword={search_name}"

    # data = {
    #     "ws":"2741536",
    #     "pf":"win32",
    #     "keyword":f"{search_name}"
    # }

    response = requests.get(search_url, headers=headers)
    book_list_base = re.findall(r'"(.*?)"', response.text)

    book_name_list = string_to_json(decode_base64_url(book_list_base[0]))
    return book_name_list


def get_book_url(search_name, book_name_list):
    book_name_list = search_book(search_name)
    count = 0
    book_name_dict = {}
    for i in range(len(book_name_list['book_list'])):
        all_book_data = book_name_list['book_list'][i]
        # print(all_book_data)
        # count_list.append(count)
        book_name_dict[f'{count}'] = {"book_name": f"{all_book_data['book_name']}",
                                      "author": f"{all_book_data['author']}",
                                      "book_uni_id": f"{all_book_data['book_uni_id']}",
                                      "book_id": f"{all_book_data['book_id']}"}
        count += 1
    return book_name_dict


def get_book(book_uni_id, book_id):
    # 两个接口
    # https://bv-jp.booktt.cc/v3/load_book_info/158714386/2545907.js?ws=2621536&tk=0404
    # https://dmit.xsjs.cc/v3/load_book_info/101373989/2158323.js?ws=2301536&tk=0404

    # print(book_uni_id,book_id)
    time.sleep(3)
    url = f"https://bv-jp.booktt.cc/v3/load_book_info/{book_uni_id}/{book_id}.js?ws=2621536&tk=0404"
    response = requests.get(url=url, headers=headers).text
    result = re.findall(']="(.*)";', response)[0]
    # print(result)
    zz_result = string_to_json(decode_base64_url(result))
    # print(zz_result)
    url2 = f"https://dmit.xsjs.cc/load_chapter_list/{zz_result['url_chapter_list_kv']}.js?t=2023030112391895800&tk=0404"
    time.sleep(3)
    response2 = requests.get(url=url2, headers=headers).text
    # print(response2)
    result2 = re.findall('chapter_list_data_str="(.*)";', response2)[0]
    # print(result2)
    zzresult2 = string_to_json(decode_base64_url(result2))
    return zzresult2


def download_book(book_name, baseurl,name):
    # print(book_name,baseurl,name)
    if not os.path.exists(book_name):
        os.makedirs(book_name)
        print(f"文件夹 '{book_name}' 已创建")
    else:
        pass
    url = f"https://dmit.xsjs.cc/load_chapter/{baseurl}.js?t=4306&tk=0404"
    response = requests.get(url, headers=headers).text
    # print(response)
    result = re.findall('chapter_data_str="(.*)";', response)[0]
    book_count = string_to_json(decode_base64_url(result))['chapter_kv']['content']
    # print(book_count)
    result2 = re.findall("<p>(.*)</p>",book_count)
    # print(result2)
    for i in result2:
        with open(f"{book_name}/{name}.txt", "a+", encoding="utf-8") as f:
            f.write(i + "\n")
    print(f"{name}下载完成！！！")

def main():
    search_name = input("请输入你想要找的的小说名：")
    book_name_dict = get_book_url(search_name, search_name)
    for i in range(len(book_name_dict)):
        # print(book_name_dict[f'{i}'])
        print(f"序号:{i},书名:{book_name_dict[f'{i}']['book_name']}，作者：{book_name_dict[f'{i}']['author']}")
    user_need = input("请输入你需要的小说序号：")
    book_toc = get_book(book_name_dict[user_need]['book_uni_id'], book_name_dict[user_need]['book_id'])
    book_toc_list = book_toc["chapter_list"]
    # print(book_toc_list)
    for i in book_toc_list:
        time.sleep(2)
        download_book(book_name_dict[user_need]['book_name'],i['url_kv'],i['name'])



if __name__ == '__main__':
    main()
