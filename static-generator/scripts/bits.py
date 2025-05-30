# Add these methods to your RobustECGProcessorVanilla class

def extract_all_persons(self):
    """Extract all persons from persName elements in edition divs - equivalent to XSL transformation"""
    try:
        print("👥 Extracting all persons from inscriptions...")

        persons_index = {}  # key -> person data
        person_occurrences = {}  # key -> list of occurrences

        for inscription in self.inscriptions:
            xml_root = inscription.get('xml_root')
            if xml_root is None:
                continue

            # Find all persName elements in edition divs (matching your XSL)
            edition_divs = self.safe_xpath(xml_root, './/tei:div[@type="edition"]')

            for edition_div in edition_divs:
                persname_elems = self.safe_xpath(edition_div, './/tei:persName[@key]')

                for persname in persname_elems:
                    key = persname.get('key', '').strip()
                    if not key:
                        continue

                    # Get person display name
                    display_name = self.safe_get_element_text(persname).strip()
                    if not display_name:
                        continue

                    # Initialize person data if not exists
                    if key not in persons_index:
                        persons_index[key] = {
                            'key': key,
                            'display_names': set(),  # Use set to avoid duplicates
                            'nymRef': persname.get('nymRef', ''),
                            'ref': persname.get('ref', ''),
                            'type': persname.get('type', ''),
                            'first_occurrence': inscription['id'],
                            'inscription_count': 0,
                            'inscriptions': []
                        }
                        person_occurrences[key] = []

                    # Add display name variant
                    persons_index[key]['display_names'].add(display_name)

                    # Create occurrence record
                    occurrence = {
                        'inscription_id': inscription['id'],
                        'inscription_title': self.get_display_title(inscription['title']),
                        'display_name': display_name,
                        'place': inscription['origin'].get('place', ''),
                        'date': inscription['dating'].get('text', ''),
                        'language': inscription['language'],
                        'file_path': inscription['filename']
                    }

                    # Add to occurrences if not already there (avoid duplicates within same inscription)
                    if not any(occ['inscription_id'] == inscription['id'] and
                             occ['display_name'] == display_name
                             for occ in person_occurrences[key]):
                        person_occurrences[key].append(occurrence)

        # Finalize person data
        for key, person_data in persons_index.items():
            occurrences = person_occurrences[key]
            person_data['occurrences'] = occurrences
            person_data['inscription_count'] = len(set(occ['inscription_id'] for occ in occurrences))

            # Convert display_names set to sorted list with primary name first
            display_names_list = sorted(list(person_data['display_names']))
            person_data['primary_name'] = display_names_list[0] if display_names_list else key
            person_data['display_names'] = display_names_list
            person_data['all_names'] = ', '.join(display_names_list)

            # Create unique inscriptions list
            unique_inscriptions = {}
            for occ in occurrences:
                if occ['inscription_id'] not in unique_inscriptions:
                    unique_inscriptions[occ['inscription_id']] = {
                        'id': occ['inscription_id'],
                        'title': occ['inscription_title'],
                        'place': occ['place'],
                        'date': occ['date'],
                        'language': occ['language'],
                        'url': f"inscriptions/{occ['inscription_id']}.html"
                    }
            person_data['inscriptions'] = list(unique_inscriptions.values())

        print(f"👥 Extracted {len(persons_index)} unique persons")

        # Save persons data
        self.save_persons_data(persons_index)

        return persons_index

    except Exception as e:
        print(f"❌ Error extracting persons: {e}")
        import traceback
        traceback.print_exc()
        return {}

