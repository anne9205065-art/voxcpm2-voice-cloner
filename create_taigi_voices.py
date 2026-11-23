#!/usr/bin/env python3
"""
create_taigi_voices.py - 生成高品質正宗臺灣台語聲音包（女聲、男聲、兒童童音）
"""

import os
import sys
import io
import requests
import soundfile as sf
import librosa
import numpy as np

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RATE = 16000

API_URL = "https://learn-language.tokyo/taigiTTS/taigi-text-to-speech"
API_HEADERS = {
    "content-type": "application/json",
    "origin": "https://learn-language.tokyo",
}

TAIGI_PRESETS = [
    {
        "name": "台語甜美女聲",
        "desc": "正宗台灣台語女聲，甜美溫柔、清澈親切",
        "text": "逐家好！真歡喜會當佇遮佮逐家開講，祝逐家逐工攏有元氣佮好心情喔！",
        "model": "model6",
        "pitch_shift": 0.0,
    },
    {
        "name": "台語沉穩男聲",
        "desc": "正宗台灣台語男聲，沉穩厚實、鄉土磁性",
        "text": "逐家平安。人生親像一條路，沓沓仔行，生活就會順利。祝各位朋友闔家平安。",
        "model": "model6",
        "pitch_shift": -5.5,
    },
    {
        "name": "台語可愛童音",
        "desc": "正宗台灣台語兒童，天真活潑、童趣清脆",
        "text": "阿公阿媽逐家好！你看我今仔日佇學校有提著大紅包喔，我欲招阿兄做伙去公園看水鴨！",
        "model": "model6",
        "pitch_shift": 5.0,
    },
]


def generate_voice(preset):
    name = preset["name"]
    desc = preset["desc"]
    text = preset["text"]
    model = preset["model"]
    shift = preset["pitch_shift"]

    print(f"[*] 正在生成【{name}】({desc})...")
    payload = {"text": text, "model": model}
    res = requests.post(API_URL, json=payload, headers=API_HEADERS, timeout=40)
    res.raise_for_status()
    data = res.json()

    audio_url = data.get("audio_url")
    if not audio_url:
        raise ValueError(f"取得【{name}】音檔網址失敗")

    raw_audio = requests.get(audio_url, timeout=30).content
    audio, sr = sf.read(io.BytesIO(raw_audio))

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    if shift != 0.0:
        audio = librosa.effects.pitch_shift(audio, sr=sr, n_steps=shift)

    if sr != SAMPLE_RATE:
        import resampy
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
    print(f"    [+] 【{name}】建立成功！長度: {duration:.1f}s，已存入 voices/{name}/")


def main():
    print("========================================")
    print("  正宗臺灣台語聲音包生成中...")
    print("========================================")
    for p in TAIGI_PRESETS:
        generate_voice(p)
    print("\n所有台語聲音已成功建置至 voices/ 目錄！")


if __name__ == "__main__":
    main()
