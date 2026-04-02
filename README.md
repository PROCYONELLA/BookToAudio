# BookToAudio 📚 ➡️ 🎧

將個人電子書轉換為高品質有聲書的自動化工具。透過這個專案，您可以將生硬的 `.epub` 或 `.pdf` 書面文字，自動改寫成如同單口 Podcast 般具有溫度的口語朗讀稿，並運用先進的語音克隆技術（GPT-SoVITS）合成專屬的有聲書。

## 🌟 核心特色

1. **智慧章節提取 (`extractor.py`)**
   - 優先支援 `.epub` 解析，保留原文章節結構，自動過濾非正文內容。
   - 包含對 `.pdf` 檔案的基礎回退支援（基於文件書籤/ToC）。
2. **Podcast 風格口語化改寫 (`rewriter.py`)**
   - 串接 **Google Gemini API** (1.5 Pro)。
   - 運用特製的 System Prompt，將文獻標記、括號補充及圖表描述，自然地轉譯為適合「聽」的敘述，同時保留關鍵英文術語。
3. **高品質聲音克隆合成 (`synthesizer.py`)**
   - 串接開源的 **GPT-SoVITS** 引擎。
   - 只要指定一段 3~10 秒的參考對話音檔，即可完整復刻該人物的音色與咬字。

---

## 🛠️ 安裝與環境設定

### 1. 安裝系統依賴
請確保您的 Mac 上已安裝 Python 3.10+ 與 FFmpeg：
```bash
brew install ffmpeg
```

### 2. 安裝 Python 套件
進入專案資料夾後，安裝相依性套件：
```bash
pip install EbookLib beautifulsoup4 pymupdf pydub google-generativeai rich python-dotenv pyyaml requests
```

### 3. 環境變數設定 (`.env`)
請在專案根目錄確認或建立 `.env` 檔案，填入：
```env
GEMINI_API_KEY=your_gemini_key_here
GPT_SOVITS_URL=http://127.0.0.1:9880  # 填寫本地端或 Colab 上 GPT-SoVITS 的 API 網址
```

### 4. 工具配置 (`config.yaml`)
最重要的步驟在於調整 `config.yaml` 裡的聲音設定：
- **`ref_audio`**: 指向參考音檔的絕對路徑（如 `seg_08.mp3`）。
- **`ref_text`**: **務必精準輸入**該參考音檔裡的人講出來的確切逐字稿（含標點符號）。

---

## 🚀 使用說明

直接執行主程式，它將啟動互動式終端介面：

```bash
python src/main.py
```
1. 終端機會自動掃描你指定的書籍根目錄。
2. 從列表中選擇要處理的書籍。
3. 腳本優先為你提取所有章節並儲存純文字檔。
4. 選擇任一目標章節，將自動接續進行「Gemini 改寫」與「GPT-SoVITS 合成」。
5. 最後輸出結果將分別存放在 `chapters/` 與 `audio/` 目錄中。

---

## 📝 後續維護與 Git 版本控制
本專案已連結至您的 GitHub。後續如果有新增或修改程式碼，請依循標準 Git 流程推播：
```bash
git add .
git commit -m "更新您的備註"
git push
```