def save_persons_data(self, persons_index):
    """Save persons data to files"""
    try:
        # Convert sets to lists for JSON serialization
        persons_for_json = {}
        for key, person_data in persons_index.items():
            person_copy = person_data.copy()
            if isinstance(person_copy.get('display_names'), set):
                person_copy['display_names'] = list(person_copy['display_names'])
            persons_for_json[key] = person_copy

        # Save as JSON
        with open(f"{self.output_dir}/persons-index.json", 'w', encoding='utf-8') as f:
            json.dump(persons_for_json, f, ensure_ascii=False, indent=2)

        # Save as readable text file
        with open(f"{self.output_dir}/persons-index.txt", 'w', encoding='utf-8') as f:
            f.write("Persons Index\n")
            f.write("=" * 50 + "\n\n")

            for key in sorted(persons_index.keys()):
                person = persons_index[key]
                f.write(f"Key: {key}\n")
                f.write(f"Primary Name: {person['primary_name']}\n")
                if len(person['display_names']) > 1:
                    f.write(f"Name Variants: {', '.join(person['display_names'][1:])}\n")
                f.write(f"Inscriptions: {person['inscription_count']}\n")
                if person.get('nymRef'):
                    f.write(f"Reference: {person['nymRef']}\n")
                if person.get('ref'):
                    f.write(f"External URL: {person['ref']}\n")
                f.write(f"First Occurrence: {person['first_occurrence']}\n")
                f.write("\nOccurrences:\n")
                for occ in person['occurrences']:
                    f.write(f"  - {occ['inscription_id']}: {occ['display_name']} ({occ['place']}, {occ['date']})\n")
                f.write("\n" + "-" * 40 + "\n\n")

        print(f"💾 Persons data saved to: {self.output_dir}/persons-index.json")
        print(f"💾 Readable index saved to: {self.output_dir}/persons-index.txt")

    except Exception as e:
        print(f"❌ Error saving persons data: {e}")

def create_persons_index_page(self, persons_index):
    """Create the main persons index page"""
    try:
        if not persons_index:
            print("⚠️ No persons to create index page")
            return

        # Sort persons by frequency and then alphabetically
        sorted_persons = sorted(
            persons_index.values(),
            key=lambda p: (-p['inscription_count'], p['primary_name'].lower())
        )

        # Create persons list HTML
        persons_html = ""
        for person in sorted_persons:
            # Create name display with variants
            name_display = person['primary_name']
            if len(person['display_names']) > 1:
                variants = [name for name in person['display_names'] if name != person['primary_name']]
                name_display += f" <span class='name-variants'>({', '.join(variants)})</span>"

            # Check if names contain Georgian text
            has_georgian = any(
                any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in name)
                for name in person['display_names']
            )
            name_class = 'georgian-text' if has_georgian else ''

            # External reference link
            external_link = ""
            if person.get('ref'):
                external_link = f'<a href="{person["ref"]}" target="_blank" class="external-ref" title="External Reference">🔗</a>'

            persons_html += f"""
                <div class="person-item" data-name="{person['primary_name'].lower()}" data-count="{person['inscription_count']}">
                    <div class="person-header">
                        <h3 class="person-name {name_class}">
                            <a href="persons/{person['key']}.html">{name_display}</a>
                            {external_link}
                        </h3>
                        <span class="person-count">{person['inscription_count']} inscription{'s' if person['inscription_count'] != 1 else ''}</span>
                    </div>
                    <div class="person-inscriptions">
                        {self.format_person_inscriptions_preview(person['inscriptions'][:5])}
                        {f'<span class="more-inscriptions">... and {len(person["inscriptions"]) - 5} more</span>' if len(person['inscriptions']) > 5 else ''}
                    </div>
                </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Persons Index - ECG</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
            <div class="nav-links">
                <a href="index.html">Home</a>
                <a href="browse.html">Browse</a>
                <a href="persons.html">Persons</a>
                <a href="bibliography.html">Bibliography</a>
            </div>
        </div>
    </nav>

    <main class="container">
        <div class="page-header">
            <h1>Index of Persons</h1>
            <p>Complete index of {len(persons_index)} persons mentioned in the Epigraphic Corpus of Georgia</p>
        </div>

        <div class="persons-controls">
            <div class="search-box">
                <input type="text" id="personsSearch" placeholder="Search persons..." class="search-input">
            </div>
            <div class="sort-controls">
                <select id="sortPersons" class="filter-select">
                    <option value="frequency">Sort by Frequency</option>
                    <option value="alphabetical">Sort Alphabetically</option>
                    <option value="inscriptions">Sort by Inscription Count</option>
                </select>
            </div>
        </div>

        <div class="persons-stats">
            <div class="stat-item">
                <strong>{len(persons_index)}</strong>
                <span>Unique Persons</span>
            </div>
            <div class="stat-item">
                <strong>{sum(p['inscription_count'] for p in persons_index.values())}</strong>
                <span>Total Occurrences</span>
            </div>
            <div class="stat-item">
                <strong>{len(set(occ['inscription_id'] for p in persons_index.values() for occ in p['occurrences']))}</strong>
                <span>Inscriptions with Persons</span>
            </div>
        </div>

        <div id="personsList" class="persons-list">
            {persons_html}
        </div>
    </main>

    <script src="static/js/persons.js"></script>
</body>
</html>"""

        with open(f"{self.output_dir}/persons.html", 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"👥 Persons index page created with {len(persons_index)} persons")

    except Exception as e:
        print(f"❌ Error creating persons index page: {e}")

