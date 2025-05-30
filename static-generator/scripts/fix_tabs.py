import os
from pathlib import Path

def fix_inscription_pages():
    """Fix the tab functionality in inscription pages"""

    inscriptions_dir = "output/inscriptions"

    if not os.path.exists(inscriptions_dir):
        print("❌ Inscriptions directory not found!")
        return

    html_files = list(Path(inscriptions_dir).glob("*.html"))
    print(f"🔧 Fixing tabs in {len(html_files)} inscription pages...")

    fixed = 0

    for html_file in html_files:
        try:
            # Read the current file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace the problematic Alpine.js syntax
            # Fix the x-data syntax
            content = content.replace(
                'x-data="{{{{ activeTab: \'overview\' }}}}"',
                'x-data="{ activeTab: \'overview\' }"'
            )

            # Fix the :class syntax
            content = content.replace(
                ':class="{{{{ active: activeTab === \'overview\' }}}}"',
                ':class="{ active: activeTab === \'overview\' }"'
            )
            content = content.replace(
                ':class="{{{{ active: activeTab === \'text\' }}}}"',
                ':class="{ active: activeTab === \'text\' }"'
            )
            content = content.replace(
                ':class="{{{{ active: activeTab === \'xml\' }}}}"',
                ':class="{ active: activeTab === \'xml\' }"'
            )

            # Write the fixed content back
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)

            fixed += 1

        except Exception as e:
            print(f"❌ Error fixing {html_file.name}: {e}")

    print(f"✅ Fixed {fixed} inscription pages")

    # Also create a simple test page to verify tabs work
    create_test_page()

def create_test_page():
    """Create a simple test page to verify tabs work"""

    test_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tab Test - ECG</title>
    <link rel="stylesheet" href="../static/css/style.css">
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="../index.html" class="brand">ECG - Tab Test</a>
        </div>
    </nav>

    <main class="container" x-data="{ activeTab: 'tab1' }">
        <h1>Tab Functionality Test</h1>

        <div class="tabs">
            <button @click="activeTab = 'tab1'" :class="{ active: activeTab === 'tab1' }">Tab 1</button>
            <button @click="activeTab = 'tab2'" :class="{ active: activeTab === 'tab2' }">Tab 2</button>
            <button @click="activeTab = 'tab3'" :class="{ active: activeTab === 'tab3' }">Tab 3</button>
        </div>

        <div x-show="activeTab === 'tab1'" class="tab-content">
            <h2>Tab 1 Content</h2>
            <p>This is the content of tab 1. If you can see this, the tabs are working!</p>
        </div>

        <div x-show="activeTab === 'tab2'" class="tab-content">
            <h2>Tab 2 Content</h2>
            <p>This is the content of tab 2. Click between tabs to test the functionality.</p>
        </div>

        <div x-show="activeTab === 'tab3'" class="tab-content">
            <h2>Tab 3 Content</h2>
            <p>This is the content of tab 3. The Alpine.js library should handle the tab switching.</p>
        </div>
    </main>
</body>
</html>"""

    with open("output/test-tabs.html", 'w', encoding='utf-8') as f:
        f.write(test_html)

    print(f"✅ Created test page: file://{Path('output/test-tabs.html').absolute()}")

if __name__ == "__main__":
    fix_inscription_pages()
