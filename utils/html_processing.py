import re

class HtmlProcessing:
    
    def __init__(self, file_path):
        self._html_content = self.load_html_from_file(file_path)
    
    def load_html_from_file(self, file_path: str) -> str:
        """Load HTML content from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:  # Specify UTF-8 encoding
                html_content = f.read()
            return html_content
        except Exception as e:
            raise IOError(f"Failed to load HTML file: {e}")
    
    def extract_html_body(self):
        """
        Extract the body content from an HTML string using regular expressions.
        
        Args:
            html_string (str): The full HTML content
        
        Returns:
            str: The extracted body content, or an empty string if no body is found
        """
        # Regex pattern to match body content
        # This handles various cases like different casing, whitespace, and attributes
        body_pattern = re.compile(r'<body[^>]*>(.*?)</body>', 
                                re.DOTALL | re.IGNORECASE)
        
        # Search for body content
        match = body_pattern.search(self._html_content)
        
        # Return matched body content or empty string
        return match.group(1).strip() if match else ''
    
    def remove_html_styles(self):
        """
        Remove all style-related content from HTML.
        This function removes:
        1. <style> tags and their content
        2. Style attributes from HTML elements
        3. <link> tags that reference CSS files
        
        Args:
            html_content (str): Original HTML content
            
        Returns:
            str: HTML content with all styles removed
        """
        modified_html = self._html_content
        
        # 1. Remove <style> tags and their content
        style_pattern = r'<style[^>]*>.*?</style>'
        modified_html = re.sub(style_pattern, '', modified_html, flags=re.DOTALL)
        
        # 2. Remove style attributes from HTML elements
        style_attr_pattern = r' style="[^"]*"'
        modified_html = re.sub(style_attr_pattern, '', modified_html)
        
        # 3. Remove <link> tags that reference CSS files
        css_link_pattern = r'<link[^>]*rel=["\']\s*stylesheet\s*["\'][^>]*>'
        modified_html = re.sub(css_link_pattern, '', modified_html)
        
        # Additional: Remove class attributes (optional, only if you want to remove all visual styling)
        # class_attr_pattern = r' class="[^"]*"'
        # modified_html = re.sub(class_attr_pattern, '', modified_html)
        
        return modified_html
    
    def replace_html_body(self, new_body_content):
        """
        Replace the content of the HTML body tag with new content.
        
        Args:
            html_content (str): The original HTML content
            new_body_content (str): The new content to place inside the body tags
            
        Returns:
            str: The modified HTML with the new body content
        """
        # Pattern to match the body content (anything between <body> and </body>)
        pattern = r'<body[^>]*>(.*?)</body>'
        
        # Replace the body content with the new content
        # re.DOTALL allows the dot to match newlines
        modified_html = re.sub(pattern, f'<body>{new_body_content}</body>', self._html_content, flags=re.DOTALL)
        
        return modified_html
    
    @staticmethod
    def save_html(new_file, html_content):
        """Save HTML content into a file"""
        try:
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            raise IOError(f"Failed to save HTML file: {e}")