def format_person_inscriptions_preview(self, inscriptions):
    """Format a preview list of inscriptions for person index page"""
    try:
        if not inscriptions:
            return "<span class='no-inscriptions'>No inscriptions</span>"

        items = []
        for inscription in inscriptions:
            # Check if title contains Georgian text
            has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in inscription['title'])
            title_class = 'georgian-text' if has_georgian else ''

            items.append(f"""
                <span class="inscription-preview">
                    <a href="{inscription['url']}" class="inscription-link {title_class}">{inscription['title']}</a>
                    <span class="inscription-meta">({inscription['place']}, {inscription['date']})</span>
                </span>
            """)

        return ''.join(items)

    except Exception as e:
        print(f"❌ Error formatting inscription preview: {e}")
        return "<span class='error'>Error displaying inscriptions</span>"

def create_individual_person_pages(self, persons_index):
    """Create individual pages for each person"""
    try:
        # Create persons directory
        os.makedirs(f"{self.output_dir}/persons", exist_ok=True)

        for key, person in persons_index.items():
            self.create_single_person_page(key, person)

        print(f"👥 Created {len(persons_index)} individual person pages")

    except Exception as e:
        print(f"❌ Error creating person pages: {e}")

def create_single_person_page(self, key, person):
    """Create a single person page"""
    try:
        # Check if name contains Georgian text
        has_georgian = any(
            any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in name)
            for name in person['display_names']
        )
        name_class = 'georgian-text' if has_georgian else ''

        # Name variants section
        name_variants_html = ""
        if len(person['display_names']) > 1:
            variants = [name for name in person['display_names'] if name != person['primary_name']]
            name_variants_html = f"""
                <div class="name-variants-section">
                    <h3>Name Variants</h3>
                    <ul class="name-variants-list {name_class}">
                        {''.join(f'<li>{variant}</li>' for variant in variants)}
                    </ul>
                </div>
            """

        # External references section
        external_refs_html = ""
        if person.get('ref') or person.get('nymRef'):
            refs = []
            if person.get('ref'):
                refs.append(f'<a href="{person["ref"]}" target="_blank" class="external-link">External Reference</a>')
            if person.get('nymRef'):
                refs.append(f'<span class="nym-ref">nymRef: {person["nymRef"]}</span>')

            external_refs_html = f"""
                <div class="external-references">
                    <h3>References</h3>
                    <div class="refs-list">
                        {'<br>'.join(refs)}
                    </div>
                </div>
            """

        # Inscriptions list
        inscriptions_html = ""
        if person['inscriptions']:
            inscriptions_items = []
            for inscription in person['inscriptions']:
                # Check if title contains Georgian
                title_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in inscription['title'])
                title_class = 'georgian-text' if title_has_georgian else ''

                # Check if place contains Georgian
                place_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in inscription['place'])
                place_class = 'georgian-text' if place_has_georgian else ''

                inscriptions_items.append(f"""
                    <div class="person-inscription-item">
                        <h4 class="inscription-title {title_class}">
                            <a href="../{inscription['url']}">{inscription['title']}</a>
                        </h4>
                        <div class="inscription-metadata">
                            <span class="inscription-id">№ {inscription['id']}</span>
                            <span class="inscription-place {place_class}">📍 {inscription['place']}</span>
                            <span class="inscription-date">📅 {inscription['date']}</span>
                            <span class="inscription-language">🌐 {inscription['language']}</span>
                        </div>
                    </div>
                """)

            inscriptions_html = f"""
                <div class="person-inscriptions-section">
                    <h3>Inscriptions ({len(person['inscriptions'])})</h3>
                    <div class="person-inscriptions-list">
                        {''.join(inscriptions_items)}
                    </div>
                </div>
            """

        # Statistics
        stats_html = f"""
            <div class="person-stats">
                <div class="stat-grid">
                    <div class="stat-item">
                        <strong>{person['inscription_count']}</strong>
                        <span>Inscription{'s' if person['inscription_count'] != 1 else ''}</span>
                    </div>
                    <div class="stat-item">
                        <strong>{len(person['occurrences'])}</strong>
                        <span>Total Occurrence{'s' if len(person['occurrences']) != 1 else ''}</span>
                    </div>
                    <div class="stat-item">
                        <strong>{len(person['display_names'])}</strong>
                        <span>Name Variant{'s' if len(person['display_names']) != 1 else ''}</span>
                    </div>
                </div>
            </div>
        """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{person['primary_name']} - Person - ECG</title>
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="../index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
            <div class="nav-links">
                <a href="../index.html">Home</a>
                <a href="../browse.html">Browse</a>
                <a href="../persons.html">Persons</a>
                <a href="../bibliography.html">Bibliography</a>
            </div>
        </div>
    </nav>

    <main class="container">
        <div class="person-header">
            <h1 class="person-name {name_class}">{person['primary_name']}</h1>
            <div class="person-key">Key: {key}</div>
        </div>

        {stats_html}

        <div class="person-content">
            {name_variants_html}
            {external_refs_html}
            {inscriptions_html}
        </div>

        <div class="back-to-index">
            <a href="../persons.html" class="btn">← Back to Persons Index</a>
        </div>
    </main>
