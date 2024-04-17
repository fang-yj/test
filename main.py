#!/usr/bin/env python3
# coding    : utf-8
# @Time     : 2024.3.5
# @Author   : fang-yj

import re
import requests
import json

if __name__ == "__main__":
    url = "https://raw.githubusercontent.com/tolinkshare/freenode/main/README.md"
    headers = {"accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers)
    content = str(resp.content)
    # r = data[10:-5]
    r = re.findall(r"vmess(.*?)```",content)
    data = "vmess" + r[0][:-4]
    # print(list(data.split(r"\n")))
    list_data = list(data.split(r"\n"))
    with open("v2ray.txt","w",encoding="utf-8") as f:
        f.write("\n".join(list_data[0:len(list_data)-8])[0:-2])
