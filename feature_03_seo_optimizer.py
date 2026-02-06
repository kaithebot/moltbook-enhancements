#!/usr/bin/env python3
"""
Feature #3: Book SEO & Discoverability Optimizer for MoltBook
Optimizes book metadata for search engines and book platforms
"""

import re
import json
import argparse
from pathlib import Path
from collections import Counter
from datetime import datetime

class BookSEOOptimizer:
    """Optimize book metadata and content for discoverability"""
    
    def __init__(self, content_path, metadata=None):
        self.content_path = Path(content_path)
        self.content = self.content_path.read_text(encoding='utf-8')
        self.metadata = metadata or {}
        self.recommendations = []
        
    def analyze(self):
        """Run complete SEO analysis"""
        self.extract_keywords()
        self.optimize_title()
        self.optimize_description()
        self.check_categories()
        self.analyze_competition()
        return self.generate_seo_report()
    
    def extract_keywords(self):
        """Extract and rank keywords from content"""
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', self.content.lower())
        words = text.split()
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                     'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                     'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
                     'they', 'them', 'their', 'there', 'then', 'than'}
        
        # Count meaningful words
        meaningful_words = [w for w in words if len(w) > 3 and w not in stop_words]
        word_counts = Counter(meaningful_words)
        
        # Get top keywords
        top_keywords = word_counts.most_common(20)
        
        self.recommendations.append({
            'type': 'keywords',
            'priority': 'high',
            'message': f'Top keywords found: {", ".join([k[0] for k in top_keywords[:10]])}',
            'keywords': top_keywords
        })
        
        return top_keywords
    
    def optimize_title(self):
        """Analyze and optimize book title"""
        title = self.metadata.get('title', '')
        
        if not title:
            # Try to extract from content
            match = re.search(r'^#\s+(.+)$', self.content, re.MULTILINE)
            if match:
                title = match.group(1)
        
        issues = []
        
        if len(title) < 10:
            issues.append("Title is too short (aim for 10-60 characters)")
        elif len(title) > 60:
            issues.append("Title is too long (aim for under 60 characters for search engines)")
        
        if not any(c.isdigit() for c in title):
            issues.append("Consider adding numbers (e.g., '7 Ways to...') for better click-through rates")
        
        # Check for power words
        power_words = ['ultimate', 'complete', 'essential', 'definitive', 'comprehensive', 
                      'secret', 'proven', 'guaranteed', 'exclusive', 'limited']
        if not any(word in title.lower() for word in power_words):
            issues.append("Consider adding power words to increase emotional appeal")
        
        self.recommendations.append({
            'type': 'title',
            'priority': 'critical',
            'current_title': title,
            'issues': issues,
            'message': f'Title: \"{title}\"' + (f' - {len(issues)} suggestions' if issues else ' - Looks good!')
        })
        
        return title
    
    def optimize_description(self):
        """Generate optimized book description"""
        # Extract first paragraph as potential description
        paragraphs = self.content.split('\n\n')
        first_para = ''
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('#'):
                first_para = p
                break
        
        # Clean markdown
        first_para = re.sub(r'[#*_]', '', first_para)
        
        suggestions = []
        
        if len(first_para) < 100:
            suggestions.append("Description is too short (aim for 150-300 characters)")
        elif len(first_para) > 500:
            suggestions.append("Description is very long (consider a shorter version for previews)")
        
        # Check for call-to-action
        if not any(cta in first_para.lower() for cta in ['discover', 'learn', 'find', 'get', 'start', 'join']):
            suggestions.append("Add a call-to-action (e.g., 'Discover how to...')")
        
        # Generate optimized description
        optimized = self._generate_description()
        
        self.recommendations.append({
            'type': 'description',
            'priority': 'high',
            'current': first_para[:200] + '...' if len(first_para) > 200 else first_para,
            'optimized': optimized,
            'suggestions': suggestions,
            'message': f'Description length: {len(first_para)} characters'
        })
        
        return optimized
    
    def _generate_description(self):
        """Generate an SEO-optimized description"""
        title = self.metadata.get('title', 'This book')
        keywords = [k[0] for k in self.extract_keywords()[:5]]
        
        description = f"Discover {title.lower()}, the ultimate guide to {', '.join(keywords[:3])}. "
        description += f"Learn proven strategies and expert insights on {keywords[0]} and {keywords[1]}. "
        description += "Perfect for beginners and experts alike. Start your journey today!"
        
        return description
    
    def check_categories(self):
        """Suggest best categories and genres"""
        keywords = [k[0] for k in self.extract_keywords()[:10]]
        
        # Simple genre mapping based on keywords
        genre_keywords = {
            'fiction': ['story', 'novel', 'character', 'plot', 'narrative'],
            'non-fiction': ['guide', 'how', 'tips', 'strategies', 'learn'],
            'business': ['business', 'money', 'success', 'entrepreneur', 'marketing'],
            'self-help': ['improve', 'better', 'life', 'change', 'growth'],
            'technology': ['tech', 'digital', 'software', 'app', 'online'],
            'health': ['health', 'fitness', 'wellness', 'diet', 'exercise']
        }
        
        genre_scores = {}
        for genre, indicators in genre_keywords.items():
            score = sum(1 for k in keywords if k in indicators)
            if score > 0:
                genre_scores[genre] = score
        
        top_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        self.recommendations.append({
            'type': 'categories',
            'priority': 'medium',
            'suggested_genres': [g[0] for g in top_genres],
            'message': f'Suggested categories: {", ".join([g[0] for g in top_genres])}'
        })
        
        return top_genres
    
    def analyze_competition(self):
        """Provide competitive insights"""
        title = self.metadata.get('title', '')
        
        # Check title uniqueness indicators
        uniqueness_score = 50  # Base score
        
        if len(title) > 20:
            uniqueness_score += 10
        if any(c.isdigit() for c in title):
            uniqueness_score += 15
        if ':' in title or '-' in title:
            uniqueness_score += 10
        
        competition_level = "High" if uniqueness_score < 60 else "Medium" if uniqueness_score < 80 else "Low"
        
        self.recommendations.append({
            'type': 'competition',
            'priority': 'medium',
            'uniqueness_score': uniqueness_score,
            'competition': competition_level,
            'message': f'Competition level: {competition_level} (uniqueness score: {uniqueness_score}/100)'
        })
        
        return competition_level
    
    def generate_seo_report(self):
        """Generate comprehensive SEO report"""
        report_lines = [
            "=" * 60,
            "BOOK SEO & DISCOVERABILITY REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"File: {self.content_path.name}",
            "=" * 60,
            ""
        ]
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_recs = sorted(self.recommendations, key=lambda x: priority_order.get(x.get('priority', 'low'), 4))
        
        for rec in sorted_recs:
            report_lines.append(f"\n[{rec['priority'].upper()}] {rec['type'].upper()}")
            report_lines.append(f"  {rec['message']}")
            
            if 'keywords' in rec:
                report_lines.append(f"\n  Top Keywords:")
                for kw, count in rec['keywords'][:5]:
                    report_lines.append(f"    • {kw}: {count} occurrences")
            
            if 'optimized' in rec:
                report_lines.append(f"\n  Suggested Description:")
                report_lines.append(f"    \"{rec['optimized']}\"")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append("ACTION ITEMS:")
        report_lines.append("1. Update book title based on recommendations")
        report_lines.append("2. Write SEO-optimized description (150-300 chars)")
        report_lines.append("3. Select appropriate categories/genres")
        report_lines.append("4. Use top keywords in metadata")
        report_lines.append("5. Add book to relevant platforms with optimized data")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description='MoltBook SEO Optimizer')
    parser.add_argument('file', help='Book content file to analyze')
    parser.add_argument('--title', help='Book title')
    parser.add_argument('--author', help='Book author')
    parser.add_argument('--output', '-o', help='Output report file')
    
    args = parser.parse_args()
    
    metadata = {
        'title': args.title or '',
        'author': args.author or 'Unknown'
    }
    
    optimizer = BookSEOOptimizer(args.file, metadata)
    report = optimizer.analyze()
    
    print(report)
    
    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"\n✅ SEO report saved to: {args.output}")


if __name__ == '__main__':
    main()
