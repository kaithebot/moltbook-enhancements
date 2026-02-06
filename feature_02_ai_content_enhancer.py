#!/usr/bin/env python3
"""
Feature #2: AI Content Enhancer for MoltBook
Provides editing suggestions, grammar checking, and style improvements
"""

import re
import argparse
from pathlib import Path
from datetime import datetime

class AIContentEnhancer:
    """Enhance content quality with AI-powered suggestions"""
    
    def __init__(self, content_path):
        self.content_path = Path(content_path)
        self.original_content = self.content_path.read_text(encoding='utf-8')
        self.suggestions = []
        
    def analyze(self):
        """Run all analysis checks"""
        self.check_grammar()
        self.check_style()
        self.check_readability()
        self.check_structure()
        return self.generate_report()
    
    def check_grammar(self):
        """Check for common grammar issues"""
        issues = []
        
        # Common grammar patterns
        patterns = [
            (r'\b(there|their|they\'re)\b', 'Check homophone usage'),
            (r'\b(your|you\'re)\b', 'Check your vs you\'re'),
            (r'\b(its|it\'s)\b', 'Check its vs it\'s'),
            (r'\b(affect|effect)\b', 'Verify affect vs effect'),
            (r'\b(then|than)\b', 'Check then vs than'),
            (r'\s{2,}', 'Multiple spaces detected'),
            (r'\n{3,}', 'Excessive line breaks'),
        ]
        
        for pattern, message in patterns:
            matches = list(re.finditer(pattern, self.original_content, re.IGNORECASE))
            for match in matches:
                line_num = self.original_content[:match.start()].count('\n') + 1
                context = self._get_context(match.start())
                issues.append({
                    'type': 'grammar',
                    'line': line_num,
                    'message': message,
                    'context': context
                })
        
        self.suggestions.extend(issues)
        return issues
    
    def check_style(self):
        """Check writing style and provide improvement suggestions"""
        style_issues = []
        
        # Passive voice detection (simplified)
        passive_patterns = [
            r'\bwas\s+\w+ed\b',
            r'\bwere\s+\w+ed\b',
            r'\bbeen\s+\w+ed\b',
        ]
        
        for pattern in passive_patterns:
            matches = re.finditer(pattern, self.original_content, re.IGNORECASE)
            for match in matches:
                line_num = self.original_content[:match.start()].count('\n') + 1
                style_issues.append({
                    'type': 'style',
                    'line': line_num,
                    'message': 'Consider using active voice for stronger writing',
                    'context': self._get_context(match.start())
                })
        
        # Word repetition
        words = re.findall(r'\b\w+\b', self.original_content.lower())
        word_counts = {}
        for word in words:
            if len(word) > 4:  # Only check longer words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated = {w: c for w, c in word_counts.items() if c > 5}
        if repeated:
            style_issues.append({
                'type': 'style',
                'line': 0,
                'message': f'Frequently repeated words: {", ".join(repeated.keys())}',
                'context': 'Consider using synonyms for variety'
            })
        
        self.suggestions.extend(style_issues)
        return style_issues
    
    def check_readability(self):
        """Calculate readability metrics"""
        text = self.original_content
        
        # Count sentences, words, syllables (simplified)
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(re.findall(r'\b\w+\b', text))
        
        # Simple Flesch Reading Ease calculation
        if sentences > 0 and words > 0:
            avg_words_per_sentence = words / sentences
            
            # Estimate syllables (simplified: count vowel groups)
            syllables = len(re.findall(r'[aeiouAEIOU]+', text))
            avg_syllables_per_word = syllables / words if words > 0 else 0
            
            # Flesch Reading Ease (simplified)
            reading_ease = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
            
            if reading_ease < 50:
                level = "Difficult - consider simplifying"
            elif reading_ease < 70:
                level = "Moderate - good for general audience"
            else:
                level = "Easy - accessible to wide audience"
            
            self.suggestions.append({
                'type': 'readability',
                'line': 0,
                'message': f'Reading ease score: {reading_ease:.1f} - {level}',
                'context': f'{avg_words_per_sentence:.1f} words/sentence, {avg_syllables_per_word:.2f} syllables/word'
            })
        
        return self.suggestions[-1] if self.suggestions else None
    
    def check_structure(self):
        """Analyze document structure"""
        structure_notes = []
        
        # Count chapters/sections
        headers = re.findall(r'^#{1,3}\s+', self.original_content, re.MULTILINE)
        if len(headers) < 3:
            structure_notes.append({
                'type': 'structure',
                'line': 0,
                'message': f'Only {len(headers)} headers found - consider adding more structure',
                'context': 'More sections improve readability and navigation'
            })
        
        # Check paragraph lengths
        paragraphs = self.original_content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]
        if long_paragraphs:
            structure_notes.append({
                'type': 'structure',
                'line': 0,
                'message': f'{len(long_paragraphs)} paragraphs are very long (>100 words)',
                'context': 'Consider breaking into smaller paragraphs for better readability'
            })
        
        self.suggestions.extend(structure_notes)
        return structure_notes
    
    def _get_context(self, position, context_chars=50):
        """Get text context around a position"""
        start = max(0, position - context_chars)
        end = min(len(self.original_content), position + context_chars)
        return self.original_content[start:end].replace('\n', ' ')
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        report_lines = [
            "=" * 60,
            "AI CONTENT ENHANCEMENT REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"File: {self.content_path.name}",
            "=" * 60,
            ""
        ]
        
        # Summary
        by_type = {}
        for s in self.suggestions:
            by_type[s['type']] = by_type.get(s['type'], 0) + 1
        
        report_lines.append("SUMMARY:")
        for stype, count in by_type.items():
            report_lines.append(f"  • {stype.capitalize()}: {count} suggestions")
        report_lines.append("")
        
        # Detailed suggestions
        if self.suggestions:
            report_lines.append("DETAILED SUGGESTIONS:")
            report_lines.append("-" * 60)
            
            for i, suggestion in enumerate(self.suggestions, 1):
                report_lines.append(f"\n{i}. [{suggestion['type'].upper()}] Line {suggestion['line']}")
                report_lines.append(f"   Issue: {suggestion['message']}")
                if suggestion['context']:
                    report_lines.append(f"   Context: \"...{suggestion['context']}...\"")
        else:
            report_lines.append("No suggestions found - great job!")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append("END OF REPORT")
        
        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description='MoltBook AI Content Enhancer')
    parser.add_argument('file', help='Content file to analyze')
    parser.add_argument('--output', '-o', help='Output report file')
    
    args = parser.parse_args()
    
    enhancer = AIContentEnhancer(args.file)
    report = enhancer.analyze()
    
    print(report)
    
    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"\n✅ Report saved to: {args.output}")


if __name__ == '__main__':
    main()
