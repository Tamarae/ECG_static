import os
import json
from lxml import etree
from pathlib import Path

class ECGWorkingProcessor:
    def __init__(self):
        self.xml_dir = "../webapps/ROOT/content/xml/epidoc"
        self.output_dir = "output"
        self.ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        self.inscriptions = []

    def process_all(self):
        """Process all XML files"""
        print("🚀 Processing ECG inscriptions...")

        # Create directories
        os.makedirs(f"{self.output_dir}/inscriptions", exist_ok=True)
        os.makedirs(f"{self.output_dir}/static/css", exist_ok=True)

        xml_files = sorted(list(Path(self.xml_dir).glob("ECG*.xml")))
        print(f"Found {len(xml_files)} XML files")

        successful = 0
        failed = 0

        # Process each file
        for xml_file in xml_files:
            try:
                inscription = self.process_single_xml(xml_file)
                if inscription:
                    self.inscriptions.append(inscription)
                    self.create_inscription_page(inscription)
                    successful += 1

                    if successful % 50 == 0:
                        print(f"✅ Processed {successful} inscriptions...")
                else:
                    failed += 1

            except Exception as e:
                print(f"❌ Failed {xml_file.name}: {str(e)[:100]}")
                failed += 1

        # Generate site pages
        self.create_index_page()
        self.create_browse_page()
        self.create_search_data()
        self.create_css()

        print(f"\n🎉 Site generated successfully!")
        print(f"✅ Processed: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Output: {Path(self.output_dir).absolute()}")
        print(f"🌐 Open: file://{Path(self.output_dir).absolute()}/index.html")

        return successful

    def process_single_xml(self, xml_path):
        """Process a single XML file"""
        tree = etree.parse(str(xml_path))
        root = tree.getroot()

        ecg_id = xml_path.stem

        # Extract data
        inscription = {
            'id': ecg_id,
            'filename': xml_path.name,
            'title': self.extract_title(root),
            'summary': self.extract_summary(root),
            'dating': self.extract_dating(root),
            'origin': self.extract_origin(root),
            'material': self.extract_material(root),
            'dimensions': self.extract_dimensions(root),
            'text_content': self.extract_text_content(root),
            'translation': self.extract_translation(root),
            'commentary': self.extract_commentary(root),
            'bibliography': self.extract_bibliography(root),
            'language': self.detect_language(root),
            'xml_source': etree.tostring(root, encoding='unicode', pretty_print=True)
        }

        return inscription

    def extract_title(self, root):
        """Extract title"""
        title_elem = root.xpath('.//tei:titleStmt/tei:title', namespaces=self.ns)
        if title_elem and title_elem[0].text:
            return title_elem[0].text.strip()
        return f"Inscription {root.xpath('.//tei:idno', namespaces=self.ns)[0].text if root.xpath('.//tei:idno', namespaces=self.ns) else 'Unknown'}"

    def extract_summary(self, root):
        """Extract summary"""
        summary_elem = root.xpath('.//tei:summary', namespaces=self.ns)
        if summary_elem:
            return self.get_element_text(summary_elem[0])
        return ""

    def extract_dating(self, root):
        """Extract dating information"""
        date_elem = root.xpath('.//tei:origDate', namespaces=self.ns)
        if date_elem:
            elem = date_elem[0]
            return {
                'when': elem.get('when', ''),
                'not_before': elem.get('notBefore', ''),
                'not_after': elem.get('notAfter', ''),
                'period': elem.get('period', ''),
                'text': self.get_element_text(elem)
            }
        return {}

    def extract_origin(self, root):
        """Extract origin/findspot"""
        origin_elem = root.xpath('.//tei:provenance[@type="found"]', namespaces=self.ns)
        if origin_elem:
            place_elem = origin_elem[0].xpath('.//tei:placeName', namespaces=self.ns)
            return {
                'place': place_elem[0].text.strip() if place_elem and place_elem[0].text else '',
                'text': self.get_element_text(origin_elem[0])
            }
        return {}

    def extract_material(self, root):
        """Extract material"""
        material_elem = root.xpath('.//tei:material', namespaces=self.ns)
        if material_elem and material_elem[0].text:
            return material_elem[0].text.strip()
        return ""

    def extract_dimensions(self, root):
        """Extract dimensions"""
        dims_elem = root.xpath('.//tei:dimensions', namespaces=self.ns)
        if dims_elem:
            dims = dims_elem[0]
            height = dims.xpath('./tei:height', namespaces=self.ns)
            width = dims.xpath('./tei:width', namespaces=self.ns)
            depth = dims.xpath('./tei:depth', namespaces=self.ns)

            return {
                'height': height[0].text if height and height[0].text else '',
                'width': width[0].text if width and width[0].text else '',
                'depth': depth[0].text if depth and depth[0].text else '',
                'unit': dims.get('unit', 'cm')
            }
        return {}

    def extract_text_content(self, root):
        """Extract inscription text content"""
        text_content = {}

        # Look for edition divs
        edition_divs = root.xpath('.//tei:div[@type="edition"]', namespaces=self.ns)

        for div in edition_divs:
            subtype = div.get('subtype', 'default')
            lang = div.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

            # Process the text
            text = self.process_edition_text(div)

            key = f"{subtype}_{lang}" if subtype != 'default' else lang
            text_content[key] = {
                'subtype': subtype,
                'language': lang,
                'content': text
            }

        return text_content

    def process_edition_text(self, div):
        """Process edition text with basic EpiDoc conversion"""
        # Get all text content
        text_parts = []

        for elem in div.iter():
            if elem.tag.endswith('}lb'):  # Line break
                text_parts.append('<br/>')
            elif elem.tag.endswith('}supplied'):  # Supplied text
                text_parts.append(f'[{elem.text or ""}]')
            elif elem.tag.endswith('}unclear'):  # Unclear text
                text_parts.append(f'({elem.text or ""})')
            elif elem.tag.endswith('}gap'):  # Gap
                text_parts.append('[...]')
            elif elem.text:
                text_parts.append(elem.text)
            if elem.tail:
                text_parts.append(elem.tail)

        return ''.join(text_parts).strip()

    def extract_translation(self, root):
        """Extract translation"""
        trans_elem = root.xpath('.//tei:div[@type="translation"]', namespaces=self.ns)
        if trans_elem:
            return self.get_element_text(trans_elem[0])
        return ""

    def extract_commentary(self, root):
        """Extract commentary"""
        comm_elem = root.xpath('.//tei:div[@type="commentary"]', namespaces=self.ns)
        if comm_elem:
            return self.get_element_text(comm_elem[0])
        return ""

    def extract_bibliography(self, root):
        """Extract bibliography"""
        bibl_elems = root.xpath('.//tei:listBibl//tei:bibl', namespaces=self.ns)
        bibliography = []
        for bibl in bibl_elems:
            bibliography.append(self.get_element_text(bibl))
        return bibliography

    def detect_language(self, root):
        """Detect primary language"""
        # Check xml:lang attribute
        lang_attrs = root.xpath('.//@xml:lang')
        if lang_attrs:
            return lang_attrs[0]

        # Simple detection based on content
        all_text = ' '.join(root.itertext())

        if any(ord(char) >= 0x10A0 and ord(char) <= 0x10FF for char in all_text):
            return 'ka'  # Georgian
        elif any(ord(char) >= 0x0370 and ord(char) <= 0x03FF for char in all_text):
            return 'grc'  # Greek
        else:
            return 'unknown'

    def get_element_text(self, elem):
        """Get all text content from element"""
        if elem is None:
            return ""
        return ' '.join(elem.itertext()).strip()

    def create_inscription_page(self, inscription):
        """Create individual inscription page"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{inscription['title']} - ECG</title>
    <link rel="stylesheet" href="../static/css/style.css">
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
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

    <main class="container" x-data="{{ activeTab: 'overview' }}">
        <div class="inscription-header">
            <h1>{inscription['title']}</h1>
            <div class="inscription-meta">
                <span class="id">🆔 {inscription['id']}</span>
                {f'<span class="date">📅 {inscription["dating"]["text"]}</span>' if inscription['dating'].get('text') else ''}
                {f'<span class="place">📍 {inscription["origin"]["place"]}</span>' if inscription['origin'].get('place') else ''}
                {f'<span class="material">🔨 {inscription["material"]}</span>' if inscription['material'] else ''}
                <span class="lang">🌐 {inscription['language']}</span>
            </div>
        </div>

        <div class="tabs">
            <button @click="activeTab = 'overview'" :class="{{ active: activeTab === 'overview' }}">Overview</button>
            <button @click="activeTab = 'text'" :class="{{ active: activeTab === 'text' }}">Text</button>
            {'<button @click="activeTab = \'translation\'" :class="{ active: activeTab === \'translation\' }">Translation</button>' if inscription['translation'] else ''}
            <button @click="activeTab = 'xml'" :class="{{ active: activeTab === 'xml' }}">XML Source</button>
        </div>

        <div x-show="activeTab === 'overview'" class="tab-content">
            <div class="overview">
                {f'<div class="summary"><h3>Summary</h3><p>{inscription["summary"]}</p></div>' if inscription['summary'] else ''}

                <div class="metadata">
                    <h3>Metadata</h3>
                    <dl>
                        <dt>Inscription ID</dt><dd>{inscription['id']}</dd>
                        <dt>Language</dt><dd>{inscription['language']}</dd>
                        {f'<dt>Dating</dt><dd>{inscription["dating"]["text"]}</dd>' if inscription['dating'].get('text') else ''}
                        {f'<dt>Origin</dt><dd>{inscription["origin"]["text"]}</dd>' if inscription['origin'].get('text') else ''}
                        {f'<dt>Material</dt><dd>{inscription["material"]}</dd>' if inscription['material'] else ''}
                    </dl>
                </div>

                {'<div class="bibliography"><h3>Bibliography</h3><ul>' + ''.join([f'<li>{bib}</li>' for bib in inscription['bibliography']]) + '</ul></div>' if inscription['bibliography'] else ''}
            </div>
        </div>

        <div x-show="activeTab === 'text'" class="tab-content">
            <div class="text-editions">
                {self.format_text_editions(inscription['text_content'])}
            </div>
        </div>

        {'<div x-show="activeTab === \'translation\'" class="tab-content"><div class="translation">' + inscription['translation'] + '</div></div>' if inscription['translation'] else ''}

        <div x-show="activeTab === 'xml'" class="tab-content">
            <pre class="xml-source"><code>{inscription['xml_source']}</code></pre>
        </div>
    </main>
</body>
</html>"""

        with open(f"{self.output_dir}/inscriptions/{inscription['id']}.html", 'w', encoding='utf-8') as f:
            f.write(html)

    def format_text_editions(self, text_content):
        """Format text editions for display"""
        if not text_content:
            return "<p>No text content available.</p>"

        html_parts = []
        for key, edition in text_content.items():
            html_parts.append(f"""
                <div class="edition">
                    <h3>{edition['subtype'].title()} ({edition['language']})</h3>
                    <div class="edition-text">{edition['content']}</div>
                </div>
            """)

        return ''.join(html_parts)

    def create_index_page(self):
        """Create homepage"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECG - Epigraphic Corpus of Georgia</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
            <div class="nav-links">
                <a href="browse.html">Browse</a>
            </div>
        </div>
    </nav>

    <main class="container">
        <div class="hero">
            <h1>Epigraphic Corpus of Georgia</h1>
            <p>Digital edition of {len(self.inscriptions)} ancient and medieval inscriptions from Georgia</p>
        </div>

        <div class="recent-inscriptions">
            <h2>Recent Inscriptions</h2>
            <div class="inscription-grid">
                {self.format_inscription_cards(self.inscriptions[:12])}
            </div>
        </div>
    </main>
</body>
</html>"""

        with open(f"{self.output_dir}/index.html", 'w', encoding='utf-8') as f:
            f.write(html)

    def create_browse_page(self):
        """Create browse page"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Browse - ECG</title>
    <link rel="stylesheet" href="static/css/style.css">
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
            <div class="nav-links">
                <a href="index.html">Home</a>
                <a href="browse.html">Browse</a>
            </div>
        </div>
    </nav>

    <main class="container" x-data="browseData()">
        <div class="browse-header">
            <h1>Browse Inscriptions</h1>
            <div class="search-box">
                <input type="text" x-model="searchTerm" placeholder="Search inscriptions..." class="search-input">
            </div>
        </div>

        <div class="browse-content">
            <div class="inscription-grid">
                <template x-for="inscription in filteredInscriptions" :key="inscription.id">
                    <div class="inscription-card">
                        <h3><a :href="'inscriptions/' + inscription.id + '.html'" x-text="inscription.title"></a></h3>
                        <div class="inscription-meta">
                            <span x-text="inscription.id"></span>
                            <span x-show="inscription.place" x-text="inscription.place"></span>
                        </div>
                    </div>
                </template>
            </div>
        </div>
    </main>

    <script>
        function browseData() {{
            return {{
                searchTerm: '',
                inscriptions: {json.dumps([{
                    'id': i['id'],
                    'title': i['title'],
                    'place': i['origin'].get('place', ''),
                    'date': i['dating'].get('text', '')
                } for i in self.inscriptions])},
                get filteredInscriptions() {{
                    if (!this.searchTerm) return this.inscriptions;
                    return this.inscriptions.filter(i =>
                        i.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                        i.id.toLowerCase().includes(this.searchTerm.toLowerCase())
                    );
                }}
            }}
        }}
    </script>
</body>
</html>"""

        with open(f"{self.output_dir}/browse.html", 'w', encoding='utf-8') as f:
            f.write(html)

    def format_inscription_cards(self, inscriptions):
        """Format inscription cards"""
        cards = []
        for inscription in inscriptions:
            cards.append(f"""
                <div class="inscription-card">
                    <h3><a href="inscriptions/{inscription['id']}.html">{inscription['title']}</a></h3>
                    <div class="inscription-meta">
                        <span class="id">{inscription['id']}</span>
                        {f'<span class="place">{inscription["origin"]["place"]}</span>' if inscription['origin'].get('place') else ''}
                        <span class="lang">{inscription['language']}</span>
                    </div>
                </div>
            """)
        return ''.join(cards)

    def create_search_data(self):
        """Create JSON search data"""
        search_data = []
        for inscription in self.inscriptions:
            search_data.append({
                'id': inscription['id'],
                'title': inscription['title'],
                'summary': inscription['summary'],
                'place': inscription['origin'].get('place', ''),
                'date': inscription['dating'].get('text', ''),
                'language': inscription['language'],
                'url': f"inscriptions/{inscription['id']}.html"
            })

        with open(f"{self.output_dir}/search-data.json", 'w', encoding='utf-8') as f:
            json.dump(search_data, f, ensure_ascii=False, indent=2)

    def create_css(self):
        """Create basic CSS"""
        css = """
/* ECG Static Site Styles */
* { box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Navigation */
.navbar {
    background: #2c3e50;
    color: white;
    padding: 1rem 0;
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand {
    font-size: 1.25rem;
    font-weight: bold;
    color: white;
    text-decoration: none;
}

.nav-links a {
    color: white;
    text-decoration: none;
    margin-left: 1rem;
}

.nav-links a:hover {
    text-decoration: underline;
}

/* Main Content */
main {
    padding: 2rem 0;
}

.hero {
    text-align: center;
    padding: 3rem 0;
    border-bottom: 1px solid #eee;
    margin-bottom: 2rem;
}

.hero h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: #2c3e50;
}

/* Inscription Cards */
.inscription-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.inscription-card {
    border: 1px solid #ddd;
    padding: 1.5rem;
    border-radius: 8px;
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.inscription-card h3 {
    margin-top: 0;
    margin-bottom: 1rem;
}

.inscription-card a {
    color: #2c3e50;
    text-decoration: none;
}

.inscription-card a:hover {
    text-decoration: underline;
}

.inscription-meta {
    font-size: 0.9rem;
    color: #666;
}

.inscription-meta span {
    margin-right: 1rem;
}

/* Individual Inscription Pages */
.inscription-header {
    border-bottom: 2px solid #2c3e50;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}

.inscription-header h1 {
    margin-bottom: 0.5rem;
    color: #2c3e50;
}

.inscription-meta span {
    background: #f8f9fa;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.9rem;
    margin-right: 0.5rem;
    display: inline-block;
    margin-bottom: 0.5rem;
}

/* Tabs */
.tabs {
    display: flex;
    border-bottom: 1px solid #ddd;
    margin-bottom: 2rem;
}

.tabs button {
    background: none;
    border: none;
    padding: 1rem 1.5rem;
    cursor: pointer;
    border-bottom: 2px solid transparent;
}

.tabs button.active {
    border-bottom-color: #2c3e50;
    color: #2c3e50;
    font-weight: bold;
}

.tabs button:hover {
    background: #f8f9fa;
}

/* Tab Content */
.tab-content {
    min-height: 300px;
}

.overview dl {
    display: grid;
    grid-template-columns: 150px 1fr;
    gap: 0.5rem 1rem;
}

.overview dt {
    font-weight: bold;
    color: #2c3e50;
}

.edition {
    margin-bottom: 2rem;
    padding: 1rem;
    border: 1px solid #eee;
    border-radius: 4px;
}

.edition h3 {
    margin-top: 0;
    color: #2c3e50;
}

.edition-text {
    font-family: 'Courier New', monospace;
    line-height: 1.8;
    white-space: pre-line;
}

.xml-source {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 0.9rem;
}

/* Search */
.search-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.browse-header {
    margin-bottom: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
    .inscription-grid {
        grid-template-columns: 1fr;
    }

    .overview dl {
        grid-template-columns: 1fr;
    }

    .tabs {
        flex-wrap: wrap;
    }

    .tabs button {
        flex: 1;
        min-width: 120px;
    }
}
"""

        with open(f"{self.output_dir}/static/css/style.css", 'w', encoding='utf-8') as f:
            f.write(css)

if __name__ == "__main__":
    processor = ECGWorkingProcessor()
    processor.process_all()
