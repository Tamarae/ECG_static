import os
import json
import re
from lxml import etree
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class ECGProcessor:
    def __init__(self):
        # Set up Jinja2 templates
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.inscriptions = []

        # Path to your XML files (relative to static-generator folder)
        self.xml_dir = "../webapps/ROOT/content/xml/epidoc"
        self.output_dir = "output"

        # TEI namespace
        self.ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    def test_xml_access(self):
        """Test if we can access your XML files"""
        xml_path = Path(self.xml_dir)
        if not xml_path.exists():
            print(f"❌ XML directory not found: {xml_path.absolute()}")
            return False

        xml_files = list(xml_path.glob("ECG*.xml"))
        print(f"✅ Found {len(xml_files)} ECG XML files")

        if xml_files:
            print("First few files:")
            for i, f in enumerate(xml_files[:5]):
                print(f"  - {f.name}")

        return len(xml_files) > 0

    def examine_single_xml(self, xml_filename="ECG001.xml"):
        """Examine structure of a single XML file"""
        xml_path = Path(self.xml_dir) / xml_filename

        if not xml_path.exists():
            print(f"❌ File not found: {xml_path}")
            return

        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            print(f"\n📄 Examining {xml_filename}")
            print(f"Root element: {root.tag}")
            print(f"Namespaces: {root.nsmap}")

            # Look for common TEI elements
            title = root.xpath('.//tei:title', namespaces=self.ns)
            if title:
                print(f"Title: {title[0].text}")

            # Look for edition text
            edition = root.xpath('.//tei:div[@type="edition"]', namespaces=self.ns)
            print(f"Edition divs found: {len(edition)}")

            # Look for translation
            translation = root.xpath('.//tei:div[@type="translation"]', namespaces=self.ns)
            print(f"Translation divs found: {len(translation)}")

            # Look for bibliography
            bibl = root.xpath('.//tei:bibl', namespaces=self.ns)
            print(f"Bibliography entries found: {len(bibl)}")

            return True

        except Exception as e:
            print(f"❌ Error parsing {xml_filename}: {e}")
            return False

    def process_single_xml_basic(self, xml_path):
        """Basic processing of a single XML file"""
        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            # Extract ECG ID from filename
            ecg_id = xml_path.stem

            # Basic extraction - we'll improve this based on your XML structure
            inscription = {
                'id': ecg_id,
                'filename': xml_path.name,
                'title': self.safe_extract_text(root, './/tei:title'),
                'xml_content': etree.tostring(root, encoding='unicode', pretty_print=True)
            }

            # Try to extract more fields
            inscription.update({
                'summary': self.safe_extract_text(root, './/tei:summary'),
                'date': self.safe_extract_text(root, './/tei:origDate'),
                'place': self.safe_extract_text(root, './/tei:placeName'),
                'material': self.safe_extract_text(root, './/tei:material'),
            })

            return inscription

        except Exception as e:
            print(f"Error processing {xml_path}: {e}")
            return None

    def safe_extract_text(self, root, xpath):
        """Safely extract text from XML element"""
        try:
            elements = root.xpath(xpath, namespaces=self.ns)
            if elements and elements[0].text:
                return elements[0].text.strip()
        except:
            pass
        return ""

    def test_process_few(self, count=3):
        """Test processing a few XML files"""
        xml_files = list(Path(self.xml_dir).glob("ECG*.xml"))[:count]

        print(f"\n🧪 Testing processing of {len(xml_files)} files...")

        for xml_file in xml_files:
            inscription = self.process_single_xml_basic(xml_file)
            if inscription:
                print(f"✅ {inscription['id']}: {inscription['title']}")
                self.inscriptions.append(inscription)
            else:
                print(f"❌ Failed to process {xml_file.name}")

        return len(self.inscriptions)

    def generate_test_page(self):
        """Generate a simple test HTML page"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECG Test - {{ inscriptions|length }} Inscriptions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; }
        .inscription { border: 1px solid #ddd; margin: 1rem 0; padding: 1rem; }
        .inscription h3 { margin-top: 0; color: #333; }
        .metadata { color: #666; font-size: 0.9em; }
        .xml-preview { background: #f5f5f5; padding: 0.5rem; margin-top: 0.5rem;
                      white-space: pre-wrap; font-family: monospace; max-height: 200px;
                      overflow-y: auto; }
    </style>
</head>
<body>
    <h1>ECG Static Generator Test</h1>
    <p>Successfully processed {{ inscriptions|length }} inscriptions</p>

    {% for inscription in inscriptions %}
    <div class="inscription">
        <h3>{{ inscription.id }} - {{ inscription.title or 'Untitled' }}</h3>
        <div class="metadata">
            {% if inscription.date %}<strong>Date:</strong> {{ inscription.date }}<br>{% endif %}
            {% if inscription.place %}<strong>Place:</strong> {{ inscription.place }}<br>{% endif %}
            {% if inscription.material %}<strong>Material:</strong> {{ inscription.material }}<br>{% endif %}
        </div>
        <details>
            <summary>View XML Preview</summary>
            <div class="xml-preview">{{ inscription.xml_content[:500] }}...</div>
        </details>
    </div>
    {% endfor %}
</body>
</html>
        """

        template = self.env.from_string(html_template)
        html = template.render(inscriptions=self.inscriptions)

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Write test file
        output_path = f"{self.output_dir}/test.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n✅ Generated test page: {Path(output_path).absolute()}")
        print(f"Open in browser: file://{Path(output_path).absolute()}")

def main():
    processor = ECGProcessor()

    print("🚀 ECG Static Generator - Local Test")
    print("=" * 50)

    # Step 1: Test XML access
    if not processor.test_xml_access():
        print("\n❌ Cannot access XML files. Please check the path.")
        return

    # Step 2: Examine a single XML file
    processor.examine_single_xml()

    # Step 3: Test processing a few files
    processed_count = processor.test_process_few()

    if processed_count > 0:
        # Step 4: Generate test HTML
        processor.generate_test_page()
        print(f"\n🎉 Success! Generated test page with {processed_count} inscriptions")
    else:
        print("\n❌ No inscriptions were processed successfully")

if __name__ == "__main__":
    main()
