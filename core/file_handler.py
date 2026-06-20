"""
File upload and processing
"""
import os
import pandas as pd
import streamlit as st
from utils.error_handler import FileError
from utils.token_counter import TokenCounter

class FileHandler:
    """Handle various file formats"""
    
    SUPPORTED_FORMATS = {
        "text": [".txt", ".md", ".csv", ".log"],
        "code": [".py", ".js", ".java", ".cpp", ".html", ".css", ".json", ".sql", ".sh"],
        "pdf": [".pdf"],
        "excel": [".xlsx", ".xls"],
        "word": [".docx"],
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
        "powerpoint": [".pptx"]
    }
    
    MAX_FILES = 5
    MAX_SIZE = 10_000_000  # 10MB
    
    @classmethod
    def get_format(cls, filename):
        """Detect file format from extension"""
        ext = os.path.splitext(filename)[1].lower()
        for fmt, extensions in cls.SUPPORTED_FORMATS.items():
            if ext in extensions:
                return fmt
        return None
    
    @classmethod
    def handle(cls, uploaded_files, gemini_agent=None):
        """Process uploaded files"""
        if len(uploaded_files) > cls.MAX_FILES:
            raise FileError(f"Max {cls.MAX_FILES} files allowed")
        
        results = []
        total_tokens = 0
        
        for file in uploaded_files:
            if file.size > cls.MAX_SIZE:
                results.append({
                    "filename": file.name,
                    "error": f"File too large (max 10MB)"
                })
                continue
            
            fmt = cls.get_format(file.name)
            if not fmt:
                results.append({
                    "filename": file.name,
                    "error": "Unsupported format"
                })
                continue
            
            try:
                content = cls._process_file(file, fmt, gemini_agent)
                tokens = TokenCounter.count(content) if content else 0
                total_tokens += tokens
                
                results.append({
                    "filename": file.name,
                    "format": fmt,
                    "content": content[:10000],  # Limit
                    "tokens": tokens,
                    "size_kb": file.size / 1024
                })
            
            except Exception as e:
                results.append({
                    "filename": file.name,
                    "error": str(e)
                })
        
        return {
            "files": results,
            "total_tokens": total_tokens,
            "count": len(results)
        }
    
    @classmethod
    def _process_file(cls, file, fmt, gemini_agent=None):
        """Process file based on format"""
        
        if fmt == "text":
            return file.read().decode('utf-8')[:50000]
        
        elif fmt == "code":
            content = file.read().decode('utf-8')
            ext = os.path.splitext(file.name)[1]
            lang_map = {'.py': 'python', '.js': 'javascript', '.java': 'java',
                       '.cpp': 'cpp', '.html': 'html', '.css': 'css',
                       '.json': 'json', '.sql': 'sql', '.sh': 'bash'}
            lang = lang_map.get(ext, '')
            return f"```{lang}\n{content[:30000]}\n```"
        
        elif fmt == "pdf":
            try:
                import pdfplumber
                with pdfplumber.open(file) as pdf:
                    text = ""
                    for page in pdf.pages[:10]:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return text[:40000] if text else "No text found in PDF"
            except:
                from PyPDF2 import PdfReader
                reader = PdfReader(file)
                text = ""
                for page in reader.pages[:10]:
                    text += page.extract_text() + "\n"
                return text[:40000]
        
        elif fmt == "excel":
            df = pd.read_excel(file)
            return df.head(100).to_string()[:30000]
        
        elif fmt == "word":
            from docx import Document
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            return text[:30000]
        
        elif fmt == "image":
            if gemini_agent:
                result = gemini_agent.analyze_image(file)
                return result["text"][:10000]
            else:
                return "[Image - requires Gemini Vision]"
        
        elif fmt == "powerpoint":
            from pptx import Presentation
            prs = Presentation(file)
            text = ""
            for slide in prs.slides[:20]:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        text += shape.text + "\n"
            return text[:30000]
        
        return None