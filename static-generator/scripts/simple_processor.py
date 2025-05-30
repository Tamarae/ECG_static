import os
import json
from lxml import etree
from pathlib import Path

def process_simple():
    xml_dir = "../webapps/ROOT/content/xml/epidoc"
    output_dir = "output"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/inscriptions", exist_ok=True)

    xml_files = list(Path(xml_dir).glob("ECG*.xml"))
    print(f"Processing {len(xml_files)} XML files...")

    inscriptions = []
    successful = 0
    failed = 0

    for xml_file in xml_files[:10]:  # Process first 10 for testing
        try:
            # Parse XML
            tree = etree.parse(str(xml_file))
            root = tree.getroot()

            # Extract basic info
            ecg_id = xml_file.stem

            # Get all text content
            all_text = ' '.join(root.itertext()).strip()

            # Create basic inscription record
            inscription = {
                'id': ecg_id,
                'filename': xml_file.name,
                'title': f"Inscription {ecg_id}",
                'content': all_text[:500] + "..." if len(all_text) > 500 else all_text,
                'full_xml': etree.tostring(root, encoding='unicode', pretty_print=True)
            }

            inscriptions.append(inscription)

            # Create individual page
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{inscription['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 2rem; }}
        .header {{ border-bottom: 2px solid #333; padding-bottom: 1rem; }}
        .content {{ margin: 2rem 0; }}
        .xml {{ background: #f5f5f5; padding: 1rem; white-space: pre-wrap; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{inscription['title']}</h1>
        <p><strong>File:</strong> {inscription['filename']}</p>
    </div>
    <div class="content">
        <h2>Content Preview</h2>
        <p>{inscription['content']}</p>
        <h2>Full XML</h2>
        <div class="xml">{inscription['full_xml']}</div>
    </div>
</body>
</html>"""

            with open(f"{output_dir}/inscriptions/{ecg_id}.html", 'w', encoding='utf-8') as f:
                f.write(html_content)

            successful += 1
            print(f"✅ {ecg_id}")

        except Exception as e:
            print(f"❌ {xml_file.name}: {e}")
            failed += 1

    # Create index page
    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ECG Static Site - {len(inscriptions)} Inscriptions</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 2rem; }}
        .inscription {{ border: 1px solid #ddd; margin: 1rem 0; padding: 1rem; }}
        .inscription h3 {{ margin-top: 0; }}
    </style>
</head>
<body>
    <h1>ECG Static Site</h1>
    <p>Successfully processed {successful} inscriptions (Failed: {failed})</p>

    {''.join([f'''
    <div class="inscription">
        <h3><a href="inscriptions/{insc['id']}.html">{insc['title']}</a></h3>
        <p><strong>File:</strong> {insc['filename']}</p>
        <p>{insc['content'][:200]}...</p>
    </div>
    ''' for insc in inscriptions])}
</body>
</html>"""

    with open(f"{output_dir}/index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)

    print(f"\n🎉 Generated simple site:")
    print(f"📁 {Path(output_dir).absolute()}")
    print(f"🌐 Open: file://{Path(output_dir).absolute()}/index.html")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")

if __name__ == "__main__":
    process_simple()
