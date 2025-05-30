#!/usr/bin/env python3
"""
Simple test to generate CSS files directly without imports
Run this from your project root directory
"""

import os
from pathlib import Path

def create_css_files():
    """Create the enhanced CSS files directly"""

    # Create CSS directory
    css_dir = Path("test_output/css")
    css_dir.mkdir(parents=True, exist_ok=True)

    # Main CSS content (fixed version with proper specificity)
    main_css = """
/* Georgian Fonts - Load first for better performance */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Georgian:wght@100;200;300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+Georgian:wght@100;200;300;400;500;600;700;800;900&display=swap');

/* CSS Reset - Override user agent styles */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html, body {
    margin: 0 !important;
    padding: 0 !important;
}

:root {
    /* Georgian Fonts - Better fallback stack */
    --font-georgian-sans: 'Noto Sans Georgian', 'DejaVu Sans', 'Arial Unicode MS', sans-serif;
    --font-georgian-serif: 'Noto Serif Georgian', 'Times New Roman', 'DejaVu Serif', serif;
    --font-latin: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

    /* Color System */
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #e74c3c;
    --background-color: #ffffff;
    --surface-color: #f8f9fa;
    --border-color: #dee2e6;
    --text-primary: #2c3e50;
    --text-secondary: #6c757d;
    --text-muted: #adb5bd;

    /* Spacing System */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-xxl: 3rem;

    /* Typography Scale */
    --font-size-xs: 0.75rem;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;
    --font-size-2xl: 1.5rem;
    --font-size-3xl: 1.875rem;
    --font-size-4xl: 2.25rem;

    /* Visual Effects */
    --radius-sm: 0.25rem;
    --radius-base: 0.375rem;
    --radius-lg: 0.75rem;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
}

/* Base Body Styling - Override user agent styles */
body {
    font-family: var(--font-latin) !important;
    font-size: var(--font-size-base) !important;
    line-height: 1.6 !important;
    color: var(--text-primary) !important;
    background-color: var(--background-color) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Georgian Text Classes - High specificity */
.georgian,
body .georgian,
html .georgian {
    font-family: var(--font-georgian-sans) !important;
    font-feature-settings: "kern" 1, "liga" 1;
    text-rendering: optimizeLegibility;
    font-weight: 400;
}

.georgian-serif,
body .georgian-serif,
html .georgian-serif {
    font-family: var(--font-georgian-serif) !important;
    font-feature-settings: "kern" 1, "liga" 1;
    text-rendering: optimizeLegibility;
}

/* Typography Reset and Styling */
h1, h2, h3, h4, h5, h6,
body h1, body h2, body h3, body h4, body h5, body h6 {
    font-weight: 600 !important;
    line-height: 1.25 !important;
    margin: 0 0 var(--spacing-md) 0 !important;
    color: var(--text-primary) !important;
}

body h1, html h1 { font-size: var(--font-size-4xl) !important; }
body h2, html h2 { font-size: var(--font-size-3xl) !important; }
body h3, html h3 { font-size: var(--font-size-2xl) !important; }
body h4, html h4 { font-size: var(--font-size-xl) !important; }

p, body p {
    margin: 0 0 var(--spacing-md) 0 !important;
    color: var(--text-secondary);
}

a, body a {
    color: var(--secondary-color);
    text-decoration: none;
    transition: color 0.2s ease;
}

a:hover, body a:hover {
    color: var(--primary-color);
    text-decoration: underline;
}

/* Layout Components with High Specificity */
.container, body .container {
    max-width: 1200px;
    margin: 0 auto !important;
    padding: 0 var(--spacing-md) !important;
}

/* Header Styling */
.header, body .header {
    background-color: var(--primary-color) !important;
    color: white !important;
    padding: var(--spacing-lg) 0 !important;
    box-shadow: var(--shadow-md);
}

.header h1, body .header h1 {
    color: white !important;
    margin-bottom: var(--spacing-sm) !important;
    font-size: var(--font-size-3xl) !important;
}

.header .subtitle, body .header .subtitle {
    color: rgba(255, 255, 255, 0.8) !important;
    font-size: var(--font-size-lg) !important;
    margin: 0 !important;
}

/* Navigation */
.nav, body .nav {
    background-color: var(--surface-color) !important;
    border-bottom: 1px solid var(--border-color);
    padding: var(--spacing-md) 0 !important;
}

.nav-list, body .nav-list {
    display: flex !important;
    list-style: none !important;
    gap: var(--spacing-lg);
    flex-wrap: wrap;
    margin: 0 !important;
    padding: 0 !important;
}

.nav-item, body .nav-item {
    margin: 0 !important;
    padding: 0 !important;
}

.nav-item a, body .nav-item a {
    display: inline-block !important;
    padding: var(--spacing-sm) var(--spacing-md) !important;
    border-radius: var(--radius-base);
    transition: background-color 0.2s ease;
    text-decoration: none !important;
    color: var(--text-primary) !important;
}

.nav-item a:hover, body .nav-item a:hover,
.nav-item a.active, body .nav-item a.active {
    background-color: var(--secondary-color) !important;
    color: white !important;
    text-decoration: none !important;
}

/* Main Content */
.main, body .main {
    padding: var(--spacing-xxl) 0 !important;
    min-height: calc(100vh - 200px);
}

/* Card Components with Strong Specificity */
.card, body .card {
    background-color: var(--background-color) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--spacing-xl) !important;
    box-shadow: var(--shadow-base) !important;
    margin-bottom: var(--spacing-xl) !important;
    transition: box-shadow 0.2s ease;
}

.card:hover, body .card:hover {
    box-shadow: var(--shadow-md) !important;
}

/* Inscription Specific Styling */
.inscription, body .inscription {
    background-color: var(--surface-color) !important;
    border-left: 4px solid var(--secondary-color) !important;
    border-radius: 0 var(--radius-base) var(--radius-base) 0 !important;
}

.inscription-header, body .inscription-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    margin-bottom: var(--spacing-md) !important;
    flex-wrap: wrap;
    gap: var(--spacing-md);
}

.inscription-id, body .inscription-id {
    font-weight: 600 !important;
    color: var(--primary-color) !important;
    font-size: var(--font-size-lg) !important;
    margin: 0 !important;
}

.inscription-metadata, body .inscription-metadata {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) !important;
    gap: var(--spacing-md) !important;
    margin-bottom: var(--spacing-lg) !important;
}

.metadata-item, body .metadata-item {
    display: flex !important;
    flex-direction: column !important;
}

.metadata-label, body .metadata-label {
    font-size: var(--font-size-sm) !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: var(--spacing-xs) !important;
}

.metadata-value, body .metadata-value {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    margin: 0 !important;
}

.inscription-text, body .inscription-text {
    background-color: var(--background-color) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-base) !important;
    padding: var(--spacing-lg) !important;
    margin: var(--spacing-md) 0 !important;
}

.text-original, body .text-original {
    font-family: var(--font-georgian-serif) !important;
    font-size: var(--font-size-lg) !important;
    line-height: 1.8 !important;
    margin-bottom: var(--spacing-lg) !important;
    direction: ltr !important;
    color: var(--text-primary) !important;
}

.text-translation, body .text-translation {
    font-style: italic !important;
    color: var(--text-secondary) !important;
    border-top: 1px solid var(--border-color) !important;
    padding-top: var(--spacing-md) !important;
    margin: 0 !important;
}

/* Bibliography */
.bibliography, body .bibliography {
    background-color: var(--surface-color) !important;
    border-radius: var(--radius-base) !important;
    padding: var(--spacing-lg) !important;
    margin-top: var(--spacing-xxl) !important;
}

.bibliography h3, body .bibliography h3 {
    color: var(--primary-color) !important;
    margin-bottom: var(--spacing-lg) !important;
}

.bibliography-list, body .bibliography-list {
    list-style: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

.bibliography-item, body .bibliography-item {
    padding: var(--spacing-md) 0 !important;
    border-bottom: 1px solid var(--border-color) !important;
    margin: 0 !important;
}

.bibliography-item:last-child, body .bibliography-item:last-child {
    border-bottom: none !important;
}

/* Dark Theme */
[data-theme="dark"] {
    --primary-color: #34495e;
    --secondary-color: #5dade2;
    --background-color: #1a1a1a;
    --surface-color: #2d3748;
    --border-color: #4a5568;
    --text-primary: #f7fafc;
    --text-secondary: #e2e8f0;
    --text-muted: #a0aec0;
}

[data-theme="dark"] .card {
    background-color: var(--surface-color);
}

[data-theme="dark"] .inscription {
    background-color: #2a3441;
}

[data-theme="dark"] .text-original {
    background-color: var(--surface-color);
    color: var(--text-primary);
}

/* Responsive */
@media (max-width: 768px) {
    .container {
        padding: 0 var(--spacing-sm);
    }

    .inscription-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .inscription-metadata {
        grid-template-columns: 1fr;
    }

    .nav-list {
        flex-direction: column;
        gap: var(--spacing-sm);
    }
}
"""

    # Write CSS file
    with open(css_dir / "main.css", "w", encoding="utf-8") as f:
        f.write(main_css)

    print(f"✓ Created: {css_dir}/main.css")

    # Create test HTML
    create_test_html()

