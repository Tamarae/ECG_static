import os
import json
import re
from lxml import etree
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class ECGProcessorEnhanced:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.inscriptions = []
        self.xml_dir = "../webapps/ROOT/content/xml/epidoc"
        self.output_dir = "output"
        self.ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    def process_all_inscriptions(self):
        """Process all XML files and generate the complete site"""
        print("🔄 Processing all ECG inscriptions...")

        # Create output directories
        os.makedirs(f"{self.output_dir}/inscriptions", exist_ok=True)
        os.makedirs(f"{self.output_dir}/static/css", exist_ok=True)
        os.makedirs(f"{self.output_dir}/static/js", exist_ok=True)

        # Get all XML files
        xml_files = sorted(list(Path(self.xml_dir).glob("ECG*.xml")))
        print(f"Found {len(xml_files)} XML files to process...")

        processed = 0
        failed = 0

        for xml_file in xml_files:
            try:
                inscription = self.process_single_xml_detailed(xml_file)
                if inscription:
                    self.inscriptions.append(inscription)
                    self.generate_inscription_page(inscription)
                    processed += 1
                    if processed % 50 == 0:
                        print(f"Processed {processed}/{len(xml_files)} inscriptions...")
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Error processing {xml_file.name}: {e}")
                failed += 1

        print(f"\n✅ Processing complete!")
        print(f"   Successfully processed: {processed}")
        print(f"   Failed: {failed}")

        # Generate site pages
        self.generate_index_page()
        self.generate_browse_page()
        self.generate_search_index()
        self.copy_static_files()

        return processed

    def process_single_xml_detailed(self, xml_path):
        """Enhanced processing of a single XML file"""
        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            ecg_id = xml_path.stem

            inscription = {
                'id': ecg_id,
                'filename': xml_path.name,
                'title': self.extract_title(root),
                'summary': self.extract_summary(root),
                'dating': self.extract_dating(root),
                'origin': self.extract_origin(root),
                'material': self.extract_material(root),
                'dimensions': self.extract_dimensions(root),
                'text_editions': self.extract_text_editions(root),
                'translation': self.extract_translation(root),
                'commentary': self.extract_commentary(root),
                'bibliography': self.extract_bibliography(root),
                'images': self.extract_images(root),
                'language': self.detect_language(root),
                'xml_content': etree.tostring(root, encoding='unicode', pretty_print=True)
            }

            return inscription

        except Exception as e:
            print(f"Error processing {xml_path}: {e}")
            return None

    def extract_title(self, root):
        """Extract title with Georgian/English support"""
        # Try different title locations
        title_paths = [
            './/tei:titleStmt/tei:title',
            './/tei:title[@type="main"]',
            './/tei:title'
        ]

        for path in title_paths:
            elements = root.xpath(path, namespaces=self.ns)
            if elements and elements[0].text:
                return elements[0].text.strip()

        # Fallback to ID
        id_elem = root.xpath('.//tei:idno[@type="filename"]', namespaces=self.ns)
        if id_elem and id_elem[0].text:
            return f"Inscription {id_elem[0].text}"

        return "Untitled Inscription"

    def extract_text_editions(self, root):
        """Extract all text editions (diplomatic, interpretive, etc.)"""
        editions = {}

        # Look for different types of editions
        edition_divs = root.xpath('.//tei:div[@type="edition"]', namespaces=self.ns)

        for div in edition_divs:
            subtype = div.get('subtype', 'default')
            lang = div.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

            # Process the text content
            text_content = self.process_inscription_text(div)

            editions[f"{subtype}_{lang}"] = {
                'subtype': subtype,
                'language': lang,
                'content': text_content
            }

        return editions

    def process_inscription_text(self, text_elem):
        """Process inscription text preserving EpiDoc markup"""
        if text_elem is None:
            return ""

        # Clone the element to avoid modifying original
        elem_copy = etree.fromstring(etree.tostring(text_elem))

        # Convert EpiDoc elements to HTML
        self.transform_epidoc_to_html(elem_copy)

        # Get the transformed content
        content = etree.tostring(elem_copy, encoding='unicode', method='html')

        # Clean up the output
        content = re.sub(r'<div[^>]*>', '', content)
        content = re.sub(r'</div>', '', content)
        content = content.strip()

        return content

    def transform_epidoc_to_html(self, element):
        """Transform EpiDoc elements to HTML"""
        transformations = {
            'lb': 'br',
            'supplied': lambda e: f'[{e.text or ""}]',
            'unclear': lambda e: f'({e.text or ""})',
            'gap': '[...]',
            'hi': 'em'  # or 'strong' depending on @rend
        }

        # This is a simplified transformation
        # You might need to customize based on your specific EpiDoc usage
        for child in element:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

            if tag == 'lb':
                child.tag = 'br'
            elif tag == 'supplied':
                child.text = f'[{child.text or ""}]'
                child.tag = 'span'
                child.set('class', 'supplied')

        return element

    def detect_language(self, root):
        """Detect the primary language of the inscription"""
        lang_elem = root.xpath('.//@xml:lang', namespaces=self.ns)
        if lang_elem:
            return lang_elem[0]

        # Try to detect from content
        text_content = ' '.join(root.xpath('.//text()', namespaces=self.ns))

        # Simple Georgian detection (contains Georgian characters)
        if re.search(r'[\u10A0-\u10FF]', text_content):
            return 'ka'  # Georgian
        elif re.search(r'[α-ωΑ-Ω]', text_content):
            return 'grc'  # Ancient Greek
        else:
            return 'unknown'

    def extract_dating(self, root):
        """Extract dating with multiple format support"""
        date_elem = root.xpath('.//tei:origDate', namespaces=self.ns)
        if date_elem:
            return {
                'when': date_elem[0].get('when'),
                'not_before': date_elem[0].get('notBefore'),
                'not_after': date_elem[0].get('notAfter'),
                'period': date_elem[0].get('period'),
                'display_text': self.extract_mixed_content(date_elem[0])
            }
        return {}

    def extract_mixed_content(self, elem):
        """Extract mixed content preserving basic formatting"""
        if elem is None:
            return ""
        return ' '.join(elem.itertext()).strip()

    def generate_inscription_page(self, inscription):
        """Generate individual inscription HTML page"""
        template_content = self.get_inscription_template()
        template = self.env.from_string(template_content)

        html = template.render(inscription=inscription)

        output_path = f"{self.output_dir}/inscriptions/{inscription['id']}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def get_inscription_template(self):
        """Return the inscription template HTML"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ inscription.title }} - ECG</title>
    <link rel="stylesheet" href="../static/css/style.css">
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="../index.html" class="nav-brand">ECG - Epigraphic Corpus of Georgia</a>
            <div class="nav-links">
                <a href="../browse.html">Browse</a>
                <a href="../search.html">Search</a>
            </div>
        </div>
    </nav>

    <main class="container" x-data="{ activeTab: 'text' }">
        <div class="inscription-header">
            <h1>{{ inscription.title }}</h1>
            <div class="inscription-id">{{ inscription.id }}</div>

            <div class="metadata-summary">
                {% if inscription.dating.display_text %}
                <span class="date">📅 {{ inscription.dating.display_text }}</span>
                {% endif %}
                {% if inscription.origin.place %}
                <span class="place">📍 {{ inscription.origin.place }}</span>
                {% endif %}
                {% if inscription.material %}
                <span class="material">🔨 {{ inscription.material }}</span>
                {% endif %}
                {% if inscription.language %}
                <span class="language">🌐 {{ inscription.language }}</span>
                {% endif %}
            </div>
        </div>

        <div class="tabs">
            <button @click="activeTab = 'text'" :class="{ active: activeTab === 'text' }">Text</button>
            <button @click="activeTab = 'details'" :class="{ active: activeTab === 'details' }">Details</button>
            {% if inscription.translation %}
            <button @click="activeTab = 'translation'" :class="{ active: activeTab === 'translation' }">Translation</button>
            {% endif %}
            <button @click="activeTab = 'xml'" :class="{ active: activeTab === 'xml' }">XML</button>
        </div>

        <div x-show="activeTab === 'text'" class="tab-content">
            {% for edition_key, edition in inscription.text_editions.items() %}
            <div class="text-section">
                <h3>{{ edition.subtype|title }} Edition ({{ edition.language }})</h3>
                <div class="inscription-text">
                    {{ edition.content | safe }}
                </div>
            </div>
            {% endfor %}
        </div>

        <div x-show="activeTab === 'details'" class="tab-content">
            <dl class="details-list">
                <dt>ID</dt><dd>{{ inscription.id }}</dd>
                {% if inscription.dating.display_text %}
                <dt>Dating</dt><dd>{{ inscription.dating.display_text }}</dd>
                {% endif %}
                {% if inscription.material %}
                <dt>Material</dt><dd>{{ inscription.material }}</dd>
                {% endif %}
            </dl>
        </div>

        {% if inscription.translation %}
        <div x-show="activeTab === 'translation'" class="tab-content">
            {{ inscription.translation | safe }}
        </div>
        {% endif %}

        <div x-show="activeTab === 'xml'" class="tab-content">
            <pre><code>{{ inscription.xml_content }}</code></pre>
        </div>
    </main>
</body>
</html>'''

if __name__ == "__main__":
    processor = ECGProcessorEnhanced()

    print("🚀 ECG Enhanced Static Generator")
    print("=" * 50)

    processed = processor.process_all_inscriptions()

    if processed > 0:
        print(f"\n🎉 Generated complete site with {processed} inscriptions!")
        print(f"📁 Output directory: {Path(processor.output_dir).absolute()}")
        print(f"🌐 Open: file://{Path(processor.output_dir).absolute()}/index.html")
