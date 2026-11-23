#!/usr/bin/env python3
"""
create_preset_voices.py - 使用 Edge-TTS 自動生成高品質精選聲音包至 voices/ 目錄。
包含：甜美女聲、沉穩男聲、電台主播、可愛女童、活潑男童等。
"""

import os
import sys
import asyncio
import tempfile
import time
import numpy as np
import soundfile as sf
import resampy
import edge_tts

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RATE = 16000

PRESET_VOICES = [
    {
        "name": "可愛女童",
        "voice_id": "zh-CN-XiaoyiNeural",
        "desc": "可愛小女孩（小藝），天真爛漫、童趣清脆",
        "text": "哈囉！你好呀！你看我今天抓到一隻好漂亮的彩色蝴蝶耶，要不要跟我一起去公園玩捉迷藏？"
    },
    {
        "name": "活潑男童",
        "voice_id": "zh-CN-YunxiaNeural",
        "desc": "調皮小男孩（雲夏），活潑元氣、熱情好動",
        "text": "耶！放假囉！今天我要跟爸爸媽媽去遊樂園玩旋轉木馬跟吃冰淇淋，真是太開心了！"
    },
    {
        "name": "甜美女聲",
        "voice_id": "zh-TW-HsiaoChenNeural",
        "desc": "台灣女聲（曉臻），甜美清澈、活潑親切",
        "text": "哈囉大家，今天心情怎麼樣呢？很高興能在這裡跟大家聊天，希望今天為大家帶來滿滿的活力與好心情喔！"
    },
    {
        "name": "陽光男聲",
        "voice_id": "zh-TW-YunJheNeural",
        "desc": "台灣男聲（雲哲），陽光自然、溫暖熱情",
        "text": "哈囉各位朋友！今天又是充滿活力的一天，無論面對什麼樣的挑戰，保持微笑、全力以赴就對了！"
    },
    {
        "name": "氣質女聲",
        "voice_id": "zh-CN-XiaoxiaoNeural",
        "desc": "新聞與旁白（曉曉），知性溫雅、咬字清晰",
        "text": "生活中的美好，往往藏在那些不經意的細節裡。靜下心來聆聽世界的聲音，總能發現許多溫暖與感動。"
    },
    {
        "name": "沉穩男聲",
        "voice_id": "zh-CN-YunxiNeural",
        "desc": "敘事與影評（雲希），低沉磁性、故事感強",
        "text": "歲月流轉，唯有真實的沉澱能夠經得起時間的考驗。在繁忙的世界中，保持專注，走好自己的每一步。"
    },
    {
        "name": "電台主播",
        "voice_id": "zh-CN-YunyangNeural",
        "desc": "專業播音（雲揚），沉著有力、大氣專業",
        "text": "各位聽眾朋友晚安，歡迎收聽今晚的特別專欄。在這個寧靜的時刻，讓我們一起回顧今日的重點要聞與精選故事。"
    },
    {
        "name": "溫柔姐姐",
        "voice_id": "zh-TW-HsiaoYuNeural",
        "desc": "台灣女聲（曉涵），柔和溫暖、舒緩療癒",
        "text": "夜深了，輕輕閉上雙眼，放下今天所有的疲憊與思緒。給自己一杯熱茶的時間，靜靜享受這份安寧吧。"
    }
]


async def generate_voice(preset, max_retries=3):
    name = preset["name"]
    voice_id = preset["voice_id"]
    text = preset["text"]
    desc = preset["desc"]

    print(f"[*] 正在生成「{name}」({desc})...")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        temp_mp3 = tf.name

    try:
        success = False
        for attempt in range(1, max_retries + 1):
            try:
                communicate = edge_tts.Communicate(text=text, voice=voice_id)
                await communicate.save(temp_mp3)
                success = True
                break
            except Exception as e:
                print(f"    [!] 第 {attempt} 次嘗試失敗 ({e})，正在重試...")
                await asyncio.sleep(1.5)

        if not success:
            raise RuntimeError(f"連續 {max_retries} 次嘗試生成失敗")

        audio, sr = sf.read(temp_mp3)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        if sr != SAMPLE_RATE:
            audio = resampy.resample(audio, sr, SAMPLE_RATE)

        peak = np.abs(audio).max()
        if peak > 0:
            audio = audio / peak * 0.95

        vdir = os.path.join(REPO_DIR, "voices", name)
        os.makedirs(vdir, exist_ok=True)

        wav_path = os.path.join(vdir, "ref_voice.wav")
        prompt_path = os.path.join(vdir, "prompt.txt")

        sf.write(wav_path, audio.astype(np.float32), SAMPLE_RATE)
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(text)

        duration = len(audio) / SAMPLE_RATE
        print(f"    [+] 完成！長度: {duration:.1f}s，已存入 voices/{name}/")
    finally:
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)


async def main():
    print("========================================")
    print("  VoxCPM2 精選聲音包生成中...")
    print("========================================")
    for preset in PRESET_VOICES:
        await generate_voice(preset)
        await asyncio.sleep(0.5)

    print("\n所有精選聲音已全部成功加入 voices/ 目錄！")


if __name__ == "__main__":
    asyncio.run(main())