def create_test_html():
    """Create test HTML file"""
    html_content = """<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ქართული ეპიგრაფიული კორპუსი - ტესტი</title>
    <link rel="stylesheet" href="css/main.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1 class="georgian">ქართული ეპიგრაფიული კორპუსი</h1>
            <p class="subtitle">Georgian Epigraphic Corpus - Enhanced Styling Test</p>
        </div>
    </header>

    <nav class="nav">
        <div class="container">
            <ul class="nav-list">
                <li class="nav-item"><a href="#" class="active">მთავარი</a></li>
                <li class="nav-item"><a href="#">ეპიგრაფები</a></li>
                <li class="nav-item"><a href="#">ბიბლიოგრაფია</a></li>
                <li class="nav-item"><a href="#" onclick="toggleTheme()">🌓 Theme</a></li>
            </ul>
        </div>
    </nav>

    <main class="main">
        <div class="container">
            <h2 class="georgian">ნიმუშის ეპიგრაფები</h2>

            <div class="card inscription">
                <div class="inscription-header">
                    <h3 class="inscription-id">ECG-001</h3>
                    <div class="metadata-value">V-VI საუკუნეები</div>
                </div>

                <div class="inscription-metadata">
                    <div class="metadata-item">
                        <span class="metadata-label">ადგილმდებარეობა</span>
                        <span class="metadata-value georgian">თბილისი</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">მასალა</span>
                        <span class="metadata-value georgian">ქვა</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">ტიპი</span>
                        <span class="metadata-value georgian">საფლავის ეპიგრაფი</span>
                    </div>
                </div>

                <div class="inscription-text">
                    <div class="text-original georgian-serif">
                        + იოვანე ქრისტეს მონაა + <br>
                        რომელმან დაწერა ესე წიგნი <br>
                        ღმერთმან შეიწყალნოს იგი +
                    </div>
                    <div class="text-translation">
                        + John is a servant of Christ +<br>
                        Who wrote this book<br>
                        May God have mercy on him +
                    </div>
                </div>
            </div>

            <div class="card inscription">
                <div class="inscription-header">
                    <h3 class="inscription-id">ECG-002</h3>
                    <div class="metadata-value">VII საუკუნე</div>
                </div>

                <div class="inscription-metadata">
                    <div class="metadata-item">
                        <span class="metadata-label">ადგილმდებარეობა</span>
                        <span class="metadata-value georgian">მცხეთა</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">მასალა</span>
                        <span class="metadata-value georgian">ქვა</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">ტიპი</span>
                        <span class="metadata-value georgian">ეკლესიის ეპიგრაფი</span>
                    </div>
                </div>

                <div class="inscription-text">
                    <div class="text-original georgian-serif">
                        + ქრისტე ღმერთო აცხოვნე მე + <br>
                        სტეფანე ცოდვილი <br>
                        რომელმან აღავსო ესე ეკლესია +
                    </div>
                    <div class="text-translation">
                        + Christ God, save me +<br>
                        Stephen the sinner<br>
                        Who erected this church +
                    </div>
                </div>
            </div>

            <div class="bibliography">
                <h3 class="georgian">ბიბლიოგრაფია</h3>
                <ul class="bibliography-list">
                    <li class="bibliography-item">
                        Gagoshidze, Giorgi. "Georgian Inscriptions of the 5th-10th Centuries." Tbilisi, 2014.
                    </li>
                    <li class="bibliography-item">
                        Khintibidze, Elguja. "Early Christian Georgian Epigraphy." Tbilisi, 2012.
                    </li>
                </ul>
            </div>
        </div>
    </main>

    <script>
        function toggleTheme() {
            const body = document.body;
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            body.setAttribute('data-theme', newTheme);
        }
    </script>
</body>
</html>"""

    html_file = Path("test_output/test.html")
    html_file.write_text(html_content, encoding='utf-8')
    print(f"✓ Created test HTML: {html_file.absolute()}")

if __name__ == "__main__":
    print("Creating Enhanced CSS Test Files")
    print("=" * 40)

    create_css_files()

    print("\n✓ Done! Open test_output/test.html in your browser")
    print("  You should see:")
    print("  - Georgian fonts loading properly")
    print("  - Professional card-based layout")
    print("  - Dark/light theme toggle")
    print("  - Responsive design")