</body>
</html>"""

        with open(f"{self.output_dir}/persons/{key}.html", 'w', encoding='utf-8') as f:
            f.write(html)

    except Exception as e:
        print(f"❌ Error creating person page for {key}: {e}")

def create_persons_javascript(self):
    """Create JavaScript for persons index page functionality"""
    persons_js = """// Persons index page functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('personsSearch');
    const sortSelect = document.getElementById('sortPersons');
    const personsList = document.getElementById('personsList');
    const allPersons = document.querySelectorAll('.person-item');

    let personsArray = Array.from(allPersons);

    function filterAndSortPersons() {
        const searchTerm = (searchInput ? searchInput.value || '' : '').toLowerCase();
        const sortBy = sortSelect ? sortSelect.value || 'frequency' : 'frequency';

        // Filter persons
        const filteredPersons = personsArray.filter(person => {
            const name = person.dataset.name || '';
            const textContent = person.textContent.toLowerCase();

            return !searchTerm ||
                   name.includes(searchTerm) ||
                   textContent.includes(searchTerm);
        });

        // Sort persons
        filteredPersons.sort((a, b) => {
            switch(sortBy) {
                case 'alphabetical':
                    return (a.dataset.name || '').localeCompare(b.dataset.name || '');
                case 'inscriptions':
                    return parseInt(b.dataset.count || '0') - parseInt(a.dataset.count || '0');
                case 'frequency':
                default:
                    // First by count, then alphabetically
                    const countDiff = parseInt(b.dataset.count || '0') - parseInt(a.dataset.count || '0');
                    return countDiff !== 0 ? countDiff : (a.dataset.name || '').localeCompare(b.dataset.name || '');
            }
        });

        // Hide all persons first
        personsArray.forEach(person => {
            person.style.display = 'none';
        });

        // Clear and re-append filtered/sorted persons
        if (personsList) {
            personsList.innerHTML = '';
            filteredPersons.forEach(person => {
                person.style.display = 'block';
                personsList.appendChild(person);
            });
        }

        // Update count
        updatePersonsCount(filteredPersons.length, personsArray.length);
    }

    function updatePersonsCount(showing, total) {
        let countDisplay = document.getElementById('personsCount');
        if (!countDisplay && personsList) {
            countDisplay = document.createElement('div');
            countDisplay.id = 'personsCount';
            countDisplay.className = 'result-count';
            personsList.parentNode.insertBefore(countDisplay, personsList);
        }

        if (countDisplay) {
            if (showing === total) {
                countDisplay.innerHTML = `<strong>Showing all ${total} persons</strong>`;
            } else {
                countDisplay.innerHTML = `
                    <strong>Showing ${showing} of ${total} persons</strong>
                    ${searchInput && searchInput.value ?
                        `<br><small>Filtered by: "${searchInput.value}"</small>` : ''}
                `;
            }
        }
    }

    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    const debouncedFilter = debounce(filterAndSortPersons, 200);

    // Event listeners
    if (searchInput) {
        searchInput.addEventListener('input', debouncedFilter);
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', filterAndSortPersons);
    }

    // Initialize
    filterAndSortPersons();

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }

        if (e.key === 'Escape' && document.activeElement === searchInput && searchInput) {
            searchInput.value = '';
            debouncedFilter();
        }
    });
});
"""

    # Add persons page CSS styles
    persons_css = """
