import os
import json
import re
from lxml import etree
from pathlib import Path

class RobustECGProcessor:
    def __init__(self):
        self.xml_dir = "../webapps/ROOT/content/xml/epidoc"
        self.output_dir = "output"
        self.ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        self.inscriptions = []

    def process_all(self):
        """Process all XML files with robust error handling"""
        print("🚀 Processing ECG inscriptions with robust error handling...")

        # Create directories
        os.makedirs(f"{self.output_dir}/inscriptions", exist_ok=True)
        os.makedirs(f"{self.output_dir}/static/css", exist_ok=True)

        xml_files = sorted(list(Path(self.xml_dir).glob("ECG*.xml")))
        print(f"Found {len(xml_files)} XML files")

        successful = 0
        failed = 0
        failed_files = []

        # Process each file with detailed error tracking
        for i, xml_file in enumerate(xml_files):
            try:
                inscription = self.process_single_xml_robust(xml_file)
                if inscription:
                    self.inscriptions.append(inscription)
                    self.create_inscription_page_safe(inscription)
                    successful += 1

                    if successful % 25 == 0:
                        print(f"✅ Processed {successful}/{len(xml_files)} inscriptions...")
                else:
                    failed += 1
                    failed_files.append(xml_file.name)

            except Exception as e:
                error_msg = str(e)[:200]
                print(f"❌ Failed {xml_file.name}: {error_msg}")
                failed += 1
                failed_files.append(f"{xml_file.name}: {error_msg}")

        # Generate site pages
        if successful > 0:
            try:
                self.create_index_page()
                self.create_browse_page()
                self.create_search_data()
                self.create_css()

                print(f"\n🎉 Site generated successfully!")
                print(f"✅ Successfully processed: {successful}")
                print(f"❌ Failed: {failed}")
                print(f"📁 Output directory: {Path(self.output_dir).absolute()}")
                print(f"🌐 Open in browser: file://{Path(self.output_dir).absolute()}/index.html")

                # Save failed files list
                if failed_files:
                    with open(f"{self.output_dir}/failed_files.txt", 'w', encoding='utf-8') as f:
                        f.write("Failed to process:\n")
                        for failed_file in failed_files:
                            f.write(f"- {failed_file}\n")
                    print(f"📝 Failed files list saved to: {self.output_dir}/failed_files.txt")

            except Exception as e:
                print(f"❌ Error generating site pages: {e}")
        else:
            print("❌ No inscriptions were successfully processed!")

        return successful

    def process_single_xml_robust(self, xml_path):
        """Process a single XML file with robust error handling"""
        try:
            # Parse XML with error recovery
            parser = etree.XMLParser(recover=True)
            tree = etree.parse(str(xml_path), parser)
            root = tree.getroot()

            if root is None:
                return None

            ecg_id = xml_path.stem

            # Extract data with safe methods
            inscription = {
                'id': ecg_id,
                'filename': xml_path.name,
                'title': self.safe_extract_title(root),
                'summary': self.safe_extract_summary(root),
                'dating': self.safe_extract_dating(root),
                'origin': self.safe_extract_origin(root),
                'material': self.safe_extract_material(root),
                'dimensions': self.safe_extract_dimensions(root),
                'text_content': self.safe_extract_text_content(root),
                'translation': self.safe_extract_translation(root),
                'commentary': self.safe_extract_commentary(root),
                'bibliography': self.safe_extract_bibliography(root),
                'language': self.safe_detect_language(root),
                'xml_source': self.safe_get_xml_string(root)
            }

            return inscription

        except Exception as e:
            print(f"❌ Error processing {xml_path.name}: {e}")
            return None

    def safe_xpath(self, root, xpath_expr, default=""):
        """Safely execute xpath with error handling"""
        try:
            elements = root.xpath(xpath_expr, namespaces=self.ns)
            if elements:
                return elements
            return []
        except Exception:
            return []

    def safe_get_text(self, element, default=""):
        """Safely get text from element"""
        try:
            if element is not None and hasattr(element, 'text') and element.text:
                return element.text.strip()
            return default
        except Exception:
            return default

    def safe_get_element_text(self, elem, default=""):
        """Safely get all text content from element"""
        try:
            if elem is None:
                return default
            text_parts = []
            for text in elem.itertext():
                if text and text.strip():
                    text_parts.append(text.strip())
            return ' '.join(text_parts) if text_parts else default
        except Exception:
            return default

    def safe_extract_title(self, root):
        """Safely extract title"""
        try:
            title_elems = self.safe_xpath(root, './/tei:titleStmt/tei:title')
            if title_elems:
                title = self.safe_get_text(title_elems[0])
                if title:
                    return title

            # Fallback to any title
            title_elems = self.safe_xpath(root, './/tei:title')
            if title_elems:
                title = self.safe_get_text(title_elems[0])
                if title:
                    return title

            return f"Inscription {root.xpath('.//tei:idno', namespaces=self.ns)[0].text if root.xpath('.//tei:idno', namespaces=self.ns) else 'Unknown'}"
        except Exception:
            return "Untitled Inscription"

    def safe_extract_summary(self, root):
        """Safely extract summary"""
        try:
            summary_elems = self.safe_xpath(root, './/tei:summary')
            if summary_elems:
                return self.safe_get_element_text(summary_elems[0])
            return ""
        except Exception:
            return ""

    def safe_extract_dating(self, root):
        """Safely extract dating information"""
        try:
            date_elems = self.safe_xpath(root, './/tei:origDate')
            if date_elems:
                elem = date_elems[0]
                return {
                    'when': elem.get('when', '') if elem is not None else '',
                    'not_before': elem.get('notBefore', '') if elem is not None else '',
                    'not_after': elem.get('notAfter', '') if elem is not None else '',
                    'period': elem.get('period', '') if elem is not None else '',
                    'text': self.safe_get_element_text(elem)
                }
            return {}
        except Exception:
            return {}

    def safe_extract_origin(self, root):
        """Safely extract origin/findspot"""
        try:
            origin_elems = self.safe_xpath(root, './/tei:provenance[@type="found"]')
            if origin_elems:
                origin_elem = origin_elems[0]
                place_elems = self.safe_xpath(origin_elem, './/tei:placeName')
                place = self.safe_get_text(place_elems[0]) if place_elems else ''

                return {
                    'place': place,
                    'text': self.safe_get_element_text(origin_elem)
                }
            return {}
        except Exception:
            return {}

    def safe_extract_material(self, root):
        """Safely extract material"""
        try:
            material_elems = self.safe_xpath(root, './/tei:material')
            if material_elems:
                return self.safe_get_text(material_elems[0])
            return ""
        except Exception:
            return ""

    def safe_extract_dimensions(self, root):
        """Safely extract dimensions"""
        try:
            dims_elems = self.safe_xpath(root, './/tei:dimensions')
            if dims_elems:
                dims = dims_elems[0]
                height_elems = self.safe_xpath(dims, './tei:height')
                width_elems = self.safe_xpath(dims, './tei:width')
                depth_elems = self.safe_xpath(dims, './tei:depth')

                return {
                    'height': self.safe_get_text(height_elems[0]) if height_elems else '',
                    'width': self.safe_get_text(width_elems[0]) if width_elems else '',
                    'depth': self.safe_get_text(depth_elems[0]) if depth_elems else '',
                    'unit': dims.get('unit', 'cm') if dims is not None else 'cm'
                }
            return {}
        except Exception:
            return {}

    def safe_extract_text_content(self, root):
        """Safely extract inscription text content"""
        try:
            text_content = {}
            edition_divs = self.safe_xpath(root, './/tei:div[@type="edition"]')

            for div in edition_divs:
                try:
                    subtype = div.get('subtype', 'default') if div is not None else 'default'
                    lang = div.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown') if div is not None else 'unknown'

                    # Process the text safely
                    text = self.safe_process_edition_text(div)

                    key = f"{subtype}_{lang}" if subtype != 'default' else lang
                    text_content[key] = {
                        'subtype': subtype,
                        'language': lang,
                        'content': text
                    }
                except Exception:
                    continue

            return text_content
        except Exception:
            return {}

    def safe_process_edition_text(self, div):
        """Safely process edition text"""
        try:
            if div is None:
                return ""

            # Simple approach: just get all text content
            text_content = self.safe_get_element_text(div)

            # Basic line break handling
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = text_content.strip()

            return text_content
        except Exception:
            return ""

    def safe_extract_translation(self, root):
        """Safely extract translation"""
        try:
            trans_elems = self.safe_xpath(root, './/tei:div[@type="translation"]')
            if trans_elems:
                return self.safe_get_element_text(trans_elems[0])
            return ""
        except Exception:
            return ""

    def safe_extract_commentary(self, root):
        """Safely extract commentary"""
        try:
            comm_elems = self.safe_xpath(root, './/tei:div[@type="commentary"]')
            if comm_elems:
                return self.safe_get_element_text(comm_elems[0])
            return ""
        except Exception:
            return ""

    def safe_extract_bibliography(self, root):
        """Safely extract bibliography"""
        try:
            bibl_elems = self.safe_xpath(root, './/tei:listBibl//tei:bibl')
            bibliography = []
            for bibl in bibl_elems:
                bib_text = self.safe_get_element_text(bibl)
                if bib_text:
                    bibliography.append(bib_text)
            return bibliography
        except Exception:
            return []

    def safe_detect_language(self, root):
        """Safely detect primary language"""
        try:
            # Check xml:lang attribute
            lang_attrs = root.xpath('.//@xml:lang')
            if lang_attrs:
                return lang_attrs[0]

            # Simple detection based on content
            all_text = self.safe_get_element_text(root)

            if any(ord(char) >= 0x10A0 and ord(char) <= 0x10FF for char in all_text if isinstance(char, str)):
                return 'ka'  # Georgian
            elif any(ord(char) >= 0x0370 and ord(char) <= 0x03FF for char in all_text if isinstance(char, str)):
                return 'grc'  # Greek
            else:
                return 'unknown'
        except Exception:
            return 'unknown'

    def safe_get_xml_string(self, root):
        """Safely get XML string"""
        try:
            return etree.tostring(root, encoding='unicode', pretty_print=True)
        except Exception:
            return "<xml>Error displaying XML source</xml>"

    def create_inscription_page_safe(self, inscription):
        """Safely create individual inscription page"""
        try:
            # Build metadata
            metadata_parts = [f'<span class="id">🆔 {inscription["id"]}</span>']

            if inscription['dating'].get('text'):
                metadata_parts.append(f'<span class="date">📅 {inscription["dating"]["text"]}</span>')

            if inscription['origin'].get('place'):
                metadata_parts.append(f'<span class="place">📍 {inscription["origin"]["place"]}</span>')

            if inscription['material']:
                metadata_parts.append(f'<span class="material">🔨 {inscription["material"]}</span>')

            metadata_parts.append(f'<span class="lang">🌐 {inscription["language"]}</span>')

            metadata_html = '\n                '.join(metadata_parts)

            # Build sections safely
            summary_section = ""
            if inscription['summary']:
                summary_section = f'<div class="summary"><h3>Summary</h3><p>{inscription["summary"]}</p></div>'

            # Text editions
            text_editions_html = self.safe_format_text_editions(inscription['text_content'])

            # Translation tab and content
            translation_tab = ""
            translation_content = ""
            if inscription['translation']:
                translation_tab = '<button @click="activeTab = \'translation\'" :class="{ active: activeTab === \'translation\' }">Translation</button>'
                translation_content = f'''<div x-show="activeTab === 'translation'" class="tab-content">
            <div class="translation">{inscription['translation']}</div>
        </div>'''

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

    <main class="container" x-data="{{{{ activeTab: 'overview' }}}}">
        <div class="inscription-header">
            <h1>{inscription['title']}</h1>
            <div class="inscription-meta">
                {metadata_html}
            </div>
        </div>

        <div class="tabs">
            <button @click="activeTab = 'overview'" :class="{{{{ active: activeTab === 'overview' }}}}">Overview</button>
            <button @click="activeTab = 'text'" :class="{{{{ active: activeTab === 'text' }}}}">Text</button>
            {translation_tab}
            <button @click="activeTab = 'xml'" :class="{{{{ active: activeTab === 'xml' }}}}">XML Source</button>
        </div>

        <div x-show="activeTab === 'overview'" class="tab-content">
            <div class="overview">
                {summary_section}
                <div class="metadata">
                    <h3>Metadata</h3>
                    <dl>
                        <dt>ID</dt><dd>{inscription['id']}</dd>
                        <dt>Language</dt><dd>{inscription['language']}</dd>
                        <dt>Material</dt><dd>{inscription['material'] or 'Not specified'}</dd>
                    </dl>
                </div>
            </div>
        </div>

        <div x-show="activeTab === 'text'" class="tab-content">
            <div class="text-editions">
                {text_editions_html}
            </div>
        </div>

        {translation_content}

        <div x-show="activeTab === 'xml'" class="tab-content">
            <pre class="xml-source"><code>{inscription['xml_source']}</code></pre>
        </div>
    </main>
