import os
from pathlib import Path

def create_vanilla_tab_version():
    """Create inscription pages with vanilla JavaScript tabs"""

    # First, let's update the robust processor to use vanilla JS
    print("🔧 Creating vanilla JavaScript version...")

    # For now, let's just fix one inscription page as a test
    inscriptions_dir = "output/inscriptions"
    html_files = list(Path(inscriptions_dir).glob("*.html"))

    if html_files:
        test_file = html_files[0]  # Take the first one

        vanilla_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Inscription - ECG</title>
    <link rel="stylesheet" href="../static/css/style.css">
    <style>
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .tabs button.active {{
            border-bottom-color: #2c3e50;
            color: #2c3e50;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="../index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
            <div class="nav-links">
                <a href="../index.html">Home</a>
                <a href="../browse.html">Browse</a>
            </div>
        </div>
    </nav>

    <main class="container">
        <div class="inscription-header">
            <h1>Test Inscription with Working Tabs</h1>
            <div class="inscription-meta">
                <span class="id">🆔 TEST001</span>
                <span class="lang">🌐 ka</span>
            </div>
        </div>

        <div class="tabs">
            <button onclick="showTab('overview')" id="tab-overview" class="active">Overview</button>
            <button onclick="showTab('text')" id="tab-text">Text</button>
            <button onclick="showTab('translation')" id="tab-translation">Translation</button>
            <button onclick="showTab('xml')" id="tab-xml">XML Source</button>
        </div>

        <div id="content-overview" class="tab-content active">
            <div class="overview">
                <div class="summary">
                    <h3>Summary</h3>
                    <p>This is a test inscription to verify that the tab functionality is working properly.</p>
                </div>

                <div class="metadata">
                    <h3>Metadata</h3>
                    <dl>
                        <dt>ID</dt><dd>TEST001</dd>
                        <dt>Language</dt><dd>Georgian</dd>
                        <dt>Material</dt><dd>Stone</dd>
                    </dl>
                </div>
            </div>
        </div>

        <div id="content-text" class="tab-content">
            <div class="text-editions">
                <div class="edition">
                    <h3>Diplomatic Edition (ka)</h3>
                    <div class="edition-text">
                        ღუმურიში საგდუხტ დეოფალთა<br/>
                        დეოფლის წარწერა
                    </div>
                </div>
            </div>
        </div>

        <div id="content-translation" class="tab-content">
            <div class="translation">
                <p>Translation of the inscription would appear here.</p>
            </div>
        </div>

        <div id="content-xml" class="tab-content">
            <pre class="xml-source"><code>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;TEI xmlns="http://www.tei-c.org/ns/1.0"&gt;
    &lt;teiHeader&gt;
        &lt;fileDesc&gt;
            &lt;titleStmt&gt;
                &lt;title&gt;Test Inscription&lt;/title&gt;
            &lt;/titleStmt&gt;
        &lt;/fileDesc&gt;
    &lt;/teiHeader&gt;
&lt;/TEI&gt;</code></pre>
        </div>
    </main>

    <script>
        function showTab(tabName) {{
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => {{
                content.classList.remove('active');
            }});

            // Remove active class from all tab buttons
            const buttons = document.querySelectorAll('.tabs button');
            buttons.forEach(button => {{
                button.classList.remove('active');
            }});

            // Show the selected tab content
            const selectedContent = document.getElementById('content-' + tabName);
            if (selectedContent) {{
                selectedContent.classList.add('active');
            }}

            // Activate the selected tab button
            const selectedButton = document.getElementById('tab-' + tabName);
            if (selectedButton) {{
                selectedButton.classList.add('active');
            }}
        }}

        // Initialize the first tab as active
        document.addEventListener('DOMContentLoaded', function() {{
            showTab('overview');
        }});
    </script>
</body>
</html>"""

        # Save as a test file
        with open("output/test-vanilla-tabs.html", 'w', encoding='utf-8') as f:
            f.write(vanilla_html)

        print(f"✅ Created vanilla JavaScript test page:")
        print(f"🌐 Open: file://{Path('output/test-vanilla-tabs.html').absolute()}")

if __name__ == "__main__":
    create_vanilla_tab_version()