/* Persons Index Page Styles */
.persons-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    max-width: 600px;
    margin: 2rem auto;
}

.persons-controls .search-box {
    width: 100%;
}

.sort-controls {
    display: flex;
    gap: 1rem;
}

.persons-stats {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin: 2rem 0;
    padding: 2rem;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 8px;
    border: 1px solid #e9ecef;
}

.stat-item {
    text-align: center;
}

.stat-item strong {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.25rem;
}

.stat-item span {
    color: #666;
    font-size: 0.9rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.persons-list {
    max-width: 900px;
    margin: 0 auto;
}

.person-item {
    background: white;
    border: 1px solid #f0f0f0;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    padding: 1.5rem 2rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.person-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    border-color: #e0e0e0;
}

.person-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 1rem;
    gap: 1rem;
}

.person-name {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    flex: 1;
}

.person-name a {
    color: #1a1a1a;
    text-decoration: none;
    transition: color 0.2s ease;
}

.person-name a:hover {
    color: #1565C0;
}

.person-name.georgian-text {
    font-family: var(--primary-georgian-font);
    font-size: 1.3rem;
}

.name-variants {
    font-size: 0.9em;
    color: #666;
    font-weight: 400;
    font-style: italic;
}

.person-count {
    background: #e3f2fd;
    color: #1565C0;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
    white-space: nowrap;
}

.external-ref {
    margin-left: 0.5rem;
    text-decoration: none;
    opacity: 0.7;
    transition: opacity 0.2s ease;
}

.external-ref:hover {
    opacity: 1;
}

.person-inscriptions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    font-size: 0.9rem;
}

.inscription-preview {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.inscription-link {
    color: #1565C0;
    text-decoration: none;
    font-weight: 500;
}

.inscription-link:hover {
    text-decoration: underline;
}

.inscription-link.georgian-text {
    font-family: var(--primary-georgian-font);
}

.inscription-meta {
    color: #666;
    font-size: 0.85em;
}

.more-inscriptions {
    color: #888;
    font-style: italic;
    font-size: 0.85em;
}

/* Individual Person Page Styles */
.person-header {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 2rem;
}

.person-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #1a1a1a;
}

.person-header h1.georgian-text {
    font-family: var(--primary-georgian-font);
    font-size: 2.8rem;
}

.person-key {
    color: #666;
    font-size: 1rem;
    font-weight: 500;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}

.person-content {
    max-width: 800px;
    margin: 0 auto;
}

.name-variants-section,
.external-references,
.person-inscriptions-section {
    margin-bottom: 3rem;
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #1565C0;
}

.name-variants-section h3,
.external-references h3,
.person-inscriptions-section h3 {
    color: #1565C0;
    margin-bottom: 1rem;
    font-size: 1.2rem;
}

