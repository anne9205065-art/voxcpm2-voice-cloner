#!/usr/bin/env python3
"""
對話生成 — 三師爸與三帥媽的閒聊
模型只載入一次，逐句切換聲音生成，最後拼接成完整對話。
"""
from voxcpm import VoxCPM
import os
import sys
import time
import argparse
import numpy as np
import soundfile as sf
from voxcpm import VoxCPM
from clone import detect_device

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# 對話腳本：(說話者, 文字)
dialogue = [
    ("三帥媽", "嘿，你今天怎麼這麼晚才回來？"),
    ("三師爸", "喔，剛剛在弄一個 AI 語音的東西，搞到忘記時間了。"),
    ("三帥媽", "AI 語音？就是那個可以模仿別人聲音的嗎？"),
    ("三師爸", "對啊，叫 VoxCPM2，開源的，還可以商用。"),
    ("三帥媽", "聽起來很厲害耶，那它有辦法模仿我的聲音嗎？"),
    ("三師爸", "已經模仿了啊，你現在聽到的就是你的聲音。"),
    ("三帥媽", "哇，真的假的！那我以後是不是不用自己錄音了？"),
    ("三師爸", "哈，理論上是啦，但還是真人講的比較有感情啦。"),
]

def load_voice(voice_name):
    """讀取指定聲音的參考音與逐字稿。"""
    voice_dir = os.path.join(REPO_DIR, "voices", voice_name)
    ref_wav = os.path.join(voice_dir, "ref_voice.wav")
    prompt_file = os.path.join(voice_dir, "prompt.txt")
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_text = f.read().strip()
    return ref_wav, prompt_text

def main():
    parser = argparse.ArgumentParser(description="多聲音對話生成")
    parser.add_argument("--a", help="說話者 A 的聲音名稱")
    parser.add_argument("--b", help="說話者 B 的聲音名稱")
    parser.add_argument("--device", "-d", help="強制指定裝置 (cuda/xpu/cpu)")
    args = parser.parse_args()

    # 取得可用聲音
    vdir = os.path.join(REPO_DIR, "voices")
    available_voices = []
    if os.path.exists(vdir):
        available_voices = [
            d for d in os.listdir(vdir)
            if os.path.isdir(os.path.join(vdir, d))
            and os.path.exists(os.path.join(vdir, d, "ref_voice.wav"))
        ]

    speaker_a = args.a
    speaker_b = args.b

    if not speaker_a:
        speaker_a = available_voices[0] if len(available_voices) > 0 else "三師爸"
    if not speaker_b:
        speaker_b = available_voices[1] if len(available_voices) > 1 else ("三帥媽" if speaker_a != "三帥媽" else "三師爸")

    device = args.device or detect_device()

    print(f"裝置: {device}")
    print(f"說話者 A: {speaker_a}")
    print(f"說話者 B: {speaker_b}")
    print("載入 VoxCPM2 模型...")
    t0 = time.time()
    model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, device=device, optimize=False)
    print(f"模型載入完成，耗時 {time.time()-t0:.1f}s\n")

    # 預載兩個聲音的參考資料
    voices = {}
    for name in [speaker_a, speaker_b]:
        try:
            voices[name] = load_voice(name)
            print(f"  已載入聲音: {name}")
        except Exception as e:
            print(f"錯誤：載入聲音「{name}」失敗：{e}")
            sys.exit(1)

    print(f"\n開始生成對話（{len(dialogue)} 句）...\n")

    clips = []
    for i, (speaker_role, text) in enumerate(dialogue, 1):
        # 角色對應到實際聲音
        actual_speaker = speaker_a if i % 2 == 1 else speaker_b
        ref_wav, prompt_text = voices[actual_speaker]
        print(f"[{i}/{len(dialogue)}] {actual_speaker}: {text}")

        t1 = time.time()
        wav = model.generate(
            text=text,
            prompt_wav_path=ref_wav,
            prompt_text=prompt_text,
            reference_wav_path=ref_wav,
            cfg_value=1.5,
            inference_timesteps=10,
        )
        elapsed = time.time() - t1
        duration = len(wav) / model.tts_model.sample_rate
        print(f"        -> {duration:.1f}s ({elapsed:.1f}s)")

        # 句子之間加 0.4 秒停頓
        pause = np.zeros(int(0.4 * model.tts_model.sample_rate), dtype=wav.dtype)
        clips.append(wav)
        clips.append(pause)

    # 拼接所有片段
    full_audio = np.concatenate(clips)
    total_duration = len(full_audio) / model.tts_model.sample_rate
    output_path = os.path.join(REPO_DIR, "output", f"dialogue_{speaker_a}_{speaker_b}.wav")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, full_audio, model.tts_model.sample_rate)

    print(f"\n對話生成完成！")
    print(f"  總長度: {total_duration:.1f}s")
    print(f"  檔案: {output_path}")

if __name__ == "__main__":
    main()
