import os
import google.generativeai as genai
from pathlib import Path

class Rewriter:
    def __init__(self, config):
        self.config = config['rewriter']
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ 環境變數中找不到 GEMINI_API_KEY！")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=self.config.get('model', 'gemini-1.5-pro-latest'),
            system_instruction=(
                "你是一個專業的有聲書編輯與 Podcast 講者。"
                "你的任務是將書面文字改寫成適合「聽」的單人 Podcast 口語版朗讀稿。"
                "規則如下：\n"
                "1. 使用第一人稱口吻，彷彿你在向聽眾解說這本書。\n"
                "2. 把書面語改為自然的口語，適當加入一些過渡句（如：『接下來說到...』、『你可以想像一下...』）。\n"
                "3. 原文中的英文術語請保留，若有英文縮寫，請保持原本的樣子。\n"
                "4. 遇到括號等補充說明的內容，請用口語自然融入句子，或是遇到不重要的參考文獻標記（如 [1]）直接刪除。\n"
                "5. 若有圖表或視覺化的敘述，改為引導聽眾想像的描述。\n"
                "6. 維持資訊密度，但讓句型簡單、好懂。完全不需要加上 Markdown 格式，只需純文字。"
            )
        )
        self.generation_config = genai.types.GenerationConfig(
            temperature=self.config.get('temperature', 0.7)
        )

    def rewrite_file(self, input_path: Path):
        output_path = input_path.parent / f"{input_path.stem}_spoken.txt"
        if output_path.exists():
            print(f"⏩ {output_path.name} 已存在，略過改寫。")
            return output_path

        print(f"✍️ 正在使用 Gemini 改寫: {input_path.name}")
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # 分段處理，避免超過單一 request 的上限
        max_chars = self.config.get('max_chunk_chars', 8000)
        chunks = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
        
        rewritten_text = ""
        for i, chunk in enumerate(chunks):
            response = self.model.generate_content(
                f"請改寫以下章節內容：\n\n{chunk}",
                generation_config=self.generation_config
            )
            rewritten_text += response.text + "\n\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rewritten_text.strip())
            
        print(f"✅ 改寫完成：{output_path.name}")
        return output_path
