# -*- coding: utf-8 -*-
import asyncio
import os
import threading
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
    s1=asyncio.run(getReply(text,model))
    return {"data": {"info":{"text":s1}}}

async def getReply(text,model):
    if model=="chatglm":
        return glmReply(text)
    elif model=="gpt":
        try:
            url = "https://api.lolimi.cn/API/AI/mfcat3.5.php?sx=你是一个可爱萝莉&msg="+text+"&type=json"
            async with httpx.AsyncClient(timeout=40) as client:
                # 用get方法发送请求
                response = await client.get(url=url)
            s=response.json().get("data")
            return s

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
def glmReply(text):

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
        model1=result.get("model")
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
    os.system("web\glm.html")
    app.run(debug=True,host='127.0.0.1', port=9081)

