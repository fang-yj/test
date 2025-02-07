#!/usr/bin/env python3
# coding    : utf-8
# @Time     : 2024.9.29
# @Author   : fang-yj

import os
import base64
import argparse
import random
import time
import re
import requests as req
from bs4 import BeautifulSoup
import json
from browser import Browser
from selenium.webdriver.common.by import By
from constants import desktopUserAgent

USER_AGENT = desktopUserAgent()

SEARCH_HEADER = {
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding':'gzip, deflate, br, zstd',
    'accept-language':'zh-CN,zh;q=0.9,en;q=0.8',
    'user-agent':USER_AGENT
}
ERROR_TIME = 0

def search_repo_names_through_fuzzy_users(fuzzy_users:list)->list:
    """
        通过模糊用户名搜索获取 v2ray 订阅发布作者
        参数:
            fuzzy_users: 模糊用户名列表
        返回:
            repo_names: 一个列表
    """
    repo_names = []
    for name in fuzzy_users:
        search_url = f'https://github.com/search?q={name}&type=users'
        resp = req.get(search_url,SEARCH_HEADER)
        print(resp)
        user = resp.get("payload").get("results")[0].get("login")
        print(user)
        return
        repo_names.append(search_repo_for_name(user))

    return repo_names

def search_repo_for_name(name:str) -> str:
    '''
        通过发布者用户名获取 v2ary 订阅发布的仓库地址
        参数:
            name : 发布者用户名
        返回:
            full_name: 返回仓库名字
    '''
    # 获取发布作者发布的仓库地址
    # https://api.github.com/users/mksshare/repos
    url = f'https://api.github.com/users/{name}/repos'
    resp = req.get(search_url,SEARCH_HEADER)
    return resp[0].get("full_name")

def search_repo_names_by_updated_desc(filter_words=[".github.io"])->list:
    """
        通过仓库更新时间获取仓库地址
        参数:
            filter_words: 查找包含制定字符的仓库地址
        返回:
            repo_names: 查找到的仓库名字
    """
    global ERROR_TIME
    url = "https://github.com/search?q=v2ray%E8%AE%A2%E9%98%85&type=repositories&s=updated&o=desc"
    resp = req.get(url,SEARCH_HEADER)
    # print(f"status_code:{resp.status_code}")
    repo_list = []
    # print(resp.status_code)
    if resp.status_code == 200:
        html_content = resp.text
        soup = BeautifulSoup(html_content,'html.parser')
        script_text = json.loads(soup.find('script', attrs={"data-target":"react-app.embeddedData"}).get_text())
        # print(f"script_text:{script_text}")
        repo_list = script_text.get("payload").get("results")
        # print(f"repo_list:{repo_list}")
    # elif ERROR_TIME < 2:
    #     ERROR_TIME += 1
    #     time.sleep(random.randint(15, 30))
    #     search_repo_names_by_updated_desc()
    else:
        return []
    repo_names = []
    for repo in repo_list:
        repo_name = repo.get("hl_name")
        # print(f"repo_name:{repo_name}")
        has_issues = repo.get("repo").get("repository").get("has_issues")
        if (any(filter_word in repo_name for filter_word in filter_words) 
            and len(repo_names)<3 
            and not has_issues):
            repo_names.append(repo_name)
    return repo_names

def repo_readme_to_v2ray_url(repo_names:list):
    """
        根据仓库名称获取readme.md，解析 readme.md 获取 v2ray 订阅链接，
        并将获取到的订阅信息保存到 v2ray.txt 中
        参数:
            repo_names: 仓库名称列表
    """
    if len(repo_names) != 0:
        saveFile(repo_names,"repo_names.txt")
    elif os.path.exists("repo_names.txt"):
        print("为查询到符合的仓库，使用备份的仓库名")
        repo_names = readFile("repo_names.txt")
    else:
        print("为查询到备份的仓库名，使用默认的仓库名")
        repo_names = ["abshare/abshare.github.io","tolinkshare2/tolinkshare2.github.io","mksshare/mksshare.github.io"]
    v2ray = ""
    with Browser(args=argumentParser()) as desktopBrowser:
        chrome = desktopBrowser.webdriver
        for repo_name in repo_names:
            time.sleep(random.randint(5, 10))
            url = f"https://raw.githubusercontent.com/{repo_name}/main/README.md"
            headers = {"accept": "application/vnd.github.v3+json",'user-agent':USER_AGENT}
            resp_text = req.get(url, headers).text
            # print(resp_text)
            str_index = find_occurrences_regex(resp_text,"```")
            # print(resp_text[str_index[2]+3:str_index[3]])
            # 获取需要的 url
            v2ray_url = resp_text[str_index[2]+3:str_index[3]-2]
            # 检查链接是否正确
            if "https://" not in v2ray_url:
                v2ray_url = v2ray_url.replace("https:/","https://")
            # 使用 chrome 访问
            print(v2ray_url)
            chrome.get(v2ray_url)
            time.sleep(3)
            v2ray_text = chrome.find_element(By.TAG_NAME,"body").text;
            # print(v2ray_text)
            if "403 Forbidden" in v2ray_text:
                print(f"{v2ray_url} 无法访问")
                continue
            v2ray += base64.b64decode(v2ray_text).decode("utf-8")
        # print(v2ray.split("\r\n"))
        desktopBrowser.closeBrowser()
    new_v2ray = v2ray.split("\r\n")
    print("保存文件")
    saveFile(new_v2ray,"v2ray.txt")
    # if os.path.exists("v2ray.txt"):
        # print("文件存在，判断要保存的内容是否更新，如果更新就保存")
        # old_v2ray = readFile("v2ray.txt")
        # if set(new_v2ray) != set(old_v2ray):
        #     print("数据发生变更，更新数据并保存")
        #     saveFile(new_v2ray,"v2ray.txt")
    # else:
    #     print("文件不存在，直接创建 v2ray.txt 并保存")
    #     saveFile(new_v2ray,"v2ray.txt")

def saveFile(data: list, file_name: str):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("\n".join(data))

def readFile(file_name: str) -> list:
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return eval(f.read())
    except:
        with open(file_name, 'r', encoding='utf-8') as f:
            return f.read().splitlines()

def find_occurrences_regex(text:str, pattern:str)->list:
    """
        到 text 查找 pattern 所有出现位置
        参数：
            text: 原始字符串
            pattern: 要查找的字符串
        返回：
            occurrences: pattern 所有出现位置
    """
    occurrences = [match.start() for match in re.finditer(pattern, text)]
    return occurrences

def argumentParser():
    parser = argparse.ArgumentParser(description="test")
    parser.add_argument(
        "-v", "--visible", action="store_true", help="Optional: Visible browser"
    )
    parser.add_argument(
        "-l", "--lang", type=str, default="zh", help="Optional: Language (ex: en)"
    )
    parser.add_argument(
        "-g", "--geo", type=str, default="CN", help="Optional: Geolocation (ex: US)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    fuzzy_users = ['tolinkshare','mksshare']
    # search_repo_names_through_fuzzy_users(fuzzy_users);
    repo_names = search_repo_names_by_updated_desc()
    repo_readme_to_v2ray_url(repo_names)
    # print(readFile("v2ray.txt"))
