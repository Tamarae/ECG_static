#!/usr/bin/env python3
"""
Debug script to check what's in the browse.html file
"""

from pathlib import Path
import re

def debug_browse_html():
    """Check the browse.html file contents"""

    # Path to browse.html
    browse_file = Path("../output/browse.html")

    print("🔍 Debugging browse.html file...")
    print("=" * 50)

    if not browse_file.exists():
        print(f"❌ browse.html not found at: {browse_file.absolute()}")
        return

    # Read the file
    with open(browse_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"📄 File size: {len(content)} characters")

    # Check for inscription items
    inscription_items = re.findall(r'class="clean-inscription-item"', content)
    print(f"🔍 Found {len(inscription_items)} inscription items in HTML")

    # Check for specific patterns
    if 'clean-inscription-list' in content:
        print("✅ Found clean-inscription-list container")
    else:
        print("❌ Missing clean-inscription-list container")

    if 'inscriptionList' in content:
        print("✅ Found inscriptionList ID")
    else:
        print("❌ Missing inscriptionList ID")

    # Check for JavaScript
    if 'browse.js' in content:
        print("✅ Found browse.js script reference")
    else:
        print("❌ Missing browse.js script reference")

    # Check for CSS
    if 'style.css' in content:
        print("✅ Found style.css reference")
    else:
        print("❌ Missing style.css reference")

    # Look for the first few inscription items
    first_item_match = re.search(r'<div class="clean-inscription-item"[^>]*data-id="([^"]*)"', content)
    if first_item_match:
        print(f"✅ First inscription ID: {first_item_match.group(1)}")
    else:
        print("❌ No inscription items found in HTML")

    # Check if items might be hidden by inline styles
    hidden_items = re.findall(r'style="[^"]*display:\s*none', content)
    if hidden_items:
        print(f"⚠️ Found {len(hidden_items)} items with display:none")

    # Extract a sample inscription item
    sample_match = re.search(r'(<div class="clean-inscription-item".*?</div>\s*</div>)', content, re.DOTALL)
    if sample_match:
        sample_item = sample_match.group(1)
        print(f"\n📝 Sample inscription item:")
        print("-" * 30)
        # Show first 500 characters
        print(sample_item[:500] + "..." if len(sample_item) > 500 else sample_item)
        print("-" * 30)

    # Check the JavaScript variables
    js_file = Path("../output/static/js/browse.js")
    if js_file.exists():
        print(f"\n📜 browse.js exists ({js_file.stat().st_size} bytes)")
    else:
        print(f"\n❌ browse.js missing")

    # Check CSS file
    css_file = Path("../output/static/css/style.css")
    if css_file.exists():
        print(f"🎨 style.css exists ({css_file.stat().st_size} bytes)")
    else:
        print(f"❌ style.css missing")

if __name__ == "__main__":
    debug_browse_html()
