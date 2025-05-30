#!/usr/bin/env python3
"""
Test script to verify CSS generation and integration
Run this to test if your enhanced CSS generator is working
"""

import os
import sys
from pathlib import Path

def test_css_generation():
    """Test CSS generation and create a sample HTML file"""

    # Find the ecg_processor directory
    current_dir = Path(__file__).parent

    # Look for ecg_processor directory
    ecg_processor_dir = None
    if (current_dir / "ecg_processor").exists():
        ecg_processor_dir = current_dir / "ecg_processor"
    elif current_dir.name == "ecg_processor":
        ecg_processor_dir = current_dir
    elif (current_dir.parent / "ecg_processor").exists():
        ecg_processor_dir = current_dir.parent / "ecg_processor"

    if ecg_processor_dir is None:
        print("✗ Could not find ecg_processor directory")
        print("Current directory:", current_dir)
        print("Available directories:", [d.name for d in current_dir.iterdir() if d.is_dir()])
        return False

    print(f"Found ecg_processor at: {ecg_processor_dir}")
    sys.path.insert(0, str(ecg_processor_dir))

    try:
        from generators.css_generator import CSSGenerator
        print("✓ Successfully imported CSSGenerator")
    except ImportError as e:
        print(f"✗ Failed to import CSSGenerator: {e}")
        print("Available files in generators/:")
        generators_dir = ecg_processor_dir / "generators"
        if generators_dir.exists():
            print([f.name for f in generators_dir.iterdir()])
        else:
            print("generators/ directory not found")
        return False

    # Create test output directory
    test_dir = project_root / "test_output"
    test_dir.mkdir(exist_ok=True)

    # Initialize CSS generator
    config = {}  # Empty config for testing
    css_gen = CSSGenerator(config)

    # Generate CSS files
    try:
        css_gen.save_css_files(str(test_dir))
        print("✓ CSS files generated successfully")
    except Exception as e:
        print(f"✗ Failed to generate CSS: {e}")
        return False

    # Check generated files
    expected_files = [
        'css/main.css',
        'css/themes.css',
        'css/search.css',
        'css/filter.css',
        'css/modal.css',
        'css/table.css',
        'css/form.css'
    ]

    for css_file in expected_files:
        file_path = test_dir / css_file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✓ {css_file} ({size:,} bytes)")
        else:
            print(f"✗ Missing: {css_file}")

    # Create a test HTML file to see the styling
    create_test_html(test_dir)

    return True

def create_test_html(output_dir):
    """Create a test HTML file with Georgian inscription styling"""

    html_content = """<!DOCTYPE html>
<html lang="ka">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ქართული ეპიგრაფიული კორპუსი - ტესტი</title>
    <link rel="stylesheet" href="css/main.css">
    <link rel="stylesheet" href="css/themes.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1 class="georgian">ქართული ეპიგრაფიული კორპუსი</h1>
            <p class="subtitle">Georgian Epigraphic Corpus - Test Page</p>
        </div>
    </header>

    <nav class="nav">
        <div class="container">
            <ul class="nav-list">
                <li class="nav-item"><a href="#" class="active">მთავარი</a></li>
                <li class="nav-item"><a href="#">ეპიგრაფები</a></li>
                <li class="nav-item"><a href="#">ბიბლიოგრაფია</a></li>
            </ul>
        </div>
    </nav>

    <main class="main">
        <div class="container">
            <div class="content-section">
                <h2 class="georgian">ნიმუში ეპიგრაფი</h2>

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
            </div>

            <div class="bibliography">
                <h3>ბიბლიოგრაფია</h3>
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
        // Test dark theme toggle
        function toggleTheme() {
            const body = document.body;
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            body.setAttribute('data-theme', newTheme);
        }

        // Add theme toggle button
        const nav = document.querySelector('.nav-list');
        const themeToggle = document.createElement('li');
        themeToggle.className = 'nav-item';
        themeToggle.innerHTML = '<a href="#" onclick="toggleTheme()">🌓 Theme</a>';
        nav.appendChild(themeToggle);
    </script>
</body>
</html>"""

    html_file = output_dir / "test.html"
    html_file.write_text(html_content, encoding='utf-8')
    print(f"✓ Created test HTML file: {html_file}")
    print(f"  Open {html_file.absolute()} in your browser to see the styling")

if __name__ == "__main__":
    print("Testing Enhanced CSS Generator for ECG Processor")
    print("=" * 50)

    if test_css_generation():
        print("\n✓ All tests passed!")
        print("\nNext steps:")
        print("1. Open test_output/test.html in your browser")
        print("2. Verify Georgian fonts are loading properly")
        print("3. Test the theme toggle button")
        print("4. Update your main ecg_processor_test.py to use the new CSS classes")
    else:
        print("\n✗ Tests failed. Check the error messages above.")
