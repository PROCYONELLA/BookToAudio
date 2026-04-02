import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

class Extractor:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chapters_dir = self.output_dir / "chapters"
        self.chapters_dir.mkdir(exist_ok=True)
        self.audio_dir = self.output_dir / "audio"
        self.audio_dir.mkdir(exist_ok=True)

    def extract_epub(self, epub_path: str):
        try:
            import ebooklib
            from ebooklib import epub
        except ImportError:
            print("❌ 請確保已安裝 EbookLib: pip install EbookLib")
            return

        print(f"📖 正在解析 EPUB: {epub_path}")
        book = epub.read_epub(epub_path)
        
        chapter_idx = 1
        metadata = {
            "book_title": book.get_metadata("DC", "title")[0][0] if book.get_metadata("DC", "title") else "Unknown Title",
            "epub_source": str(epub_path),
            "chapters": []
        }

        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = item.get_content()
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            
            # 簡單過濾過短的非正文內容 (如空頁)
            if len(text) < 100:
                continue

            # 嘗試抓取標題，若無則用檔案名
            title_tag = soup.find(['h1', 'h2', 'h3'])
            chapter_name = title_tag.get_text(strip=True) if title_tag else item.get_name()
            # 檔案名稱中替換不合法字元
            safe_name = re.sub(r'[\\/*?:"<>|]', "_", chapter_name)[:30]
            
            filename = f"{chapter_idx:02d}_{safe_name}.txt"
            filepath = self.chapters_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {chapter_name}\n\n")
                f.write(text)

            metadata["chapters"].append({
                "index": chapter_idx,
                "name": chapter_name,
                "filename": filename,
                "char_count": len(text),
                "rewritten": False
            })
            
            print(f"✅ 提取章節：{chapter_name} ({len(text)} 字)")
            chapter_idx += 1

        metadata["total_chapters"] = len(metadata["chapters"])
        
        metadata_path = self.chapters_dir / "00_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        print(f"\n🎉 提取完成！共 {metadata['total_chapters']} 個章節。儲存於：{self.chapters_dir}")

    def extract_pdf(self, pdf_path: str):
        try:
            import fitz
        except ImportError:
            print("❌ 請確保已安裝 PyMuPDF: pip install PyMuPDF")
            return

        print(f"📖 正在解析 PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()

        metadata = {
            "book_title": Path(pdf_path).stem,
            "pdf_source": str(pdf_path),
            "chapters": []
        }

        if not toc:
            print("⚠️ 此 PDF 沒有書籤 (Table of Contents)，將只能整本提取。")
            text = ""
            for page in doc:
                text += page.get_text()
            
            filename = "01_全書內容.txt"
            with open(self.chapters_dir / filename, 'w', encoding='utf-8') as f:
                f.write(text)
                
            metadata["chapters"].append({
                "index": 1,
                "name": "全書內容",
                "filename": filename,
                "char_count": len(text),
                "rewritten": False
            })
        else:
            chapter_idx = 1
            for i, entry in enumerate(toc):
                level, title, page = entry
                # 只提取第一層或第二層章節
                if level > 2: continue
                
                start_page = page - 1
                end_page = toc[i+1][2] - 1 if i + 1 < len(toc) else len(doc)
                
                text = ""
                for p in range(start_page, end_page):
                    text += doc[p].get_text()
                    
                safe_name = re.sub(r'[\\/*?:"<>|]', "_", title)[:30]
                filename = f"{chapter_idx:02d}_{safe_name}.txt"
                
                with open(self.chapters_dir / filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {title}\n\n{text}")

                metadata["chapters"].append({
                    "index": chapter_idx,
                    "name": title,
                    "filename": filename,
                    "char_count": len(text),
                    "rewritten": False
                })
                print(f"✅ 提取章節：{title} ({len(text)} 字)")
                chapter_idx += 1

        metadata["total_chapters"] = len(metadata["chapters"])
        metadata_path = self.chapters_dir / "00_metadata.json"
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        print(f"\n🎉 PDF 提取完成！共 {metadata['total_chapters']} 個章節。")
