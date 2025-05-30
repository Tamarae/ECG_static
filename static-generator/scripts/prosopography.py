#!/usr/bin/env python3
"""
Prosopography Extractor for Georgian Epigraphic Corpus
Extracts person names with type="local" from TEI/EpiDoc XML files
"""

import xml.etree.ElementTree as ET
import json
import csv
import argparse
import os
from pathlib import Path
from collections import defaultdict, Counter
import re

class ProsopographyExtractor:
    def __init__(self):
        self.tei_ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        self.persons = defaultdict(lambda: {
            'canonical_name': '',
            'variants': set(),
            'attestations': [],
            'roles': set(),
            'locations': set(),
            'dates': set(),
            'notes': []
        })

    def extract_from_file(self, file_path):
        """Extract prosopographic data from a single TEI file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Get file identifier (assuming filename or tei:idno)
            file_id = self._get_file_id(root, file_path)

            # Find all persName elements with type="local" in edition sections
            pers_names = root.findall('.//tei:div[@type="edition"]//tei:persName[@type="local"]', self.tei_ns)

            for pers_name in pers_names:
                self._process_person_name(pers_name, file_id)

        except ET.ParseError as e:
            print(f"Error parsing {file_path}: {e}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _get_file_id(self, root, file_path):
        """Extract file identifier from TEI header or filename"""
        # Try to get from tei:idno
        idno = root.find('.//tei:publicationStmt//tei:idno', self.tei_ns)
        if idno is not None and idno.text:
            return idno.text.strip()

        # Try to get from xml:id on TEI root
        tei_id = root.get('{http://www.w3.org/XML/1998/namespace}id')
        if tei_id:
            return tei_id

        # Fall back to filename
        return Path(file_path).stem

    def _process_person_name(self, pers_name_elem, file_id):
        """Process a single persName element"""
        # Get the key (canonical identifier)
        key = pers_name_elem.get('key', '').strip()
        if not key:
            # If no key, use the text content as key
            key = self._normalize_name(pers_name_elem.text or '')

        if not key:
            return

        # Get the displayed name
        displayed_name = self._extract_text_content(pers_name_elem)

        # Get location information (line/section reference)
        location_ref = self._get_location_reference(pers_name_elem)

        # Extract additional information from attributes
        role = pers_name_elem.get('role', '')

        # Store the person data
        person = self.persons[key]

        # Set canonical name if not already set
        if not person['canonical_name']:
            person['canonical_name'] = key

        # Add name variant
        if displayed_name and displayed_name != key:
            person['variants'].add(displayed_name)

        # Add attestation
        attestation = {
            'source': file_id,
            'location': location_ref,
            'displayed_form': displayed_name,
            'context': self._get_context(pers_name_elem)
        }
        person['attestations'].append(attestation)

        # Add role if present
        if role:
            person['roles'].add(role)

        # Extract additional info from context (roles, locations from text)
        self._extract_contextual_info(pers_name_elem, person)

    def _extract_text_content(self, elem):
        """Extract all text content from an element"""
        if elem.text:
            text = elem.text.strip()
        else:
            text = ''

        for child in elem:
            if child.text:
                text += child.text.strip()
            if child.tail:
                text += child.tail.strip()

        return text.strip()

    def _get_location_reference(self, elem):
        """Get line/section reference for the person name"""
        # Look for ancestor elements that might contain location info
        current = elem
        while current is not None:
            # Check for @n attribute (line numbers)
            if current.get('n'):
                return current.get('n')
            # Check for specific elements
            if current.tag.endswith('}l') or current.tag.endswith('}lb'):  # line or linebreak
                return current.get('n', '')
            current = current.getparent() if hasattr(current, 'getparent') else None
        return ''

    def _get_context(self, elem):
        """Get surrounding context for the person name"""
        # Get parent element text for context
        parent = elem.getparent() if hasattr(elem, 'getparent') else None
        if parent is not None:
            context = self._extract_text_content(parent)
            # Limit context length
            if len(context) > 200:
                context = context[:200] + '...'
            return context
        return ''

    def _extract_contextual_info(self, elem, person):
        """Extract roles, locations, dates from surrounding context"""
        context = self._get_context(elem)

        # Simple pattern matching for Georgian roles and locations
        # You can expand these patterns based on your corpus
        role_patterns = [
            r'მხატვართუხუცესი',
            r'დეკანოზი',
            r'მაშენებელი',
            r'ხელოსანი',
            r'მეფე',
            r'ურბნისელი',
            r'ბოლნისის'
        ]

        for pattern in role_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                person['roles'].add(pattern)

        # Extract location references
        location_patterns = [
            r'ურბნისის?',
            r'ბოლნისის?',
            r'ყარსის?'
        ]

        for pattern in location_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                person['locations'].add(pattern)

    def _normalize_name(self, name):
        """Normalize name for use as key"""
        return name.strip().replace(' ', '_').lower()

    def process_directory(self, directory_path):
        """Process all XML files in a directory"""
        xml_files = list(Path(directory_path).rglob('*.xml'))

        print(f"Found {len(xml_files)} XML files")

        for xml_file in xml_files:
            print(f"Processing: {xml_file}")
            self.extract_from_file(xml_file)

        print(f"Extracted data for {len(self.persons)} persons")

    def export_to_json(self, output_path):
        """Export prosopographic data to JSON"""
        # Convert sets to lists for JSON serialization
        export_data = {}
        for key, person in self.persons.items():
            export_data[key] = {
                'canonical_name': person['canonical_name'],
                'variants': list(person['variants']),
                'attestations': person['attestations'],
                'roles': list(person['roles']),
                'locations': list(person['locations']),
                'dates': list(person['dates']),
                'notes': person['notes'],
                'attestation_count': len(person['attestations'])
            }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"Exported JSON to: {output_path}")

    def export_to_csv(self, output_path):
        """Export prosopographic data to CSV"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'canonical_name', 'variants', 'attestation_count',
                'sources', 'roles', 'locations', 'first_attestation'
            ])

            # Data rows
            for key, person in self.persons.items():
                sources = ', '.join(set(att['source'] for att in person['attestations']))
                variants = ', '.join(person['variants'])
                roles = ', '.join(person['roles'])
                locations = ', '.join(person['locations'])
                first_att = person['attestations'][0]['source'] if person['attestations'] else ''

                writer.writerow([
                    person['canonical_name'],
                    variants,
                    len(person['attestations']),
                    sources,
                    roles,
                    locations,
                    first_att
                ])

        print(f"Exported CSV to: {output_path}")

    def generate_statistics(self):
        """Generate statistics about the prosopographic data"""
        total_persons = len(self.persons)
        total_attestations = sum(len(p['attestations']) for p in self.persons.values())

        # Most frequently attested persons
        freq_persons = sorted(
            [(k, len(v['attestations'])) for k, v in self.persons.items()],
            key=lambda x: x[1], reverse=True
        )[:10]

        # Source distribution
        source_counts = Counter()
        for person in self.persons.values():
            for att in person['attestations']:
                source_counts[att['source']] += 1

        print(f"\n=== PROSOPOGRAPHY STATISTICS ===")
        print(f"Total persons: {total_persons}")
        print(f"Total attestations: {total_attestations}")
        print(f"Average attestations per person: {total_attestations/total_persons:.2f}")

        print(f"\nMost frequently attested persons:")
        for name, count in freq_persons:
            print(f"  {name}: {count} attestations")

        print(f"\nTop sources by person mentions:")
        for source, count in source_counts.most_common(10):
            print(f"  {source}: {count} persons")

def main():
    parser = argparse.ArgumentParser(description='Extract prosopographic data from TEI/EpiDoc XML files')
    parser.add_argument('input_dir', help='Directory containing XML files')
    parser.add_argument('--output-json', help='Output JSON file path')
    parser.add_argument('--output-csv', help='Output CSV file path')
    parser.add_argument('--stats', action='store_true', help='Show statistics')

    args = parser.parse_args()

    extractor = ProsopographyExtractor()
    extractor.process_directory(args.input_dir)

    if args.output_json:
        extractor.export_to_json(args.output_json)

    if args.output_csv:
        extractor.export_to_csv(args.output_csv)

    if args.stats:
        extractor.generate_statistics()

    # Default exports if no specific output specified
    if not args.output_json and not args.output_csv:
        extractor.export_to_json('prosopography.json')
        extractor.export_to_csv('prosopography.csv')
        extractor.generate_statistics()

if __name__ == '__main__':
    main()
