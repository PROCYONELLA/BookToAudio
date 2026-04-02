import requests
import os
import re
from pathlib import Path
from pydub import AudioSegment

class Synthesizer:
    def __init__(self, config):
        self.config = config['tts']
        self.api_url = os.environ.get("GPT_SOVITS_URL", "http://127.0.0.1:9880")
        
    def _split_sentences(self, text):
        # 依照標點符號分句，GPT-SoVITS 適合處理短句
        sentences = re.split(r'([。！？\n])', text)
        chunks = []
        current_chunk = ""
        for i in range(0, len(sentences)-1, 2):
            sentence = sentences[i] + sentences[i+1]
            if len(current_chunk) + len(sentence) > 300: # 每次大概送300字元
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def synthesize(self, text_path: Path, output_path: Path):
        if output_path.exists():
            print(f"⏩ 音檔已存在，略過：{output_path.name}")
            return
            
        print(f"🔊 正在使用 GPT-SoVITS 合成: {text_path.name}")
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        chunks = self._split_sentences(text)
        
        ref_audio_path = self.config.get("ref_audio")
        ref_text = self.config.get("ref_text")
        
        if "請在這裡填寫" in ref_text:
            print("❌ 錯誤：請先在 config.yaml 裡填入參考音檔的真實文字！")
            return
            
        combined_audio = AudioSegment.empty()
        
        for i, chunk in enumerate(chunks):
            if not chunk.strip(): continue
            
            payload = {
                "refer_wav_path": str(Path(ref_audio_path).resolve()),
                "prompt_text": ref_text,
                "prompt_language": self.config.get("prompt_language", "zh"),
                "text": chunk,
                "text_language": self.config.get("text_language", "zh")
            }
            
            try:
                response = requests.post(self.api_url, json=payload)
                if response.status_code == 200:
                    temp_wav = output_path.parent / f"temp_{i}.wav"
                    with open(temp_wav, 'wb') as f:
                        f.write(response.content)
                    
                    segment = AudioSegment.from_wav(temp_wav)
                    combined_audio += segment
                    temp_wav.unlink()  # 刪除暫存擋
                else:
                    print(f"⚠️ 合成失敗 (段落 {i})，狀態碼：{response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"❌ 無法連線至 GPT-SoVITS 伺服器 ({self.api_url})")
                print("💡 請確保您本地端或 Colab 已啟動 GPT-SoVITS 的 API 服務！")
                return
                
        # 輸出最終 MP3
        combined_audio.export(output_path, format="mp3")
        print(f"✅ 音檔合成完成：{output_path.name}")
