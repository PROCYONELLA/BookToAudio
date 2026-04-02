import argparse
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

# 載入 .env 變數
load_dotenv()

# rich imports
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich import print as rprint

from extractor import Extractor
from rewriter import Rewriter
from synthesizer import Synthesizer

console = Console()

def load_config():
    config_path = Path(__file__).parent.parent / "config.yaml"
    if not config_path.exists():
        console.print("[red]❌ 找不到 config.yaml！[/red]")
        sys.exit(1)
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    console.print("[bold blue]🎧 BookToAudio - 電子書轉有聲書自動化流程[/bold blue]")
    config = load_config()
    
    books_dir = Path(config.get("books_dir", ""))
    if not books_dir.exists():
        console.print(f"[red]❌ 找不到書籍目錄：{books_dir}[/red]")
        sys.exit(1)

    # 1. 列出可用的書籍 (EPUB / PDF)
    console.print(f"\n[cyan]📂 正在掃描目錄：{books_dir}[/cyan]")
    books = []
    for file in books_dir.iterdir():
        if file.suffix.lower() in [".epub", ".pdf"]:
            books.append(file)
            
    if not books:
        console.print("[yellow]⚠️ 找不到任何 EPUB 或 PDF 書籍。[/yellow]")
        sys.exit(0)
        
    table = Table(title="可用的書籍列表")
    table.add_column("編號", style="cyan", no_wrap=True)
    table.add_column("書名", style="green")
    table.add_column("格式", style="magenta")
    
    for idx, book in enumerate(books):
        table.add_row(str(idx + 1), book.stem, book.suffix[1:].upper())
        
    console.print(table)
    
    book_idx = IntPrompt.ask("👉 請輸入要處理的書籍編號", choices=[str(i+1) for i in range(len(books))]) - 1
    selected_book = books[book_idx]
    
    output_dir = books_dir / f"{selected_book.stem}_audiobook"
    
    # 初始化模組
    extractor = Extractor(str(output_dir))
    rewriter = Rewriter(config)
    synthesizer = Synthesizer(config)
    
    # 2. 擷取章節
    console.print("\n[bold yellow]步驟 1：擷取書籍章節...[/bold yellow]")
    if selected_book.suffix.lower() == ".epub":
        extractor.extract_epub(str(selected_book))
    else:
        extractor.extract_pdf(str(selected_book))
        
    # 3. 列出章節並選擇
    chapters_dir = output_dir / "chapters"
    txt_files = sorted([f for f in chapters_dir.iterdir() if f.name.endswith(".txt") and not f.name.endswith("_spoken.txt")])
    
    if not txt_files:
        console.print("[red]❌ 無法找到任何擷取出來的章節文字。[/red]")
        sys.exit(1)
        
    console.print(f"\n[bold green]共找到 {len(txt_files)} 個章節[/bold green]")
    for idx, f in enumerate(txt_files):
        console.print(f"[{idx+1}] {f.stem}")
        
    target_idx = IntPrompt.ask("\n👉 請輸入要處理的章節編號 (先處理一個作為測試)", choices=[str(i+1) for i in range(len(txt_files))]) - 1
    target_chapter = txt_files[target_idx]
    
    # 4. 改寫與合成
    console.print("\n[bold yellow]步驟 2：使用 Gemini 產生口語朗讀稿...[/bold yellow]")
    spoken_txt_path = rewriter.rewrite_file(target_chapter)
    
    console.print("\n[bold yellow]步驟 3：使用 GPT-SoVITS 合成有聲書...[/bold yellow]")
    output_mp3 = extractor.audio_dir / f"{target_chapter.stem}.mp3"
    synthesizer.synthesize(spoken_txt_path, output_mp3)
    
    console.print("\n[bold green]🎉 處理完成！[/bold green]")
    console.print(f"👉 朗讀稿：{spoken_txt_path}")
    console.print(f"👉 最終音檔：{output_mp3}")

if __name__ == "__main__":
    main()
