# Agents：VoxCPM2 Voice Cloner 使用指南

本專案提供基於 VoxCPM2 的語音克隆與生成工具，專為 AI Agent 設計。Agent 應完全依據使用者的自然語言指令自動選用工具執行。

## 工具清單

### 1. clone.py — 用已錄製的聲音生成語音

```bash
python clone.py "要生成的文字" --voice <聲音名稱>
```

- `<聲音名稱>`：對應 `voices/<名稱>/` 目錄
- 輸出：`output/cloned_voice.wav`
- 首次執行會自動下載 VoxCPM2 模型（約 4.7GB）

範例：
```bash
python clone.py "同學們早安，今天我們來上數學課。" --voice 甜美女聲
```

### 2. dialogue.py — 用多個聲音生成對話

```bash
python dialogue.py --a <聲音A> --b <聲音B>
```

- 支援指定 `--a` 與 `--b` 角色聲音，若未指定則自動採用 `voices/` 目錄中前兩個可用聲音
- 輸出：`output/dialogue_<A>_<B>.wav`
- 若要自訂對話台詞，編輯 `dialogue.py` 中的 `dialogue` 清單

### 3. record.py — 命令列錄音（無 UI 備案）

```bash
python record.py --voice <聲音名稱>
```

## 聲音管理

- 已錄製的聲音列表：`ls voices/`（目錄名即聲音名稱）
- 每個聲音目錄包含：
  - `ref_voice.wav` — 參考音檔（16kHz 單聲道）
  - `prompt.txt` — 逐字稿（錄音時念的文字）

## 裝置偵測

執行 `clone.py` 或 `dialogue.py` 時會自動偵測裝置：
- NVIDIA GPU → CUDA 模式
- Intel Arc GPU → XPU 模式（需 patch，install.ps1 已處理）
- 無獨顯 → CPU 模式（較慢）

## 常見使用者自然語言對照

| 使用者說的 | Agent 應執行的 |
|-----------|---------------|
| 用甜美女聲說「同學們早安」 | `python clone.py "同學們早安" --voice 甜美女聲` |
| 讓哆啦A夢跟大雄對話 | `python dialogue.py --a 哆啦A夢 --b 大雄` |
| 錄製新的聲音 | 引導使用者開啟 `http://127.0.0.1:7860` 或執行 `record.py --voice <名稱>` |
| 有哪些已錄製的聲音 | `ls voices/` |
