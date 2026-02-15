#!/usr/bin/env python3
"""
Feature #1: Multi-Format Auto-Generator for MoltBook
Converts source content to EPUB, PDF, and Audiobook Script formats
"""

import argparse
import re
from pathlib import Path
from datetime import datetime

class MultiFormatGenerator:
    """Generate multiple output formats from a single source document"""
    
    def __init__(self, source_file, metadata=None):
        self.source = Path(source_file)
        self.content = self.source.read_text(encoding='utf-8')
        self.metadata = metadata or {}
        
    def to_epub(self, output_path=None):
        """Generate EPUB format"""
        if not output_path:
            output_path = self.source.with_suffix('.epub.html')
        
        # Create EPUB-ready HTML structure
        title = self.metadata.get('title', self.source.stem)
        author = self.metadata.get('author', 'Unknown')
        
        epub_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{title}</title>
    <meta charset="utf-8"/>
</head>
<body>
    <h1>{title}</h1>
    <p class="author">By {author}</p>
    {self._markdown_to_html(self.content)}
</body>
</html>"""
        
        Path(output_path).write_text(epub_html, encoding='utf-8')
        return f"✅ EPUB HTML generated: {output_path}"
    
    def to_pdf(self, output_path=None):
        """Generate PDF-ready format (HTML for PDF conversion)"""
        if not output_path:
            output_path = self.source.with_suffix('.pdf.html')
        
        title = self.metadata.get('title', self.source.stem)
        author = self.metadata.get('author', 'Unknown')
        
        pdf_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Georgia, serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; }}
        h1 {{ text-align: center; font-size: 2.5em; margin-bottom: 0.5em; }}
        .author {{ text-align: center; font-style: italic; color: #666; margin-bottom: 3em; }}
        h2 {{ color: #333; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }}
        p {{ text-align: justify; margin-bottom: 1.2em; }}
        .page-break {{ page-break-after: always; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="author">By {author}</p>
    <div class="page-break"></div>
    {self._markdown_to_html(self.content)}
</body>
</html>"""
        
        Path(output_path).write_text(pdf_html, encoding='utf-8')
        return f"✅ PDF HTML generated: {output_path}"
    
    def to_audiobook_script(self, output_path=None):
        """Generate audiobook narration script with timing cues"""
        if not output_path:
            output_path = self.source.with_suffix('.audiobook.txt')
        
        title = self.metadata.get('title', self.source.stem)
        author = self.metadata.get('author', 'Unknown')
        
        # Convert to narration-friendly format
        script_content = self._to_narration_format()
        
        audiobook_script = f"""AUDIOBOOK NARRATION SCRIPT
{title}
By {author}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

=== NARRATOR NOTES ===
- Pace: Conversational, engaging
- Tone: Match content mood
- Pause at [PAUSE] markers
- Emphasize words in *asterisks*

=== SCRIPT ===

[OPENING - 5 sec silence]

"{title}"
By {author}

[PAUSE 2 seconds]

{script_content}

[ENDING - 5 sec silence]

=== END OF SCRIPT ===

Word count: {len(self.content.split())}
Estimated duration: {len(self.content.split()) / 150:.1f} minutes (at 150 WPM)"""
        
        Path(output_path).write_text(audiobook_script, encoding='utf-8')
        return f"✅ Audiobook script generated: {output_path}"
    
    def _markdown_to_html(self, text):
        """Simple markdown to HTML conversion"""
        # Headers
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Bold and italic
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Paragraphs
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<'):
                p = f'<p>{p}</p>'
            html_paragraphs.append(p)
        
        return '\n\n'.join(html_paragraphs)
    
    def _to_narration_format(self):
        """Convert content to narration-friendly format"""
        text = self.content
        
        # Remove markdown formatting that doesn't work for audio
        text = re.sub(r'#+ ', '', text)  # Remove headers
        text = re.sub(r'\*\*', '', text)  # Remove bold markers
        text = re.sub(r'\*', '', text)    # Remove italic markers
        
        # Add narration cues
        lines = text.split('\n')
        narration_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Add emphasis markers for key phrases
                if line.startswith('Chapter') or line.startswith('Part'):
                    narration_lines.append(f"\n[PAUSE]\n*{line}*\n[PAUSE]\n")
                else:
                    narration_lines.append(line)
        
        return '\n\n'.join(narration_lines)
    
    def generate_all(self, output_dir=None):
        """Generate all formats at once"""
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            base_path = output_dir / self.source.stem
        else:
            base_path = self.source.parent / self.source.stem
        
        results = []
        results.append(self.to_epub(f"{base_path}_epub.html"))
        results.append(self.to_pdf(f"{base_path}_print.html"))
        results.append(self.to_audiobook_script(f"{base_path}_audiobook.txt"))
        
        return "\n".join(results)


def main():
    parser = argparse.ArgumentParser(description='MoltBook Multi-Format Generator')
    parser.add_argument('source', help='Source markdown/text file')
    parser.add_argument('--title', help='Book title')
    parser.add_argument('--author', help='Book author')
    parser.add_argument('--output-dir', help='Output directory')
    parser.add_argument('--format', choices=['epub', 'pdf', 'audiobook', 'all'], 
                       default='all', help='Output format')
    
    args = parser.parse_args()
    
    metadata = {
        'title': args.title or Path(args.source).stem,
        'author': args.author or 'Unknown'
    }
    
    generator = MultiFormatGenerator(args.source, metadata)
    
    if args.format == 'all':
        print(generator.generate_all(args.output_dir))
    elif args.format == 'epub':
        print(generator.to_epub())
    elif args.format == 'pdf':
        print(generator.to_pdf())
    elif args.format == 'audiobook':
        print(generator.to_audiobook_script())
    
    print("\n✨ Multi-format generation complete!")


if __name__ == '__main__':
    main()
