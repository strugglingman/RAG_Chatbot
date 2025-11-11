"""Document processing service"""
import os
import re
import csv
import json
from pypdf import PdfReader
from docx import Document


def read_text(file_path: str, text_max: int = 400000):
    """Read text from various file formats"""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        reader = PdfReader(file_path)
        pages_text = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text:
                pages_text.append((page_num, text))
        return pages_text
    
    if ext == ".csv":
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            all_rows = [",".join(row) for row in reader]
            return [(0, "\n".join(all_rows)[:text_max])]
    
    if ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return [(0, json.dumps(data, indent=2)[:text_max])]
            except Exception:
                return [(0, f.read()[:text_max])]
    
    if ext == ".docx":
        doc = Document(file_path)
        return [(0, "\n".join([p.text for p in doc.paragraphs])[:text_max])]
    
    with open(file_path, "r", encoding="utf-8") as f:
        return [(0, f.read()[:text_max])]


def sentence_split(text: str) -> list[str]:
    """Split text into sentences"""
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text.strip())
    return [p.strip() for p in parts if p and p.strip()]


def make_chunks(pages_text: list, target: int = 400, overlap: int = 90) -> list[tuple]:
    """Split document into overlapping chunks"""
    all_chunks = []
    
    for page_num, text in pages_text:
        chunks, buff, size = [], [], 0
        sentences = sentence_split(text)
        
        for s in sentences:
            buff.append(s)
            if size + len(s) <= target:
                size += len(s) + 1
            else:
                if buff:
                    chunks.append((page_num, ' '.join(buff)))
                
                overlap_sentences = []
                overlap_size = 0
                for sent in reversed(buff):
                    if overlap_size + len(sent) + (1 if overlap_sentences else 0) <= overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_size += len(sent) + (1 if overlap_size > 0 else 0)
                    else:
                        break
                
                buff = overlap_sentences
                size = sum(len(s) for s in buff) + max(0, len(buff) - 1)
        
        if buff:
            chunks.append((page_num, ' '.join(buff)))
        
        all_chunks.extend(chunks)
    
    return all_chunks