</body>
</html>"""

            with open(f"{self.output_dir}/inscriptions/{inscription['id']}.html", 'w', encoding='utf-8') as f:
                f.write(html)

        except Exception as e:
            print(f"❌ Error creating page for {inscription['id']}: {e}")

    def safe_format_text_editions(self, text_content):
        """Safely format text editions"""
        try:
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

            return ''.join(html_parts) if html_parts else "<p>No text editions available.</p>"
        except Exception:
            return "<p>Error displaying text content.</p>"

    def create_index_page(self):
        """Create homepage"""
        try:
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
        except Exception as e:
            print(f"❌ Error creating index page: {e}")

    def create_browse_page(self):
        """Create browse page"""
        try:
            search_data = json.dumps([{
                'id': i['id'],
                'title': i['title'],
                'place': i['origin'].get('place', ''),
                'date': i['dating'].get('text', '')
            } for i in self.inscriptions])

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
            <h1>Browse Inscriptions ({len(self.inscriptions)} total)</h1>
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
                inscriptions: {search_data},
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
        except Exception as e:
            print(f"❌ Error creating browse page: {e}")

    def format_inscription_cards(self, inscriptions):
        """Format inscription cards"""
        try:
            cards = []
            for inscription in inscriptions:
                place_span = ""
                if inscription['origin'].get('place'):
                    place_span = f'<span class="place">{inscription["origin"]["place"]}</span>'

                cards.append(f"""
                    <div class="inscription-card">
                        <h3><a href="inscriptions/{inscription['id']}.html">{inscription['title']}</a></h3>
                        <div class="inscription-meta">
                            <span class="id">{inscription['id']}</span>
                            {place_span}
                            <span class="lang">{inscription['language']}</span>
                        </div>
                    </div>
                """)
            return ''.join(cards)
        except Exception as e:
            print(f"❌ Error formatting cards: {e}")
            return "<p>Error displaying inscriptions</p>"

    def create_search_data(self):
        """Create JSON search data"""
        try:
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
        except Exception as e:
            print(f"❌ Error creating search data: {e}")

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
    processor = RobustECGProcessor()
    processor.process_all()
