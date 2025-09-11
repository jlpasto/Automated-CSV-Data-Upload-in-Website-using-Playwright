#!/usr/bin/env python3
"""
Test script to demonstrate the URL validation functionality
"""
import os
import sys

# Add the current directory to the path so we can import from main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import is_valid_url

def test_url_validation():
    """Test the URL validation function with various inputs"""
    print("Testing URL validation functionality...")
    print("=" * 50)
    
    test_cases = [
        # Valid URLs
        ("https://tourdevines.com.au/", True, "Valid HTTPS URL"),
        ("http://example.com", True, "Valid HTTP URL"),
        ("https://www.google.com/search?q=test", True, "Valid URL with query parameters"),
        ("https://subdomain.example.com/path", True, "Valid URL with subdomain and path"),
        
        # Invalid URLs
        ("", False, "Empty string"),
        ("   ", False, "Whitespace only"),
        ("not-a-url", False, "Plain text without protocol"),
        ("www.example.com", False, "URL without protocol"),
        ("example.com", False, "Domain without protocol"),
        ("ftp://example.com", False, "FTP protocol (not HTTP/HTTPS)"),
        ("https://", False, "HTTPS without domain"),
        ("http://", False, "HTTP without domain"),
        (None, False, "None value"),
        (123, False, "Non-string value"),
    ]
    
    for url, expected, description in test_cases:
        result = is_valid_url(url)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status} | {description}")
        print(f"      Input: {repr(url)}")
        print(f"      Expected: {expected}, Got: {result}")
        print()
    
    print("=" * 50)
    print("URL validation test completed!")

if __name__ == "__main__":
    test_url_validation()
