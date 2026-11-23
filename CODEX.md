# CODEX.md — VoxCPM2 Voice Cloner 指南

本專案提供基於 VoxCPM2 的語音克隆與自然語言生成工具，專為 AI Agent 設計。

## 核心設計原則
- **自然語言優先**：使用者透過自然語言指令操作，Codex Agent 自動解析使用者的意圖、聲音名稱與發音文字，調用對應腳本。
- **好聽耐聽**：所有預設聲音均經調校，音質自然舒緩。

## 執行指令

### 1. 語音生成 (`clone.py`)
```bash
python clone.py "<文字>" --voice "<聲音名稱>"
```
- 虛擬環境：`.\.venv\Scripts\python.exe`
- 輸出檔案：`output/cloned_voice.wav`
- 若未指定 `--voice`，自動採用 `voices/` 內第一個可用聲音。

### 2. 多角色對話 (`dialogue.py`)
```bash
python dialogue.py --a "<說話者A>" --b "<說話者B>"
```
- 輸出檔案：`output/dialogue_<A>_<B>.wav`

### 3. 查看可用聲音
```bash
ls voices/
```

### 4. 錄音介面
```bash
python app.py
```
- 存取網址：`http://127.0.0.1:7860`

## 自然語言意圖對照表
| 使用者指令 | Codex 應執行的動作 |
|---|---|
| 「用[聲音]說[文字]」 | `python clone.py "[文字]" --voice "[聲音]"` |
| 「讓[A]和[B]對話」 | 調整 dialogue.py 或直接 `python dialogue.py --a "[A]" --b "[B]"` |
| 「有哪些聲音」 | 列出 `voices/` 目錄並依風格介紹 |
| 「我想錄製自己的聲音」 | 引導 `http://127.0.0.1:7860` 或 `python record.py` |
