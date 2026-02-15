#!/usr/bin/env python3
"""
Feature #6: Accessibility by Design for MoltBook
WCAG compliance checker and accessibility enhancement tools
"""

import re
import argparse
from pathlib import Path
from datetime import datetime

class AccessibilityChecker:
    """Check and enhance content for accessibility compliance"""
    
    def __init__(self, content_path=None):
        self.content_path = Path(content_path) if content_path else None
        self.content = self.content_path.read_text(encoding='utf-8') if self.content_path else ""
        self.issues = []
        self.wcag_version = "2.1"
        self.compliance_level = "AA"
    
    def check_wcag_compliance(self, html_content=None):
        """Check HTML content for WCAG compliance"""
        if html_content:
            self.content = html_content
        
        self.issues = []
        self._check_alt_text()
        self._check_headings()
        self._check_contrast()
        self._check_form_labels()
        self._check_link_text()
        self._check_language()
        self._check_skip_navigation()
        
        return self.issues
    
    def _check_alt_text(self):
        """Check for images without alt text"""
        img_pattern = r'<img[^>]*?(?!alt=)[^>]*?>'
        matches = re.finditer(img_pattern, self.content, re.IGNORECASE)
        
        for match in matches:
            self.issues.append({
                'type': 'error',
                'wcag': '1.1.1 Non-text Content (A)',
                'message': 'Image missing alt text',
                'context': match.group()[:50],
                'fix': 'Add alt="description" to img tag'
            })
    
    def _check_headings(self):
        """Check for proper heading structure"""
        h1_count = len(re.findall(r'<h1', self.content, re.IGNORECASE))
        h2_count = len(re.findall(r'<h2', self.content, re.IGNORECASE))
        
        if h1_count > 1:
            self.issues.append({
                'type': 'error',
                'wcag': '1.3.1 Info and Relationships (A)',
                'message': f'Multiple H1 headings found ({h1_count})',
                'context': 'Page structure',
                'fix': 'Use only one H1 per page'
            })
        elif h1_count == 0:
            self.issues.append({
                'type': 'error',
                'wcag': '1.3.1 Info and Relationships (A)',
                'message': 'No H1 heading found',
                'context': 'Page structure',
                'fix': 'Add an H1 heading as the main page title'
            })
        
        if h2_count > 0 and h1_count == 0:
            self.issues.append({
                'type': 'warning',
                'wcag': '1.3.1 Info and Relationships (A)',
                'message': 'H2 used without H1',
                'context': 'Page structure',
                'fix': 'Add H1 before H2'
            })
    
    def _check_contrast(self):
        """Check for color contrast issues"""
        color_pattern = r'style="[^"]*color:\s*([^;"]+)'
        matches = re.finditer(color_pattern, self.content, re.IGNORECASE)
        
        for match in matches:
            color = match.group(1).strip()
            light_colors = ['white', '#fff', '#ffffff', 'yellow', '#ffff00']
            if any(lc in color.lower() for lc in light_colors):
                self.issues.append({
                    'type': 'warning',
                    'wcag': '1.4.3 Contrast (Minimum) (AA)',
                    'message': f'Light color detected: {color}',
                    'context': f'style="{match.group(0)}"',
                    'fix': 'Ensure color contrast ratio is at least 4.5:1'
                })
    
    def _check_form_labels(self):
        """Check for form inputs without labels"""
        input_pattern = r'<(input|select|textarea)[^>]*>'
        matches = re.finditer(input_pattern, self.content, re.IGNORECASE)
        
        for match in matches:
            if 'aria-label' not in match.group() and 'aria-labelledby' not in match.group():
                self.issues.append({
                    'type': 'error',
                    'wcag': '1.3.1 Info and Relationships (A)',
                    'message': 'Form element missing label',
                    'context': match.group()[:50],
                    'fix': 'Add aria-label or label element'
                })
    
    def _check_link_text(self):
        """Check for non-descriptive link text"""
        link_pattern = r'<a[^>]*>(.*?)</a>'
        matches = re.finditer(link_pattern, self.content, re.IGNORECASE | re.DOTALL)
        
        bad_texts = ['click here', 'read more', 'link', 'here', 'more']
        
        for match in matches:
            link_text = re.sub(r'<[^>]+>', '', match.group(1)).strip().lower()
            if link_text in bad_texts:
                self.issues.append({
                    'type': 'warning',
                    'wcag': '2.4.4 Link Purpose (A)',
                    'message': f'Non-descriptive link text: "{link_text}"',
                    'context': match.group()[:50],
                    'fix': 'Use descriptive link text'
                })
    
    def _check_language(self):
        """Check for language attribute"""
        if '<html' in self.content.lower() and 'lang=' not in self.content.lower():
            self.issues.append({
                'type': 'error',
                'wcag': '3.1.1 Language of Page (A)',
                'message': 'HTML missing lang attribute',
                'context': '<html> tag',
                'fix': 'Add lang="en" to html tag'
            })
    
    def _check_skip_navigation(self):
        """Check for skip navigation link"""
        if '<a' in self.content.lower():
            if not re.search(r'skip|main-content', self.content, re.IGNORECASE):
                self.issues.append({
                    'type': 'recommendation',
                    'wcag': '2.4.1 Bypass Blocks (A)',
                    'message': 'Consider adding skip navigation link',
                    'context': 'Page navigation',
                    'fix': 'Add "Skip to main content" link'
                })
    
    def generate_accessible_html(self, original_html):
        """Generate accessibility-enhanced HTML"""
        enhanced = original_html
        
        if '<html' in enhanced and 'lang=' not in enhanced:
            enhanced = enhanced.replace('<html', '<html lang="en"')
        
        if '<body>' in enhanced.lower() and 'skip' not in enhanced.lower():
            skip_link = '<a href="#main-content" class="skip-link">Skip to main content</a>\n'
            enhanced = re.sub(r'(<body[^>]*>)', r'\1\n' + skip_link, enhanced, flags=re.IGNORECASE)
        
        return enhanced
    
    def generate_dyslexia_css(self):
        """Generate CSS for dyslexia-friendly reading"""
        return """/* Dyslexia-Friendly Styles */
.dyslexia-friendly {
    font-family: 'OpenDyslexic', 'Comic Sans MS', sans-serif;
    line-height: 1.6;
    letter-spacing: 0.05em;
    word-spacing: 0.1em;
}

.dyslexia-friendly p {
    max-width: 65ch;
    margin-bottom: 1.5em;
}

.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #000;
    color: #fff;
    padding: 8px;
    text-decoration: none;
}

.skip-link:focus {
    top: 0;
}
"""
    
    def generate_report(self):
        """Generate accessibility compliance report"""
        errors = [i for i in self.issues if i['type'] == 'error']
        warnings = [i for i in self.issues if i['type'] == 'warning']
        
        report = f"""
========================================
WCAG {self.wcag_version} {self.compliance_level} ACCESSIBILITY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
========================================

SUMMARY:
- Errors (must fix): {len(errors)}
- Warnings (should fix): {len(warnings)}
- Compliance Status: {'PASS' if len(errors) == 0 else 'NEEDS WORK'}

"""
        
        if errors:
            report += "\nERRORS:\n" + "-" * 50 + "\n"
            for i, issue in enumerate(errors, 1):
                report += f"\n{i}. [{issue['wcag']}]\n"
                report += f"   {issue['message']}\n"
                report += f"   Fix: {issue['fix']}\n"
        
        if warnings:
            report += "\n\nWARNINGS:\n" + "-" * 50 + "\n"
            for i, issue in enumerate(warnings, 1):
                report += f"\n{i}. {issue['message']}\n"
        
        if not self.issues:
            report += "\n✅ No accessibility issues found!\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='MoltBook Accessibility Checker')
    parser.add_argument('file', help='HTML file to check')
    parser.add_argument('--fix', action='store_true', help='Generate fixed HTML')
    parser.add_argument('--css', action='store_true', help='Generate dyslexia CSS')
    
    args = parser.parse_args()
    
    checker = AccessibilityChecker(args.file)
    checker.check_wcag_compliance()
    
    print(checker.generate_report())
    
    if args.fix:
        with open(args.file, 'r') as f:
            original = f.read()
        enhanced = checker.generate_accessible_html(original)
        output_file = args.file.replace('.html', '_accessible.html')
        with open(output_file, 'w') as f:
            f.write(enhanced)
        print(f"\n✅ Enhanced HTML saved to: {output_file}")
    
    if args.css:
        css = checker.generate_dyslexia_css()
        with open('dyslexia-friendly.css', 'w') as f:
            f.write(css)
        print(f"\n✅ CSS saved to: dyslexia-friendly.css")


if __name__ == '__main__':
    main()