.name-variants-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.name-variants-list li {
    padding: 0.5rem 0;
    border-bottom: 1px solid #e9ecef;
    font-size: 1.1rem;
}

        .name-variants-list li:last-child {
            border-bottom: none;
        }

        .name-variants-list.georgian-text {
            font-family: var(--primary-georgian-font);
        }

        .refs-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .external-link {
            color: #1565C0;
            text-decoration: none;
            font-weight: 500;
        }

        .external-link:hover {
            text-decoration: underline;
        }

        .nym-ref {
            color: #666;
            font-size: 0.95rem;
            font-family: monospace;
        }

        .person-inscriptions-list {
            display: grid;
            gap: 1.5rem;
        }

        .person-inscription-item {
            background: white;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            transition: all 0.2s ease;
        }

        .person-inscription-item:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        .person-inscription-item h4 {
            margin: 0 0 1rem 0;
            font-size: 1.1rem;
        }

        .person-inscription-item h4 a {
            color: #1a1a1a;
            text-decoration: none;
        }

        .person-inscription-item h4 a:hover {
            color: #1565C0;
        }

        .person-inscription-item h4.georgian-text {
            font-family: var(--primary-georgian-font);
        }

        .inscription-metadata {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            font-size: 0.85rem;
        }

        .inscription-metadata span {
            background: #f5f5f5;
            color: #666;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-weight: 500;
        }

        .inscription-metadata .georgian-text {
            font-family: var(--primary-georgian-font);
        }

        .back-to-index {
            text-align: center;
            margin: 3rem 0;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .persons-stats {
                flex-direction: column;
                gap: 1.5rem;
                text-align: center;
            }

            .person-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.75rem;
            }

            .person-name {
                font-size: 1.1rem;
            }

            .person-name.georgian-text {
                font-size: 1.2rem;
            }

            .person-header h1 {
                font-size: 2rem;
            }

            .person-header h1.georgian-text {
                font-size: 2.2rem;
            }

            .stat-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
                text-align: center;
            }

            .name-variants-section,
            .external-references,
            .person-inscriptions-section {
                padding: 1.5rem;
                margin-bottom: 2rem;
            }

            .person-inscription-item {
                padding: 1.25rem;
            }

            .inscription-metadata {
                gap: 0.5rem;
            }

            .inscription-metadata span {
                font-size: 0.8rem;
                padding: 0.25rem 0.5rem;
            }
        }
        """

    try:
        with open(f"{self.output_dir}/static/js/persons.js", 'w', encoding='utf-8') as f:
            f.write(persons_js)

        # Append persons CSS to main CSS file
        with open(f"{self.output_dir}/static/css/style.css", 'a', encoding='utf-8') as f:
            f.write('\n\n/* Persons Index Styles */\n')
            f.write(persons_css)

        print("📜 Persons JavaScript and CSS created successfully!")

    except Exception as e:
        print(f"❌ Error creating persons JavaScript/CSS: {e}")

    # Also update your navigation to include persons link in all HTML templates:
    
    def update_navigation_with_persons(self):
        """Update navigation in existing HTML templates to include persons link"""
        navigation_html = '''
                    <a href="index.html">Home</a>
                    <a href="browse.html">Browse</a>
                    <a href="persons.html">Persons</a>
                    <a href="bibliography.html">Bibliography</a>
        '''
        # This navigation should be used in all your HTML templates
    
    # Now update your main process_all method to include person processing:
    
    def process_all(self):
        """Process all XML files with robust error handling and debugging - UPDATED WITH PERSONS"""
        print("🚀 Processing ECG inscriptions with person indexing...")
    
        # Create directories
        os.makedirs(f"{self.output_dir}/inscriptions", exist_ok=True)
        os.makedirs(f"{self.output_dir}/persons", exist_ok=True)  # Add persons directory
        os.makedirs(f"{self.output_dir}/static/css", exist_ok=True)
        os.makedirs(f"{self.output_dir}/static/js", exist_ok=True)
        os.makedirs(f"{self.output_dir}/static/images", exist_ok=True)
    
        # DEBUG: Test XML processing first
        print("🔍 Running initial diagnostics...")
        if not self.debug_xml_processing():
            print("❌ XML processing test failed - aborting")
            return 0
    
        # Process bibliography first
        print("📚 Processing bibliography...")
        self.process_bibliography()
    
        # Copy images
        print("🖼️ Copying images...")
        self.copy_images()
    
        xml_files = sorted(list(Path(self.xml_dir).glob("*.xml")))
        print(f"📄 Found {len(xml_files)} XML files to process")
    
        successful = 0
        failed = 0
        failed_files = []
    
        # Initialize inscriptions list
        self.inscriptions = []
        print(f"🔍 DEBUG: Initialized inscriptions list, current count: {len(self.inscriptions)}")
    
        # Process each XML file
        for i, xml_file in enumerate(xml_files):
            try:
                inscription = self.process_single_xml_robust(xml_file)
                if inscription:
                    self.inscriptions.append(inscription)
                    self.create_inscription_page_vanilla(inscription)
                    successful += 1
    
                    if successful % 25 == 0:
                        print(f"✅ Processed {successful}/{len(xml_files)} inscriptions... (Total in memory: {len(self.inscriptions)})")
                else:
                    print(f"⚠️ Failed to process {xml_file.name} - inscription was None")
                    failed += 1
                    failed_files.append(xml_file.name)
    
            except Exception as e:
                error_msg = str(e)[:200]
                print(f"❌ Exception processing {xml_file.name}: {error_msg}")
                failed += 1
                failed_files.append(f"{xml_file.name}: {error_msg}")
    
        # DEBUG: Final check before site generation
        print(f"\n🔍 FINAL CHECK: After processing all XML files:")
        print(f"   ✅ Successfully processed: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📊 Total inscriptions in memory: {len(self.inscriptions)}")
    
        has_inscriptions = self.debug_before_site_generation()
    
        # Generate site pages ONLY if we have successfully processed inscriptions
        if successful > 0 and has_inscriptions:
            try:
                print(f"\n🏗️ Generating site pages with {len(self.inscriptions)} inscriptions...")
    
                self.build_bibliography_references()
    
                # Extract place names
                self.extract_all_place_names()
    
                # Debug places
                missing, found = self.debug_missing_places()
                inscription_places = self.debug_inscription_places()
                place_names_data = self.debug_place_names_file()
    
                # Generate map data
                self.generate_map_data()
                self.debug_coordinate_assignments()
                self.debug_map_coordinates()
                self.validate_and_fix_coordinates()
    
                # NEW: Extract and process persons
                print(f"\n👥 Processing persons index...")
                persons_index = self.extract_all_persons()
    
                if persons_index:
                    print(f"👥 Creating persons pages...")
                    self.create_persons_index_page(persons_index)
                    self.create_individual_person_pages(persons_index)
                    self.create_persons_javascript()
                else:
                    print("⚠️ No persons found to index")
    
                # Generate other site pages
                print(f"🏠 Creating index page...")
                self.create_index_page()
    
                print(f"📋 Creating browse page...")
                self.create_browse_page_vanilla()
    
                print(f"📚 Creating bibliography page...")
                self.create_bibliography_page()
    
                print(f"🔍 Creating search data...")
                self.create_search_data()
    
                print(f"🎨 Creating CSS...")
                self.create_css_vanilla()
    
                print(f"📜 Creating JavaScript...")
                self.create_javascript()
    
                print(f"\n🎉 Site generated successfully!")
                print(f"✅ Successfully processed: {successful}")
                print(f"❌ Failed: {failed}")
                print(f"📚 Bibliography entries: {len(self.bibliography)}")
                print(f"👥 Persons indexed: {len(persons_index) if persons_index else 0}")
    
                # Show language statistics
                lang_stats = {}
                for inscription in self.inscriptions:
                    lang = inscription.get('language', 'unknown')
                    lang_stats[lang] = lang_stats.get(lang, 0) + 1
    
                print(f"🌐 Language distribution:")
                for lang, count in sorted(lang_stats.items()):
                    print(f"   {lang}: {count}")
    
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
                import traceback
                traceback.print_exc()
        else:
            print("❌ No inscriptions were successfully processed!")
    
        return successful
