# -*- coding: utf-8 -*-
import asyncio
import os
import threading
import webbrowser
from asyncio import sleep


import asyncio
import json

import httpx as httpx
import zhipuai
import yaml
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
@app.route('/', methods=['GET'])
@cross_origin()
def synthesize():
    text=request.values.get("text")
    model = request.values.get("model")
    # 解析请求中的参数
    print(text)
    s1=asyncio.run(getReply(text,model))
    return {"data": {"info":{"text":s1}}}

async def getReply(text,model):
    if text=="/refresh":
        with open('data/id.yaml', 'r', encoding='utf-8') as f:
            result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
        result0["gpt1"]=None
        result0["gpt2"] = None
        with open('data/id.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(result0, file, allow_unicode=True)

    if "glm" in model:
        return glmReply(model,text)
    elif model=="gpt1":
        try:
            with open('data/id.yaml', 'r', encoding='utf-8') as f:
                result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
            try:
                id=result2.get("gpt1")
            except:
                id=None
            if id != None:
                url = "https://api.vkeys.cn/API/gpt?msg=" + text + "&session_id=" + id
            else:
                url = "https://api.vkeys.cn/API/gpt?msg=" + text
            async with httpx.AsyncClient(timeout=100) as client:  # 100s超时
                r = await client.get(url)  # 发起请求
                id=r.json().get("session_id")
                result2["gpt1"] = id
                with open('data/id.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(result2, file, allow_unicode=True)
            return r.json().get("data").get("content"),  # 返回结果
        except:
            return "无法连接到gpt3.5，请检查网络或重试"
    elif model=="gpt2":
        try:
            with open('data/id.yaml', 'r', encoding='utf-8') as f:
                result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
            try:
                id=result1.get("gpt2")
            except:
                id=None
            if id != None:
                url = "https://ybapi.cn/API/gpt.php?type=1&msg=" + text + "&id=" + id
            else:
                url = "https://ybapi.cn/API/gpt.php?type=1&msg=" + text
            async with httpx.AsyncClient(timeout=100) as client:  # 100s超时
                r = await client.get(url)  # 发起请求
                id=r.json().get("id")
                result1["gpt2"]=id
            with open('data/id.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(result1, file, allow_unicode=True)
            return r.json().get("text") # 返回结果

        except:
            return "无法连接到gpt3.5，请检查网络或重试"
    elif model=="xh":
        try:
            url = "https://api.lolimi.cn/API/AI/xh.php?msg=" + text
            async with httpx.AsyncClient(timeout=40) as client:
                # 用get方法发送请求
                response = await client.get(url=url)
            s = response.json().get("data").get("output")

            return s
        except:
            return "无法连接到讯飞星火，请检查网络或重试"
    elif model == "wx":
        try:
            url = "https://api.lolimi.cn/API/AI/wx.php?msg=" + text
            async with httpx.AsyncClient(timeout=40) as client:
            # 用get方法发送请求
                response = await client.get(url=url)
            s = response.json().get("data").get("output")
            return s
        except:
            return "调用文心一言失败，请检查网络或重试"
    elif model=="rwkv":
        try:
            with open('config/config.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            rwkvPort=result.get("rwkvPort")
            url = "http://127.0.0.1:"+rwkvPort+"/chat/completions"
            async with httpx.AsyncClient(timeout=100) as client:
                data = {"messages": [{"role": "user", "content": text}], "model": "rwkv", "stream": False,
                        "max_tokens": 1000, "temperature": 1.2, "top_p": 0.5, "presence_penalty": 0.4,
                        "frequency_penalty": 0.4}
                r = await client.post(url, json=data)
                return r.json().get('choices')[0].get("message").get("content")
        except:
            return "无法连接到本地rwkv语音模型，请检查端口配置"
    else:
        return "暂未支持该模型，请等待更新"
def glmReply(model,text):

    print("user:" + text)
    if text=="/clear":
        prompt=[{"content": "你好","role": "user"},{"content": "早上好，今天过得怎么样","role": "assistant"}]
        with open('data/data.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(prompt, file, allow_unicode=True)
        str1="清理完成"
    else:

        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)
        zhipuai.api_key = result.get("apiKey")
        model1=model
        bot_info=result.get("bot_info")
        with open('data/data.yaml', 'r', encoding='utf-8') as f:
            result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
        prompt = result1
        prompt.append({"role": "user","content":text})

        print("当前模式:" + model1)

        if model1 == "chatglm_pro":
            response = zhipuai.model_api.sse_invoke(
                model="chatglm_pro",
                prompt=prompt,
                temperature=0.95,
                top_p=0.7,
                incremental=True
            )
        elif model1 == "chatglm_std":
            response = zhipuai.model_api.sse_invoke(
                model="chatglm_std",
                prompt=prompt,
                temperature=0.95,
                top_p=0.7,
                incremental=True
            )
        elif model1 == "chatglm_lite":
            response = zhipuai.model_api.sse_invoke(
                model="chatglm_lite",
                prompt=prompt,
                temperature=0.95,
                top_p=0.7,
            )
        else:
            response = zhipuai.model_api.sse_invoke(
                model="characterglm",
                meta=bot_info,
                prompt=prompt,
                incremental=True
            )

        str1=""
        for event in response.events():
          if event.event == "add":
              str1+=event.data
              #print(event.data)
          elif event.event == "error" or event.event == "interrupted":
              str1 += event.data
              #print(event.data)
          elif event.event == "finish":
              str1 += event.data
              #print(event.data)
              print(event.meta)
          else:
              str1 += event.data
              #print(event.data)
        #print(str1)
        prompt.append({"role": "assistant","content":str1})
    print("chatGLM:"+str1)
    with open('data/data.yaml', 'w', encoding="utf-8") as file:
        yaml.dump(prompt, file, allow_unicode=True)
    return str1

if __name__ == '__main__':

    webbrowser.open(os.getcwd()+"/web/gml.html")
    app.run(debug=True,host='127.0.0.1', port=9088)

