import os
import json
import re
from lxml import etree
from pathlib import Path

class RobustECGProcessorVanilla:
    def __init__(self):
        self.xml_dir = "../../webapps/ROOT/content/xml/epidoc"
        self.output_dir = "../output"
        self.bibliography_path = "../../webapps/ROOT/content/xml/authority/bibliography.xml"
        self.images_dir = "../../webapps/ROOT/content/images"
        self.ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        self.inscriptions = []
        self.bibliography = {}


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
                persons_index = self.extract_all_persons_enhanced()
    
                if persons_index:
                    print(f"👥 Creating persons pages...")
                    self.create_enhanced_persons_index_page(persons_index)
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



    def debug_xml_processing(self):
        """Debug method to check XML processing issues"""
        try:
            xml_files = sorted(list(Path(self.xml_dir).glob("*.xml")))
            print(f"🔍 DEBUG: Found {len(xml_files)} XML files in {self.xml_dir}")

            if not xml_files:
                print(f"❌ No XML files found in directory: {Path(self.xml_dir).absolute()}")
                return False

            print(f"📁 XML directory path check:")
            xml_dir_path = Path(self.xml_dir)
            print(f"   Absolute path: {xml_dir_path.absolute()}")
            print(f"   Directory exists: {xml_dir_path.exists()}")
            print(f"   Is directory: {xml_dir_path.is_dir()}")

            if xml_dir_path.exists():
                all_files = list(xml_dir_path.glob("*"))
                print(f"   All files in directory: {len(all_files)}")
                xml_files_count = len([f for f in all_files if f.suffix.lower() == '.xml'])
                print(f"   XML files: {xml_files_count}")

            print(f"📁 First 10 XML files:")
            for i, xml_file in enumerate(xml_files[:10]):
                file_size = xml_file.stat().st_size if xml_file.exists() else 0
                print(f"   {i+1}. {xml_file.name} ({file_size} bytes)")
            if len(xml_files) > 10:
                print(f"   ... and {len(xml_files) - 10} more files")

            # Test processing the first file
            if xml_files:
                print(f"\n🔍 Testing processing of first file: {xml_files[0].name}")
                try:
                    test_inscription = self.process_single_xml_robust(xml_files[0])

                    if test_inscription:
                        print(f"✅ Successfully processed test file")
                        print(f"   ID: {test_inscription.get('id', 'NO_ID')}")
                        print(f"   Title: {self.get_display_title(test_inscription.get('title', 'NO_TITLE'))}")
                        print(f"   Language: {test_inscription.get('language', 'NO_LANG')}")
                        print(f"   Has text: {bool(test_inscription.get('text_content'))}")
                        print(f"   Has images: {len(test_inscription.get('images', []))}")
                        return True
                    else:
                        print(f"❌ process_single_xml_robust returned None for test file")
                        return False
                except Exception as e:
                    print(f"❌ Exception processing test file: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                return False

        except Exception as e:
            print(f"❌ Error in debug XML processing: {e}")
            import traceback
            traceback.print_exc()
            return False

    def debug_before_site_generation(self):
        """Debug state before generating site pages"""
        print(f"\n🔍 DEBUG: State before site generation:")
        print(f"   Inscriptions count: {len(self.inscriptions)}")
        print(f"   Bibliography entries: {len(self.bibliography)}")

        if self.inscriptions:
            print(f"   First inscription ID: {self.inscriptions[0].get('id')}")
            print(f"   Last inscription ID: {self.inscriptions[-1].get('id')}")

            # Check languages
            languages = set(insc.get('language', 'unknown') for insc in self.inscriptions)
            print(f"   Languages found: {sorted(languages)}")

            # Check for common issues
            empty_ids = [i for i, insc in enumerate(self.inscriptions) if not insc.get('id')]
            if empty_ids:
                print(f"   ⚠️ Found {len(empty_ids)} inscriptions with empty IDs")

            empty_titles = [i for i, insc in enumerate(self.inscriptions) if not insc.get('title')]
            if empty_titles:
                print(f"   ⚠️ Found {len(empty_titles)} inscriptions with empty titles")

        else:
            print(f"   ❌ NO INSCRIPTIONS - This will cause browse page to be empty!")
            print(f"   🔍 Checking if XML processing worked at all...")

            # Try to process one file manually for debugging
            xml_files = sorted(list(Path(self.xml_dir).glob("*.xml")))
            if xml_files:
                print(f"   📄 Attempting to manually process first XML file: {xml_files[0].name}")
                try:
                    test_result = self.process_single_xml_robust(xml_files[0])
                    if test_result:
                        print(f"   ✅ Manual processing worked - something went wrong in the loop")
                        print(f"   📊 Test result keys: {list(test_result.keys())}")
                    else:
                        print(f"   ❌ Manual processing also failed")
                except Exception as e:
                    print(f"   ❌ Manual processing threw exception: {e}")

        return len(self.inscriptions) > 0



    def process_bibliography(self):
        """Process the main bibliography.xml file"""
        try:
            if not Path(self.bibliography_path).exists():
                print(f"⚠️  Bibliography file not found at {self.bibliography_path}")
                return

            parser = etree.XMLParser(recover=True)
            tree = etree.parse(str(self.bibliography_path), parser)
            root = tree.getroot()

            print("📚 Processing bibliography...")

            # Find all bibl elements with xml:id
            bibl_elements = self.safe_xpath(root, './/tei:bibl[@xml:id]')

            for bibl in bibl_elements:
                bib_id = bibl.get('{http://www.w3.org/XML/1998/namespace}id') or bibl.get('xml:id')
                if bib_id:
                    # Extract abbreviation if present
                    abbrev_elem = self.safe_xpath(bibl, './tei:bibl[@type="abbrev"]')
                    abbrev_text = ""
                    if abbrev_elem:
                        abbrev_text = self.safe_get_element_text(abbrev_elem[0])

                    self.bibliography[bib_id] = {
                        'id': bib_id,
                        'type': 'bibl',
                        'content': self.safe_get_element_text(bibl),
                        'abbrev': abbrev_text,
                        'structured': self.parse_bibl_content(bibl)
                    }

            # Also check for biblStruct elements (though your file doesn't seem to have them)
            biblstruct_elements = self.safe_xpath(root, './/tei:biblStruct[@xml:id]')
            for biblstruct in biblstruct_elements:
                bib_id = biblstruct.get('{http://www.w3.org/XML/1998/namespace}id') or biblstruct.get('xml:id')
                if bib_id:
                    self.bibliography[bib_id] = {
                        'id': bib_id,
                        'type': 'biblStruct',
                        'content': self.safe_get_element_text(biblstruct),
                        'abbrev': "",
                        'structured': self.parse_biblstruct_content(biblstruct)
                    }

            print(f"📚 Processed {len(self.bibliography)} bibliography entries")

        except Exception as e:
            print(f"❌ Error processing bibliography: {e}")

    def build_bibliography_references(self):
        """Build back-references from bibliography to inscriptions"""
        try:
            # Create a mapping of bibliography entries to inscriptions that cite them
            bib_to_inscriptions = {}

            for inscription in self.inscriptions:
                for ref in inscription.get('bibliography_refs', []):
                    bib_id = ref['id']
                    if bib_id not in bib_to_inscriptions:
                        bib_to_inscriptions[bib_id] = []

                    # Add inscription info with cited range if available
                    inscription_ref = {
                        'id': inscription['id'],
                        'title': inscription['title'],
                        'cited_range': ref.get('cited_range', '')
                    }
                    bib_to_inscriptions[bib_id].append(inscription_ref)

            # Add back-references to bibliography entries
            for bib_id, inscription_refs in bib_to_inscriptions.items():
                if bib_id in self.bibliography:
                    self.bibliography[bib_id]['cited_by'] = inscription_refs

            print(f"🔗 Built back-references for {len(bib_to_inscriptions)} bibliography entries")

        except Exception as e:
            print(f"❌ Error building bibliography references: {e}")

    def parse_bibl_content(self, bibl):
        """Parse a bibl element for structured content"""
        try:
            result = {}

            # Extract author
            author_elems = self.safe_xpath(bibl, './/tei:author')
            if author_elems:
                result['author'] = self.safe_get_element_text(author_elems[0])

            # Extract title
            title_elems = self.safe_xpath(bibl, './/tei:title')
            if title_elems:
                result['title'] = self.safe_get_element_text(title_elems[0])

            # Extract date
            date_elems = self.safe_xpath(bibl, './/tei:date')
            if date_elems:
                result['date'] = self.safe_get_element_text(date_elems[0])

            # Extract publisher
            publisher_elems = self.safe_xpath(bibl, './/tei:publisher')
            if publisher_elems:
                result['publisher'] = self.safe_get_element_text(publisher_elems[0])

            return result
        except Exception:
            return {}

    def parse_biblstruct_content(self, biblstruct):
        """Parse a biblStruct element for structured content"""
        try:
            result = {}

            # Extract from analytic section (article/chapter info)
            analytic = self.safe_xpath(biblstruct, './tei:analytic')
            if analytic:
                analytic_elem = analytic[0]
                author_elems = self.safe_xpath(analytic_elem, './/tei:author')
                if author_elems:
                    result['author'] = self.safe_get_element_text(author_elems[0])
                title_elems = self.safe_xpath(analytic_elem, './/tei:title')
                if title_elems:
                    result['title'] = self.safe_get_element_text(title_elems[0])

            # Extract from monogr section (book/journal info)
            monogr = self.safe_xpath(biblstruct, './tei:monogr')
            if monogr:
                monogr_elem = monogr[0]
                if not result.get('author'):
                    author_elems = self.safe_xpath(monogr_elem, './/tei:author')
                    if author_elems:
                        result['author'] = self.safe_get_element_text(author_elems[0])

                if not result.get('title'):
                    title_elems = self.safe_xpath(monogr_elem, './/tei:title')
                    if title_elems:
                        result['title'] = self.safe_get_element_text(title_elems[0])

                # Extract imprint info
                imprint = self.safe_xpath(monogr_elem, './tei:imprint')
                if imprint:
                    imprint_elem = imprint[0]
                    date_elems = self.safe_xpath(imprint_elem, './/tei:date')
                    if date_elems:
                        result['date'] = self.safe_get_element_text(date_elems[0])
                    publisher_elems = self.safe_xpath(imprint_elem, './/tei:publisher')
                    if publisher_elems:
                        result['publisher'] = self.safe_get_element_text(publisher_elems[0])

            return result
        except Exception:
            return {}

    def copy_images(self):
        """Copy images to output directory"""
        try:
            images_source = Path(self.images_dir)
            images_dest = Path(f"{self.output_dir}/static/images")

            if not images_source.exists():
                print(f"⚠️  Images directory not found at {images_source}")
                return

            # Copy image files
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
            copied = 0

            for img_file in images_source.rglob('*'):
                if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                    dest_file = images_dest / img_file.relative_to(images_source)
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    try:
                        import shutil
                        shutil.copy2(img_file, dest_file)
                        copied += 1
                    except Exception as e:
                        print(f"⚠️  Could not copy {img_file.name}: {e}")

            print(f"🖼️  Copied {copied} images")

        except Exception as e:
            print(f"❌ Error copying images: {e}")

    def find_inscription_images(self, inscription_id):
        """Find images related to an inscription"""
        try:
            images = []
            images_source = Path(self.images_dir)

            if not images_source.exists():
                return images

            # Look for images matching the inscription ID
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

            for img_file in images_source.rglob(f"{inscription_id}*"):
                if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                    relative_path = img_file.relative_to(images_source)
                    images.append({
                        'filename': img_file.name,
                        'path': str(relative_path).replace('\\', '/'),
                        'caption': self.generate_image_caption(img_file.name)
                    })

            return sorted(images, key=lambda x: x['filename'])
        except Exception:
            return []

    def generate_image_caption(self, filename):
        """Generate a caption for an image based on filename"""
        try:
            # Remove extension and inscription ID
            name = Path(filename).stem

            # Simple caption generation based on common patterns
            if '_photo' in name.lower() or '_photograph' in name.lower():
                return "Photograph of inscription"
            elif '_drawing' in name.lower() or '_sketch' in name.lower():
                return "Drawing of inscription"
            elif '_detail' in name.lower():
                return "Detail view"
            elif '_context' in name.lower():
                return "Contextual view"
            else:
                return "Image of inscription"
        except Exception:
            return "Image"

    def extract_facsimile_images(self, root):
        """Extract image references from facsimile section"""
        try:
            images = []

            # Look for facsimile/surface/graphic elements
            graphic_elems = self.safe_xpath(root, './/tei:facsimile//tei:graphic[@url]')

            for graphic in graphic_elems:
                url = graphic.get('url', '')
                if url:
                    # Extract descriptions in different languages
                    desc_ka = ""
                    desc_en = ""

                    # Look for desc elements as siblings or children
                    desc_elems = self.safe_xpath(graphic.getparent(), './/tei:desc')
                    for desc in desc_elems:
                        lang = desc.get('{http://www.w3.org/XML/1998/namespace}lang', '')
                        text = self.safe_get_element_text(desc)
                        if lang == 'ka':
                            desc_ka = text
                        elif lang == 'en':
                            desc_en = text

                    # Check if image file exists
                    image_path = Path(self.images_dir) / url
                    if image_path.exists():
                        images.append({
                            'filename': url,
                            'path': url,
                            'caption_ka': desc_ka,
                            'caption_en': desc_en,
                            'caption': desc_en if desc_en else (desc_ka if desc_ka else self.generate_image_caption(url))
                        })
                    else:
                        print(f"⚠️  Image not found: {image_path}")

            return images

        except Exception as e:
            print(f"❌ Error extracting facsimile images: {e}")
            return []

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

            # Extract facsimile images first
            facsimile_images = self.extract_facsimile_images(root)

            # Fallback to filename-based search if no facsimile images found
            if not facsimile_images:
                facsimile_images = self.find_inscription_images(ecg_id)

            # Extract data with safe methods
            inscription = {
                'id': ecg_id,
                'filename': xml_path.name,
                'title': self.safe_extract_title(root),
                'summary': self.safe_extract_summary(root),
                'dating': self.safe_extract_dating(root),
                'origin': self.safe_extract_origin(root),
                'material': self.safe_extract_material(root),
                'object_type': self.safe_extract_object_type(root),
                'dimensions': self.safe_extract_dimensions(root),
                'text_content': self.safe_extract_text_content(root),
                'translation': self.safe_extract_translation(root),
                'commentary': self.safe_extract_commentary(root),
                'bibliography': self.safe_extract_bibliography(root),
                'bibliography_refs': self.extract_bibliography_references(root),
                'images': facsimile_images,
                'language': self.safe_detect_language(root),
                'xml_source': self.safe_get_xml_string(root),
                'xml_root': root
            }

            return inscription

        except Exception as e:
            print(f"❌ Error processing {xml_path.name}: {e}")
            return None

    def extract_bibliography_references(self, root):
        """Extract bibliography references (ptr/@target) from inscription - FIXED VERSION"""
        try:
            refs = []
            # Look for ptr elements with target attributes in bibliography divs
            bibliography_divs = self.safe_xpath(root, './/tei:div[@type="bibliography"]')

            for div in bibliography_divs:
                ptr_elements = self.safe_xpath(div, './/tei:ptr[@target]')

                for ptr in ptr_elements:
                    target = ptr.get('target', '')
                    if target.startswith('#'):
                        bib_id = target[1:]  # Remove the #
                        if bib_id in self.bibliography:
                            # Get the parent bibl element to extract citedRange if present
                            parent_bibl = ptr.getparent()
                            cited_range = ""
                            if parent_bibl is not None:
                                # Look for citedRange elements in the same bibl
                                cited_range_elems = self.safe_xpath(parent_bibl, './/tei:citedRange')
                                if cited_range_elems:
                                    cited_range = self.safe_get_element_text(cited_range_elems[0])

                            refs.append({
                                'id': bib_id,
                                'entry': self.bibliography[bib_id],
                                'cited_range': cited_range
                            })

            # Also look for ref elements with target attributes
            ref_elements = self.safe_xpath(root, './/tei:ref[@target]')

            for ref in ref_elements:
                target = ref.get('target', '')
                if target.startswith('#'):
                    bib_id = target[1:]  # Remove the #
                    if bib_id in self.bibliography:
                        refs.append({
                            'id': bib_id,
                            'entry': self.bibliography[bib_id],
                            'cited_range': ""
                        })

            return refs
        except Exception:
            return []

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
        """Safely extract title with bilingual support"""
        try:
            titles = {}
            title_elems = self.safe_xpath(root, './/tei:titleStmt/tei:title')

            for elem in title_elems:
                lang = elem.get('{http://www.w3.org/XML/1998/namespace}lang', 'default')
                title_text = self.safe_get_text(elem)
                if title_text:
                    titles[lang] = title_text

            # Fallback to any title if no titleStmt
            if not titles:
                title_elems = self.safe_xpath(root, './/tei:title')
                for elem in title_elems:
                    lang = elem.get('{http://www.w3.org/XML/1998/namespace}lang', 'default')
                    title_text = self.safe_get_text(elem)
                    if title_text:
                        titles[lang] = title_text

            # Return bilingual title or fallback
            if titles:
                return titles

            # Final fallback
            idno_elems = root.xpath('.//tei:idno', namespaces=self.ns)
            idno_text = idno_elems[0].text if idno_elems else 'Unknown'
            return {'default': f"Inscription {idno_text}"}

        except Exception:
            return {'default': "Untitled Inscription"}

    def safe_extract_summary(self, root):
        """Safely extract summary with bilingual support"""
        try:
            summaries = {}
            summary_elems = self.safe_xpath(root, './/tei:summary')

            for elem in summary_elems:
                lang = elem.get('{http://www.w3.org/XML/1998/namespace}lang', 'default')
                summary_text = self.safe_get_element_text(elem)
                if summary_text:
                    summaries[lang] = summary_text

            return summaries if summaries else {}
        except Exception:
            return {}

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
        """Safely extract material with links"""
        try:
            material_elems = self.safe_xpath(root, './/tei:material')
            if material_elems:
                materials = []
                for elem in material_elems:
                    material_text = self.safe_get_text(elem)
                    material_ref = elem.get('ref', '')
                    material_lang = elem.get('{http://www.w3.org/XML/1998/namespace}lang', '')

                    if material_text:
                        materials.append({
                            'text': material_text,
                            'ref': material_ref,
                            'lang': material_lang
                        })

                return materials if materials else ""
            return ""
        except Exception:
            return ""

    def safe_extract_object_type(self, root):
        """Safely extract object type with links"""
        try:
            object_type_elems = self.safe_xpath(root, './/tei:objectType')
            if object_type_elems:
                object_types = []
                for elem in object_type_elems:
                    obj_text = self.safe_get_text(elem)
                    obj_ref = elem.get('ref', '')
                    obj_lang = elem.get('{http://www.w3.org/XML/1998/namespace}lang', '')

                    if obj_text:
                        object_types.append({
                            'text': obj_text,
                            'ref': obj_ref,
                            'lang': obj_lang
                        })

                return object_types if object_types else ""
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
        """Process EpiDoc edition text with academic formatting - NO COLOR CODING"""
        try:
            if div is None:
                return ""

            # Create interpretive edition (normal processing with spaces)
            interpretive_result = self.process_edition_with_lines(div, "interpretive")

            # Create diplomatic edition (abbreviations only, script converted)
            diplomatic_result = self.process_edition_with_lines(div, "diplomatic")

            # Return both versions with bilingual academic styling
            result = f"""<div class="edition-container">
                <div class="interpretive-edition">
                    <h4 class="edition-title bilingual-label"><span class="ka">კრიტიკული გამოცემა</span> <span class="en">Interpretive Edition</span></h4>
                    <div class="edition-text academic-edition">{interpretive_result}</div>
                </div>
                <div class="diplomatic-edition">
                    <h4 class="edition-title bilingual-label"><span class="ka">დიპლომატიური გამოცემა</span> <span class="en">Diplomatic Edition</span></h4>
                    <div class="edition-text academic-edition diplomatic-text">{diplomatic_result}</div>
                </div>
            </div>"""

            return result

        except Exception as e:
            print(f"⚠️  EpiDoc processing error: {e}")
            return self.safe_get_element_text(div)


    def process_edition_with_lines(self, elem, edition_type):
        """Process edition with proper line handling - ACADEMIC CLEAN VERSION"""
        try:
            if elem is None:
                return ""

            # Get language and ana for script conversion
            lang = self.get_element_language(elem)
            ana_value = self.get_element_ana(elem)

            # Process the element tree while tracking line breaks
            result = self.process_element_for_lines(elem, edition_type, lang, ana_value)

            # Split result by line break markers and format
            parts = result.split('|||LB|||')
            formatted_lines = []

            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue

                # Check if this part contains a line number marker
                if part.startswith('LN:'):
                    # Extract line number and content
                    if ':' in part[3:]:  # Skip 'LN:' and look for next ':'
                        colon_pos = part.find(':', 3)  # Find colon after 'LN:'
                        line_num = part[3:colon_pos]  # Extract line number
                        content = part[colon_pos+1:].strip()  # Extract content

                        # Clean up extra spaces in content but preserve single spaces between words
                        import re
                        content = re.sub(r'\s+', ' ', content).strip()

                        if line_num.isdigit():
                            line_number = int(line_num)
                            # ONLY show line numbers for every 5th line (5, 10, 15, etc.) - NEVER line 1
                            if line_number % 5 == 0 and line_number > 0:
                                formatted_lines.append(f'<div class="edition-line numbered-line"><span class="line-number">{line_num}</span><span class="line-content">{content}</span></div>')
                            else:
                                # Don't show line number, just content
                                formatted_lines.append(f'<div class="edition-line"><span class="line-content">{content}</span></div>')
                        else:
                            # Malformed line marker, treat as regular content
                            content = part.replace('LN:', '').strip()
                            import re
                            content = re.sub(r'\s+', ' ', content).strip()
                            formatted_lines.append(f'<div class="edition-line"><span class="line-content">{content}</span></div>')
                    else:
                        # Malformed line marker, treat as regular content
                        content = part.replace('LN:', '').strip()
                        import re
                        content = re.sub(r'\s+', ' ', content).strip()
                        formatted_lines.append(f'<div class="edition-line"><span class="line-content">{content}</span></div>')
                else:
                    # Regular content without line marker
                    if part.strip():
                        import re
                        content = re.sub(r'\s+', ' ', part).strip()
                        formatted_lines.append(f'<div class="edition-line"><span class="line-content">{content}</span></div>')

            return '\n'.join(formatted_lines) if formatted_lines else f'<div class="edition-line"><span class="line-content">{result}</span></div>'

        except Exception as e:
            print(f"Error processing edition with lines: {e}")
            return f'<div class="edition-line"><span class="line-content">{str(e)}</span></div>'


    def process_element_for_lines(self, elem, edition_type, lang, ana_value):
        """Process element while preserving line structure and spaces - CLEAN VERSION"""
        try:
            if elem is None:
                return ""

            result = ""

            # Handle text before children - preserve spaces
            if elem.text and not self.is_comment_text(elem.text):
                text = elem.text
                if text:
                    if edition_type == "diplomatic":
                        text = self.convert_to_diplomatic_script(text, lang, ana_value)
                    result += text

            # Process children
            for i, child in enumerate(elem):
                child_tag = str(child.tag) if child.tag is not None else ""

                if 'lb' in child_tag:
                    # Line break handling
                    line_num = child.get('n', '')
                    break_attr = child.get('break', '')

                    # Add hyphen for word continuation in interpretive edition only
                    if break_attr == 'no' and edition_type == "interpretive":
                        result += '-'

                    # Add line break marker with line number
                    if line_num:
                        result += f'|||LB|||LN:{line_num}:'
                    else:
                        result += f'|||LB|||'

                elif 'expan' in child_tag:
                    # Handle expansions
                    if edition_type == "diplomatic":
                        # Only show abbreviated form
                        for grandchild in child:
                            if 'abbr' in str(grandchild.tag):
                                abbr_text = self.process_element_for_lines(grandchild, edition_type, lang, ana_value)
                                result += abbr_text
                    else:
                        # Show expanded form abbr(ex)
                        abbr_parts = []
                        ex_parts = []

                        for grandchild in child:
                            if 'abbr' in str(grandchild.tag):
                                abbr_parts.append(self.process_element_for_lines(grandchild, edition_type, lang, ana_value))
                            elif 'ex' in str(grandchild.tag):
                                ex_parts.append(self.process_element_for_lines(grandchild, edition_type, lang, ana_value))

                        # Combine properly
                        combined = ""
                        for j in range(max(len(abbr_parts), len(ex_parts))):
                            if j < len(abbr_parts):
                                combined += abbr_parts[j]
                            if j < len(ex_parts):
                                combined += f"({ex_parts[j]})"
                        result += combined

                elif any(name_elem in child_tag for name_elem in ['name', 'persName', 'placeName', 'roleName', 'geogName', 'orgName']):
                    # Handle names - ADD SPACE BEFORE if not at start and previous wasn't a line break
                    if result and not result.endswith('|||LB|||') and not result.endswith(':'):
                        # Check if we need a space - don't add if last character is already a space or hyphen
                        if not result[-1].isspace() and result[-1] != '-':
                            result += ' '

                    name_content = self.process_element_for_lines(child, edition_type, lang, ana_value)

                    # Get attributes for links and tooltips
                    ref = child.get('ref', '')
                    key = child.get('key', '')
                    name_type = child.get('type', '')

                    # Build tooltip text
                    tooltip_parts = []
                    if key:
                        tooltip_parts.append(f"key: {key}")
                    if name_type:
                        tooltip_parts.append(f"type: {name_type}")

                    tooltip = "; ".join(tooltip_parts) if tooltip_parts else ""

                    # Create the formatted element with link if available
                    if ref and edition_type == "interpretive":
                        # Create clickable link with tooltip
                        if tooltip:
                            result += f'<strong class="name-element"><a href="{ref}" target="_blank" title="{tooltip}" class="external-link">{name_content}</a></strong>'
                        else:
                            result += f'<strong class="name-element"><a href="{ref}" target="_blank" class="external-link">{name_content}</a></strong>'
                    elif tooltip and edition_type == "interpretive":
                        # Just tooltip, no link
                        result += f'<strong class="name-element" title="{tooltip}">{name_content}</strong>'
                    else:
                        # Plain bold text (diplomatic edition or no attributes)
                        result += f'<strong class="name-element">{name_content}</strong>'

                elif 'w' in child_tag:
                    # Handle words - ADD SPACE BEFORE if not at start and previous wasn't a line break
                    if result and not result.endswith('|||LB|||') and not result.endswith(':'):
                        # Check if we need a space - don't add if last character is already a space or hyphen
                        if not result[-1].isspace() and result[-1] != '-':
                            result += ' '

                    word_content = self.process_element_for_lines(child, edition_type, lang, ana_value)
                    lemma = child.get('lemma', '')
                    if lemma and edition_type == "interpretive":
                        result += f'<span class="word-element" title="lemma: {lemma}">{word_content}</span>'
                    else:
                        result += word_content

                else:
                    # Recursively process other elements
                    child_result = self.process_element_for_lines(child, edition_type, lang, ana_value)
                    result += child_result

                # Handle tail text - preserve spaces
                if child.tail and not self.is_comment_text(child.tail):
                    tail = child.tail
                    if tail:
                        if edition_type == "diplomatic":
                            tail = self.convert_to_diplomatic_script(tail, lang, ana_value)
                        result += tail

            return result

        except Exception as e:
            print(f"Error processing element: {e}")
            return ""


    def format_xml_source(self, div):
        """Format XML source with syntax highlighting for the XML tab"""
        try:
            if div is None:
                return ""

            # Get the XML string of just the edition div
            xml_string = etree.tostring(div, encoding='unicode', pretty_print=True)

            # Apply syntax highlighting
            formatted_xml = self.highlight_xml_syntax(xml_string)

            return formatted_xml

        except Exception as e:
            print(f"Error formatting XML: {e}")
            return str(div) if div is not None else ""

    #აქ იწყება XML სინტაქსის ხაზგასმა
    def highlight_xml_syntax(self, xml_string):
        """Apply simple syntax highlighting to XML"""
        try:
            import html

            # Simply escape the XML and return it with basic styling
            # The CSS will handle the colors
            escaped_xml = html.escape(xml_string)

            # Very simple highlighting - just wrap the whole thing
            return f'<pre class="xml-content">{escaped_xml}</pre>'

        except Exception as e:
            print(f"Error highlighting XML: {e}")
            return f'<pre class="xml-content">{html.escape(xml_string) if xml_string else ""}</pre>'


    def process_edition_recursive(self, elem, edition_type):
        """Recursively process edition elements with proper EpiDoc line formatting"""
        try:
            if elem is None:
                return ""

            tag_name = str(elem.tag) if elem.tag is not None else ""
            result = ""

            # Get language and ana for script conversion
            lang = self.get_element_language(elem)
            ana_value = self.get_element_ana(elem)

            # Handle text before children (skip if it's a comment)
            if elem.text and not self.is_comment_text(elem.text):
                text = elem.text
                if edition_type == "diplomatic":
                    text = self.convert_to_diplomatic_script(text, lang, ana_value)
                result += text

            # Process children
            for i, child in enumerate(elem):
                child_tag = str(child.tag) if child.tag is not None else ""

                if 'lb' in child_tag:
                    # Line break handling according to EpiDoc/Leiden conventions
                    line_num = child.get('n', '')
                    break_attr = child.get('break', '')

                    # For interpretive edition, add hyphen for word continuation
                    if break_attr == 'no' and edition_type == "interpretive":
                        result += '-'
                    # For diplomatic edition, NO hyphen - just break the line

                    # Add proper line break with number
                    if line_num and line_num.isdigit():
                        line_number = int(line_num)
                        # Show line numbers only for every 5th line, or line 1
                        if line_number % 5 == 0:
                            result += f'\n<span class="line-number major">{line_num}</span> '
                        else:
                            # Just line break, no visible number
                            result += '\n<span class="line-break"></span>'
                    else:
                        result += '\n'

                elif 'expan' in child_tag:
                    # Handle expansion
                    if edition_type == "diplomatic":
                        # Only show abbr content
                        for grandchild in child:
                            if 'abbr' in str(grandchild.tag):
                                abbr_text = self.process_edition_recursive(grandchild, edition_type)
                                result += abbr_text
                    else:
                        # Show abbr(ex) format
                        abbr_parts = []
                        ex_parts = []

                        for grandchild in child:
                            if 'abbr' in str(grandchild.tag):
                                abbr_parts.append(self.process_edition_recursive(grandchild, edition_type))
                            elif 'ex' in str(grandchild.tag):
                                ex_parts.append(self.process_edition_recursive(grandchild, edition_type))

                        # Combine abbr and ex properly
                        combined = ""
                        for j in range(max(len(abbr_parts), len(ex_parts))):
                            if j < len(abbr_parts):
                                combined += abbr_parts[j]
                            if j < len(ex_parts):
                                combined += f"({ex_parts[j]})"
                        result += combined

                elif any(text_elem in child_tag for text_elem in ['name', 'persName', 'placeName', 'geogName', 'orgName', 'roleName']):
                    # Name-type elements (name, persName, placeName, roleName, etc.)
                    name_content = self.process_edition_recursive(child, edition_type)

                    # Get attributes for tooltip and links
                    nymref = child.get('nymRef', '')
                    ref = child.get('ref', '')
                    key = child.get('key', '')
                    name_type = child.get('type', '')

                    # Build tooltip text
                    tooltip_parts = []
                    if nymref:
                        tooltip_parts.append(f"refers to: {nymref}")
                    if key:
                        tooltip_parts.append(f"key: {key}")
                    if name_type:
                        tooltip_parts.append(f"type: {name_type}")

                    tooltip = "; ".join(tooltip_parts) if tooltip_parts else ""

                    # Create the formatted element
                    if ref and edition_type == "interpretive":
                        # Create clickable link with tooltip
                        if tooltip:
                            result += f'<strong><a href="{ref}" target="_blank" title="{tooltip}" class="external-link">{name_content}</a></strong>'
                        else:
                            result += f'<strong><a href="{ref}" target="_blank" class="external-link">{name_content}</a></strong>'
                    elif tooltip and edition_type == "interpretive":
                        # Just tooltip, no link
                        result += f'<strong title="{tooltip}">{name_content}</strong>'
                    else:
                        # Plain bold text
                        result += f'<strong>{name_content}</strong>'

                    # Check if we need space after the name
                    next_sibling = child.getnext()
                    if next_sibling is not None and not ('lb' in str(next_sibling.tag) and next_sibling.get('break') == 'no'):
                        result += ' '

                elif 'w' in child_tag:
                    # Word element - process children and add lemma if interpretive
                    word_content = self.process_edition_recursive(child, edition_type)
                    lemma = child.get('lemma', '')
                    if lemma and edition_type == "interpretive":
                        result += f'<span title="lemma: {lemma}">{word_content}</span>'
                    else:
                        result += word_content

                    # Check if we need space after the word
                    next_sibling = child.getnext()
                    if next_sibling is not None and not ('lb' in str(next_sibling.tag) and next_sibling.get('break') == 'no'):
                        result += ' '

                else:
                    # Process other elements recursively
                    result += self.process_edition_recursive(child, edition_type)

                # Handle tail text (skip if it's a comment)
                if child.tail and not self.is_comment_text(child.tail):
                    tail = child.tail
                    if edition_type == "diplomatic":
                        tail = self.convert_to_diplomatic_script(tail, lang, ana_value)
                    result += tail

            return result

        except Exception as e:
            print(f"Error in recursive processing: {e}")
            return ""

    def format_edition_lines(self, text):
        """Format edition text with proper line structure according to EpiDoc conventions"""
        try:
            if not text:
                return ""

            # Split by actual line breaks and process each line
            lines = text.split('\n')
            formatted_lines = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if line starts with line number (major)
                if line.startswith('<span class="line-number major'):
                    formatted_lines.append(f'<div class="edition-line numbered">{line}</div>')
                # Check if line starts with line break marker (no number)
                elif line.startswith('<span class="line-break">'):
                    # Remove the line-break span and just create a regular line
                    content = line.replace('<span class="line-break"></span>', '').strip()
                    if content:
                        formatted_lines.append(f'<div class="edition-line">{content}</div>')
                    else:
                        formatted_lines.append(f'<div class="edition-line"></div>')
                elif formatted_lines:
                    # This is continuation of previous line, append to last line
                    last_line = formatted_lines[-1]
                    if last_line.endswith('</div>'):
                        formatted_lines[-1] = last_line[:-6] + ' ' + line + '</div>'
                    else:
                        formatted_lines[-1] += ' ' + line
                else:
                    # First line without number
                    formatted_lines.append(f'<div class="edition-line">{line}</div>')

            return '\n'.join(formatted_lines)

        except Exception as e:
            print(f"Error formatting edition lines: {e}")
            return text




    def is_comment_text(self, text):
        """Check if text is from an XML comment"""
        try:
            if not text:
                return False
            # Comments often contain extra whitespace and line breaks
            # This is a simple heuristic - you might need to adjust
            stripped = text.strip()
            if not stripped:
                return True
            # Check for comment-like patterns (lots of whitespace, specific Georgian words that appear in your comment)
            if 'ქე გაოსენე' in stripped or len(stripped.split('\n')) > 3:
                return True
            return False
        except Exception:
            return False
    #XML ფორმატირება
    def format_xml_source_for_edition(self, text_content):
        """Format XML source for display in XML tab"""
        try:
            # For now, create a mock XML structure based on text_content
            # This is a simplified version - you can enhance it later
            if not text_content:
                return '<div class="xml-notice">No edition content available</div>'

            # Create a sample XML structure
            xml_sample = '''<div type="edition" xml:lang="ka" ana="mtavruli" xml:space="preserve">
    <ab>
        <lb n="1"/><w lemma="ქრისტე"><expan><abbr>ქ</abbr><ex>რისტ</ex><abbr>ე</abbr></expan></w>
        <w lemma="განსუენება"><expan><abbr>გა</abbr><ex>ნ</ex><abbr>ო</abbr><ex>ჳ</ex><abbr>ს</abbr><ex>უ</ex><abbr>ენე</abbr></expan></w>
        <w lemma="სულ">სოჳ<lb n="2" break="no"/>ლსა</w>
        <name nymRef="ვაჩა">ვაჩაჲს<lb n="3" break="no"/>ასა</name>
        <name nymRef="გურა"><expan><abbr>გო</abbr><ex>ჳ</ex><abbr>რაჲ<lb n="4" break="no"/>სასა</abbr></expan></name>
        <name nymRef="მირა"><expan><abbr>მ</abbr><ex>ი</ex><abbr>რა</abbr><ex>ჲ</ex><abbr>ს</abbr><ex>ა</ex><abbr>ს</abbr><ex>ა</ex></expan></name>
    </ab>
</div>'''

            return self.highlight_xml_syntax(xml_sample)

        except Exception as e:
            return f'<div class="xml-error">Error formatting XML: {e}</div>'

    #აქ იწყება ტექსტის ტრანსფორმაცია
    def convert_to_diplomatic_script(self, text, lang, ana_value):
        """Convert text to diplomatic edition following EpiDoc standards"""
        try:
            if not text or not isinstance(text, str):
                return text

            # Georgian script conversions
            if lang == 'ka':
                georgian_lower = 'აბგდევზჱთიკლმნჲოპჟრსტჳუფქღყშჩცძწჭხჴჯჰჵ'

                if ana_value == 'mtavruli':
                    # Asomtavruli (Georgian majuscule/capitals)
                    georgian_upper = 'ႠႡႢႣႤႥႦჁႧႨႩႪႫႬჂႭႮႯႰႱႲჃႳႴႵႶႷႸႹႺႻႼႽႾჄႿჀჅ'
                    return text.translate(str.maketrans(georgian_lower, georgian_upper))

                elif ana_value == 'nuskhuri':
                    # Nuskhuri (Georgian ecclesiastical script)
                    georgian_nuskhuri = 'ⴀⴁⴂⴃⴄⴅⴆⴡⴇⴈⴉⴊⴋⴌⴢⴍⴎⴏⴐⴑⴒⴣⴓⴔⴕⴖⴗⴘⴙⴚⴛⴜⴝⴞⴤⴟⴠⴥ'
                    return text.translate(str.maketrans(georgian_lower, georgian_nuskhuri))

            # Armenian script conversion
            elif lang == 'hy':
                armenian_lower = 'աբգդեզէըթժիլխծկհձղճմյնշոչպջռսվտրցւփք'
                armenian_upper = 'ԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՒՓՔ'
                return text.translate(str.maketrans(armenian_lower, armenian_upper))

            # Greek and other scripts - uppercase with diacritics removed
            else:
                # Remove punctuation and normalize
                text = text.replace("'", "").replace("··", "").replace(",", "").replace(".", "").replace(";", "")
                text = text.replace("\n", "").replace(" ", "")

                # Greek specific character normalization
                text = text.replace('\u03f2', '\u03f9')  # lunate sigma normalization

                # Convert to uppercase and remove diacritics
                import unicodedata
                # Normalize to NFD (decomposed form)
                text = unicodedata.normalize('NFD', text)

                # Remove Greek diacritics
                diacritics_to_remove = '\u0300\u0301\u0308\u0313\u0314\u0342\u0345'
                for diacritic in diacritics_to_remove:
                    text = text.replace(diacritic, '')

                return text.upper()

            return text

        except Exception:
            return text
    #აქ მთავრდება ტექსტის ტრანსფორმაცია

    #აქ იწყება ენის მოძებნა
    def get_element_language(self, elem):
        """Get language from element or ancestors"""
        try:
            # Check current element first
            lang = elem.get('{http://www.w3.org/XML/1998/namespace}lang', '')
            if lang:
                return lang

            # Check ancestors
            parent = elem.getparent()
            while parent is not None:
                lang = parent.get('{http://www.w3.org/XML/1998/namespace}lang', '')
                if lang:
                    return lang
                parent = parent.getparent()

            return 'unknown'
        except Exception:
            return 'unknown'
    #აქ მთავრდება ენის მოძებნა

    #აქ იწყება ანას მოძებნა
    def get_element_ana(self, elem):
        """Get ana attribute from element or ancestors"""
        try:
            # Check current element first
            ana = elem.get('ana', '')
            if ana:
                return ana

            # Check ancestors
            parent = elem.getparent()
            while parent is not None:
                ana = parent.get('ana', '')
                if ana:
                    return ana
                parent = parent.getparent()

            return ''
        except Exception:
            return ''
    #აქ მთავრდება ანას მოძებნა
    def get_element_language(self, elem):
        """Get language from element or ancestors"""
        try:
            # Check current element first
            lang = elem.get('{http://www.w3.org/XML/1998/namespace}lang', '')
            if lang:
                return lang

            # Check ancestors
            parent = elem.getparent()
            while parent is not None:
                lang = parent.get('{http://www.w3.org/XML/1998/namespace}lang', '')
                if lang:
                    return lang
                parent = parent.getparent()

            return 'unknown'
        except Exception:
            return 'unknown'
    #აქ მთავრდება ენის მოძებნა

    #აქ იწყება ანას მოძებნა
    def get_element_ana(self, elem):
        """Get ana attribute from element or ancestors"""
        try:
            # Check current element first
            ana = elem.get('ana', '')
            if ana:
                return ana

            # Check ancestors
            parent = elem.getparent()
            while parent is not None:
                ana = parent.get('ana', '')
                if ana:
                    return ana
                parent = parent.getparent()

            return ''
        except Exception:
            return ''

    def safe_extract_translation(self, root):
        """Safely extract translation"""
        try:
            trans_elems = self.safe_xpath(root, './/tei:div[@type="translation"]')
            if trans_elems:
                translations = {}
                for trans_elem in trans_elems:
                    lang = trans_elem.get('{http://www.w3.org/XML/1998/namespace}lang', 'default')
                    translation_text = self.safe_get_element_text(trans_elem)
                    if translation_text:
                        translations[lang] = translation_text

                # Return bilingual translations or single translation
                if translations:
                    return translations
                else:
                    # Fallback to first translation element
                    return self.safe_get_element_text(trans_elems[0])
            return ""
        except Exception:
            return ""

    def safe_extract_commentary(self, root):
        """Safely extract commentary"""
        try:
            comm_elems = self.safe_xpath(root, './/tei:div[@type="commentary"]')
            if comm_elems:
                commentaries = {}
                for comm_elem in comm_elems:
                    lang = comm_elem.get('{http://www.w3.org/XML/1998/namespace}lang', 'default')
                    commentary_text = self.safe_get_element_text(comm_elem)
                    if commentary_text:
                        commentaries[lang] = commentary_text

                # Return bilingual commentaries or single commentary
                if commentaries:
                    return commentaries
                else:
                    # Fallback to first commentary element
                    return self.safe_get_element_text(comm_elems[0])
            return ""
        except Exception:
            return ""

    def safe_extract_bibliography(self, root):
        """Safely extract bibliography from listBibl elements - ENHANCED VERSION"""
        try:
            bibliography = []

            # Look for bibliography div first
            bibl_divs = self.safe_xpath(root, './/tei:div[@type="bibliography"]')

            for div in bibl_divs:
                # Look for bibl elements directly in the bibliography div
                bibl_elems = self.safe_xpath(div, './/tei:bibl')

                for bibl in bibl_elems:
                    # Extract the full text content
                    bib_text = self.safe_get_element_text(bibl)

                    # Also look for ptr and citedRange separately
                    ptr_elems = self.safe_xpath(bibl, './/tei:ptr[@target]')
                    cited_range_elems = self.safe_xpath(bibl, './/tei:citedRange')

                    # If we have ptr and citedRange, format them properly
                    if ptr_elems and cited_range_elems:
                        target = ptr_elems[0].get('target', '').replace('#', '')
                        cited_range = self.safe_get_element_text(cited_range_elems[0])

                        # Get the bibliography entry if it exists
                        if target in self.bibliography:
                            bib_entry = self.bibliography[target]
                            # Use abbreviation if available, otherwise use content
                            display_text = bib_entry.get('abbrev', '') or bib_entry.get('content', '')
                            if cited_range:
                                bib_text = f"{display_text}, {cited_range}"
                            else:
                                bib_text = display_text

                    if bib_text and bib_text.strip():
                        bibliography.append(bib_text.strip())

            # Fallback: look in listBibl if nothing found in bibliography div
            if not bibliography:
                bibl_elems = self.safe_xpath(root, './/tei:listBibl//tei:bibl')
                for bibl in bibl_elems:
                    bib_text = self.safe_get_element_text(bibl)
                    if bib_text:
                        bibliography.append(bib_text)

            return bibliography
        except Exception:
            return []




    def extract_facsimile_images(self, root):
        """Extract image references from facsimile section"""
        try:
            images = []

            # Look for facsimile/surface/graphic elements
            graphic_elems = self.safe_xpath(root, './/tei:facsimile//tei:graphic[@url]')

            for graphic in graphic_elems:
                url = graphic.get('url', '')
                if url:
                    # Skip URLs that are web links (not local images)
                    if url.startswith('http://') or url.startswith('https://'):
                        print(f"⚠️  Skipping web URL in facsimile: {url}")
                        continue

                    # Extract descriptions in different languages
                    desc_ka = ""
                    desc_en = ""

                    # Look for desc elements as siblings or children
                    desc_elems = self.safe_xpath(graphic.getparent(), './/tei:desc')
                    for desc in desc_elems:
                        lang = desc.get('{http://www.w3.org/XML/1998/namespace}lang', '')
                        text = self.safe_get_element_text(desc)
                        if lang == 'ka':
                            desc_ka = text
                        elif lang == 'en':
                            desc_en = text

                    # Check if image file exists
                    image_path = Path(self.images_dir) / url
                    if image_path.exists():
                        images.append({
                            'filename': url,
                            'path': url,
                            'caption_ka': desc_ka,
                            'caption_en': desc_en,
                            'caption': desc_en if desc_en else (desc_ka if desc_ka else self.generate_image_caption(url))
                        })
                    else:
                        print(f"⚠️  Image not found: {image_path}")

            return images

        except Exception as e:
            print(f"❌ Error extracting facsimile images: {e}")
            return []

    def find_inscription_images(self, inscription_id):
        """Find images related to an inscription"""
        try:
            images = []
            images_source = Path(self.images_dir)

            if not images_source.exists():
                return images

            # Look for images matching the inscription ID
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

            for img_file in images_source.rglob(f"{inscription_id}*"):
                if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                    relative_path = img_file.relative_to(images_source)
                    images.append({
                        'filename': img_file.name,
                        'path': str(relative_path).replace('\\', '/'),
                        'caption': self.generate_image_caption(img_file.name)
                    })

            return sorted(images, key=lambda x: x['filename'])
        except Exception:
            return []

    def generate_image_caption(self, filename):
        """Generate a caption for an image based on filename"""
        try:
            # Remove extension and inscription ID
            name = Path(filename).stem

            # Simple caption generation based on common patterns
            if '_photo' in name.lower() or '_photograph' in name.lower():
                return "Photograph of inscription"
            elif '_drawing' in name.lower() or '_sketch' in name.lower():
                return "Drawing of inscription"
            elif '_detail' in name.lower():
                return "Detail view"
            elif '_context' in name.lower():
                return "Contextual view"
            else:
                return "Image of inscription"
        except Exception:
            return "Image"

    def safe_detect_language(self, root):
        """Safely detect primary language from edition div"""
        try:
            # First check xml:lang attribute in edition divs
            edition_divs = self.safe_xpath(root, './/tei:div[@type="edition"]')
            if edition_divs:
                for div in edition_divs:
                    lang = div.get('{http://www.w3.org/XML/1998/namespace}lang')
                    if lang:
                        return lang

            # Fallback: Check xml:lang attribute anywhere in the document
            lang_attrs = root.xpath('.//@xml:lang')
            if lang_attrs:
                return lang_attrs[0]

            # Final fallback: Simple detection based on content
            all_text = self.safe_get_element_text(root)

            if any(ord(char) >= 0x10A0 and ord(char) <= 0x10FF for char in all_text if isinstance(char, str)):
                return 'ka'  # Georgian
            elif any(ord(char) >= 0x0370 and ord(char) <= 0x03FF for char in all_text if isinstance(char, str)):
                return 'grc'  # Greek
            elif any(ord(char) >= 0x0530 and ord(char) <= 0x058F for char in all_text if isinstance(char, str)):
                return 'hy'  # Armenian
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

    
    
    
    def generate_person_uri(self, key, person_data):
        """Generate clean, URL-safe URI for person"""
        import re
        import unicodedata
        
        # Try to use English name if available
        if person_data.get('nymRef'):
            base_name = person_data['nymRef']
        elif len(person_data['display_names']) > 0:
            # Use the shortest name variant as it's often cleaner
            base_name = min(person_data['display_names'], key=len)
        else:
            base_name = key
        
        # Clean the name for URI
        # First, try transliteration for Georgian text
        clean_name = self.transliterate_georgian_for_uri(base_name)
        
        # Remove special characters and normalize
        clean_name = unicodedata.normalize('NFD', clean_name)
        clean_name = re.sub(r'[^\w\s-]', '', clean_name)
        clean_name = re.sub(r'[\s_]+', '-', clean_name)
        clean_name = clean_name.lower().strip('-')
        
        # If still problematic, use incremental ID
        if not clean_name or len(clean_name) < 2:
            clean_name = f"person-{abs(hash(key)) % 10000}"
        
        return clean_name
    
    def transliterate_georgian_for_uri(self, text):
        """Simple Georgian to Latin transliteration for URIs"""
        georgian_to_latin = {
            'ა': 'a', 'ბ': 'b', 'გ': 'g', 'დ': 'd', 'ე': 'e', 'ვ': 'v', 'ზ': 'z',
            'თ': 'th', 'ი': 'i', 'კ': 'k', 'ლ': 'l', 'მ': 'm', 'ნ': 'n', 'ო': 'o',
            'პ': 'p', 'ჟ': 'zh', 'რ': 'r', 'ს': 's', 'ტ': 't', 'უ': 'u', 'ფ': 'ph',
            'ქ': 'q', 'ღ': 'gh', 'ყ': 'qh', 'შ': 'sh', 'ჩ': 'ch', 'ც': 'ts', 'ძ': 'dz',
            'წ': 'tst', 'ჭ': 'tch', 'ხ': 'kh', 'ჯ': 'j', 'ჰ': 'h'
        }
        
        result = ""
        for char in text.lower():
            if char in georgian_to_latin:
                result += georgian_to_latin[char]
            elif char.isalnum() or char in ['-', '_', ' ']:
                result += char
            # Skip other characters
        
        return result
    
    
    
    
    #აქ იწყება პროსოპოგრაფია

    def extract_all_persons_enhanced(self):
        """Extract all persons with enhanced metadata and clean URIs"""
        try:
            print("👥 Extracting persons with enhanced metadata...")
    
            persons_index = {}
            person_occurrences = {}
    
            for inscription in self.inscriptions:
                xml_root = inscription.get('xml_root')
                if xml_root is None:
                    continue
    
                edition_divs = self.safe_xpath(xml_root, './/tei:div[@type="edition"]')
    
                for edition_div in edition_divs:
                    persname_elems = self.safe_xpath(edition_div, './/tei:persName[@key]')
    
                    for persname in persname_elems:
                        key = persname.get('key', '').strip()
                        if not key:
                            continue
    
                        display_name = self.safe_get_element_text(persname).strip()
                        if not display_name:
                            continue
    
                        # Initialize person data
                        if key not in persons_index:
                            persons_index[key] = {
                                'key': key,
                                'display_names': set(),
                                'nymRef': persname.get('nymRef', ''),
                                'ref': persname.get('ref', ''),
                                'type': persname.get('type', ''),
                                'role': persname.get('role', ''),
                                'first_occurrence': inscription['id'],
                                'inscription_count': 0,
                                'inscriptions': [],
                                # New enhanced fields
                                'locations': set(),
                                'roles': set(),
                                'material_types': set(),
                                'object_types': set()
                            }
                            person_occurrences[key] = []
    
                        # Add display name variant
                        persons_index[key]['display_names'].add(key)
                        
                        # Extract additional metadata
                        inscription_date = inscription['dating'].get('text', '')
                        inscription_location = inscription['origin'].get('place', '')
                        
                        # Track locations
                        if inscription_location:
                            persons_index[key]['locations'].add(inscription_location)
                        
                        # Track roles
                        role = persname.get('role', '') or persname.get('type', '')
                        if role:
                            persons_index[key]['roles'].add(role)
                        
                        # Track material and object types
                        if inscription.get('material'):
                            material_display = self.format_material_display(inscription['material'])
                            if material_display:
                                persons_index[key]['material_types'].add(material_display)
                        
                        if inscription.get('object_type'):
                            object_display = self.format_object_type_display(inscription['object_type'])
                            if object_display:
                                persons_index[key]['object_types'].add(object_display)
    
                        # Create occurrence record
                        occurrence = {
                            'inscription_id': inscription['id'],
                            'inscription_title': self.get_display_title(inscription['title']),
                            'display_name': key,
                            'place': inscription_location,
                            'date': inscription_date,
                            'language': inscription['language'],
                            'file_path': inscription['filename'],
                            'role': role,
                            'nymRef': persname.get('nymRef', ''),
                            'ref': persname.get('ref', ''),
                            'certainty': persname.get('cert', 'high'),
                            'material': self.format_material_display(inscription['material']),
                            'object_type': self.format_object_type_display(inscription['object_type'])
                        }
    
                        # Add unique occurrences
                        if not any(occ['inscription_id'] == inscription['id'] and 
                                 occ['display_name'] == display_name 
                                 for occ in person_occurrences[key]):
                            person_occurrences[key].append(occurrence)
    
            # Finalize person data and generate URIs
            for key, person_data in persons_index.items():
                occurrences = person_occurrences[key]
                person_data['occurrences'] = occurrences
                person_data['inscription_count'] = len(set(occ['inscription_id'] for occ in occurrences))
    
                # Use key as primary name and generate clean URI
                person_data['primary_name'] = key
                person_data['uri'] = self.generate_person_uri(key, person_data)
                
                # DEBUG: Print simplified information
                print(f"🔍 PERSON DEBUG:")
                print(f"   Key/Primary name: '{key}'")
                print(f"   URI: '{person_data['uri']}'")
                print(f"   Locations: {person_data['locations']}")
                print()
                
                person_data['all_names'] = key  # Just use the key
    
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
                            'role': occ['role'],
                            'material': occ['material'],
                            'object_type': occ['object_type'],
                            'url': f"inscriptions/{occ['inscription_id']}.html"
                        }
                person_data['inscriptions'] = list(unique_inscriptions.values())
    
            print(f"👥 Extracted {len(persons_index)} unique persons with enhanced metadata")
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



    def create_enhanced_persons_index_page(self, persons_index):
        """Create enhanced persons index page with manuscript background - clean design"""
        try:
            if not persons_index:
                print("⚠️ No persons to create index page")
                return
    
            # Sort persons by frequency and then alphabetically
            sorted_persons = sorted(
                persons_index.values(),
                key=lambda p: (-p['inscription_count'], p['primary_name'].lower())
            )
    
            # Create advanced filter options
            all_locations = set()
            all_roles = set()
            
            for person in sorted_persons:
                all_locations.update(person['locations'])
                all_roles.update(person['roles'])
    
            # Remove empty values
            all_locations = {loc for loc in all_locations if loc}
            all_roles = {role for role in all_roles if role}
    
            # Create persons list HTML
            persons_html = ""
            for person in sorted_persons:
                # Check if names contain Georgian text
                has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in person['primary_name'])
                name_class = 'georgian-text' if has_georgian else ''
    
                # External reference link
                external_link = ""
                if person.get('ref'):
                    external_link = f'<a href="{person["ref"]}" target="_blank" class="external-ref" title="External Reference">🔗</a>'
    
                # Name variants display
                name_variants = ""
                if len(person['display_names']) > 1:
                    other_names = [name for name in person['display_names'] if name != person['primary_name']]
                    if other_names:
                        variants_preview = ' / '.join(other_names[:2])
                        if len(other_names) > 2:
                            variants_preview += f" +{len(other_names) - 2} more"
                        name_variants = f'<div class="person-variants {name_class}">{variants_preview}</div>'
    
                persons_html += f"""
                    <div class="person-item enhanced" 
                         data-name="{person['primary_name'].lower()}" 
                         data-count="{person['inscription_count']}"
                         data-locations="{' '.join(person['locations']).lower()}"
                         data-roles="{' '.join(person['roles']).lower()}"
                         data-uri="{person['uri']}">
                        <div class="person-header">
                            <div class="person-title-section">
                                <h3 class="person-name {name_class}">
                                    <a href="persons/{person['uri']}.html">{person['primary_name']}</a>
                                    {external_link}
                                </h3>
                                {name_variants}
                            </div>
                            <div class="person-stats">
                                <span class="attestation-count">{person['inscription_count']} წარწერა</span>
                            </div>
                        </div>
                        
                        <div class="person-inscriptions-preview">
                            {self.format_enhanced_inscriptions_preview(person['inscriptions'][:3])}
                            {f'<span class="more-inscriptions">... კიდევ {len(person["inscriptions"]) - 3} წარწერა</span>' if len(person['inscriptions']) > 3 else ''}
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
        <style>
            /* Enhanced Persons Index with Manuscript Background - Clean Design */
            .page-header {{
                position: relative;
                text-align: center;
                padding: 4rem 0 3rem;
                background: #fafafa;
                overflow: hidden;
            }}
    
            .page-header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: url('https://upload.wikimedia.org/wikipedia/commons/8/85/%E1%83%90%E1%83%9C%E1%83%90%E1%83%A1%E1%83%94%E1%83%A3%E1%83%9A%E1%83%98_%E1%83%9C%E1%83%A3%E1%83%A1%E1%83%AE%E1%83%90.jpg');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                opacity: 0.25;
                z-index: 1;
            }}
    
            .page-header > * {{
                position: relative;
                z-index: 2;
            }}
    
            .page-header h1 {{
                font-size: 3rem;
                font-weight: 700;
                color: #1a1a1a;
                margin-bottom: 0.5rem;
                letter-spacing: -0.02em;
            }}
    
            .page-header h1:first-of-type {{
                font-family: var(--primary-georgian-font);
                font-size: 3.2rem;
                color: #1a1a1a;
            }}
    
            .page-header p {{
                font-size: 1.2rem;
                color: #666;
                margin-bottom: 2rem;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
                font-weight: 500;
            }}
    
            /* Clean Controls */
            .persons-controls {{
                display: -webkit-box;
                align-items: center;
                gap: 1.5rem;
                max-width: 870px;
                margin: 2rem auto;
                background: white;
                padding: 2rem;
                border-radius: 8px;
                border: 1px solid #f0f0f0;
            }}
    
            .persons-controls .search-section {{
                display: flex;
            }}
    
            .persons-controls .search-input {{
                display: flex;
                padding: 1rem 1.25rem;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 1rem;
                font-family: var(--mixed-script-font);
                background: white;
                transition: border-color 0.2s ease;
            }}
    
            .persons-controls .search-input:focus {{
                outline: none;
                border-color: #1565C0;
            }}
    
            .filter-controls {{
                display: flex;
                gap: 1.5rem;
                width: 100%;
                justify-content: center;
                flex-wrap: wrap;
            }}
    
            .filter-group {{
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                min-width: 180px;
            }}
    
            .filter-group label {{
                font-weight: 600;
                color: #495057;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
    
            .filter-select {{
                padding: 0.75rem 1rem;
                border: 1px solid #ddd;
                border-radius: 6px;
                background: white;
                font-family: var(--mixed-script-font);
                font-size: 0.95rem;
                color: #555;
                cursor: pointer;
                transition: border-color 0.2s ease;
            }}
    
            .filter-select:focus {{
                outline: none;
                border-color: #1565C0;
            }}
    
            /* Clean Statistics */
            .persons-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin: 3rem auto;
                max-width: 800px;
                padding: 0 1rem;
            }}
    
            .stat-item {{
                background: white;
                padding: 2rem 1.5rem;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #f0f0f0;
                transition: transform 0.2s ease;
            }}
    
            .stat-item:hover {{
                transform: translateY(-2px);
            }}
    
            .stat-item strong {{
                display: block;
                font-size: 2.5rem;
                font-weight: 700;
                color: #1a1a1a;
                margin-bottom: 0.5rem;
            }}
    
            .stat-item span {{
                color: #666;
                font-size: 0.95rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
    
            .stat-item span.georgian {{
                font-family: var(--primary-georgian-font);
                text-transform: none;
                letter-spacing: normal;
            }}
    
            /* Clean person items */
            .persons-list {{
                max-width: 900px;
                margin: 0 auto;
                padding: 0 1rem;
            }}
    
            .person-item.enhanced {{
                background: white;
                border: 1px solid #f0f0f0;
                border-radius: 8px;
                margin-bottom: 1.5rem;
                padding: 1.5rem 2rem;
                transition: transform 0.2s ease;
            }}
    
            .person-item.enhanced:hover {{
                transform: translateY(-2px);
            }}
    
            .person-header {{
                display: flex;
                justify-content: space-between;
                align-items: baseline;
                margin-bottom: 1rem;
                gap: 1rem;
            }}
    
            .person-name {{
                font-size: 1.25rem;
                font-weight: 600;
                margin: 0;
                flex: 1;
            }}
    
            .person-name a {{
                color: #1a1a1a;
                text-decoration: none;
                transition: color 0.2s ease;
            }}
    
            .person-name a:hover {{
                color: #1565C0;
            }}
    
            .person-name.georgian-text {{
                font-family: var(--primary-georgian-font);
                font-size: 1.3rem;
            }}
    
            .person-variants {{
                font-size: 0.9em;
                color: #666;
                font-weight: 400;
                font-style: italic;
                margin-top: 0.25rem;
            }}
    
            .person-variants.georgian-text {{
                font-family: var(--primary-georgian-font);
            }}
    
            .attestation-count {{
                background: #e3f2fd;
                color: #1565C0;
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.85rem;
                font-weight: 600;
                white-space: nowrap;
            }}
    
            .external-ref {{
                margin-left: 0.5rem;
                text-decoration: none;
                opacity: 0.7;
                transition: opacity 0.2s ease;
            }}
    
            .external-ref:hover {{
                opacity: 1;
            }}
    
            .person-inscriptions-preview {{
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
                font-size: 0.9rem;
            }}
    
            .inscription-preview {{
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
            }}
    
            .inscription-link {{
                color: #1565C0;
                text-decoration: none;
                font-weight: 500;
            }}
    
            .inscription-link:hover {{
                text-decoration: underline;
            }}
    
            .inscription-link.georgian-text {{
                font-family: var(--primary-georgian-font);
            }}
    
            .inscription-meta {{
                color: #666;
                font-size: 0.85em;
                display: flex;
                gap: 1rem;
            }}
    
            .inscription-meta .georgian-text {{
                font-family: var(--primary-georgian-font);
            }}
    
            .more-inscriptions {{
                color: #888;
                font-style: italic;
                font-size: 0.85em;
                margin-top: 0.5rem;
            }}
    
            /* Responsive Design */
            @media (max-width: 768px) {{
                .page-header h1 {{
                    font-size: 2.2rem;
                }}
    
                .page-header h1:first-of-type {{
                    font-size: 2.5rem;
                }}
    
                .page-header {{
                    padding: 3rem 1rem 2rem;
                }}
    
                .persons-controls {{
                    padding: 1.5rem;
                    margin: 2rem 1rem;
                }}
    
                .filter-controls {{
                    flex-direction: column;
                    gap: 1rem;
                }}
    
                .filter-group {{
                    min-width: auto;
                }}
    
                .persons-stats {{
                    grid-template-columns: repeat(2, 1fr);
                    gap: 1rem;
                    margin: 2rem 1rem;
                }}
    
                .stat-item {{
                    padding: 1.5rem 1rem;
                }}
    
                .stat-item strong {{
                    font-size: 2rem;
                }}
    
                .person-header {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 0.75rem;
                }}
    
                .person-name {{
                    font-size: 1.1rem;
                }}
    
                .person-name.georgian-text {{
                    font-size: 1.2rem;
                }}
            }}
    
            @media (max-width: 480px) {{
                .persons-stats {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="container">
                <a href="index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
                <div class="nav-links">
                    <a href="index.html">საწყისი</a>
                    <a href="browse.html">წარწერები</a>
                    <a href="persons.html" class="active">პირები</a>
                    <a href="bibliography.html">ბიბლიოგრაფია</a>
                </div>
            </div>
        </nav>
    
        <main class="container">
            <div class="page-header">
                <h1>პროსოპოგრაფია</h1>
                <h1>Index of Persons</h1>
                <p>საქართველოს ეპიგრაფიკულ კორპუსში მოხსენიებული {len(persons_index)} პირი</p>
            </div>
    
            <div class="persons-controls">
                <div class="search-section">
                    <input type="text" id="personsSearch" placeholder="ძიება..." class="search-input">
                </div>
                
                <div class="filter-controls">
                    <div class="filter-group">
                        <select id="roleFilter" class="filter-select">
                            <option value="">ტიპი</option>
                            {''.join(f'<option value="{role}">{role}</option>' for role in sorted(all_roles))}
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <select id="sortPersons" class="filter-select">
                            <option value="frequency">დალაგება</option>
                            <option value="alphabetical">ანბანურად</option>
                            <option value="inscriptions">სიხშრით</option>
                        </select>
                    </div>
                </div>
            </div>
    
 
    
            <div id="personsList" class="persons-list enhanced">
                {persons_html}
            </div>
        </main>
    
        <script src="static/js/persons-enhanced.js"></script>
    </body>
    </html>"""
    
            with open(f"{self.output_dir}/persons.html", 'w', encoding='utf-8') as f:
                f.write(html)
    
            print(f"👥 Enhanced persons index page created with manuscript background and {len(persons_index)} persons")
    
        except Exception as e:
            print(f"❌ Error creating enhanced persons index page: {e}")
            import traceback
            traceback.print_exc()

    

    def format_enhanced_inscriptions_preview(self, inscriptions):
        """Format a preview list of inscriptions for enhanced person index page"""
        try:
            if not inscriptions:
                return "<span class='no-inscriptions'>No inscriptions</span>"
    
            items = []
            for inscription in inscriptions:
                # Check if title contains Georgian text
                has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in inscription['title'])
                title_class = 'georgian-text' if has_georgian else ''
    
                # Check if place contains Georgian text
                place_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in inscription['place']) if inscription['place'] else False
                place_class = 'georgian-text' if place_has_georgian else ''
    
                place_display = inscription['place'] if inscription['place'] else 'Unknown location'
    
                items.append(f"""
                    <span class="inscription-preview">
                        <a href="{inscription['url']}" class="inscription-link {title_class}">{inscription['title']}</a>
                        <span class="inscription-meta">
                            <span class="place {place_class}">📍 {place_display}</span>
                            <span class="date">📅 {inscription['date'] if inscription['date'] else 'Unknown date'}</span>
                        </span>
                    </span>
                """)
    
            return ''.join(items)
    
        except Exception as e:
            print(f"❌ Error formatting inscription preview: {e}")
            return "<span class='error'>Error displaying inscriptions</span>"
   
    
    
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
                self.create_enhanced_single_person_page(key, person)
    
            print(f"👥 Created {len(persons_index)} individual person pages")
    
        except Exception as e:
            print(f"❌ Error creating person pages: {e}")
    
    def create_enhanced_single_person_page(self, key, person):
        """Create enhanced single person page with co-occurrence data while maintaining traditional scholarly style"""
        print(f"🔍 DEBUG: Creating enhanced page for: {key}")
        try:
            # Check if name contains Georgian text
            has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in person['primary_name'])
            name_class = 'georgian-text' if has_georgian else ''
    
            # Generate co-occurrence data
            co_occurring_persons = self.find_co_occurring_persons(person)
            
            # Generate comprehensive attestation details
            detailed_attestations = self.create_detailed_attestations_traditional(person)
            
            # Create name variants section (if any)
            name_variants_html = ""
            if len(person['display_names']) > 1:
                variants = [name for name in person['display_names'] if name != person['primary_name']]
                if variants:
                    variants_items = []
                    for variant in variants:
                        variant_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in variant)
                        variant_class = 'georgian-text' if variant_has_georgian else ''
                        variants_items.append(f'<span class="name-variant {variant_class}">{variant}</span>')
                    
                    name_variants_html = f"""
                        <div class="name-variants-section">
                            <h4>სახელის ვარიანტები / Name Variants</h4>
                            <div class="variants-list">
                                {', '.join(variants_items)}
                            </div>
                        </div>
                    """
    
            # Create co-occurrence section
            co_occurrence_html = ""
            if co_occurring_persons:
                co_items = []
                for co_person in co_occurring_persons[:10]:  # Limit to top 10
                    co_name = co_person['name']
                    co_count = co_person['shared_inscriptions']
                    co_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in co_name)
                    co_class = 'georgian-text' if co_has_georgian else ''
                    
                    # Create link to co-occurring person's page
                    co_uri = self.generate_person_uri(co_name, {'primary_name': co_name, 'display_names': [co_name]})
                    co_items.append(f"""
                        <div class="co-occurrence-item">
                            <a href="{co_uri}.html" class="co-person-link {co_class}">{co_name}</a>
                            <span class="co-count">{co_count} shared inscription{'s' if co_count != 1 else ''}</span>
                        </div>
                    """)
                
                co_occurrence_html = f"""
                    <div class="co-occurrence-section">
                        <h4>თანამოწმეები / Co-attested Persons</h4>
                        <div class="co-persons-list">
                            {''.join(co_items)}
                        </div>
                    </div>
                """
    
            # External references section (keep your existing logic)
            external_refs_html = ""
            if person.get('ref') or person.get('nymRef'):
                refs = []
                if person.get('ref'):
                    refs.append(f'<a href="{person["ref"]}" target="_blank" class="external-link">🔗 External Reference</a>')
                if person.get('nymRef'):
                    refs.append(f'<div class="nym-ref"><strong>nymRef:</strong> <code>{person["nymRef"]}</code></div>')
    
                external_refs_html = f"""
                    <div class="external-references-section">
                        <h4>გარე ბმულები / External References</h4>
                        <div class="refs-content">
                            {'<br>'.join(refs)}
                        </div>
                    </div>
                """
    
            # Build the complete HTML (preserving your centered name style)
            html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{person['primary_name']} - პროსოპოგრაფია</title>
        <link rel="stylesheet" href="../static/css/style.css">
        <meta name="description" content="Prosopographical record for {person['primary_name']} from the Epigraphic Corpus of Georgia">
    </head>
    <body>
        <nav class="navbar">
            <div class="container">
                <a href="../index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
                <div class="nav-links">
                    <a href="../index.html">საწყისი</a>
                    <a href="../browse.html">წარწერები</a>
                    <a href="../persons.html">პირები</a>
                    <a href="../bibliography.html">ბიბლიოგრაფია</a>
                </div>
            </div>
        </nav>
    
        <main class="container">
            <div class="breadcrumb">
                <a href="../persons.html">პროსოპოგრაფია</a> / <span>{person['primary_name']}</span>
            </div>
            
            <!-- Centered Person Header (Your Style) -->
            <div class="person-header">
                <h1 class="person-name {name_class}">{person['primary_name']}</h1>
                
            </div>
    
            <!-- Two Column Grid (Simplified Layout) -->
            <div class="two-column-grid">            
                <!-- Left Column: Name Variants & References -->
                <div class="card">
                    {name_variants_html}
                    {external_refs_html}
                </div>
    
                <!-- Center Column: Attestations & Sources (Your Style) -->
                <div class="card">
                    <h3>წყაროები / Sources and Attestations</h3>
                    <p style="margin-bottom: 16px;"><strong>სულ:</strong> {len(person['occurrences'])}</p>
                    
                    <div class="attestations-content">
                        {detailed_attestations}
                    </div>
                </div>
    
                <!-- Right Column: Co-occurring Persons -->
                <div class="card">
                    {co_occurrence_html}
                    
                    <!-- Citation -->
                    <div class="citation-section">
                        <h4>ციტირება / Citation</h4>
                        <div class="citation-text">
                            პროსოპოგრაფია. "{person['primary_name']}." 
                            წვდომის თარიღი: <span id="access-date"></span>. 
                            georgianprosopography.org/person/{person['uri']}
                        </div>
                    </div>
                </div>
            </div>
        </main>
    
        <script>
            // Set access date
            document.getElementById('access-date').textContent = new Date().toLocaleDateString('ka-GE');
            
            // Export functionality
            function exportPersonData() {{
                const data = {{
                    name: "{person['primary_name']}",
                    uri: "{person['uri']}",
                    inscriptions: {person['inscription_count']},
                    locations: {len(person['locations'])},
                    attestations: {len(person['occurrences'])}
                }};
                
                const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: 'application/json' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{person["uri"]}.json';
                a.click();
                URL.revokeObjectURL(url);
            }}
            
            // Copy URL functionality
            function copyUrl() {{
                navigator.clipboard.writeText(window.location.href).then(() => {{
                    alert('URL copied to clipboard!');
                }}).catch(err => {{
                    console.error('Could not copy URL: ', err);
                }});
            }}
        </script>
    </body>
    </html>"""
    
            # Use clean URI for filename
            with open(f"{self.output_dir}/persons/{person['uri']}.html", 'w', encoding='utf-8') as f:
                f.write(html)
                
            print(f"✅ Enhanced person page created: {person['uri']}.html")
    
        except Exception as e:
            print(f"❌ Error creating enhanced person page for {key}: {e}")
            import traceback
            traceback.print_exc()
    
    def find_co_occurring_persons(self, target_person):
        """Find persons who appear in the same inscriptions as the target person"""
        try:
            co_occurrences = {}
            target_inscription_ids = set(insc['id'] for insc in target_person['inscriptions'])
            
            # Check all other persons in the index
            for other_key, other_person in self.persons_index.items():
                if other_key == target_person['key']:
                    continue  # Skip self
                    
                other_inscription_ids = set(insc['id'] for insc in other_person['inscriptions'])
                shared_inscriptions = target_inscription_ids.intersection(other_inscription_ids)
                
                if shared_inscriptions:
                    co_occurrences[other_person['primary_name']] = {
                        'name': other_person['primary_name'],
                        'uri': other_person['uri'],
                        'shared_inscriptions': len(shared_inscriptions),
                        'shared_inscription_ids': list(shared_inscriptions)
                    }
            
            # Sort by number of shared inscriptions (descending)
            return sorted(co_occurrences.values(), key=lambda x: x['shared_inscriptions'], reverse=True)
            
        except Exception as e:
            print(f"❌ Error finding co-occurring persons: {e}")
            return []
    
    def create_detailed_attestations_traditional(self, person):
        """Create detailed attestations in traditional scholarly format"""
        try:
            if not person['inscriptions']:
                return '<div class="no-attestations">არ არის მოწმობები ხელმისაწვდომი / No attestations available</div>'
            
            attestations_html = []
            
            for i, inscription in enumerate(person['inscriptions'], 1):
                # Check if title contains Georgian
                title_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in inscription['title'])
                title_class = 'georgian-text' if title_has_georgian else ''
                
                # Check if place contains Georgian  
                place_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in inscription['place']) if inscription['place'] else False
                place_class = 'georgian-text' if place_has_georgian else ''
                
                # Format the attestation (Your ID-first style)
                attestations_html.append(f'''
                    <div class="attestation-entry">
                        <div class="attestation-header">
                            <strong class="inscription-id">{inscription['id']}</strong>
                            <span class="inscription-tag">INSCRIPTION</span>
                        </div>
                        <h4 class="inscription-title {title_class}">
                            <a href="../{inscription['url']}" target="_blank">{inscription['title']}</a>
                        </h4>
                        <div class="attestation-details">
                            {f'<span class="detail-place {place_class}">📍 {inscription["place"]}</span>' if inscription['place'] else ''}
                            {f'<span class="detail-date">📅 {inscription["date"]}</span>' if inscription['date'] else ''}
                            <span class="detail-language">{inscription['language']}</span>
                        </div>
                    </div>
                ''')
            
            return '\n'.join(attestations_html)
            
        except Exception as e:
            print(f"❌ Error creating detailed attestations: {e}")
            return '<div class="error-attestations">Error loading attestations</div>'
    
    def format_location_distribution(self, person):
        """Format geographic distribution of person's attestations"""
        try:
            if not person['locations']:
                return '<div class="no-locations">გეოგრაფიული მონაცემები არ არის / No geographic data available</div>'
            
            location_items = []
            for location in person['locations']:
                # Count inscriptions from this location
                location_count = sum(1 for insc in person['inscriptions'] if insc['place'] == location)
                loc_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in location)
                loc_class = 'georgian-text' if loc_has_georgian else ''
                
                location_items.append(f'''
                    <div class="location-item">
                        <span class="location-name {loc_class}">{location}</span>
                        <span class="location-count">{location_count}</span>
                    </div>
                ''')
            
            return '\n'.join(location_items)
            
        except Exception as e:
            print(f"❌ Error formatting location distribution: {e}")
            return '<div class="error-locations">Error displaying locations</div>'

    

    def create_detailed_attestations_section(self, person):
        """Create detailed attestations section for person page"""
        try:
            if not person['inscriptions']:
                return '<div class="no-attestations"><p>No attestations available.</p></div>'
    
            attestations_html = '<div class="attestations-section"><h3>Epigraphic Attestations</h3><div class="attestations-list">'
            
            for i, inscription in enumerate(person['inscriptions'], 1):
                # Check if title contains Georgian
                title_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in inscription['title'])
                title_class = 'georgian-text' if title_has_georgian else ''
    
                # Check if place contains Georgian  
                place_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in inscription['place']) if inscription['place'] else False
                place_class = 'georgian-text' if place_has_georgian else ''
    
                # Format the attestation
                attestations_html += '''
                    <div class="attestation-item">
                        <div class="attestation-header">
                            <div class="attestation-number">#''' + str(i) + '''</div>
                            <div class="attestation-title">
                                <h4 class="''' + title_class + '''">
                                    <a href="../''' + inscription['url'] + '''" target="_blank">''' + inscription['title'] + '''</a>
                                </h4>
                                <div class="attestation-id">Inscription: ''' + inscription['id'] + '''</div>
                            </div>
                        </div>
                        
                        <div class="attestation-details">
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <span class="detail-label">Location:</span>
                                    <span class="detail-value ''' + place_class + '''">''' + (inscription['place'] if inscription['place'] else 'Unknown') + '''</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Date:</span>
                                    <span class="detail-value">''' + (inscription['date'] if inscription['date'] else 'Unknown') + '''</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Language:</span>
                                    <span class="detail-value">''' + inscription['language'] + '''</span>
                                </div>'''
                
                # Add role if available
                if inscription.get('role'):
                    attestations_html += '''
                                <div class="detail-item">
                                    <span class="detail-label">Role:</span>
                                    <span class="detail-value">''' + inscription['role'] + '''</span>
                                </div>'''
                
                attestations_html += '''
                            </div>
                        </div>
                    </div>
                '''
            
            attestations_html += '</div></div>'
            return attestations_html
    
        except Exception as e:
            print(f"❌ Error creating attestations section: {e}")
            return '<div class="error-attestations"><p>Error loading attestations.</p></div>'   
   
   
    #აქ იწყება ადგილების ექსტრაქცია
    def extract_all_place_names(self):
        """Extract all unique place names from origPlace elements with coordinates"""
        try:
            print("🗺️  Extracting place names from origPlace elements...")

            xml_files = sorted(list(Path(self.xml_dir).glob("*.xml")))
            place_names = {
                'ka': {},  # Georgian names with coordinates
                'en': {},  # English names with coordinates
                'all_places': []  # All places with full info
            }

            # Get coordinates mapping
            coordinates_map = self.create_coordinates_mapping()
            print(f"📍 Loaded {len(coordinates_map)} coordinate mappings")

            for xml_file in xml_files:
                try:
                    parser = etree.XMLParser(recover=True)
                    tree = etree.parse(str(xml_file), parser)
                    root = tree.getroot()

                    # Extract ONLY from origPlace elements
                    origplace_elems = self.safe_xpath(root, './/tei:origPlace')
                    for origplace in origplace_elems:
                        # Extract Georgian place names
                        ka_segs = self.safe_xpath(origplace, './/tei:seg[@xml:lang="ka"]')
                        for seg in ka_segs:
                            place_text = self.safe_get_element_text(seg).strip()
                            if place_text:
                                coords = self.find_coordinates(place_text, coordinates_map)
                                place_names['ka'][place_text] = coords

                        # Extract English place names
                        en_segs = self.safe_xpath(origplace, './/tei:seg[@xml:lang="en"]')
                        for seg in en_segs:
                            place_text = self.safe_get_element_text(seg).strip()
                            if place_text:
                                coords = self.find_coordinates(place_text, coordinates_map)
                                place_names['en'][place_text] = coords

                        # Also check for direct text in origPlace (fallback)
                        if not ka_segs and not en_segs:
                            place_text = self.safe_get_element_text(origplace).strip()
                            if place_text:
                                coords = self.find_coordinates(place_text, coordinates_map)
                                place_names['ka'][place_text] = coords

                except Exception as e:
                    print(f"⚠️  Error processing {xml_file.name}: {e}")
                    continue

            # Build the all_places array from ka and en dictionaries
            all_places_set = set()  # Use set to avoid duplicates

            # Add Georgian places
            for place, coords in place_names['ka'].items():
                has_coords = coords.get('lat') is not None and coords.get('lon') is not None
                all_places_set.add((
                    place,
                    'ka',
                    coords.get('lat'),
                    coords.get('lon'),
                    has_coords
                ))

            # Add English places
            for place, coords in place_names['en'].items():
                has_coords = coords.get('lat') is not None and coords.get('lon') is not None
                all_places_set.add((
                    place,
                    'en',
                    coords.get('lat'),
                    coords.get('lon'),
                    has_coords
                ))

            # Convert set to list of dictionaries
            place_names['all_places'] = [
                {
                    'name': place,
                    'language': lang,
                    'lat': lat,
                    'lon': lon,
                    'has_coordinates': has_coords
                }
                for place, lang, lat, lon, has_coords in sorted(all_places_set)
            ]

            # Save results to files
            self.save_place_names_with_coordinates(place_names)

            print(f"📍 Found {len(place_names['ka'])} Georgian place names")
            print(f"📍 Found {len(place_names['en'])} English place names")
            print(f"📍 Total unique places: {len(place_names['all_places'])}")

            # Count places with coordinates
            with_coords = sum(1 for p in place_names['all_places'] if p['has_coordinates'])
            print(f"🗺️  Places with coordinates: {with_coords}/{len(place_names['all_places'])}")

            return place_names

        except Exception as e:
            print(f"❌ Error extracting place names: {e}")
            return {'ka': {}, 'en': {}, 'all_places': []}
    # ღია არის დაკარგული მეთოდის დამატება - დაიწყება
    def load_place_names_from_file(self):
        """Load place names from existing JSON file"""
        try:
            place_names_file = Path(f"{self.output_dir}/place-names.json")
            if place_names_file.exists():
                with open(place_names_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ Loaded place names from {place_names_file}")
                    return data
            else:
                print(f"⚠️  Place names file not found: {place_names_file}")
                # Return empty structure that matches expected format
                return {'ka': {}, 'en': {}, 'all_places': []}
        except Exception as e:
            print(f"❌ Error loading place names file: {e}")
            # Return empty structure that matches expected format
            return {'ka': {}, 'en': {}, 'all_places': []}
    # ღია არის დაკარგული მეთოდის დამატება - დასრულება

    # ღია არის რუქის კოორდინატების დებაგი - დაიწყება
    def debug_map_coordinates(self):
        """Debug coordinate issues for map pins"""
        try:
            print("🔍 Debugging map coordinates...")

            # Load the map data file to see what coordinates we have
            map_data_file = Path(f"{self.output_dir}/map-data.json")
            if map_data_file.exists():
                with open(map_data_file, 'r', encoding='utf-8') as f:
                    map_data = json.load(f)

                print(f"📊 Map data contains {len(map_data)} locations:")

                # Check coordinate ranges
                if map_data:
                    lats = [float(loc['lat']) for loc in map_data if loc.get('lat') is not None]
                    lons = [float(loc['lon']) for loc in map_data if loc.get('lon') is not None]

                    if lats and lons:
                        print(f"📍 Latitude range: {min(lats):.4f} to {max(lats):.4f}")
                        print(f"📍 Longitude range: {min(lons):.4f} to {max(lons):.4f}")

                        # Show sample of locations
                        print(f"\n✅ Sample of locations with coordinates:")
                        for i, loc in enumerate(map_data[:5]):
                            print(f"   {loc['place']}: {loc['lat']}, {loc['lon']} ({loc['count']} inscriptions)")

                    else:
                        print("❌ No valid coordinates found in map data!")
                else:
                    print("❌ Map data is empty!")
            else:
                print(f"❌ Map data file not found: {map_data_file}")

        except Exception as e:
            print(f"❌ Error debugging map coordinates: {e}")
            import traceback
            traceback.print_exc()

    def validate_and_fix_coordinates(self):
        """Validate and fix coordinate issues"""
        try:
            print("🔧 Validating and fixing coordinates...")

            coordinates_map = self.create_coordinates_mapping()
            print(f"📍 Available coordinates: {len(coordinates_map)}")

            # Count inscriptions by place
            place_counts = {}
            for inscription in self.inscriptions:
                place = inscription['origin'].get('place', '').strip()
                if place:
                    place_counts[place] = place_counts.get(place, 0) + 1

            print(f"\n📊 Inscription places (top 10):")
            for place, count in sorted(place_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                coords = self.find_coordinates(place, coordinates_map)
                has_coords = coords.get('lat') is not None and coords.get('lon') is not None
                status = "✅" if has_coords else "❌"
                print(f"   {status} {place}: {count} inscriptions")

            return place_counts

        except Exception as e:
            print(f"❌ Error validating coordinates: {e}")
            return {}
    # ღია არის რუქის კოორდინატების დებაგი - დასრულება

    def find_coordinates(self, place_name, coordinates_map):
        """Find coordinates for a place name"""
        try:
            # Try exact match first
            if place_name in coordinates_map:
                return coordinates_map[place_name]

            # Try partial matches (case insensitive)
            place_lower = place_name.lower()
            for coord_place, coord_data in coordinates_map.items():
                coord_place_lower = coord_place.lower()
                if (coord_place_lower in place_lower or
                    place_lower in coord_place_lower or
                    place_name in coord_place or coord_place in place_name):
                    return coord_data

            # No match found
            return {'lat': None, 'lon': None}

        except Exception:
            return {'lat': None, 'lon': None}

    def save_place_names_with_coordinates(self, place_names):
        """Save place names with coordinates to files"""
        try:
            # Save as JSON with coordinates
            with open(f"{self.output_dir}/place-names.json", 'w', encoding='utf-8') as f:
                json.dump(place_names, f, ensure_ascii=False, indent=2)

            # Save as readable text file
            with open(f"{self.output_dir}/place-names.txt", 'w', encoding='utf-8') as f:
                f.write("Place Names with Coordinates:\n")
                f.write("=" * 60 + "\n\n")

                for place_info in place_names['all_places']:
                    f.write(f"Place: {place_info['name']} ({place_info['language']})\n")
                    if place_info['has_coordinates']:
                        f.write(f"  Coordinates: {place_info['lat']}, {place_info['lon']}\n")
                    else:
                        f.write(f"  Coordinates: Not found\n")
                    f.write("\n")

                with_coords = sum(1 for p in place_names['all_places'] if p['has_coordinates'])
                f.write(f"Summary: {with_coords}/{len(place_names['all_places'])} places have coordinates\n")

            print(f"💾 Place names with coordinates saved to: {self.output_dir}/place-names.json")
            print(f"💾 Readable list saved to: {self.output_dir}/place-names.txt")

        except Exception as e:
            print(f"❌ Error saving place names: {e}")
    #აქ მთავრდება ადგილების ექსტრაქცია

    def create_coordinates_mapping(self):
        """Create coordinates mapping for Georgian places with comprehensive GPS data"""
        try:
            # Your comprehensive Georgian places with accurate coordinates
            georgian_coordinates = {
                # Georgian place names
                "წილკანი": {"lat": 41.9333, "lon": 44.6833, "name_en": "Tsilkani", "has_coordinates": True},
                "სეფიეთი": {"lat": 42.1167, "lon": 43.8500, "name_en": "Sepieti", "has_coordinates": True},
                "არმაზციხე, ბაგინეთი": {"lat": 41.8333, "lon": 44.7000, "name_en": "Armaztsikhe, Bagineti", "has_coordinates": True},
                "ნოსირი": {"lat": 41.7500, "lon": 44.6000, "name_en": "Nosiri", "has_coordinates": True},
                "კავთისხევი": {"lat": 41.8200, "lon": 44.7300, "name_en": "Kavtiskhevi", "has_coordinates": True},
                "მცხეთა, სამთავროს სამაროვანი": {"lat": 41.8451, "lon": 44.7188, "name_en": "Samtavro necropolis", "has_coordinates": True},
                "ზნაკვა, ჯვარისას ეკლესია": {"lat": 41.9000, "lon": 44.8000, "name_en": "Znakva, Jvarisa Church", "has_coordinates": True},
                "ვანი": {"lat": 42.0833, "lon": 42.5, "name_en": "Vani", "has_coordinates": True},
                "წყისე": {"lat": 41.9500, "lon": 44.7500, "name_en": "Tskise", "has_coordinates": True},
                "აკაურთა, ბოლნისის მუნიციპალიტეტი": {"lat": 41.3889, "lon": 44.5126, "name_en": "Akaurta, Bolnisi municipality", "has_coordinates": True},
                "ნუხა": {"lat": 41.5583, "lon": 45.3833, "name_en": "Nukha", "has_coordinates": True},
                "არმაზისხევი": {"lat": 41.8423, "lon": 44.7145, "name_en": "Armaziskhevi", "has_coordinates": True},
                "ატენის სიონი": {"lat": 41.9039, "lon": 44.0959, "name_en": "Ateni Sioni", "has_coordinates": True},
                "წებელდა": {"lat": 42.9167, "lon": 40.0833, "name_en": "Tsebrelda", "has_coordinates": True},
                "კაზრეთი": {"lat": 41.3333, "lon": 44.3000, "name_en": "Kazreti", "has_coordinates": True},
                "ვაშნარი": {"lat": 41.7000, "lon": 44.5500, "name_en": "Vashnari", "has_coordinates": True},
                "სამთავროს უბანი, მცხეთა": {"lat": 41.8451, "lon": 44.7188, "name_en": "Samtavro, Mtskheta", "has_coordinates": True},
                "ზემო ნიქოზი, ღვთაების ტაძარი": {"lat": 42.0000, "lon": 44.1000, "name_en": "Zemo Nikozi, Deity Church", "has_coordinates": True},
                "ზემო ნიქოზი, მთავარანგელოზის ტაძარი": {"lat": 42.0000, "lon": 44.1000, "name_en": "Zemo Nikozi, Archangel Church", "has_coordinates": True},
                "ჯვრის მონასტერი, მცხეთა": {"lat": 41.8383, "lon": 44.7333, "name_en": "Jvari Monastery, Mtskheta", "has_coordinates": True},
                "ურბნისის სიონი": {"lat": 41.7500, "lon": 44.6167, "name_en": "Urbnisi Sioni", "has_coordinates": True},
                "ლამაზი გორა, ბოლნისის მუნიციპალიტეტი": {"lat": 41.3889, "lon": 44.5126, "name_en": "Lamazi Gora, Bolnisi", "has_coordinates": True},
                "ლამაზი გორა, ბოლნისი": {"lat": 41.3889, "lon": 44.5126, "name_en": "Lamazi Gora, Bolnisi", "has_coordinates": True},
                "პალესტინა, იუდას უდაბნო, წმიდა თეოდორეს სახელობის ქართული მონასტერი": {"lat": 31.5497, "lon": 35.1654, "name_en": "Palestine, Judean Desert, Georgian Monastery of Saint Theodore", "has_coordinates": True},
                "ბოლნისის სიონი": {"lat": 41.3889, "lon": 44.5126, "name_en": "Bolnisi Sioni", "has_coordinates": True},
                "ანაპა": {"lat": 44.8951, "lon": 37.3167, "name_en": "Anapa", "has_coordinates": True},
                "მცხეთა": {"lat": 41.8451, "lon": 44.7188, "name_en": "Mtskheta", "has_coordinates": True},
                "მცხეთა, მოგვთა უბანი": {"lat": 41.8451, "lon": 44.7188, "name_en": "Mtskheta, Mogvta District", "has_coordinates": True},
                "უკანგორი": {"lat": 41.9167, "lon": 44.8333, "name_en": "Ukangori", "has_coordinates": True},
                "ზარზმის მონასტერი": {"lat": 41.5500, "lon": 42.6500, "name_en": "Zarzma Monastery", "has_coordinates": True},
                "ფიის წმინდა თეოდორეს ეკლესია": {"lat": 41.6000, "lon": 42.8000, "name_en": "Phia Church of St. Theodore", "has_coordinates": True},
                "სოფელ ხეოთის ნამონასტრალი": {"lat": 41.7667, "lon": 44.6833, "name_en": "Village Kheoti Former Monastery", "has_coordinates": True},
                "აგარის (ურვალის) ეკლესია": {"lat": 41.8000, "lon": 43.7000, "name_en": "Agara (Urvali) Church", "has_coordinates": True},
                "საროს ციხე": {"lat": 41.7000, "lon": 42.9000, "name_en": "Saro Castle", "has_coordinates": True},
                "წუნდის ეკლესია": {"lat": 41.6500, "lon": 42.7500, "name_en": "Tsunda Church", "has_coordinates": True},
                "ვანის ქვაბები": {"lat": 41.3667, "lon": 43.2833, "name_en": "Vanis Kvabebi", "has_coordinates": True},
                "საფარის მონასტრის წმ. საბას ტაძარი": {"lat": 41.5500, "lon": 42.6500, "name_en": "Sapara Monastery St. Saba Cathedral", "has_coordinates": True},
                "ბიეთის ეკლესია": {"lat": 41.6167, "lon": 42.9333, "name_en": "Bieti Church", "has_coordinates": True},
                "თმოგვის ციხე": {"lat": 41.3500, "lon": 43.2000, "name_en": "Tmogvi Castle", "has_coordinates": True},
                "ვარძია": {"lat": 41.3718, "lon": 43.2545, "name_en": "Vardzia", "has_coordinates": True},
                "პატარა სმადის ეკლესია": {"lat": 41.4000, "lon": 43.3000, "name_en": "Patara Smada Church", "has_coordinates": True},
                "საფარის წმ. გიორგის ეკლესია": {"lat": 41.5500, "lon": 42.6500, "name_en": "Sapara St. George Church", "has_coordinates": True},
                "ვალეს ღვთისმშობლის ეკლესია": {"lat": 42.1667, "lon": 43.5833, "name_en": "Vale Mother of God Church", "has_coordinates": True},
                "ქარზამეთის ეკლესია": {"lat": 41.8333, "lon": 44.8333, "name_en": "Karzamet Church", "has_coordinates": True},
                "უმ ლეისუნი, იერუსალიმი": {"lat": 31.7683, "lon": 35.2137, "name_en": "Um Leisuni, Jerusalem", "has_coordinates": True},
                "სათხე": {"lat": 41.6667, "lon": 44.8333, "name_en": "Satkhis", "has_coordinates": True},
                "აბასთუმნის ძველი ეკლესია": {"lat": 41.7500, "lon": 42.8333, "name_en": "Abastumani Old Church", "has_coordinates": True},
                "ახალციხე": {"lat": 41.6386, "lon": 42.9813, "name_en": "Akhaltsikhe", "has_coordinates": True},
                "ბორჯომი": {"lat": 41.8477, "lon": 43.3913, "name_en": "Borjomi", "has_coordinates": True},
                "ლაილაში": {"lat": 41.6000, "lon": 42.8500, "name_en": "Lailashi", "has_coordinates": True},
                "ხვილიშას ტაძარი, ასპინძის მუნიციპალიტეტი": {"lat": 41.5167, "lon": 43.2500, "name_en": "Khvilisha Temple, Aspindza Municipality", "has_coordinates": True},
                "ხცისი": {"lat": 41.8500, "lon": 44.7500, "name_en": "Khtsis", "has_coordinates": True},
                "არმაზი": {"lat": 41.8333, "lon": 44.7000, "name_en": "Armazi", "has_coordinates": True},
                "ზღუდერი": {"lat": 42.7167, "lon": 40.1667, "name_en": "Zghuderi", "has_coordinates": True},
                "საფარის მონასტრის მიძინების ტაძარი": {"lat": 41.5500, "lon": 42.6500, "name_en": "Sapara Monastery Dormition Cathedral", "has_coordinates": True},
                "ბორი": {"lat": 42.0833, "lon": 43.5000, "name_en": "Bori", "has_coordinates": True},
                "აირავანქი": {"lat": 40.1642, "lon": 44.7019, "name_en": "Hayravank", "has_coordinates": True},
                "უდე, ადიგენის მუნიციპალიტეტი": {"lat": 41.6833, "lon": 42.7167, "name_en": "Ude, Adigeni Municipality", "has_coordinates": True},
                "ბოდოკლდის ეკლესია": {"lat": 41.6000, "lon": 42.7000, "name_en": "Bodolkdi Church", "has_coordinates": True},
                "ოპიზა": {"lat": 41.8000, "lon": 43.6000, "name_en": "Opiza", "has_coordinates": True},
                "ბოგა, ახალციხის მუნიციპალიტეტი": {"lat": 41.6333, "lon": 42.9167, "name_en": "Boga, Akhaltsikhe Municipality", "has_coordinates": True},
                "ციხისუბანი, ადიგენის მუნიციპალიტეტი": {"lat": 41.6500, "lon": 42.7333, "name_en": "Tsikhisubani, Adigeni Municipality", "has_coordinates": True},
                "ამხეს ნასოფლარი, ადიგენის მუნიციპალიტეტი": {"lat": 41.6667, "lon": 42.7500, "name_en": "Amkhes Nasoflari, Adigeni Municipality", "has_coordinates": True},
                "ვარძიის ღვთისმშობლის მიძინების ტაძარი": {"lat": 41.3718, "lon": 43.2545, "name_en": "Vardzia Dormition of the Mother of God Cathedral", "has_coordinates": True},
                "საფარის მონასტერი": {"lat": 41.5500, "lon": 42.6500, "name_en": "Sapara Monastery", "has_coordinates": True},
                "ბიეთის ეკლესია, ახალციხის მუნიციპალიტეტი": {"lat": 41.6167, "lon": 42.9333, "name_en": "Bieti Church, Akhaltsikhe Municipality", "has_coordinates": True},
                "კუმურდო": {"lat": 41.2833, "lon": 43.4167, "name_en": "Kumurdo", "has_coordinates": True},
                "მცხეთის ჯვარი": {"lat": 41.8383, "lon": 44.7333, "name_en": "Mtskheta Jvari", "has_coordinates": True},
                "ანისი": {"lat": 40.5067, "lon": 43.5725, "name_en": "Ani", "has_coordinates": True},
                "ჰაღბატი": {"lat": 41.0955, "lon": 44.714, "name_en": "Haghpat", "has_coordinates": True},
                "ბერდიკი": {"lat": 41.3500, "lon": 44.4500, "name_en": "Berdik", "has_coordinates": True},
                "დმანისი": {"lat": 41.3298, "lon": 44.2073, "name_en": "Dmanisi", "has_coordinates": True},
                "სამთავრო": {"lat": 41.8451, "lon": 44.7188, "name_en": "Samtavro", "has_coordinates": True},
                "ჟინვალი": {"lat": 42.0717, "lon": 44.7797, "name_en": "Zhinvali", "has_coordinates": True},
                "ფაშიანთა": {"lat": 42.3333, "lon": 40.5000, "name_en": "Pashianta", "has_coordinates": True},
                "წანდრიფში": {"lat": 43.2833, "lon": 40.0500, "name_en": "Tsandripshi", "has_coordinates": True},
                "ბიჭვინთა": {"lat": 43.1611, "lon": 40.3456, "name_en": "Bichvinta", "has_coordinates": True},
                "ბიჭვინტა": {"lat": 43.1611, "lon": 40.3456, "name_en": "Bichvinta", "has_coordinates": True},
                "ახალი ათონი": {"lat": 43.0869, "lon": 40.0908, "name_en": "New Athos", "has_coordinates": True},
                "ეშერა": {"lat": 43.0500, "lon": 40.1000, "name_en": "Eshera", "has_coordinates": True},
                "სოხუმი": {"lat": 42.865, "lon": 41.0236, "name_en": "Sokhumi", "has_coordinates": True},
                "ფიჭვნარი": {"lat": 41.6833, "lon": 41.7333, "name_en": "Pichvnari", "has_coordinates": True},
                "ატენი": {"lat": 41.9039, "lon": 44.0959, "name_en": "Ateni", "has_coordinates": True},
                "ითხვისი": {"lat": 42.0167, "lon": 43.7500, "name_en": "Itkhvisi", "has_coordinates": True},
                "გვანდრა": {"lat": 42.2000, "lon": 43.6000, "name_en": "Gvandra", "has_coordinates": True},
                "საირხე": {"lat": 42.1833, "lon": 43.6167, "name_en": "Sairkhe", "has_coordinates": True},
                "წებელდა (ლარი)": {"lat": 42.9167, "lon": 40.0833, "name_en": "Tsebrelda (Lari)", "has_coordinates": True},
                "ნოქალაქევი": {"lat": 42.3167, "lon": 42.1833, "name_en": "Nokalakevi", "has_coordinates": True},
                "ახტალა": {"lat": 41.1000, "lon": 44.7833, "name_en": "Akhtala", "has_coordinates": True},
                "ცაიში": {"lat": 42.4000, "lon": 42.2000, "name_en": "Tsaishi", "has_coordinates": True},
                "ძალისა": {"lat": 41.8667, "lon": 44.8167, "name_en": "Dzalisa", "has_coordinates": True},
                "ნაკიფარი": {"lat": 42.0000, "lon": 43.5000, "name_en": "Nakipari", "has_coordinates": True},
                "ვანის ნაქალაქარი": {"lat": 42.0833, "lon": 42.5, "name_en": "Vani Archaeological Site", "has_coordinates": True},
                "ჰნევანქი (ძელი ჭეშმარიტი), სომხეთი": {"lat": 40.9167, "lon": 44.8333, "name_en": "Hnevank (True Cross), Armenia", "has_coordinates": True},
                "ჯუჯაქენდის ეკლესია, სომხეთი": {"lat": 40.8500, "lon": 44.7500, "name_en": "Jujaqendi Church, Armenia", "has_coordinates": True},
                "ქობაირის მონასტერი, სომხეთი": {"lat": 41.0167, "lon": 44.6333, "name_en": "Kobayr Monastery, Armenia", "has_coordinates": True},
                "სოფ. კოშის ეკლესია, სომხეთი": {"lat": 40.9500, "lon": 44.7000, "name_en": "Village Kosh Church, Armenia", "has_coordinates": True},
                "კურთანის ეკლესია, სომხეთი": {"lat": 40.9833, "lon": 44.7167, "name_en": "Kurtan Church, Armenia", "has_coordinates": True},
                "თეჟარუიქის ეკლესია, სომხეთი": {"lat": 40.9667, "lon": 44.7333, "name_en": "Tezharuiq Church, Armenia", "has_coordinates": True},
                "შაჰნაზარის ქვემო ეკლესია, სომხეთი": {"lat": 40.9000, "lon": 44.6833, "name_en": "Shahnazar Lower Church, Armenia", "has_coordinates": True},
                "შაჰნაზარის ზემო ეკლესია, სომხეთი": {"lat": 40.9100, "lon": 44.6900, "name_en": "Shahnazar Upper Church, Armenia", "has_coordinates": True},
                "უკანგორის ეკლესიის ახლოს მდებარე სასაფლაოზეა ნაპოვნი": {"lat": 41.9167, "lon": 44.8333, "name_en": "Cemetery found near Ukangori Church", "has_coordinates": True},
                "ხუნზახი, დაღესტანი": {"lat": 42.5500, "lon": 46.7500, "name_en": "Khunzakh, Dagestan", "has_coordinates": True},
                "სოფ. ურადა, შამილის რაონი, დაღესტანი": {"lat": 42.4833, "lon": 46.6167, "name_en": "Village Urada, Shamil District, Dagestan", "has_coordinates": True},
                "სოფ. რუღჟაბი, ღუნიბის რაიონი, დაღესტანი": {"lat": 42.4167, "lon": 46.9333, "name_en": "Village Ruzhgabi, Ghunib District, Dagestan", "has_coordinates": True},
                "გინიჩუტლი, დაღესტანი": {"lat": 42.3833, "lon": 46.8167, "name_en": "Ginichutli, Dagestan", "has_coordinates": True},
                "სოფ. მითლიჰურიბი, შამილის რაონი, დაღესტანი": {"lat": 42.4667, "lon": 46.6333, "name_en": "Village Mitlikhuribi, Shamil District, Dagestan", "has_coordinates": True},
                "სოფ. ჰოწატლი, ხუნზახის რაიონი, დაღესტანი": {"lat": 42.5333, "lon": 46.7333, "name_en": "Village Hotsatli, Khunzakh District, Dagestan", "has_coordinates": True},
                "სოფ. მურუხი, ჭაროდის რაიონი, დაღესტანი": {"lat": 42.1833, "lon": 46.9167, "name_en": "Village Murukhi, Charoda District, Dagestan", "has_coordinates": True},
                "ყარსის ციხე, თურქეთი": {"lat": 40.6017, "lon": 43.0939, "name_en": "Kars Fortress, Turkey", "has_coordinates": True},
                "ანჩისხატის ტაძარი, თბილისი": {"lat": 41.6919, "lon": 44.8097, "name_en": "Anchiskhati Cathedral, Tbilisi", "has_coordinates": True},
                "ვარძიის ღვთისმშობლის სახელობის ეკლესია": {"lat": 41.3718, "lon": 43.2545, "name_en": "Vardzia Mother of God Church", "has_coordinates": True},
                "ვანის ქვაბები, ასპინძის მუნიციპალიტეტი": {"lat": 41.3667, "lon": 43.2833, "name_en": "Vani Caves, Aspindza Municipality", "has_coordinates": True},
                "ჰალას ნაქალაქარი, დაღესტანი": {"lat": 42.3167, "lon": 46.8833, "name_en": "Halas Archaeological Site, Dagestan", "has_coordinates": True},
                "ხუნძი, დაღესტანი": {"lat": 42.4500, "lon": 46.8000, "name_en": "Khundzi, Dagestan", "has_coordinates": True},
                "სოფ. თანუსი, ხუნზახის რაიონი, დაღესტანი": {"lat": 42.5167, "lon": 46.7667, "name_en": "Village Tanusi, Khunzakh District, Dagestan", "has_coordinates": True},
                "აქაროს მთა, დაღესტანი": {"lat": 42.4000, "lon": 46.9000, "name_en": "Mount Akaro, Dagestan", "has_coordinates": True},
                "მაცხვარიში": {"lat": 42.7500, "lon": 40.2167, "name_en": "Matskharishi", "has_coordinates": True},
                "ლატალი": {"lat": 43.0000, "lon": 42.7833, "name_en": "Latali", "has_coordinates": True},
                "ფარი": {"lat": 42.9500, "lon": 42.6333, "name_en": "Pari", "has_coordinates": True},
                "ტიმოთესუბანი": {"lat": 41.8167, "lon": 43.5833, "name_en": "Timotesubani", "has_coordinates": True},
                "ლიპი": {"lat": 42.2500, "lon": 42.4833, "name_en": "Lipi", "has_coordinates": True},
                "წალენჯიხა": {"lat": 42.6167, "lon": 42.0333, "name_en": "Tsalenjikha", "has_coordinates": True},
                "მარტვილი": {"lat": 42.4167, "lon": 42.3833, "name_en": "Martvili", "has_coordinates": True},
                "ხობი": {"lat": 42.3167, "lon": 41.9000, "name_en": "Khobi", "has_coordinates": True},
                "გელათი": {"lat": 42.2917, "lon": 42.7567, "name_en": "Gelati", "has_coordinates": True},
                "ოსტია": {"lat": 41.7520, "lon": 12.2920, "name_en": "Ostia", "has_coordinates": True},
                "მსიგხუას ეკლესია": {"lat": 42.5833, "lon": 40.1667, "name_en": "Msigkhva Church", "has_coordinates": True},
                "მსიგხუა": {"lat": 42.5833, "lon": 40.1667, "name_en": "Msigkhva", "has_coordinates": True},
                "ბედიის ტაძარი": {"lat": 42.7000, "lon": 40.2000, "name_en": "Bedia Cathedral", "has_coordinates": True},
                "ბედია": {"lat": 42.7000, "lon": 40.2000, "name_en": "Bedia", "has_coordinates": True},
                "ბესლეთის ხიდის წარწერა": {"lat": 42.8500, "lon": 41.0000, "name_en": "Beslet Bridge Inscription", "has_coordinates": True},
                "ილორი": {"lat": 42.8000, "lon": 40.1500, "name_en": "Ilori", "has_coordinates": True},
                "ილორის წმინდა გიორგის ეკლესია": {"lat": 42.8000, "lon": 40.1500, "name_en": "Ilori St. George Church", "has_coordinates": True},
                "ღუმურიში": {"lat": 42.6500, "lon": 40.2500, "name_en": "Ghumurishi", "has_coordinates": True},
                "ანუხვა": {"lat": 43.0167, "lon": 40.1833, "name_en": "Anukhva", "has_coordinates": True},
                "წარჩე": {"lat": 42.9000, "lon": 40.3000, "name_en": "Tsarche", "has_coordinates": True},
                "წკელიკარი": {"lat": 42.8500, "lon": 40.2500, "name_en": "Tskelikari", "has_coordinates": True},
                "დიხაზურგა": {"lat": 42.9500, "lon": 40.3500, "name_en": "Dikhazurga", "has_coordinates": True},
                "ლიხნი": {"lat": 42.9167, "lon": 40.2500, "name_en": "Likhni", "has_coordinates": True},
                "ლიხნის ღვთისმშობლის მიძინების ტაძარი": {"lat": 42.9167, "lon": 40.2500, "name_en": "Likhni Dormition of the Mother of God Cathedral", "has_coordinates": True},
                "ჭლოუ": {"lat": 42.8800, "lon": 40.2800, "name_en": "Chlou", "has_coordinates": True},
                "გუდავა": {"lat": 42.8833, "lon": 42.7167, "name_en": "Gudava", "has_coordinates": True},
                "ლიხნის ტაძარი": {"lat": 42.9167, "lon": 40.2500, "name_en": "Likhni Cathedral", "has_coordinates": True},
                "დავით გარეჯის მონასტერი": {"lat": 41.4456, "lon": 45.3789, "name_en": "David Gareja Monastery", "has_coordinates": True},
                "დავით გარეჯი, უდაბნო, სატრაპეზო": {"lat": 41.4456, "lon": 45.3789, "name_en": "David Gareja, Desert, Refectory", "has_coordinates": True},
                "მოხისი": {"lat": 41.7500, "lon": 44.5833, "name_en": "Mokhisi", "has_coordinates": True},
                "ჭყონდიდი": {"lat": 42.2833, "lon": 42.1167, "name_en": "Chkondidi", "has_coordinates": True},

                # Add missing places with partial names matching
                "სათხის": {"lat": 41.6667, "lon": 44.8333, "name_en": "Satkhis", "has_coordinates": True},
                "ახალი ათონ": {"lat": 43.0869, "lon": 40.0908, "name_en": "New Athos", "has_coordinates": True},

                # English versions
                "Tsilkani": {"lat": 41.9333, "lon": 44.6833, "name_ka": "წილკანი", "has_coordinates": True},
                "Sepieti": {"lat": 42.1167, "lon": 43.8500, "name_ka": "სეფიეთი", "has_coordinates": True},
                "Armaztsikhe, Bagineti": {"lat": 41.8333, "lon": 44.7000, "name_ka": "არმაზციხე, ბაგინეთი", "has_coordinates": True},
                "Nosiri": {"lat": 41.7500, "lon": 44.6000, "name_ka": "ნოსირი", "has_coordinates": True},
                "Kavtiskhevi": {"lat": 41.8200, "lon": 44.7300, "name_ka": "კავთისხევი", "has_coordinates": True},
                "Samtavro necropolis": {"lat": 41.8451, "lon": 44.7188, "name_ka": "მცხეთა, სამთავროს სამაროვანი", "has_coordinates": True},
                "Znakva, Jvarisa Church": {"lat": 41.9000, "lon": 44.8000, "name_ka": "ზნაკვა, ჯვარისას ეკლესია", "has_coordinates": True},
                "Vani": {"lat": 42.0833, "lon": 42.5, "name_ka": "ვანი", "has_coordinates": True},
                "Tskise": {"lat": 41.9500, "lon": 44.7500, "name_ka": "წყისე", "has_coordinates": True},
                "Akaurta, Bolnisi municipality": {"lat": 41.3889, "lon": 44.5126, "name_ka": "აკაურთა, ბოლნისის მუნიციპალიტეტი", "has_coordinates": True},
                "Nukha": {"lat": 41.5583, "lon": 45.3833, "name_ka": "ნუხა", "has_coordinates": True},
                "Armaziskhevi": {"lat": 41.8423, "lon": 44.7145, "name_ka": "არმაზისხევი", "has_coordinates": True},
                "Ateni Sioni": {"lat": 41.9039, "lon": 44.0959, "name_ka": "ატენის სიონი", "has_coordinates": True},
                "Kazreti": {"lat": 41.3333, "lon": 44.3000, "name_ka": "კაზრეთი", "has_coordinates": True},
                "Vashnari": {"lat": 41.7000, "lon": 44.5500, "name_ka": "ვაშნარი", "has_coordinates": True},
                "Samtavro, Mtskheta": {"lat": 41.8451, "lon": 44.7188, "name_ka": "სამთავროს უბანი, მცხეთა", "has_coordinates": True},
                "Zemo Nikozi, Deity Church": {"lat": 42.0000, "lon": 44.1000, "name_ka": "ზემო ნიქოზი, ღვთაების ტაძარი", "has_coordinates": True},
                "Zemo Nikozi, Archangel Church": {"lat": 42.0000, "lon": 44.1000, "name_ka": "ზემო ნიქოზი, მთავარანგელოზის ტაძარი", "has_coordinates": True},
                "Jvari Monastery, Mtskheta": {"lat": 41.8383, "lon": 44.7333, "name_ka": "ჯვრის მონასტერი, მცხეთა", "has_coordinates": True},
                "Urbnisi Sioni": {"lat": 41.7500, "lon": 44.6167, "name_ka": "ურბნისის სიონი", "has_coordinates": True},
                "Lamazi Gora, Bolnisi": {"lat": 41.3889, "lon": 44.5126, "name_ka": "ლამაზი გორა, ბოლნისი", "has_coordinates": True},
                "Bolnisi Sioni": {"lat": 41.3889, "lon": 44.5126, "name_ka": "ბოლნისის სიონი", "has_coordinates": True},
                "Mtskheta": {"lat": 41.8451, "lon": 44.7188, "name_ka": "მცხეთა", "has_coordinates": True},
                "Ukangori": {"lat": 41.9167, "lon": 44.8333, "name_ka": "უკანგორი", "has_coordinates": True},
                "Zarzma Monastery": {"lat": 41.5500, "lon": 42.6500, "name_ka": "ზარზმის მონასტერი", "has_coordinates": True},
                "Phia Church of St. Theodore": {"lat": 41.6000, "lon": 42.8000, "name_ka": "ფიის წმინდა თეოდორეს ეკლესია", "has_coordinates": True},
                "Village Kheoti Former Monastery": {"lat": 41.7667, "lon": 44.6833, "name_ka": "სოფელ ხეოთის ნამონასტრალი", "has_coordinates": True},
                "Agara (Urvali) Church": {"lat": 41.8000, "lon": 43.7000, "name_ka": "აგარის (ურვალის) ეკლესია", "has_coordinates": True},
                "Saro Castle": {"lat": 41.7000, "lon": 42.9000, "name_ka": "საროს ციხე", "has_coordinates": True},
                "Tsunda Church": {"lat": 41.6500, "lon": 42.7500, "name_ka": "წუნდის ეკლესია", "has_coordinates": True},
                "Vanis Kvabebi": {"lat": 41.3667, "lon": 43.2833, "name_ka": "ვანის ქვაბები", "has_coordinates": True},
                "Sapara Monastery St. Saba Cathedral": {"lat": 41.5500, "lon": 42.6500, "name_ka": "საფარის მონასტრის წმ. საბას ტაძარი", "has_coordinates": True},
                "Bieti Church": {"lat": 41.6167, "lon": 42.9333, "name_ka": "ბიეთის ეკლესია", "has_coordinates": True},
                "Tmogvi Castle": {"lat": 41.3500, "lon": 43.2000, "name_ka": "თმოგვის ციხე", "has_coordinates": True},
                "Vardzia": {"lat": 41.3718, "lon": 43.2545, "name_ka": "ვარძია", "has_coordinates": True},
                "Patara Smada Church": {"lat": 41.4000, "lon": 43.3000, "name_ka": "პატარა სმადის ეკლესია", "has_coordinates": True},
                "Sapara St. George Church": {"lat": 41.5500, "lon": 42.6500, "name_ka": "საფარის წმ. გიორგის ეკლესია", "has_coordinates": True},
                "Hayravank": {"lat": 40.1642, "lon": 44.7019, "name_ka": "აირავანქი", "has_coordinates": True},
                "Ani": {"lat": 40.5067, "lon": 43.5725, "name_ka": "ანისი", "has_coordinates": True},
                "Haghpat": {"lat": 41.0955, "lon": 44.714, "name_ka": "ჰაღბატი", "has_coordinates": True},
                "Berdik": {"lat": 41.3500, "lon": 44.4500, "name_ka": "ბერდიკი", "has_coordinates": True},
                "Dmanisi": {"lat": 41.3298, "lon": 44.2073, "name_ka": "დმანისი", "has_coordinates": True},
                "Samtavro": {"lat": 41.8451, "lon": 44.7188, "name_ka": "სამთავრო", "has_coordinates": True},
                "Zhinvali": {"lat": 42.0717, "lon": 44.7797, "name_ka": "ჟინვალი", "has_coordinates": True},
                "Pashianta": {"lat": 42.3333, "lon": 40.5000, "name_ka": "ფაშიანთა", "has_coordinates": True},
                "Tsandripshi": {"lat": 43.2833, "lon": 40.0500, "name_ka": "წანდრიფში", "has_coordinates": True},
                "Bichvinta": {"lat": 43.1611, "lon": 40.3456, "name_ka": "ბიჭვინთა", "has_coordinates": True},
                "New Athos": {"lat": 43.0869, "lon": 40.0908, "name_ka": "ახალი ათონი", "has_coordinates": True},
                "Eshera": {"lat": 43.0500, "lon": 40.1000, "name_ka": "ეშერა", "has_coordinates": True},
                "Sokhumi": {"lat": 42.865, "lon": 41.0236, "name_ka": "სოხუმი", "has_coordinates": True},
                "Pichvnari": {"lat": 41.6833, "lon": 41.7333, "name_ka": "ფიჭვნარი", "has_coordinates": True},
                "Ateni": {"lat": 41.9039, "lon": 44.0959, "name_ka": "ატენი", "has_coordinates": True},
                "Itkhvisi": {"lat": 42.0167, "lon": 43.7500, "name_ka": "ითხვისი", "has_coordinates": True},
                "Gvandra": {"lat": 42.2000, "lon": 43.6000, "name_ka": "გვანდრა", "has_coordinates": True},
                "Sairkhe": {"lat": 42.1833, "lon": 43.6167, "name_ka": "საირხე", "has_coordinates": True},
                "Tsebrelda (Lari)": {"lat": 42.9167, "lon": 40.0833, "name_ka": "წებელდა (ლარი)", "has_coordinates": True},
                "Nokalakevi": {"lat": 42.3167, "lon": 42.1833, "name_ka": "ნოქალაქევი", "has_coordinates": True},
                "Akhtala": {"lat": 41.1000, "lon": 44.7833, "name_ka": "ახტალა", "has_coordinates": True},
                "Tsaishi": {"lat": 42.4000, "lon": 42.2000, "name_ka": "ცაიში", "has_coordinates": True},
                "Dzalisa": {"lat": 41.8667, "lon": 44.8167, "name_ka": "ძალისა", "has_coordinates": True},
                "Nakipari": {"lat": 42.0000, "lon": 43.5000, "name_ka": "ნაკიფარი", "has_coordinates": True},
                "Vani Archaeological Site": {"lat": 42.0833, "lon": 42.5, "name_ka": "ვანის ნაქალაქარი", "has_coordinates": True},
                "Kobayr Monastery, Armenia": {"lat": 41.0167, "lon": 44.6333, "name_ka": "ქობაირის მონასტერი, სომხეთი", "has_coordinates": True},
                "David Gareja Monastery": {"lat": 41.4456, "lon": 45.3789, "name_ka": "დავით გარეჯის მონასტერი", "has_coordinates": True},
                "Mokhisi": {"lat": 41.7500, "lon": 44.5833, "name_ka": "მოხისი", "has_coordinates": True},
                "Chkondidi": {"lat": 42.2833, "lon": 42.1167, "name_ka": "ჭყონდიდი", "has_coordinates": True},
                "Gelati": {"lat": 42.2917, "lon": 42.7567, "name_ka": "გელათი", "has_coordinates": True},
                "Ostia": {"lat": 41.7520, "lon": 12.2920, "name_ka": "ოსტია", "has_coordinates": True},
                "Bedia": {"lat": 42.7000, "lon": 40.2000, "name_ka": "ბედია", "has_coordinates": True},
                "Ilori": {"lat": 42.8000, "lon": 40.1500, "name_ka": "ილორი", "has_coordinates": True},
                "Likhni": {"lat": 42.9167, "lon": 40.2500, "name_ka": "ლიხნი", "has_coordinates": True},
                "Chlou": {"lat": 42.8800, "lon": 40.2800, "name_ka": "ჭლოუ", "has_coordinates": True},
                "Timotesubani": {"lat": 41.8167, "lon": 43.5833, "name_ka": "ტიმოთესუბანი", "has_coordinates": True},
                "Satkhis": {"lat": 41.6667, "lon": 44.8333, "name_ka": "სათხე", "has_coordinates": True}
            }

            return georgian_coordinates

        except Exception as e:
            print(f"❌ Error creating coordinates mapping: {e}")
            return {}


    def debug_missing_places(self):
        """Debug method to find all place names that don't have coordinates"""
        try:
            print("🔍 Debugging all place names from inscriptions...")

            coordinates_map = self.create_coordinates_mapping()
            missing_places = set()
            found_places = set()

            for inscription in self.inscriptions:
                place = inscription['origin'].get('place', '').strip()
                if place:
                    # Check if we have coordinates for this place
                    coords = self.find_coordinates(place, coordinates_map)
                    if coords.get('lat') is None:
                        missing_places.add(place)
                        print(f"❌ Missing: '{place}'")
                    else:
                        found_places.add(place)
                        print(f"✅ Found: '{place}' -> {coords['lat']}, {coords['lon']}")

            print(f"\n📊 Summary:")
            print(f"   Found coordinates: {len(found_places)} places")
            print(f"   Missing coordinates: {len(missing_places)} places")

            if missing_places:
                print(f"\n📝 Missing places list:")
                for place in sorted(missing_places):
                    print(f"   \"{place}\": {{\"lat\": 0.0, \"lon\": 0.0, \"name_en\": \"\", \"has_coordinates\": False}},")

            return missing_places, found_places

        except Exception as e:
            print(f"❌ Error in debug: {e}")
            return set(), set()


    # Replace your generate_map_data() method with this improved version
    # that includes coordinate spreading to fix pin jumping

    def generate_map_data(self):
        """Generate map data with coordinate clustering prevention"""
        try:
            print("🗺️ Generating map data with coordinate spreading...")

            # Load coordinates mapping
            coordinates_map = self.create_coordinates_mapping()

            print(f"📍 Coordinates map has {len(coordinates_map)} entries")

            map_data = []
            coordinate_usage = {}  # Track coordinate usage to prevent clustering

            # Count inscriptions per place
            place_counts = {}
            for inscription in self.inscriptions:
                place = inscription['origin'].get('place', '').strip()
                if place:
                    if place not in place_counts:
                        place_counts[place] = []
                    place_counts[place].append(inscription)

            print(f"📍 Found {len(place_counts)} unique places in inscriptions")

            # Create map markers with coordinate clustering prevention
            matched_places = 0
            coordinate_debug = []
            language_stats = {'ka': 0, 'grc': 0, 'hy': 0, 'mixed': 0, 'other': 0, 'unknown': 0, 'arc': 0, 'he': 0, 'la': 0}

            for place, inscriptions_list in place_counts.items():
                coords = self.find_coordinates(place, coordinates_map)

                if coords.get('lat') is not None and coords.get('lon') is not None:
                    lat, lon = float(coords['lat']), float(coords['lon'])

                    # Validate coordinates are reasonable for Georgia/Caucasus region
                    if 35 <= lat <= 50 and 35 <= lon <= 50:

                        # Check for coordinate clustering and apply offset if needed
                        coord_key = f"{lat:.4f},{lon:.4f}"
                        if coord_key in coordinate_usage:
                            # Apply small offset to prevent exact overlap
                            offset_count = len(coordinate_usage[coord_key])
                            offset_angle = offset_count * (2 * math.pi / 8)  # Distribute in circle
                            offset_distance = 0.012  # Slightly larger offset (~1.3km) for better separation

                            original_lat, original_lon = lat, lon
                            lat += offset_distance * math.cos(offset_angle)
                            lon += offset_distance * math.sin(offset_angle)

                            print(f"🔧 Applied offset to '{place}': {original_lat:.4f},{original_lon:.4f} -> {lat:.4f},{lon:.4f}")
                            coordinate_debug.append(f"🔧 OFFSET: '{place}' -> [{lat:.4f}, {lon:.4f}] (was clustered with {coordinate_usage[coord_key]})")
                        else:
                            coordinate_usage[coord_key] = []
                            coordinate_debug.append(f"✅ PLACED: '{place}' -> [{lat:.4f}, {lon:.4f}]")

                        coordinate_usage[coord_key].append(place)

                        # Process inscriptions with language detection
                        enhanced_inscriptions = []
                        place_languages = {}

                        for insc in inscriptions_list:
                            # Use actual language from inscription
                            detected_lang = insc.get('language', 'unknown')

                            # If unknown, try to detect from title
                            if detected_lang == 'unknown':
                                detected_lang = self.detect_language_from_inscription_title(insc)

                            # Count languages for this place
                            place_languages[detected_lang] = place_languages.get(detected_lang, 0) + 1
                            language_stats[detected_lang] = language_stats.get(detected_lang, 0) + 1

                            enhanced_inscriptions.append({
                                'id': insc['id'],
                                'title': self.get_display_title(insc['title']),
                                'language': detected_lang,
                                'url': f'inscriptions/{insc["id"]}.html'
                            })

                        map_data.append({
                            'place': place,
                            'lat': lat,
                            'lon': lon,
                            'count': len(inscriptions_list),
                            'inscriptions': enhanced_inscriptions,
                            'languages': place_languages
                        })
                        matched_places += 1
                    else:
                        coordinate_debug.append(f"⚠️ INVALID: '{place}' -> [{lat}, {lon}] (out of range)")
                else:
                    coordinate_debug.append(f"❌ MISSING: '{place}' -> No coordinates found")

            # Print debugging info
            print(f"\n📊 Coordinate Assignment Results:")

            # Show clustering fixes first
            clustered_fixes = [line for line in coordinate_debug if "OFFSET" in line]
            if clustered_fixes:
                print(f"🔧 Fixed {len(clustered_fixes)} clustered coordinates:")
                for fix in clustered_fixes[:10]:  # Show first 10
                    print(f"   {fix}")
                if len(clustered_fixes) > 10:
                    print(f"   ... and {len(clustered_fixes) - 10} more fixes")

            # Show other results
            other_results = [line for line in coordinate_debug if "OFFSET" not in line]
            if other_results:
                print(f"\n📍 Other coordinate assignments:")
                for result in other_results[:10]:  # Show first 10
                    print(f"   {result}")
                if len(other_results) > 10:
                    print(f"   ... and {len(other_results) - 10} more")

            # Print coordinate clustering analysis
            print(f"\n🔍 Final Coordinate Analysis:")
            final_clusters = {}
            for coord_key, places in coordinate_usage.items():
                if len(places) > 1:
                    final_clusters[coord_key] = places

            if final_clusters:
                print(f"⚠️ Still have {len(final_clusters)} clusters after spreading:")
                for coord, places in list(final_clusters.items())[:3]:
                    print(f"   {coord}: {len(places)} places -> {', '.join(places[:2])}{'...' if len(places) > 2 else ''}")
            else:
                print("✅ No coordinate clustering after spreading - pin jumping should be fixed!")

            # Print language statistics
            print(f"\n📊 Language Distribution for Map:")
            total_inscriptions = sum(language_stats.values())
            for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
                if count > 0:  # Only show languages that exist
                    percentage = (count / total_inscriptions * 100) if total_inscriptions > 0 else 0
                    lang_name = {
                        'ka': 'Georgian',
                        'grc': 'Greek',
                        'hy': 'Armenian',
                        'arc': 'Aramaic',
                        'he': 'Hebrew',
                        'la': 'Latin',
                        'unknown': 'Unknown',
                        'other': 'Other',
                        'mixed': 'Mixed'
                    }.get(lang, lang)
                    print(f"   {lang_name}: {count} ({percentage:.1f}%)")

            # Save map data
            with open(f"{self.output_dir}/map-data.json", 'w', encoding='utf-8') as f:
                json.dump(map_data, f, ensure_ascii=False, indent=2)

            print(f"\n🗺️ Generated map data for {matched_places} locations")
            print(f"📄 Map data saved to: {self.output_dir}/map-data.json")
            print(f"🔧 Applied coordinate spreading to fix pin jumping!")

            return map_data

        except Exception as e:
            print(f"❌ Error generating map data: {e}")
            import traceback
            traceback.print_exc()
            return []

    # Also add this helper method if you don't have it
    def detect_language_from_inscription_title(self, inscription):
        """Detect language from inscription title"""
        try:
            title = self.get_display_title(inscription.get('title', ''))

            if not title:
                return 'unknown'

            import re

            # Georgian detection (multiple Unicode ranges)
            if re.search(r'[\u10A0-\u10FF\u2D00-\u2D2F\u1C90-\u1CBF]', title):
                return 'ka'

            # Greek detection
            if re.search(r'[\u0370-\u03FF\u1F00-\u1FFF]', title):
                return 'grc'

            # Armenian detection
            if re.search(r'[\u0530-\u058F\uFB13-\uFB17]', title):
                return 'hy'

            # Hebrew detection
            if re.search(r'[\u0590-\u05FF]', title):
                return 'he'

            # Arabic detection
            if re.search(r'[\u0600-\u06FF]', title):
                return 'ar'

            # Aramaic detection (similar to Hebrew range, but check content)
            if 'aramaic' in title.lower() or 'arc' in inscription.get('language', '').lower():
                return 'arc'

            # Latin detection
            if re.search(r'^[a-zA-Z\s\-\.]+$', title):
                return 'la'

            return 'unknown'

        except Exception:
            return 'unknown'
    # ღია არის generate_map_data მეთოდის ჩანაცვლება - დასრულება

    # ღია არის კოორდინატების სპეციფიური დებაგი - დაიწყება
    def debug_coordinate_assignments(self):
        """Debug specific coordinate assignments that might be wrong"""
        try:
            print("\n🔍 Debugging specific coordinate assignments...")

            coordinates_map = self.create_coordinates_mapping()

            # Test specific places that should have different coordinates
            test_places = [
                'მცხეთა',  # Should be ~41.8451, 44.7188
                'ვანი',    # Should be ~42.0833, 42.5
                'ახალი ათონი',  # Should be ~43.0869, 40.0908
                'ხუნზახი, დაღესტანი',  # Should be ~42.55, 46.75
                'ქობაირის მონასტერი, სომხეთი'  # Should be ~41.0167, 44.6333
            ]

            for place in test_places:
                if place in coordinates_map:
                    coord = coordinates_map[place]
                    print(f"🔍 '{place}': lat={coord.get('lat')}, lon={coord.get('lon')}")
                else:
                    # Try fuzzy matching
                    found = self.find_coordinates(place, coordinates_map)
                    print(f"🔍 '{place}': FUZZY -> lat={found.get('lat')}, lon={found.get('lon')}")

            return True

        except Exception as e:
            print(f"❌ Error in coordinate debugging: {e}")
            return False
    # ღია არის კოორდინატების სპეციფიური დებაგი - დასრულება

    #აქ იწყება ადგილების დებაგი
    def debug_inscription_places(self):
        """Debug what places are actually in inscriptions"""
        try:
            print("🔍 Debugging inscription places...")

            place_counts = {}
            for inscription in self.inscriptions:
                place = inscription['origin'].get('place', '').strip()
                if place:
                    if place not in place_counts:
                        place_counts[place] = 0
                    place_counts[place] += 1
                else:
                    print(f"   No place found for inscription {inscription['id']}")

            print(f"\n📍 Places found in inscriptions ({len(place_counts)} unique):")
            for place, count in sorted(place_counts.items()):
                print(f"   '{place}': {count} inscriptions")

            return place_counts

        except Exception as e:
            print(f"❌ Error debugging places: {e}")
            return {}

    def debug_place_names_file(self):
        """Debug what's in the place-names.json file"""
        try:
            print("\n🔍 Debugging place-names.json...")

            place_names = self.load_place_names_from_file()

            print(f"📄 Place names file structure:")
            print(f"   - 'ka' section: {len(place_names.get('ka', {}))} places")
            print(f"   - 'en' section: {len(place_names.get('en', {}))} places")
            print(f"   - 'all_places' section: {len(place_names.get('all_places', []))} places")

            print(f"\n📍 First 10 places in 'all_places':")
            for i, place_info in enumerate(place_names.get('all_places', [])[:10]):
                print(f"   {i+1}. '{place_info.get('name', 'NO_NAME')}' ({place_info.get('language', 'no_lang')}) - "
                      f"Coords: {place_info.get('has_coordinates', False)}")

            return place_names

        except Exception as e:
            print(f"❌ Error debugging place names: {e}")
            return {}
    #აქ მთავრდება ადგილების დებაგი

    def safe_extract_complete_metadata(self, root):
        """Extract comprehensive metadata from TEI header"""
        try:
            metadata = {}

            # Editor information
            editor_elems = self.safe_xpath(root, './/tei:titleStmt/tei:editor')
            if editor_elems:
                metadata['editor'] = self.safe_get_element_text(editor_elems[0])

            # Authority/Institution
            authority_elems = self.safe_xpath(root, './/tei:publicationStmt/tei:authority')
            if authority_elems:
                metadata['authority'] = self.safe_get_element_text(authority_elems[0])

            # Collection information
            collection_elems = self.safe_xpath(root, './/tei:msIdentifier/tei:collection')
            if collection_elems:
                metadata['collection'] = self.safe_get_element_text(collection_elems[0])

            # Layout information (written lines, etc.)
            layout_elems = self.safe_xpath(root, './/tei:layoutDesc/tei:layout')
            if layout_elems:
                layout = layout_elems[0]
                written_lines = layout.get('writtenLines', '')
                layout_text = self.safe_get_element_text(layout)
                metadata['layout'] = {
                    'written_lines': written_lines,
                    'description': layout_text
                }

            # Hand description (script, style, execution)
            hand_elems = self.safe_xpath(root, './/tei:handDesc/tei:handNote')
            if hand_elems:
                hand = hand_elems[0]
                script = hand.get('script', '')
                style = hand.get('style', '')

                # Extract execution and script type from rs elements
                execution_elems = self.safe_xpath(hand, './/tei:rs[@type="execution"]')
                script_type_elems = self.safe_xpath(hand, './/tei:rs[@type="script"]')

                execution = self.safe_get_element_text(execution_elems[0]) if execution_elems else ''
                script_type = self.safe_get_element_text(script_type_elems[0]) if script_type_elems else ''

                # Letter height
                height_elems = self.safe_xpath(hand, './/tei:height')
                letter_height = self.safe_get_element_text(height_elems[0]) if height_elems else ''

                metadata['handwriting'] = {
                    'script': script,
                    'style': style,
                    'execution': execution,
                    'script_type': script_type,
                    'letter_height': letter_height,
                    'description': self.safe_get_element_text(hand)
                }


                # Provenance information (circumstances, context)
                provenance_elems = self.safe_xpath(root, './/tei:provenance[@type="found"]')
                if provenance_elems:
                    prov_elem = provenance_elems[0]

                    # Ancient findspot
                    ancient_spot_elems = self.safe_xpath(prov_elem, './/tei:placeName[@type="ancientFindspot"]')
                    if ancient_spot_elems:
                        ancient_spot_elem = ancient_spot_elems[0]
                        text = self.safe_get_element_text(ancient_spot_elem)
                        ref_url = ancient_spot_elem.get('ref')  # Extract the ref attribute

                        # Debug prints
                        print(f"DEBUG ancient: text = {text}")
                        print(f"DEBUG ancient: ref_url = {ref_url}")

                        if ref_url:
                            # Create dict with both text and URL
                            ancient_spot = {
                                'text': text,
                                'url': ref_url
                            }
                        else:
                            # Just text if no ref attribute
                            ancient_spot = text
                    else:
                        ancient_spot = ''

                    # Circumstances
                    circumstances_elems = self.safe_xpath(prov_elem, './/tei:rs[@type="circumstances"]')
                    circumstances = self.safe_get_element_text(circumstances_elems[0]) if circumstances_elems else ''

                    # Context
                    context_elems = self.safe_xpath(prov_elem, './/tei:rs[@type="context"]')
                    context = self.safe_get_element_text(context_elems[0]) if context_elems else ''

                # Modern findspot
                modern_spot_elems = self.safe_xpath(root, './/tei:provenance[@type="observed"]//tei:placeName[@type="modernSpot"]')
                if modern_spot_elems:
                    modern_spot_elem = modern_spot_elems[0]
                    text = self.safe_get_element_text(modern_spot_elem)
                    ref_url = modern_spot_elem.get('ref')  # Extract the ref attribute

                    if ref_url:
                        # Create dict with both text and URL
                        modern_spot = {
                            'text': text,
                            'url': ref_url
                        }
                    else:
                        # Just text if no ref attribute
                        modern_spot = text
                else:
                    modern_spot = ''

                metadata['provenance'] = {
                    'circumstances': circumstances,
                    'context': context,
                    'modern_location': modern_spot,
                    'ancient_location': ancient_spot  # ADD THIS LINE!
                }



            # Dating evidence and method
            date_elems = self.safe_xpath(root, './/tei:origDate')
            if date_elems:
                date_elem = date_elems[0]
                evidence = date_elem.get('evidence', '')
                precision = date_elem.get('precision', '')
                dating_method = date_elem.get('datingMethod', '')

                if 'dating' not in metadata:
                    metadata['dating'] = {}

                metadata['dating'].update({
                    'evidence': evidence,
                    'precision': precision,
                    'dating_method': dating_method
                })

            # License information
            license_elems = self.safe_xpath(root, './/tei:licence')
            if license_elems:
                license_elem = license_elems[0]
                license_target = license_elem.get('target', '')
                license_text = self.safe_get_element_text(license_elem)
                metadata['license'] = {
                    'url': license_target,
                    'text': license_text
                }

            # Revision history
            revision_elems = self.safe_xpath(root, './/tei:revisionDesc/tei:change')
            if revision_elems:
                revisions = []
                for change in revision_elems:
                    when = change.get('when', '')
                    who = change.get('who', '')
                    description = self.safe_get_element_text(change)
                    revisions.append({
                        'date': when,
                        'author': who,
                        'description': description
                    })
                metadata['revisions'] = revisions

            return metadata

        except Exception as e:
            print(f"❌ Error extracting complete metadata: {e}")
            return {}

    def create_enhanced_overview_section(self, inscription):
        """Create enhanced academic-style overview section"""
        try:
            # Extract complete metadata
            complete_metadata = self.safe_extract_complete_metadata(inscription.get('xml_root'))

            sections = []

            # Summary Section
            if inscription['summary']:
                summary_html = self.format_bilingual_text(inscription['summary'])
                sections.append(f'''
                    <div class="summary">
                        <h3>შინაარსი / Summary</h3>
                        <div class="summary-content">{summary_html}</div>
                    </div>
                ''')

            # Basic Information
            basic_items = []
            basic_items.append(f'''
                <div class="meta-item">
                    <span class="bilingual-label"><span class="ka">იდენტიფიკატორი</span> <span class="en">ID</span>:</span>
                    <span class="meta-value">{inscription["id"]}</span>
                </div>
            ''')

            # Format language display
            lang_display = {
                'ka': 'Georgian (ka)',
                'grc': 'Greek (grc)',
                'hy': 'Armenian (hy)',
                'unknown': 'Unknown'
            }.get(inscription['language'], inscription['language'])

            basic_items.append(f'''
                <div class="meta-item">
                    <span class="bilingual-label"><span class="ka">ენა</span> <span class="en">Language</span>:</span>
                    <span class="meta-value">{lang_display}</span>
                </div>
            ''')

            if complete_metadata.get('editor'):
                basic_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">რედაქტორი</span> <span class="en">Editor</span>:</span>
                        <span class="meta-value georgian-text">{complete_metadata["editor"]}</span>
                    </div>
                ''')

            if complete_metadata.get('authority'):
                basic_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">გამომცემელი</span> <span class="en">Authority</span>:</span>
                        <span class="meta-value georgian-text">{complete_metadata["authority"]}</span>
                    </div>
                ''')

            if complete_metadata.get('collection'):
                basic_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">კოლექცია</span> <span class="en">Collection</span>:</span>
                        <span class="meta-value georgian-text">{complete_metadata["collection"]}</span>
                    </div>
                ''')

            if basic_items:
                sections.append(f'''
                    <div class="metadata-group">
                        <h4>ძირითადი ინფორმაცია / Basic Information</h4>
                        {''.join(basic_items)}
                    </div>
                ''')

            # Dating Information
            dating_items = []
            dating_data = inscription['dating']
            complete_dating = complete_metadata.get('dating', {})

            if dating_data.get('text'):
                dating_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">დათარიღება</span> <span class="en">Dating</span>:</span>
                        <span class="meta-value">{dating_data["text"]}</span>
                    </div>
                ''')

            if dating_data.get('not_before') or dating_data.get('not_after'):
                period = f"{dating_data.get('not_before', '')} - {dating_data.get('not_after', '')}"
                dating_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">პერიოდი</span> <span class="en">Period</span>:</span>
                        <span class="meta-value">{period} CE</span>
                    </div>
                ''')

            if complete_dating.get('evidence'):
                dating_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">დათარიღების საფუძველი</span> <span class="en">Dating Evidence</span>:</span>
                        <span class="meta-value">{complete_dating["evidence"]}</span>
                    </div>
                ''')

            if complete_dating.get('precision'):
                dating_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">სიზუსტე</span> <span class="en">Precision</span>:</span>
                        <span class="meta-value">{complete_dating["precision"]}</span>
                    </div>
                ''')

            if dating_items:
                sections.append(f'''
                    <div class="metadata-group">
                        <h4>დათარიღება / Dating</h4>
                        {''.join(dating_items)}
                    </div>
                ''')

            # Physical Description
            physical_items = []

            if inscription['material']:
                material_display = self.format_material_display(inscription['material'])
                # Check if material contains Georgian text
                material_class = 'georgian-text' if any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in material_display) else 'meta-value'
                physical_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">მასალა</span> <span class="en">Material</span>:</span>
                        <span class="{material_class}">{material_display}</span>
                    </div>
                ''')

            if inscription['object_type']:
                object_display = self.format_object_type_display(inscription['object_type'])
                object_class = 'georgian-text' if any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in object_display) else 'meta-value'
                physical_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">ობიექტის ტიპი</span> <span class="en">Object Type</span>:</span>
                        <span class="{object_class}">{object_display}</span>
                    </div>
                ''')

            if inscription['dimensions'].get('height') or inscription['dimensions'].get('width'):
                dims = inscription['dimensions']
                dim_parts = []
                if dims.get('height'):
                    dim_parts.append(f'<span class="measurement">H: {dims["height"]}{dims.get("unit", "cm")}</span>')
                if dims.get('width'):
                    dim_parts.append(f'<span class="measurement">W: {dims["width"]}{dims.get("unit", "cm")}</span>')
                if dims.get('depth'):
                    dim_parts.append(f'<span class="measurement">D: {dims["depth"]}{dims.get("unit", "cm")}</span>')

                physical_items.append(f'''
                    <div class="meta-item">
                        <span class="bilingual-label"><span class="ka">ზომები</span> <span class="en">Dimensions</span>:</span>
                        <span class="meta-value">{" × ".join(dim_parts)}</span>
                    </div>
                ''')

            if physical_items:
                sections.append(f'''
                    <div class="metadata-group">
                        <h4>ფიზიკური აღწერა / Physical Description</h4>
                        {''.join(physical_items)}
                    </div>
                ''')

            # Layout and Paleography
            paleo_items = []

            if complete_metadata.get('layout'):
                layout = complete_metadata['layout']
                if layout.get('written_lines'):
                    paleo_items.append(f'''
                        <div class="meta-item">
                            <span class="bilingual-label"><span class="ka">სტრიქონების რაოდენობა</span> <span class="en">Written Lines</span>:</span>
                            <span class="meta-value">{layout["written_lines"]}</span>
                        </div>
                    ''')

            if complete_metadata.get('handwriting'):
                hand = complete_metadata['handwriting']
                if hand.get('script_type'):
                    paleo_items.append(f'''
                        <div class="meta-item">
                            <span class="bilingual-label"><span class="ka">დამწერლობა</span> <span class="en">Script</span>:</span>
                            <span class="meta-value georgian-text">{hand["script_type"]}</span>
                        </div>
                    ''')

                if hand.get('execution'):
                    paleo_items.append(f'''
                        <div class="meta-item">
                            <span class="bilingual-label"><span class="ka">შესრულება</span> <span class="en">Execution</span>:</span>
                            <span class="meta-value georgian-text">{hand["execution"]}</span>
                        </div>
                    ''')

                if hand.get('letter_height'):
                    paleo_items.append(f'''
                        <div class="meta-item">
                            <span class="bilingual-label"><span class="ka">ასოების სიმაღლე</span> <span class="en">Letter Height</span>:</span>
                            <span class="meta-value"><span class="measurement">{hand["letter_height"]} cm</span></span>
                        </div>
                    ''')

                if hand.get('description'):
                    paleo_items.append(f'''
                        <div class="meta-description">
                            <span class="georgian-text">{hand["description"]}</span>
                        </div>
                    ''')

            if paleo_items:
                sections.append(f'''
                    <div class="metadata-group">
                        <h4>განლაგება და პალეოგრაფია / Layout and Paleography</h4>
                        {''.join(paleo_items)}
                    </div>
                ''')

                # Origin and Provenance
                prov_items = []

                # Ancient findspot (from complete_metadata)
                if complete_metadata.get('provenance', {}).get('ancient_location'):
                    ancient_loc = complete_metadata['provenance']['ancient_location']

                    if isinstance(ancient_loc, dict) and ancient_loc.get('url'):
                        ancient_loc_span = f'''<span class="meta-value">
                                            <a href="{ancient_loc["url"]}" class="meta-link" target="_blank">
                                                {ancient_loc.get("text", "Location")}
                                            </a>
                                        </span>'''
                    else:
                        ancient_loc_span = f'<span class="meta-value georgian-text">{ancient_loc}</span>'

                    prov_items.append(f'''
                        <div class="meta-item">
                            <span class="bilingual-label"><span class="ka">აღმოჩენილია</span> <span class="en">Find Location</span>:</span>
                            {ancient_loc_span}
                        </div>
                    ''')

                # Modern location
                if complete_metadata.get('provenance', {}).get('modern_location'):
                    modern_loc = complete_metadata['provenance']['modern_location']

                    if isinstance(modern_loc, dict) and modern_loc.get('url'):
                        modern_loc_span = f'''<span class="meta-value">
                                            <a href="{modern_loc["url"]}" class="meta-link" target="_blank">
                                                {modern_loc.get("text", "Location")}
                                            </a>
                                        </span>'''
                    else:
                        modern_loc_span = f'<span class="meta-value georgian-text">{modern_loc}</span>'

                    prov_items.append(f'''
                        <div class="meta-item">
                            <span class="bilingual-label"><span class="ka">თანამედროვე მდებარეობა</span> <span class="en">Current Location</span>:</span>
                            {modern_loc_span}
                        </div>
                    ''')

                # Circumstances
                if complete_metadata.get('provenance', {}).get('circumstances'):
                    circumstances = complete_metadata['provenance']['circumstances']
                    prov_items.append(f'''
                        <div class="meta-description">
                            <strong>აღმოჩენის გარემოებები / Discovery Circumstances:</strong> {circumstances}
                        </div>
                    ''')

                if prov_items:
                    sections.append(f'''
                        <div class="metadata-group">
                            <h4>წარმოშობა და მდებარეობა / Origin and Provenance</h4>
                            {''.join(prov_items)}
                        </div>
                    ''')


            # Publication Information
            pub_items = []

            if complete_metadata.get('license'):
                license_info = complete_metadata['license']
                if license_info.get('url'):
                    pub_items.append(f'''
                        <div class="meta-item">
                            <span class="bilingual-label"><span class="ka">ლიცენზია</span> <span class="en">License</span>:</span>
                            <span class="meta-value">
                                <a href="{license_info["url"]}" class="meta-link" target="_blank">
                                    {license_info.get("text", "Creative Commons License")}
                                </a>
                            </span>
                        </div>
                    ''')

            if complete_metadata.get('revisions'):
                revisions = complete_metadata['revisions']
                revision_items = []
                for rev in revisions:
                    revision_items.append(f'''
                        <div class="revision-item">
                            {rev.get('date', '')} ({rev.get('author', '')}): {rev.get('description', '')}
                        </div>
                    ''')

                if revision_items:
                    pub_items.append(f'''
                        <div class="meta-item">
                            <span class="bilingual-label"><span class="ka">რევიზიების ისტორია</span> <span class="en">Revision History</span>:</span>
                            <div class="revision-list">
                                {''.join(revision_items)}
                            </div>
                        </div>
                    ''')

            if pub_items:
                sections.append(f'''
                    <div class="metadata-group">
                        <h4>გამოცემის ინფორმაცია / Publication Information</h4>
                        {''.join(pub_items)}
                    </div>
                ''')

            return f'<div class="overview">{"".join(sections)}</div>'

        except Exception as e:
            print(f"❌ Error creating enhanced overview: {e}")
            return f'<div class="overview"><p>Error displaying overview: {e}</p></div>'





    def create_inscription_page_vanilla(self, inscription):
        """Create individual inscription page with vanilla JavaScript tabs"""
        try:
            # Build metadata
            metadata_parts = [f'<span class="id">№ {inscription["id"]}</span>']

            if inscription['dating'].get('text'):
                metadata_parts.append(f'<span class="date">📅 {inscription["dating"]["text"]}</span>')

            if inscription['origin'].get('place'):
                metadata_parts.append(f'<span class="place">📍 {inscription["origin"]["place"]}</span>')

            if inscription['material']:
                metadata_parts.append(f'<span class="material">🔨 {self.format_material_display(inscription["material"])}</span>')

            if inscription['object_type']:
                metadata_parts.append(f'<span class="object-type">📦 {self.format_object_type_display(inscription["object_type"])}</span>')

            metadata_parts.append(f'<span class="lang">🌐 {inscription["language"]}</span>')

            metadata_html = '\n                '.join(metadata_parts)

            # Build sections safely with bilingual support
            summary_section = ""
            if inscription['summary']:
                summary_html = self.format_bilingual_text(inscription['summary'])
                summary_section = f'<div class="summary"><h3><span class="ka">შინაარსი</span> <span class="en">Summary</span></h3>{summary_html}</div>'

            # Get display title
            display_title = self.get_display_title(inscription['title'])
            title_html = self.format_bilingual_text(inscription['title'], display_title)

            # Text editions
            text_editions_html = self.safe_format_text_editions(inscription['text_content'])

            # Images section
            images_html = self.format_images_section(inscription['images'])
            images_tab = ""
            images_content = ""
            if inscription['images']:
                images_tab = '<button onclick="showTab(\'images\')" id="tab-images"><span class="ka">სურათები</span> <span class="en">Images</span></button>'
                images_content = f'<div id="content-images" class="tab-content">{images_html}</div>'

            # Translation content
            translation_content = ""
            translation_tab = ""
            if inscription['translation']:
                translation_tab = '<button onclick="showTab(\'translation\')" id="tab-translation"><span class="ka">თარგმანი</span> <span class="en">Translation</span></button>'
                translation_content = f'''<div id="content-translation" class="tab-content">
            <div class="translation">{inscription['translation']}</div>
        </div>'''

            # Commentary content
            commentary_content = ""
            commentary_tab = ""
            if inscription['commentary']:
                commentary_tab = '<button onclick="showTab(\'commentary\')" id="tab-commentary"><span class="ka">კომენტარი</span> <span class="en">Commentary</span></button>'
                commentary_content = f'''<div id="content-commentary" class="tab-content">
            <div class="commentary">{inscription['commentary']}</div>
        </div>'''

            # Build metadata dl
            metadata_dl_parts = []
            metadata_dl_parts.append(f'<dt>ID</dt><dd>{inscription["id"]}</dd>')
            metadata_dl_parts.append(f'<dt>Language</dt><dd>{inscription["language"]}</dd>')

            if inscription['dating'].get('text'):
                metadata_dl_parts.append(f'<dt>Dating</dt><dd>{inscription["dating"]["text"]}</dd>')

            if inscription['origin'].get('text'):
                metadata_dl_parts.append(f'<dt>Origin</dt><dd>{inscription["origin"]["text"]}</dd>')

            if inscription['material']:
                metadata_dl_parts.append(f'<dt>Material</dt><dd>{self.format_material_display(inscription["material"])}</dd>')

            if inscription['object_type']:
                metadata_dl_parts.append(f'<dt>Object Type</dt><dd>{self.format_object_type_display(inscription["object_type"])}</dd>')

            if inscription['dimensions'].get('height') or inscription['dimensions'].get('width'):
                dims = inscription['dimensions']
                dim_text = ""
                if dims.get('height'):
                    dim_text += f"H: {dims['height']}{dims.get('unit', 'cm')}"
                if dims.get('width'):
                    if dim_text:
                        dim_text += " × "
                    dim_text += f"W: {dims['width']}{dims.get('unit', 'cm')}"
                if dims.get('depth'):
                    if dim_text:
                        dim_text += " × "
                    dim_text += f"D: {dims['depth']}{dims.get('unit', 'cm')}"
                metadata_dl_parts.append(f'<dt>Dimensions</dt><dd>{dim_text}</dd>')

            metadata_dl = '\n                        '.join(metadata_dl_parts)

            # Bibliography section with links
            bibliography_section = self.format_bibliography_section(inscription)

            # Determine main language for html lang attribute
            html_lang = inscription['language'] if inscription['language'] in ['ka', 'en', 'hy'] else 'en'
            display_title = self.get_display_title(inscription['title'])

            html = f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title} - ECG</title>
    <link rel="stylesheet" href="../static/css/style.css">
    <!-- Remove the problematic font preloads -->
</head>


<body>
    <nav class="navbar">
        <div class="container">
            <a href="../index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
            <div class="nav-links">
                <a href="index.html">საწყისი</a>
                <a href="browse.html">წარწერები</a>
                <a href="persons.html">პირები</a>
                <a href="bibliography.html">ბიბლიოგრაფია</a>
            </div>
        </div>
    </nav>

    <main class="container">
        <div class="inscription-header">
            <h1>{title_html}</h1>
            <div class="inscription-meta">
                {metadata_html}
            </div>
        </div>

        <div class="tabs">
            <button onclick="showTab('overview')" id="tab-overview" class="active"><span class="ka">მიმოხილვა</span> <span class="en">Overview</span></button>
            <button onclick="showTab('text')" id="tab-text"><span class="ka">ტექსტი</span> <span class="en">Text</span></button>
            {images_tab}
            {translation_tab}
            {commentary_tab}
            <button onclick="showTab('xml')" id="tab-xml"><span class="en">XML Source</span></button>
        </div>



        <div id="content-overview" class="tab-content active">
            {self.create_enhanced_overview_section(inscription)}
            {bibliography_section}
        </div>

        <div id="content-text" class="tab-content">
            <div class="text-editions">
                {text_editions_html}
            </div>
        </div>

        {images_content}
        {translation_content}
        {commentary_content}

        <div id="content-xml" class="tab-content">
            <div class="xml-formatted">{self.format_xml_source_for_edition(inscription['text_content'])}</div>
        </div>
    </main>

    <script src="../static/js/tabs.js"></script>
</body>
</html>"""

            with open(f"{self.output_dir}/inscriptions/{inscription['id']}.html", 'w', encoding='utf-8') as f:
                f.write(html)

        except Exception as e:
            print(f"❌ Error creating page for {inscription['id']}: {e}")

    def format_images_section(self, images):
        """Format images section for inscription page"""
        try:
            if not images:
                return "<p>No images available for this inscription.</p>"

            images_html = '<div class="image-gallery">'
            for image in images:
                images_html += f'''
                    <div class="image-item">
                        <img src="../static/images/{image['path']}" alt="{image['caption']}" loading="lazy">
                        <div class="image-caption">{image['caption']}</div>
                    </div>
                '''
            images_html += '</div>'
            return images_html

        except Exception:
            return "<p>Error displaying images.</p>"


    def format_bibliography_section(self, inscription):
        """Format bibliography section - ONLY References section with links"""
        try:
            sections = []

            # ONLY show linked bibliography references (remove local bibliography)
            if inscription['bibliography_refs']:
                ref_items = []
                for ref in inscription['bibliography_refs']:
                    bib_entry = ref['entry']

                    # Get the abbreviation if available
                    abbrev_text = ""
                    if 'abbrev' in bib_entry and bib_entry['abbrev']:
                        abbrev_text = bib_entry['abbrev']
                    else:
                        # Fallback to structured data
                        structured = bib_entry.get('structured', {})
                        author = structured.get('author', '')
                        date = structured.get('date', '')
                        if author and date:
                            abbrev_text = f"{author} {date}"
                        else:
                            # Use first 50 characters of content
                            content = bib_entry.get('content', '')
                            abbrev_text = content[:50] + "..." if len(content) > 50 else content

                    # Add cited range if available
                    citation_text = abbrev_text
                    if ref.get('cited_range'):
                        citation_text += f", {ref['cited_range']}"

                    # Check if citation contains Georgian text
                    has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in citation_text)
                    font_class = 'georgian-bibliography' if has_georgian else 'bibliography-item'

                    ref_items.append(f'''
                        <li class="{font_class}">
                            <a href="../bibliography.html#{ref["id"]}" class="bib-ref">{citation_text}</a>
                        </li>
                    ''')

                if ref_items:
                    # Join the items outside the f-string
                    ref_items_html = '\n'.join(ref_items)
                    sections.append(f'''
                        <div class="linked-bibliography">
                            <h4><span class="ka">ბიბლიოგრაფია</span> <span class="en">Bibliography</span></h4>
                            <ul class="bibliography-list">{ref_items_html}</ul>
                        </div>
                    ''')

            if sections:
                # Join sections outside the f-string
                sections_html = ''.join(sections)
                return f'<div class="bibliography-section">{sections_html}</div>'
            return ""

        except Exception as e:
            print(f"❌ Error formatting bibliography: {e}")
            return ""




    def format_bilingual_text(self, text_data, fallback=""):
        """Format bilingual text for display"""
        try:
            if isinstance(text_data, dict):
                ka_text = text_data.get('ka', '')
                en_text = text_data.get('en', '')
                default_text = text_data.get('default', '')

                # Prefer ka and en, fallback to default or first available
                if ka_text and en_text:
                    return f'<div class="bilingual-text"><div class="text-ka">{ka_text}</div><div class="text-en">{en_text}</div></div>'
                elif ka_text:
                    return f'<div class="text-ka">{ka_text}</div>'
                elif en_text:
                    return f'<div class="text-en">{en_text}</div>'
                elif default_text:
                    return default_text
                else:
                    # Return first available language
                    for lang, text in text_data.items():
                        if text:
                            return f'<div class="text-{lang}">{text}</div>'

            return str(text_data) if text_data else fallback
        except Exception:
            return fallback

    def get_display_title(self, title_data):
        """Get display title, preferring English for links, Georgian for display"""
        try:
            if isinstance(title_data, dict):
                # For display, prefer Georgian, then English, then default
                return title_data.get('ka') or title_data.get('en') or title_data.get('default') or "Untitled"
            return str(title_data) if title_data else "Untitled"
        except Exception:
            return "Untitled"

    def format_material_display(self, materials):
        """Format material for display with links"""
        try:
            if isinstance(materials, str):
                return materials

            if isinstance(materials, list) and materials:
                formatted_materials = []
                for material in materials:
                    if isinstance(material, dict):
                        text = material.get('text', '')
                        ref = material.get('ref', '')
                        lang = material.get('lang', '')

                        if ref:
                            formatted_materials.append(f'<a href="{ref}" target="_blank" title="EAGLE vocabulary ({lang})">{text}</a>')
                        else:
                            formatted_materials.append(text)
                    else:
                        formatted_materials.append(str(material))

                return ' / '.join(formatted_materials)

            return str(materials)
        except Exception:
            return str(materials) if materials else ""

    def format_object_type_display(self, object_types):
        """Format object type for display with links"""
        try:
            if isinstance(object_types, str):
                return object_types

            if isinstance(object_types, list) and object_types:
                formatted_types = []
                for obj_type in object_types:
                    if isinstance(obj_type, dict):
                        text = obj_type.get('text', '')
                        ref = obj_type.get('ref', '')
                        lang = obj_type.get('lang', '')

                        if ref:
                            formatted_types.append(f'<a href="{ref}" target="_blank" title="EAGLE vocabulary ({lang})">{text}</a>')
                        else:
                            formatted_types.append(text)
                    else:
                        formatted_types.append(str(obj_type))

                return ' / '.join(formatted_types)

            return str(object_types)
        except Exception:
            return str(object_types) if object_types else ""
        """Format material for display with links"""
        try:
            if isinstance(materials, str):
                return materials

            if isinstance(materials, list) and materials:
                formatted_materials = []
                for material in materials:
                    if isinstance(material, dict):
                        text = material.get('text', '')
                        ref = material.get('ref', '')
                        lang = material.get('lang', '')

                        if ref:
                            formatted_materials.append(f'<a href="{ref}" target="_blank" title="EAGLE vocabulary ({lang})">{text}</a>')
                        else:
                            formatted_materials.append(text)
                    else:
                        formatted_materials.append(str(material))

                return ' / '.join(formatted_materials)

            return str(materials)
        except Exception:
            return str(materials) if materials else ""

    def format_object_type_display(self, object_types):
        """Format object type for display with links"""
        try:
            if isinstance(object_types, str):
                return object_types

            if isinstance(object_types, list) and object_types:
                formatted_types = []
                for obj_type in object_types:
                    if isinstance(obj_type, dict):
                        text = obj_type.get('text', '')
                        ref = obj_type.get('ref', '')
                        lang = obj_type.get('lang', '')

                        if ref:
                            formatted_types.append(f'<a href="{ref}" target="_blank" title="EAGLE vocabulary ({lang})">{text}</a>')
                        else:
                            formatted_types.append(text)
                    else:
                        formatted_types.append(str(obj_type))

                return ' / '.join(formatted_types)

            return str(object_types)
        except Exception:
            return str(object_types) if object_types else ""

    def safe_format_text_editions(self, text_content, primary_language="ka"):
        """Safely format text editions with academic styling"""
        try:
            if not text_content:
                return '<div class="no-text-content"><p>No text content available.</p></div>'

            html_parts = []
            for key, edition in text_content.items():
                # Determine language and script attributes
                lang = edition.get('language', primary_language)
                subtype = edition.get('subtype', 'default')

                # Apply appropriate classes and attributes
                edition_classes = ["text-edition"]
                lang_attr = ""

                if lang == 'ka':
                    lang_attr = 'lang="ka"'
                    if 'mtavruli' in key.lower() or subtype == 'mtavruli':
                        edition_classes.append("mtavruli-edition")
                    elif 'diplomatic' in key.lower():
                        edition_classes.append("diplomatic-edition")

                edition_class_str = ' '.join(edition_classes)

                html_parts.append(f"""
                    <div class="{edition_class_str}" {lang_attr}>
                        <div class="edition-content">{edition['content']}</div>
                    </div>
                """)

            return ''.join(html_parts) if html_parts else '<div class="no-text-content"><p>No text editions available.</p></div>'
        except Exception:
            return '<div class="no-text-content"><p>Error displaying text content.</p></div>'


    # ღია არის თანამედროვე მინიმალისტური რუქა ენის ფერებით - დაიწყება
    def create_index_page(self):
        """Create homepage with modern minimalist map - using external JavaScript"""
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
                <a href="index.html" class="brand">ECG</a>
                <div class="nav-links">
                    <a href="browse.html">წარწერები</a>
                    <a href="persons.html">პირები</a>
                    <a href="bibliography.html">ბიბლიოგრაფია</a>
                </div>
            </div>
        </nav>

        <main class="container">


            <div class="hero">
                <h1>საქართველოს ეპიგრაფიკული კორპუსი</h1> <h1>Epigraphic Corpus of Georgia</h1>
                <p>Digital edition of ancient and medieval inscriptions from Georgia and the Caucasus</p>
            </div>

            <div class="map-container">
                <div class="map-legend">
                    <iframe width='100%' height='400px' src="https://api.mapbox.com/styles/v1/tamarae24/cmb4m3t5a00k901s9gk68b53y.html?title=false&access_token=pk.eyJ1IjoidGFtYXJhZTI0IiwiYSI6ImNtYjB0czAwdDB2OGcybXNoejI2eGp6cTYifQ.AesnE6yuzOEmJIBIWSH6ag&zoomwheel=false#5/41.34/41.76" title="ECG" style="border:none;"></iframe>
                </div>
            </div>

            <div class="recent-inscriptions">
                <h2>ბოლოს დამატებული | Recent Inscriptions</h2>
                <div class="inscription-grid">
                    {self.format_inscription_cards(self.inscriptions[:8])}
                </div>
                <div class="view-all">
                    <a href="browse.html" class="btn">»</a>
                </div>
            </div>
        </main>


    </body>
    </html>"""

            with open(f"{self.output_dir}/index.html", 'w', encoding='utf-8') as f:
                f.write(html)

            print("🏠 Clean homepage created with external map handler!")

        except Exception as e:
            print(f"❌ Error creating index page: {e}")


        # Additional method to enhance map data generation with language information
        def generate_enhanced_map_data(self):
            """Generate map data with enhanced language detection"""
            try:
                print("🗺️  Generating enhanced map data with language information...")

                # Load place names with coordinates
                place_names = self.load_place_names_from_file()
                coordinates_map = self.create_coordinates_mapping()

                print(f"📍 Coordinates map has {len(coordinates_map)} entries")

                map_data = []

                # Count inscriptions per place
                place_counts = {}
                for inscription in self.inscriptions:
                    place = inscription['origin'].get('place', '').strip()
                    if place:
                        if place not in place_counts:
                            place_counts[place] = []
                        place_counts[place].append(inscription)

                print(f"📍 Found {len(place_counts)} unique places in inscriptions")

                # Create map markers with enhanced language data
                for place, inscriptions_list in place_counts.items():
                    coords = self.find_coordinates(place, coordinates_map)

                    if coords.get('lat') is not None and coords.get('lon') is not None:
                        lat, lon = float(coords['lat']), float(coords['lon'])

                        # Validate coordinates are reasonable
                        if 35 <= lat <= 50 and 35 <= lon <= 50:
                            # Enhanced inscription data with language information
                            enhanced_inscriptions = []
                            for insc in inscriptions_list:
                                enhanced_inscriptions.append({
                                    'id': insc['id'],
                                    'title': self.get_display_title(insc['title']),
                                    'language': insc.get('language', 'unknown'),
                                    'url': f'inscriptions/{insc["id"]}.html'
                                })

                            map_data.append({
                                'place': place,
                                'lat': lat,
                                'lon': lon,
                                'count': len(inscriptions_list),
                                'inscriptions': enhanced_inscriptions
                            })

                # Save enhanced map data
                with open(f"{self.output_dir}/map-data.json", 'w', encoding='utf-8') as f:
                    json.dump(map_data, f, ensure_ascii=False, indent=2)

                print(f"🗺️  Generated enhanced map data for {len(map_data)} locations")
                return map_data

            except Exception as e:
                print(f"❌ Error generating enhanced map data: {e}")
                return []



    # ღია არის თანამედროვე მინიმალისტური რუქა ენის ფერებით - დასრულება

    def create_browse_page_vanilla(self):
        """Create browse page with clean list view using homepage-style indicators"""
        try:
            # Add debugging to see what's happening
            print(f"🔍 DEBUG: Creating browse page with {len(self.inscriptions)} inscriptions")

            # Check if we have inscriptions
            if not self.inscriptions:
                print("❌ No inscriptions found when creating browse page!")
                inscriptions_html = "<p>No inscriptions available.</p>"
            else:
                print(f"✅ Processing {len(self.inscriptions)} inscriptions for browse page")
                inscriptions_html = self.format_clean_inscription_list(self.inscriptions)
                print(f"✅ Generated HTML length: {len(inscriptions_html)} characters")

            html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Browse - ECG</title>
        <link rel="stylesheet" href="static/css/style.css">
    </head>
    <body>
        <nav class="navbar">
            <div class="container">
                <a href="index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
                <div class="nav-links">
                    <a href="index.html">საწყისი</a>
                    <a href="browse.html">წარწერები</a>
                    <a href="persons.html">პირები</a>
                    <a href="bibliography.html">ბიბლიოგრაფია</a>
                </div>
            </div>
        </nav>

        <main class="container">
            <div class="browse-header">
                <h1>საქართველოს ეპიგრაფიკული კორპუსი</h1>
                <p class="browse-subtitle">ანტიკური და შუასაუკუნეების {len(self.inscriptions)} წარწერის ციფრული გამოცემა</p>

                <div class="browse-controls">
                    <div class="search-box">
                        <input type="text" id="searchInput" placeholder="ძიება..." class="search-input">
                    </div>
                    <div class="filters">
                        <select id="languageFilter" class="filter-select">
                            <option value="">ენა</option>
                            <option value="ka">ქართული</option>
                            <option value="grc">ბერძნული</option>
                            <option value="hy">სომხური</option>
                            <option value="unknown">სხვა</option>
                        </select>
                        <select id="sortSelect" class="filter-select">
                            <option value="id">დალაგება</option>
                            <option value="title">სათაური</option>
                            <option value="place">ადგილი</option>
                            <option value="date">თარიღი</option>
                            <option value="language">ენა</option>
                        </select>
                    </div>
                </div>
            </div>

            <div class="browse-content">
                <div id="inscriptionList" class="clean-inscription-list">
                    {inscriptions_html}
                </div>
            </div>
        </main>

        <script src="static/js/browse.js"></script>
    </body>
    </html>"""

            with open(f"{self.output_dir}/browse.html", 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"📄 Browse page created successfully with {len(self.inscriptions)} inscriptions")

        except Exception as e:
            print(f"❌ Error creating browse page: {e}")
            import traceback
            traceback.print_exc()


    def create_bibliography_page(self):
        """Create bibliography page"""
        try:
            if not self.bibliography:
                print("⚠️  No bibliography entries to display")
                return

            # Sort bibliography entries alphabetically by abbreviation or author
            sorted_entries = sorted(self.bibliography.values(), key=lambda x:
                x.get('abbrev', x['structured'].get('author', x['structured'].get('title', x['id']))).lower())

            bibliography_html = ""
            for entry in sorted_entries:
                structured = entry['structured']
                abbrev = entry.get('abbrev', '')
                author = structured.get('author', '')
                title = structured.get('title', '')
                date = structured.get('date', '')
                publisher = structured.get('publisher', '')

                # Format the entry - use abbreviation if available, otherwise build from structured data
                formatted_entry = ""
                if abbrev:
                    formatted_entry = f"<strong>{abbrev}</strong><br>"

                entry_parts = []
                if author:
                    entry_parts.append(f"<span class=\"author\">{author}</span>")
                if title:
                    entry_parts.append(f"<em>{title}</em>")
                if publisher:
                    entry_parts.append(f"{publisher}")
                if date:
                    entry_parts.append(f"{date}")

                if entry_parts:
                    content_text = ". ".join(entry_parts) + "."
                    formatted_entry = formatted_entry + content_text

                # If structured formatting failed, use the raw content
                if not formatted_entry.strip() or formatted_entry == f"<strong>{abbrev}</strong><br>":
                    content_text = entry['content'] if abbrev else entry['content']
                    formatted_entry = (f"<strong>{abbrev}</strong><br>" if abbrev else "") + content_text

                # Add back-references to inscriptions that cite this entry
                cited_by_html = ""
                if 'cited_by' in entry and entry['cited_by']:
                    cited_links = []
                    for inscription_ref in entry['cited_by']:
                        link_text = inscription_ref['title']
                        if inscription_ref.get('cited_range'):
                            link_text += f" ({inscription_ref['cited_range']})"
                        cited_links.append(f'<a href="inscriptions/{inscription_ref["id"]}.html">{link_text}</a>')

                    cited_by_html = f'''
                        <div class="cited-by">
                            <strong>Cited by:</strong> {', '.join(cited_links)}
                        </div>
                    '''

                bibliography_html += f'''
                    <div class="bibliography-entry" id="{entry['id']}">
                        <div class="bib-content">{formatted_entry}</div>
                        {cited_by_html}
                        <div class="bib-id">ID: {entry['id']}</div>
                    </div>
                '''

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bibliography - ECG</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="brand">ECG - Epigraphic Corpus of Georgia</a>
            <div class="nav-links">
                <a href="index.html">საწყისი</a>
                <a href="browse.html">წარწერები</a>
                <a href="persons.html">პირები</a>
                <a href="bibliography.html">ბიბლიოგრაფია</a>
            </div>
        </div>
    </nav>

    <main class="container">
        <div class="page-header">
            <h1>Bibliography</h1>
            <p>Complete bibliography for the Epigraphic Corpus of Georgia ({len(self.bibliography)} entries)</p>
        </div>

        <div class="bibliography-search">
            <input type="text" id="bibliographySearch" placeholder="Search bibliography..." class="search-input">
        </div>

        <div class="bibliography-list" id="bibliographyList">
            {bibliography_html}
        </div>
    </main>

    <script src="static/js/bibliography.js"></script>
</body>
</html>"""

            with open(f"{self.output_dir}/bibliography.html", 'w', encoding='utf-8') as f:
                f.write(html)

        except Exception as e:
            print(f"❌ Error creating bibliography page: {e}")


    def format_inscription_cards(self, inscriptions):
        """Format inscription cards with consistent language indicators"""
        try:
            cards = []
            for inscription in inscriptions:
                place_span = ""
                if inscription['origin'].get('place'):
                    place_span = f'<span class="place">📍 {inscription["origin"]["place"]}</span>'

                date_span = ""
                if inscription['dating'].get('text'):
                    date_span = f'<span class="date">📅 {inscription["dating"]["text"]}</span>'

                # Add image indicator
                image_indicator = ""
                if inscription['images']:
                    image_indicator = f'<span class="has-images">📷 {len(inscription["images"])}</span>'

                # Language indicator - keep homepage style (simple gray background)
                language_code = inscription.get('language', 'unknown')

                cards.append(f"""
                    <div class="inscription-card" data-id="{inscription['id']}" data-title="{self.get_display_title(inscription['title']).lower()}" data-language="{inscription['language']}">
                        <h3><a href="inscriptions/{inscription['id']}.html">{self.get_display_title(inscription['title'])}</a></h3>
                        <div class="inscription-meta">
                            <span class="id">№ {inscription['id']}</span>
                            {place_span}
                            {date_span}
                            <span class="lang">{language_code}</span>
                            {image_indicator}
                        </div>
                    </div>
                """)
            return ''.join(cards)
        except Exception as e:
            print(f"❌ Error formatting cards: {e}")
            return "<p>Error displaying inscriptions</p>"


    def format_clean_inscription_list(self, inscriptions):
        """Format inscriptions as a clean list with homepage-style indicators"""
        try:
            print(f"🔍 DEBUG: Formatting {len(inscriptions)} inscriptions for clean list")

            if not inscriptions:
                return "<p>No inscriptions available to display.</p>"

            list_items = []
            for i, inscription in enumerate(inscriptions):
                # Debug first few inscriptions
                if i < 3:
                    print(f"🔍 Debug: Processing inscription {inscription.get('id', 'NO_ID')}")

                # Get display information safely
                title = self.get_display_title(inscription.get('title', {}))
                place = inscription.get('origin', {}).get('place', 'Unknown location')
                date = inscription.get('dating', {}).get('text', 'Unknown date')

                # Language indicator - UPDATED to match homepage style with language codes (no colored backgrounds)
                language_code = inscription.get('language', 'unknown')
                language_display = language_code  # Just show the language code as-is

                # Create summary if available
                summary = ""
                if inscription.get('summary'):
                    summary_text = self.get_display_title(inscription['summary'])
                    if summary_text:
                        # Detect if summary contains Georgian text
                        has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in summary_text)
                        summary_class = 'georgian-text' if has_georgian else ''
                        summary = f'<div class="inscription-summary {summary_class}">{summary_text[:200]}{"..." if len(summary_text) > 200 else ""}</div>'

                # Image indicator - homepage style
                image_indicator = ""
                if inscription.get('images'):
                    image_indicator = f'<span class="indicator has-images" title="{len(inscription["images"])} images">📷 {len(inscription["images"])}</span>'

                # Material and object type as indicators
                additional_indicators = []
                if inscription.get('material'):
                    material_display = self.format_material_display(inscription['material'])
                    if material_display:
                        # Check for Georgian text in material
                        has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in material_display)
                        material_class = 'georgian-indicator' if has_georgian else ''
                        additional_indicators.append(f'<span class="indicator material-indicator {material_class}" title="Material">🔨 {material_display}</span>')

                if inscription.get('object_type'):
                    object_display = self.format_object_type_display(inscription['object_type'])
                    if object_display:
                        # Check for Georgian text in object type
                        has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in object_display)
                        object_class = 'georgian-indicator' if has_georgian else ''
                        additional_indicators.append(f'<span class="indicator object-indicator {object_class}" title="Object Type">📦 {object_display}</span>')

                # Check if title contains Georgian text
                title_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in title)
                title_class = 'georgian-text' if title_has_georgian else ''

                # Check if place contains Georgian text
                place_has_georgian = any(ord(c) >= 0x10A0 and ord(c) <= 0x10FF for c in place)
                place_class = 'georgian-text' if place_has_georgian else ''

                list_items.append(f"""
                    <div class="clean-inscription-item" data-id="{inscription.get('id', '')}" data-title="{title.lower()}"
                         data-language="{inscription.get('language', '')}" data-place="{place.lower()}" data-date="{date.lower()}">
                        <div class="inscription-header">
                            <div class="inscription-title-section">
                                <h3 class="inscription-title {title_class}">
                                    <a href="inscriptions/{inscription.get('id', '')}.html">{title}</a>
                                </h3>
                                <span class="inscription-id">№ {inscription.get('id', '')}</span>
                            </div>
                        </div>

                        <div class="inscription-indicators">
                            <span class="indicator language-indicator">{language_display}</span>
                            <span class="indicator place-indicator {place_class}" title="Location">📍 {place}</span>
                            <span class="indicator date-indicator" title="Dating">📅 {date}</span>
                            {image_indicator}
                            {' '.join(additional_indicators)}
                        </div>

                        {summary}
                    </div>
                """)

            result = ''.join(list_items)
            print(f"✅ Formatted {len(list_items)} inscription items, HTML length: {len(result)}")
            return result

        except Exception as e:
            print(f"❌ Error formatting clean inscription list: {e}")
            import traceback
            traceback.print_exc()
            return f"<p>Error displaying inscriptions: {e}</p>"


    def create_search_data(self):
        """Create JSON search data"""
        try:
            search_data = []
            for inscription in self.inscriptions:
                search_data.append({
                    'id': inscription['id'],
                    'title': self.get_display_title(inscription['title']),
                    'summary': self.get_display_title(inscription['summary']) if inscription['summary'] else '',
                    'place': inscription['origin'].get('place', ''),
                    'date': inscription['dating'].get('text', ''),
                    'language': inscription['language'],
                    'has_images': len(inscription['images']) > 0,
                    'image_count': len(inscription['images']),
                    'url': f"inscriptions/{inscription['id']}.html"
                })

            with open(f"{self.output_dir}/search-data.json", 'w', encoding='utf-8') as f:
                json.dump(search_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error creating search data: {e}")


    def create_css_vanilla(self):
        """Create modern minimalist CSS with better font loading"""
        css = """/* Modern Minimalist ECG Design with Robust Font Loading */

    /* CSS Variables for Georgian fonts with fallbacks */
    :root {
        --primary-georgian-font: 'BPG Nino', 'Sylfaen', 'DejaVu Sans', 'Arial Unicode MS', sans-serif;
        --mtavruli-font: 'BPG Nino Mtavruli', 'BPG Banner', 'Sylfaen', 'DejaVu Sans', serif;
        --inscription-font: 'BPG Classic Medium', 'BPG Banner', 'Sylfaen', 'Times New Roman', serif;
        --metadata-font: 'BPG Arial', 'BPG DejaVu Sans', 'Sylfaen', 'Arial', sans-serif;
        --mixed-script-font: 'BPG Nino', 'Sylfaen', -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
    }

    /* Load fonts with better error handling */
    @font-face {
        font-family: 'BPG Nino';
        src: local('BPG Nino'), local('Sylfaen');
        font-display: swap; /* Better loading performance */
    }

    @font-face {
        font-family: 'BPG Nino Mtavruli';
        src: local('BPG Nino Mtavruli'), local('Sylfaen');
        font-display: swap;
    }

    * { box-sizing: border-box; }

    body {
        font-family: var(--mixed-script-font);
        line-height: 1.6;
        margin: 0;
        padding: 0;
        color: #1a1a1a;
        background: #ffffff;
        font-weight: 400;
    }

    /* Georgian text styling with robust fallbacks */
    [lang="ka"], .georgian, .text-ka, .georgian-text {
        font-family: var(--primary-georgian-font);
        font-feature-settings: "kern" 1, "liga" 1;
        text-rendering: optimizeLegibility;
    }

    /* Asomtavruli/Mtavruli inscriptions */
    [ana="mtavruli"], .mtavruli, .asomtavruli {
        font-family: var(--mtavruli-font);
        font-weight: bold;
        letter-spacing: 1.5px;
    }

    /* Mixed script handling for titles and metadata */
    .bilingual-text {
        font-family: var(--mixed-script-font);
    }

    .bilingual-text .text-ka {
        font-family: var(--primary-georgian-font);
        font-size: 1.1em;
        line-height: 1.4;
    }

    .bilingual-text .text-en {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
    }

    /* Inscription text editions */
    .edition-text {
        font-family: var(--inscription-font);
        font-size: 1.1em;
        line-height: 1.8;
        text-align: center;
    }

    .diplomatic {
        font-family: var(--mtavruli-font);
        letter-spacing: 2px;
    }

    /* Names in inscriptions */
    .edition-text strong, .edition-text name {
        color: #2980b9;
        font-weight: bold;
    }

    /* Title and Headers with Georgian fonts */
    h1, h2, h3, .hero h1, .inscription-card h3 {
        font-family: var(--mixed-script-font);
    }

    h1[lang="ka"], h2[lang="ka"], h3[lang="ka"],
    .title[lang="ka"], .text-ka h1, .text-ka h2, .text-ka h3 {
        font-family: var(--primary-georgian-font);
        font-weight: 600;
    }

    /* Translation section */
    .translation {
        font-family: var(--primary-georgian-font);
        font-size: 1.05em;
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 6px;
        border-left: 4px solid #28a745;
        text-align: center;
        font-style: italic;
    }

    /* Commentary section */
    .commentary {
        font-family: var(--metadata-font);
        font-size: 0.95em;
        line-height: 1.7;
        text-align: justify;
    }

    /* XML source formatting */
    .xml-content {
        font-family: 'Courier New', 'SF Mono', 'Monaco', monospace;
        font-size: 0.85em;
        line-height: 1.4;
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 6px;
        overflow-x: auto;
        border: 1px solid #e9ecef;
    }

    /* Metadata sections */
    .metadata dl {
        font-family: var(--metadata-font);
    }

    .metadata dt {
        font-weight: 600;
        color: #495057;
    }

    .metadata dd {
        margin-bottom: 0.75rem;
    }

    /* Inscription item titles in browse page */
    .inscription-item h3 a {
        font-family: var(--mixed-script-font);
        text-decoration: none;
        color: #1a1a1a;
    }

    .inscription-item h3 a[lang="ka"] {
        font-family: var(--primary-georgian-font);
        font-size: 1.1em;
    }

    /* Academic Overview Styles */
    .overview {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 2px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-family: 'Crimson Text', Georgia, var(--primary-georgian-font), serif;
        line-height: 1.7;
        color: #2c2c2c;
    }

    .summary {
        padding: 2rem 2.5rem;
        border-bottom: 1px solid #f0f0f0;
        background: linear-gradient(135deg, #fafbfc 0%, #ffffff 100%);
    }

    .summary h3 {
        font-family: var(--metadata-font);
        font-size: 1.1rem;
        font-weight: 600;
        color: #4a5568;
        margin: 0 0 1rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .summary-content {
        font-size: 1.05rem;
        color: #2d3748;
        font-style: italic;
    }

    /* Metadata Groups */
    .metadata-group {
        padding: 1.5rem 2.5rem;
        border-bottom: 1px solid #f5f5f5;
    }

    .metadata-group:last-child {
        border-bottom: none;
    }

    .metadata-group h4 {
        font-family: var(--metadata-font);
        font-size: 0.95rem;
        font-weight: 600;
        color: #4a5568;
        margin: 0 0 1.25rem 0;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }

    /* Inline Metadata Items */
    .meta-item {
        margin-bottom: 0.75rem;
        font-size: 1rem;
        line-height: 1.6;
    }

    .meta-label {
        font-weight: 600;
        color: #2d3748;
    }

    .meta-value {
        color: #4a5568;
        margin-left: 0.25rem;
    }

    /* Updated Bilingual Labels - Georgian bold, English light */
    .bilingual-label {
        font-weight: normal; /* Remove overall bold */
        color: #2d3748;
    }

    .bilingual-label .ka {
        font-family: var(--primary-georgian-font);
        color: #1a365d;
        font-weight: 600; /* Georgian labels bold */
    }

    .bilingual-label .en {
        color: #718096; /* Lighter gray for English */
        font-style: italic;
        font-size: 0.9em;
        font-weight: 400; /* English labels normal weight */
        opacity: 0.8; /* Make English even more subtle */
    }

    /* Special styling for long descriptions */
    .meta-description {
        margin-top: 0.5rem;
        padding: 1rem 1.25rem;
        background: #f7fafc;
        border-left: 3px solid #cbd5e0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #4a5568;
        border-radius: 0 4px 4px 0;
        font-family: var(--primary-georgian-font);
    }

    /* Links and references */
    .meta-link {
        color: #3182ce;
        text-decoration: none;
        border-bottom: 1px dotted #3182ce;
    }

    .meta-link:hover {
        color: #2c5282;
        border-bottom-style: solid;
    }

    /* Dimensions and measurements */
    .measurement {
        font-family: var(--metadata-font);
        font-size: 0.9em;
        color: #2d3748;
        background: #edf2f7;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-weight: 500;
    }

    /* Revision history */
    .revision-list {
        font-size: 0.9rem;
        color: #718096;
        margin-top: 0.5rem;
        font-family: var(--primary-georgian-font);
    }

    .revision-item {
        margin-bottom: 0.25rem;
        padding-left: 1rem;
        position: relative;
    }

    .revision-item::before {
        content: "•";
        position: absolute;
        left: 0;
        color: #cbd5e0;
    }

    /* REST OF YOUR EXISTING CSS CONTINUES HERE... */

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1.5rem;
    }

    /* Navigation */
    .navbar {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid #f0f0f0;
        padding: 1rem 0;
        position: sticky;
        top: 0;
        z-index: 100;
    }

    .navbar .container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .brand {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        text-decoration: none;
        letter-spacing: -0.02em;
    }

    .nav-links {
        display: flex;
        gap: 2rem;
    }

    .nav-links a {
        color: #666;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.95rem;
        transition: color 0.2s ease;
    }

    .nav-links a:hover {
        color: #1a1a1a;
    }

    /* Hero */
    main { padding: 0; }

    .hero {
        text-align: center;
        padding: 4rem 0 3rem;
        background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
    }

    .hero h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #1a1a1a;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }

    .hero p {
        font-size: 1.25rem;
        color: #666;
        margin-bottom: 2.5rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }

    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 2rem;
    }

    .stat {
        text-align: center;
    }

    .stat strong {
        display: block;
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }

    .stat span {
        color: #888;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }



    /* Recent inscriptions */
    .recent-inscriptions {
       padding: 4rem 1.5rem;
       background: #fafafa;
    }

    .recent-inscriptions h2 {
       text-align: center;
       font-size: 2rem;
       font-weight: 600;
       margin-bottom: 2.5rem;
       color: #1a1a1a;
    }

    .inscription-grid {
       display: grid;
       grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
       gap: 1.5rem;
       margin-bottom: 2.5rem;
    }

    .inscription-card {
       background: white;
       border-radius: 8px;
       padding: 1.5rem;
       box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
       border: 1px solid #f0f0f0;
       transition: all 0.2s ease;
    }

    .inscription-card:hover {
       transform: translateY(-2px);
       box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }

    .inscription-card h3 {
       margin: 0 0 1rem 0;
       font-size: 1rem;
       font-weight: 600;
    }

    .inscription-card a {
       color: #1a1a1a;
       text-decoration: none;
    }

    .inscription-card a:hover {
       color: #1565C0;
    }

    .inscription-meta {
       display: flex;
       flex-wrap: wrap;
       gap: 0.5rem;
       font-size: 0.8rem;
    }

    .inscription-meta span {
        background: #f5f5f5;
        color: #666;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: 500;
        font-size: 0.8rem;
    }

    /* Button */
    .view-all {
       text-align: center;
    }

    .btn {
       display: inline-block;
       background: #f5f5f5
       color: white;
       padding: 0.875rem 2rem;
       text-decoration: none;
       border-radius: 6px;
       font-weight: 500;
       transition: all 0.2s ease;
    }

    .btn:hover {
       background: #333;
       transform: translateY(-1px);
    }

    /* Mapbox overrides */
    .mapboxgl-popup-content {
       padding: 0 !important;
       border-radius: 8px !important;
       box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12) !important;
    }

    /* Mobile */
    @media (max-width: 768px) {
       .hero h1 { font-size: 2.5rem; }
       .hero-stats { flex-direction: column; gap: 1.5rem; }
       .map-legend { position: static; margin-bottom: 1rem; flex-direction: row; flex-wrap: wrap; }
       #inscriptions-map { height: 400px; }
       .inscription-grid { grid-template-columns: 1fr; }

       /* Academic overview mobile adjustments */
       .metadata-group {
           padding: 1.25rem 1.5rem;
       }

       .summary {
           padding: 1.5rem 2rem;
       }

       .meta-item {
           font-size: 0.95rem;
       }

       .bilingual-label .ka,
       .bilingual-label .en {
           display: block;
           margin-bottom: 0.25rem;
       }
    }

    /* Navigation tabs, browse page, and other existing styles */
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
       transition: all 0.3s;
    }

    .tabs button.active {
       border-bottom-color: #1565C0;
       color: #1565C0;
       font-weight: 600;
    }

    .tab-content {
       display: none;
       padding: 1rem 0;
    }

    .tab-content.active {
       display: block;
    }

    /* Browse page */
    .browse-header {
       margin-bottom: 2rem;
       text-align: center;
    }

    .search-input {
       width: 100%;
       max-width: 400px;
       padding: 0.75rem;
       border: 1px solid #ddd;
       border-radius: 6px;
       font-size: 1rem;
    }

    .inscription-list {
       max-width: 900px;
       margin: 0 auto;
    }

    .inscription-item {
       border-bottom: 1px solid #f0f0f0;
       padding: 1.5rem 0;
       transition: background-color 0.2s ease;
    }

    .inscription-item:hover {
       background-color: #fafafa;
    }

    /* Bibliography page */
    .bibliography-entry {
       margin-bottom: 1.5rem;
       padding: 1.5rem;
       background: white;
       border: 1px solid #f0f0f0;
       border-radius: 8px;
       font-family: var(--metadata-font);
    }

    /* Updated EpiDoc Line Formatting Styles */

    /* Edition text with proper line formatting */
    .epidoc-lines {
        font-family: var(--inscription-font);
        font-size: 0.9em;
        line-height: 1.8;
        text-align: left;
        padding: 2rem;
        background: #fafafa;
        border-left: 1px solid #2980b9;
        margin: 1rem 0;
    }

    .diplomatic .epidoc-lines {
        font-family: var(--mtavruli-font);
        letter-spacing: 2px;
        border-left-color: #1565C0;
    }

    /* Individual edition lines */
    .edition-line {
        display: block;
        margin: 0.4rem 0;
        min-height: 1.2em;
        position: relative;
        padding-left: 0;
    }

    /* Numbered lines (every 5th line) */
    .edition-line.numbered {
        margin: 0.6rem 0;
        font-weight: 500;
    }

    /* Line numbers - only show for every 5th line */
    .line-number.major {
        display: inline-block;
        min-width: 2.5em;
        text-align: right;
        color: #333;
        font-size: 0.9em;
        font-weight: 700;
        margin-right: 1em;
        font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        vertical-align: baseline;
        background: #e8f5e8;
        padding: 0.2em 0.4em;
        border-radius: 3px;
    }

    /* Line break styling for visual separation */
    .edition-line::after {
        content: "";
        position: absolute;
        right: -1rem;
        top: 50%;
        height: 1px;
        width: 0.5rem;
        background: #ddd;
        opacity: 0.3;
    }

    .edition-line.numbered::after {
        background: #2E7D32;
        opacity: 0.5;
        width: 1rem;
    }

    /* Names and entities styling within lines */
    .edition-line strong {
        color: #2980b9;
        font-weight: 600;
    }

    /* Abbreviations and expansions */
    .edition-line .abbr {
        border-bottom: 1px dotted #666;
    }

    .edition-line .expansion {
        font-style: italic;
        color: #666;
        font-size: 0.95em;
    }

    /* Tooltips for lemmas and references */
    .edition-line [title] {
        cursor: help;
        border-bottom: 1px dotted #999;
    }

    /* External links within inscriptions */
    .edition-line .external-link {
        color: #1565C0;
        text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: border-color 0.2s ease;
    }

    .edition-line .external-link:hover {
        border-bottom-color: #1565C0;
    }

    /* Diplomatic edition specific styles */
    .diplomatic .edition-line {
        letter-spacing: 1px;
    }

    .diplomatic .line-number.major {
        background: #e3f2fd;
    }

    .diplomatic .edition-line.numbered::after {
        background: #1565C0;
    }

    /* Responsive line formatting */
    @media (max-width: 768px) {
        .epidoc-lines {
            font-size: 1.1em;
            padding: 1.5rem 1rem;
            line-height: 1.6;
        }

        .line-number.major {
            min-width: 2em;
            font-size: 0.8em;
            margin-right: 0.75em;
        }

        .edition-line::after {
            right: -0.5rem;
            width: 0.3rem;
        }
    }

    /* Print styles for academic papers */
    @media print {
        .epidoc-lines {
            background: none;
            border: 1px solid #333;
            font-size: 11pt;
            line-height: 1.6;
        }

        .line-number.major {
            font-size: 9pt;
            background: none;
            border: 1px solid #333;
        }

        .edition-line .external-link {
            color: #000;
            text-decoration: underline;
        }

        .edition-line::after {
            display: none;
        }
    }
    /* Add these comprehensive font fixes to your CSS */

/* Global font consistency - ensure all text uses mixed-script font by default */
body, html {
    font-family: var(--mixed-script-font);
}

/* Navigation and brand - support Georgian */
.navbar, .nav-links, .brand {
    font-family: var(--mixed-script-font);
}

.brand {
    font-family: var(--primary-georgian-font); /* Brand can be Georgian */
}

/* Page titles and main headings */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--mixed-script-font);
}

/* Inscription page title */
.inscription-header h1 {
    font-family: var(--primary-georgian-font);
}

/* Tab buttons - crucial fix */
.tabs button {
    font-family: var(--mixed-script-font);
    font-weight: 500;
}

.tabs button .ka {
    font-family: var(--primary-georgian-font);
    font-weight: 600;
}

.tabs button .en {
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
    font-weight: 400;
    opacity: 0.8;
}

/* Tab content headers */
.tab-content h3, .tab-content h4 {
    font-family: var(--mixed-script-font);
}

/* Hero section */
.hero h1, .hero p {
    font-family: var(--mixed-script-font);
}

/* Inscription cards */
.inscription-card, .inscription-card h3, .inscription-card a {
    font-family: var(--mixed-script-font);
}

/* Browse page elements */
.browse-header h1 {
    font-family: var(--mixed-script-font);
}

.search-input, .filters select {
    font-family: var(--mixed-script-font);
}

/* Inscription list items */
.inscription-item h3, .inscription-item h3 a {
    font-family: var(--mixed-script-font);
}

/* Metadata in inscription meta */
.inscription-meta, .inscription-metadata {
    font-family: var(--mixed-script-font);
}

/* Bibliography page */
.bibliography-entry, .bib-content {
    font-family: var(--mixed-script-font);
}

/* Buttons */
.btn, button, input[type="submit"] {
    font-family: var(--mixed-script-font);
}

/* Form elements */
input, select, textarea {
    font-family: var(--mixed-script-font);
}

/* Map popup elements */
.popup-header h3, .popup-inscription {
    font-family: var(--mixed-script-font);
}

/* Stats and numbers */
.hero-stats, .stat {
    font-family: var(--mixed-script-font);
}

/* Specific Georgian text elements */
.georgian-text, [lang="ka"], .text-ka {
    font-family: var(--primary-georgian-font) !important;
}

/* English text elements */
.text-en, [lang="en"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif !important;
}

/* Mixed bilingual elements */
.bilingual-text {
    font-family: var(--mixed-script-font);
}

/* Ensure consistent spacing in mixed text */
.ka + .en::before {
    content: " ";
    white-space: pre;
}

/* Page headers across all pages */
.page-header h1, .browse-header h1 {
    font-family: var(--mixed-script-font);
}

/* Footer elements if you add them */
footer, .footer {
    font-family: var(--mixed-script-font);
}

/* All links */
a {
    font-family: inherit; /* Inherit from parent */
}

/* Ensure all text inputs use consistent fonts */
input[type="text"], input[type="search"], textarea, select {
    font-family: var(--mixed-script-font);
}

/* Error and status messages */
.error, .success, .warning, .info {
    font-family: var(--mixed-script-font);
}

/* Tooltips and small text */
.tooltip, small, .small-text {
    font-family: var(--mixed-script-font);
    font-size: 0.9em;
}

/* Specific fix for any remaining inconsistencies */
* {
    font-family: inherit;
}

/* Override any remaining system defaults */
body * {
    font-family: var(--mixed-script-font);
}

/* But preserve special cases */
.georgian-text, [lang="ka"], .text-ka,
.bilingual-label .ka, .summary-content,
.meta-description, .revision-list {
    font-family: var(--primary-georgian-font) !important;
}

.edition-text {
    font-family: var(--inscription-font) !important;
}

.diplomatic {
    font-family: var(--mtavruli-font) !important;
}

.xml-content, code, pre {
    font-family: 'Courier New', 'SF Mono', 'Monaco', monospace !important;
}/* Bibliography Section - Matching Academic Overview Style */
.bibliography-section {
    /* Remove the inconsistent box styling */
    margin-top: 0;
    padding: 0;
    background: none;
    border-radius: 0;
    border-left: none;
}

/* Style as a metadata group to match overview */
.linked-bibliography {
    padding: 1.5rem 2.5rem;
    border-bottom: 1px solid #f5f5f5;
    margin: 0;
    border-top: 1px solid #f5f5f5; /* Add top border to separate */
}

.linked-bibliography h4 {
    font-family: var(--metadata-font);
    font-size: 0.95rem;
    font-weight: 600;
    color: #4a5568;
    margin: 0 0 1.25rem 0;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
}

.linked-bibliography h4 .ka {
    font-family: var(--primary-georgian-font);
    color: #1a365d;
    font-weight: 600;
}

.linked-bibliography h4 .en {
    color: #718096;
    font-style: italic;
    font-size: 0.9em;
    font-weight: 400;
    opacity: 0.8;
}

.bibliography-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.bibliography-list li {
    margin-bottom: 0.75rem;
    font-size: 1rem;
    line-height: 1.6;
    padding: 0;
    position: relative;
}

/* Remove the bullet points for cleaner academic look */
.bibliography-list li::before {
    display: none;
}

/* Georgian bibliography items */
.georgian-bibliography {
    font-family: var(--primary-georgian-font) !important;
    font-size: 1rem;
    color: #4a5568;
}

/* Regular bibliography items */
.bibliography-item {
    font-family: var(--mixed-script-font);
    color: #4a5568;
}

/* Bibliography links - academic style */
.bib-ref {
    color: #3182ce;
    text-decoration: none;
    font-family: inherit;
    display: block;
    padding: 0.5rem 0;
    border-bottom: 1px dotted transparent;
    transition: all 0.2s ease;
}

.bib-ref:hover {
    color: #2c5282;
    border-bottom-color: #3182ce;
    background: rgba(49, 130, 206, 0.03);
    padding-left: 0.5rem;
}

/* Responsive bibliography matching overview */
@media (max-width: 768px) {
    .linked-bibliography {
        padding: 1.25rem 1.5rem;
    }

    .bibliography-list li {
        font-size: 0.95rem;
    }

    .georgian-bibliography {
        font-size: 0.95rem;
    }
}/* Academic Text Edition Styles - Clean, Professional, No Color Coding */

/* Main text editions container */
.text-editions {
    background: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 2px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin: 1rem 0;
}

/* Edition container for interpretive/diplomatic sections */
.edition-container {
    /* Remove any previous colorful styling */
}

/* Individual edition sections */
.interpretive-edition,
.diplomatic-edition {
    padding: 2rem 2.5rem;
    border-bottom: 1px solid #f0f0f0;
}

.diplomatic-edition {
    border-bottom: none; /* Last section doesn't need bottom border */
}

/* Edition titles with bilingual styling */
.edition-title {
    font-family: var(--metadata-font);
    font-size: 1rem;
    font-weight: 600;
    color: #4a5568;
    margin: 0 0 1.5rem 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
}

/* Bilingual edition titles - matching overview section */
.edition-title.bilingual-label {
    font-weight: normal; /* Remove overall bold */
    text-transform: none; /* Remove uppercase for bilingual titles */
}

.edition-title.bilingual-label .ka {
    font-family: var(--primary-georgian-font);
    color: #1a365d;
    font-weight: 600; /* Georgian bold */
}

.edition-title.bilingual-label .en {
    color: #718096; /* Lighter gray for English */
    font-style: italic;
    font-size: 0.9em;
    font-weight: 400; /* English normal weight */
    opacity: 0.8; /* Make English even more subtle */
}

/* Academic edition text - clean, scholarly presentation */
.academic-edition {
    font-family: var(--inscription-font);
    font-size: 1em;
    line-height: 2;
    color: #2c2c2c;
    text-align: left;
    padding: 0;
    background: none;
    border: none;
    margin: 0;
}

/* Diplomatic text styling */
.diplomatic-text {
    font-family: var(--mtavruli-font);
    letter-spacing: 1px;
    font-weight: normal;
}

/* Individual edition lines - clean academic layout */
.edition-line {
    display: flex;
    align-items: baseline;
    margin: 0.8rem 0;
    min-height: 1.5em;
    position: relative;
}

/* Line with number */
.numbered-line {
    margin: 1rem 0;
}

/* Line numbers - small, external, neutral */
.line-number {
    display: inline-block;
    min-width: 2em;
    text-align: right;
    color: #666;
    font-size: 0.75em;
    font-weight: 500;
    margin-right: 1.5em;
    font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    flex-shrink: 0;
    /* Remove all background colors and styling */
    background: none;
    border: none;
    padding: 0;
}

/* Line content */
.line-content {
    flex: 1;
    line-height: inherit;
}

/* Name elements - subtle emphasis */
.name-element {
    font-weight: 600;
    color: #2c2c2c; /* Same as regular text, just bold */
}

/* Word elements with lemma tooltips */
.word-element {
    cursor: help;
    border-bottom: 1px dotted #999;
}

.word-element:hover {
    background: rgba(0,0,0,0.02);
}

/* External links within inscriptions - minimal styling */
.external-link {
    color: #2c2c2c;
    text-decoration: none;
    border-bottom: 1px solid #ccc;
    transition: border-color 0.2s ease;
}

.external-link:hover {
    border-bottom-color: #666;
}

/* No text content fallback */
.no-text-content {
    padding: 2rem;
    text-align: center;
    color: #666;
    font-style: italic;
    background: #f9f9f9;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .interpretive-edition,
    .diplomatic-edition {
        padding: 1.5rem 1.25rem;
    }

    .academic-edition {
        font-size: 1.1em;
        line-height: 1.8;
    }

    .line-number {
        min-width: 1.5em;
        margin-right: 1em;
        font-size: 0.7em;
    }

    .edition-line {
        margin: 0.6rem 0;
    }
}

/* Print styles for academic papers */
@media print {
    .text-editions {
        background: none;
        border: 1px solid #333;
        box-shadow: none;
    }

    .interpretive-edition,
    .diplomatic-edition {
        border-bottom: 1px solid #333;
        padding: 1rem 0;
    }

    .academic-edition {
        font-size: 11pt;
        line-height: 1.6;
    }

    .line-number {
        font-size: 8pt;
        color: #000;
    }

    .edition-title {
        font-size: 10pt;
        font-weight: bold;
        border-bottom: 1px solid #333;
    }

    .name-element {
        font-weight: bold;
        color: #000;
    }

    .external-link {
        color: #000;
        text-decoration: underline;
        border: none;
    }
}

/* Override any existing colorful styles */
.epidoc-lines {
    /* Reset previous styling */
    background: none !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

.edition-text {
    /* Ensure consistency */
    font-family: inherit;
    background: none;
    border: none;
    padding: 0;
}

/* Remove any line break visual elements */
.edition-line::after {
    display: none !important;
}

/* Ensure clean, academic appearance */
.line-number.major {
    /* Override any previous colorful styling */
    background: none !important;
    color: #666 !important;
    border: none !important;
    padding: 0 !important;
    font-size: 0.75em !important;
    font-weight: 500 !important;
}/* Academic Text Edition Styles - Clean, Professional, No Color Coding */

/* Main text editions container */
.text-editions {
    background: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 2px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin: 1rem 0;
}

/* Edition container for interpretive/diplomatic sections */
.edition-container {
    /* Remove any previous colorful styling */
}

/* Individual edition sections */
.interpretive-edition,
.diplomatic-edition {
    padding: 2rem 2.5rem;
    border-bottom: 1px solid #f0f0f0;
}

.diplomatic-edition {
    border-bottom: none; /* Last section doesn't need bottom border */
}

/* Edition titles with bilingual styling */
.edition-title {
    font-family: var(--metadata-font);
    font-size: 1rem;
    font-weight: 600;
    color: #4a5568;
    margin: 0 0 1.5rem 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
}

/* Bilingual edition titles - matching overview section */
.edition-title.bilingual-label {
    font-weight: normal; /* Remove overall bold */
    text-transform: none; /* Remove uppercase for bilingual titles */
}

.edition-title.bilingual-label .ka {
    font-family: var(--primary-georgian-font);
    color: #1a365d;
    font-weight: 600; /* Georgian bold */
}

.edition-title.bilingual-label .en {
    color: #718096; /* Lighter gray for English */
    font-style: italic;
    font-size: 0.9em;
    font-weight: 400; /* English normal weight */
    opacity: 0.8; /* Make English even more subtle */
}

/* Academic edition text - clean, scholarly presentation */
.academic-edition {
    font-family: var(--inscription-font);
    font-size: 1.2em;
    line-height: 2;
    color: #2c2c2c;
    text-align: left;
    padding: 0;
    background: none;
    border: none;
    margin: 0;
}

/* Diplomatic text styling */
.diplomatic-text {
    font-family: var(--mtavruli-font);
    letter-spacing: 1px;
    font-weight: normal;
}

/* Individual edition lines - clean academic layout */
.edition-line {
    display: flex;
    align-items: baseline;
    margin: 0.8rem 0;
    min-height: 1.5em;
    position: relative;
}

/* Line with number */
.numbered-line {
    margin: 1rem 0;
}

/* Line numbers - small, external, neutral */
.line-number {
    display: inline-block;
    min-width: 2em;
    text-align: right;
    color: #666;
    font-size: 0.75em;
    font-weight: 500;
    margin-right: 1.5em;
    font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    flex-shrink: 0;
    /* Remove all background colors and styling */
    background: none;
    border: none;
    padding: 0;
}

/* Line content */
.line-content {
    flex: 1;
    line-height: inherit;
}

/* Name elements - subtle emphasis */
.name-element {
    font-weight: 600;
    color: #2c2c2c; /* Same as regular text, just bold */
}

/* Word elements with lemma tooltips */
.word-element {
    cursor: help;
    border-bottom: 1px dotted #999;
}

.word-element:hover {
    background: rgba(0,0,0,0.02);
}

/* External links within inscriptions - styled for academic use */
.external-link {
    color: #3182ce;
    text-decoration: none;
    border-bottom: 1px solid #3182ce;
    transition: all 0.2s ease;
}

.external-link:hover {
    color: #2c5282;
    border-bottom-color: #2c5282;
    background: rgba(49, 130, 206, 0.05);
}

/* No text content fallback */
.no-text-content {
    padding: 2rem;
    text-align: center;
    color: #666;
    font-style: italic;
    background: #f9f9f9;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .interpretive-edition,
    .diplomatic-edition {
        padding: 1.5rem 1.25rem;
    }

    .academic-edition {
        font-size: 1.1em;
        line-height: 1.8;
    }

    .line-number {
        min-width: 1.5em;
        margin-right: 1em;
        font-size: 0.7em;
    }

    .edition-line {
        margin: 0.6rem 0;
    }
}

/* Print styles for academic papers */
@media print {
    .text-editions {
        background: none;
        border: 1px solid #333;
        box-shadow: none;
    }

    .interpretive-edition,
    .diplomatic-edition {
        border-bottom: 1px solid #333;
        padding: 1rem 0;
    }

    .academic-edition {
        font-size: 11pt;
        line-height: 1.6;
    }

    .line-number {
        font-size: 8pt;
        color: #000;
    }

    .edition-title {
        font-size: 10pt;
        font-weight: bold;
        border-bottom: 1px solid #333;
    }

    .name-element {
        font-weight: bold;
        color: #000;
    }

    .external-link {
        color: #000;
        text-decoration: underline;
        border: none;
    }
}

/* Override any existing colorful styles */
.epidoc-lines {
    /* Reset previous styling */
    background: none !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

.edition-text {
    /* Ensure consistency */
    font-family: inherit;
    background: none;
    border: none;
    padding: 0;
}

/* Remove any line break visual elements */
.edition-line::after {
    display: none !important;
}

/* Ensure clean, academic appearance */
.line-number.major {
    /* Override any previous colorful styling */
    background: none !important;
    color: #666 !important;
    border: none !important;
    padding: 0 !important;
    font-size: 0.75em !important;
    font-weight: 500 !important;
}/* Clean Browse Page Styles - Homepage-style List Design */

/* Browse header */
.browse-header {
    text-align: center;
    padding: 3rem 0 2rem;
    background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
    margin-bottom: 2rem;
}

.browse-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #1a1a1a;
    letter-spacing: -0.02em;
}

.browse-subtitle {
    font-size: 1.1rem;
    color: #666;
    margin-bottom: 2rem;
    font-weight: 500;
}

/* Browse controls */
.browse-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    max-width: 600px;
    margin: 0 auto;
}

.search-box {
    width: 100%;
}

.search-input {
    width: 100%;
    padding: 0.875rem 1.25rem;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    font-family: var(--mixed-script-font);
    background: white;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.search-input:focus {
    outline: none;
    border-color: #1565C0;
    box-shadow: 0 2px 8px rgba(21, 101, 192, 0.12);
    transform: translateY(-1px);
}

.filters {
    display: flex;
    gap: 1rem;
    width: 100%;
    justify-content: center;
}

.filter-select {
    padding: 0.75rem 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    background: white;
    font-family: var(--mixed-script-font);
    font-size: 0.95rem;
    color: #555;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 140px;
}

.filter-select:focus {
    outline: none;
    border-color: #1565C0;
    box-shadow: 0 2px 6px rgba(21, 101, 192, 0.1);
}

/* Clean inscription list */
.clean-inscription-list {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 1rem;
}

.clean-inscription-item {
    background: white;
    border: 1px solid #f0f0f0;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    padding: 1.5rem 2rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.clean-inscription-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    border-color: #e0e0e0;
}

/* Inscription header */
.inscription-header {
    margin-bottom: 1rem;
}

.inscription-title-section {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}

.inscription-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    line-height: 1.3;
    flex: 1;
    min-width: 200px;
}

.inscription-title a {
    color: #1a1a1a;
    text-decoration: none;
    transition: color 0.2s ease;
}

.inscription-title a:hover {
    color: #1565C0;
}

.inscription-title.georgian-text {
    font-family: var(--primary-georgian-font);
    font-size: 1.3rem;
}

.inscription-id {
    font-size: 0.9rem;
    color: #888;
    font-weight: 600;
    background: #f5f5f5;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    white-space: nowrap;
}

/* Inscription indicators - homepage style */
.inscription-indicators {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.4rem 0.75rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.2s ease;
    white-space: nowrap;
}

/* Language indicators with specific colors */
.language-indicator {
    background: #f5f5f5 !important;
    color: #666 !important;
    font-weight: 500;
    font-size: 0.85rem;
    padding: 0.4rem 0.75rem;
    border-radius: 6px;
    font-family: var(--mixed-script-font);
    border: none;
}

.lang-georgian {
    background: #f5f5f5 !important;
    color: #666 !important;
}

.lang-greek {
    background: #f5f5f5 !important;
    color: #666 !important;
}

.lang-armenian {
    background: #f5f5f5 !important;
    color: #666 !important;
}

.lang-unknown, .lang-other {
    background: #f5f5f5 !important;
    color: #666 !important;
}

/* Other indicators */
.place-indicator {
    background: #f5f5f5 !important;
    color: #666 !important;
    border: 1px solid #e9ecef;
}

.place-indicator.georgian-text {
    font-family: var(--primary-georgian-font);
}

.date-indicator {
    color: #856404;
    border: 1px solid #f5f5f5;
}

.has-images {
    color: #0c5460;
    border: 1px solid #f5f5f5;
}

.material-indicator {
    color: #721c24;
    border: 1px solid #f5f5f5;
}

.material-indicator.georgian-indicator {
    font-family: var(--primary-georgian-font);
}

.object-indicator {
    color: #41464b;
    border: 1px solid #f5f5f5;
}

.object-indicator.georgian-indicator {
    font-family: var(--primary-georgian-font);
}

/* Hover effects for indicators */
.indicator:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

/* Summary section */
.inscription-summary {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #555;
    background: #f8f9fa;
    padding: 1rem 1.25rem;
    border-radius: 6px;
    border-left: 3px solid #e9ecef;
    font-style: italic;
    margin-top: 0.75rem;
}

.inscription-summary.georgian-text {
    font-family: var(--primary-georgian-font);
    font-size: 1rem;
}

/* Result count display */
.result-count {
    text-align: center;
    margin: 1.5rem 0;
    padding: 1rem;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 8px;
    color: #495057;
    font-size: 0.95rem;
    font-weight: 500;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* Responsive design */
@media (max-width: 768px) {
    .browse-header {
        padding: 2rem 0 1.5rem;
    }

    .browse-header h1 {
        font-size: 2rem;
    }

    .browse-controls {
        padding: 0 1rem;
    }

    .filters {
        flex-direction: column;
        gap: 0.75rem;
    }

    .filter-select {
        width: 100%;
        min-width: auto;
    }

    .clean-inscription-item {
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }

    .inscription-title-section {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
    }

    .inscription-title {
        font-size: 1.1rem;
        min-width: auto;
    }

    .inscription-title.georgian-text {
        font-size: 1.2rem;
    }

    .inscription-indicators {
        gap: 0.5rem;
    }

    .indicator {
        font-size: 0.8rem;
        padding: 0.35rem 0.6rem;
    }

    .inscription-summary {
        padding: 0.875rem 1rem;
        font-size: 0.9rem;
    }
}

@media (max-width: 480px) {
    .clean-inscription-item {
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    .inscription-indicators {
        gap: 0.4rem;
    }

    .indicator {
        font-size: 0.75rem;
        padding: 0.3rem 0.5rem;
    }
}

/* Animation for filtered items */
.clean-inscription-item {
    animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Loading state */
.clean-inscription-list[data-loading="true"] {
    opacity: 0.6;
    pointer-events: none;
}

.clean-inscription-list[data-loading="true"]::after {
    content: "Loading...";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 1rem 2rem;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    font-weight: 500;
    color: #666;
}/* IMPROVED MAP LEGEND STYLES - Replace your existing map legend CSS */

.map-legend {
    top: 20px;
    left: 20px;
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(12px);
    padding: 1rem 1.25rem;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    z-index: 10;
    min-width: 220px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

.legend-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e9ecef;
    margin-bottom: 0.75rem;
}

.legend-header span {
    font-size: 0.85rem;
    font-weight: 700;
    color: #2c3e50;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.reset-filter {
    background: #e74c3c;
    color: white;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 5px;
    font-size: 0.7rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.reset-filter:hover {
    background: #c0392b;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(231, 76, 60, 0.3);
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.85rem;
    font-weight: 500;
    color: #34495e;
    padding: 0.6rem 0.8rem;
    border-radius: 6px;
    transition: all 0.2s ease;
    margin-bottom: 0.25rem;
    cursor: pointer;
    user-select: none;
    border: 1px solid transparent;
}

.clickable-legend:hover {
    background: rgba(52, 73, 94, 0.08);
    transform: translateX(3px);
    border-color: rgba(52, 73, 94, 0.2);
}

.clickable-legend.active {
    background: rgba(21, 101, 192, 0.12);
    border-color: rgba(21, 101, 192, 0.4);
    color: #1565C0;
    font-weight: 600;
    transform: translateX(3px);
    box-shadow: 0 2px 8px rgba(21, 101, 192, 0.2);
}

.legend-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    flex-shrink: 0;
    transition: all 0.2s ease;
    border: 2px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
}

.clickable-legend:hover .legend-dot {
    transform: scale(1.15);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.clickable-legend.active .legend-dot {
    transform: scale(1.2);
    box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.3);
}

/* Language-specific colors */
.legend-dot.georgian { background: #27ae60; }  /* Brighter green */
.legend-dot.greek { background: #3498db; }     /* Brighter blue */
.legend-dot.armenian { background: #e67e22; }  /* Brighter orange */
.legend-dot.mixed { background: #9b59b6; }     /* Brighter purple */
.legend-dot.other { background: #7f8c8d; }     /* Medium gray */

.legend-item span:last-child.count {
    margin-left: auto;
    background: #ecf0f1;
    color: #2c3e50;
    padding: 0.25rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 700;
    min-width: 24px;
    text-align: center;
    transition: all 0.2s ease;
}

.clickable-legend:hover .count {
    background: #bdc3c7;
    color: #2c3e50;
}

.clickable-legend.active .count {
    background: #1565C0;
    color: white;
    transform: scale(1.05);
}

/* Hide counts that are 0 */
.count:empty,
.count[style*="display: none"] {
    display: none !important;
}

/* Enhanced map container */
.map-container {
    position: relative;
    margin: 3rem 0;
    padding: 0 1.5rem;
}



/* Responsive adjustments */
@media (max-width: 768px) {
    .map-legend {
        position: static;
        margin-bottom: 1rem;
        width: 100%;
        max-width: none;
        left: auto;
        top: auto;
        min-width: auto;
    }

    .legend-header {
        justify-content: center;
        text-align: center;
    }

    .legend-item {
        font-size: 0.8rem;
        padding: 0.5rem 0.6rem;
    }

    .legend-dot {
        width: 12px;
        height: 12px;
    }

    .count {
        font-size: 0.7rem !important;
        padding: 0.2rem 0.5rem !important;
        min-width: 20px;
    }

    .reset-filter {
        font-size: 0.65rem;
        padding: 0.3rem 0.6rem;
    }

}/* Language indicators - Homepage style (simple gray background, no colors) */

/* Homepage inscription cards - maintain original styling */
.inscription-meta span {
    background: #f5f5f5;
    color: #666;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: 500;
    font-size: 0.8rem;
}

/* Browse page language indicators - match homepage exactly */
.language-indicator {
    background: #f5f5f5 !important;
    color: #666 !important;
    font-weight: 500;
    font-size: 0.85rem;
    padding: 0.4rem 0.75rem;
    border-radius: 6px;
    font-family: var(--mixed-script-font);
    border: none;
}

/* Remove any colored backgrounds - keep consistent gray styling */
.lang-georgian,
.lang-greek,
.lang-armenian,
.lang-unknown,
.lang-other {
    background: #f5f5f5 !important;
    color: #666 !important;
}

/* Ensure all language indicators have consistent styling */
.inscription-card .lang,
.clean-inscription-item .language-indicator {
    background: #f5f5f5;
    color: #666;
    font-weight: 500;
    text-transform: none; /* Don't uppercase */
    letter-spacing: normal;
}

/* Hover effects for browse page indicators */
.clean-inscription-item .language-indicator:hover {
    background: #e8e8e8;
    color: #555;
}

/* Override default webkit link styling EXCEPT for navigation */
a:-webkit-any-link:not(.brand):not(.nav-links a) {
    color: #3182ce;
    cursor: pointer;
    text-decoration: underline;
}

/* General link styling for content links only (not navigation) */
main a, .container a:not(.brand):not(.nav-links a) {
    color: #3182ce;
    text-decoration: none;
    transition: color 0.2s ease;
}

main a:hover, .container a:not(.brand):not(.nav-links a):hover {
    color: #2c5282;
    text-decoration: underline;
}

/* Preserve original navbar styling */
.brand {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a1a1a !important;
    text-decoration: none !important;
    letter-spacing: -0.02em;
}

.nav-links a {
    color: #666 !important;
    text-decoration: none !important;
    font-weight: 500;
    font-size: 0.95rem;
    transition: color 0.2s ease;
}

.nav-links a:hover {
    color: #1a1a1a !important;
    text-decoration: none !important;
}
/* Enhanced Person Page Styles - Clean Traditional Design */

/* Better Button Styles (from persons page) */
.btn {
    padding: 0.5rem 1rem;
    border-radius: 6px;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    cursor: pointer;
    display: inline-block;
}

.btn-secondary {
    background: #6c757d;
    color: white;
    border: none;
}

.btn-secondary:hover {
    background: #5a6268;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(108, 117, 125, 0.3);
}

.btn-outline {
    background: white;
    color: #6c757d;
    border: 1px solid #6c757d;
}

.btn-outline:hover {
    background: #6c757d;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(108, 117, 125, 0.2);
}

.person-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-top: 20px;
    flex-wrap: wrap;
}

/* Two-column layout */
.two-column-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

@media (max-width: 768px) {
    .two-column-grid {
        grid-template-columns: 1fr;
    }
    
    .person-actions {
        flex-direction: column;
        gap: 8px;
    }
    
    .btn {
        text-align: center;
    }
}

/* Name Variants Section */
.name-variants-section {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
}

.name-variants-section h4 {
    color: var(--primary);
    margin-bottom: 10px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.variants-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.name-variant {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 4px 12px;
    border-radius: 2px;
    font-size: 14px;
    color: var(--text-secondary);
}

.name-variant.georgian-text {
    font-family: var(--primary-georgian-font);
}

/* Enhanced Attestations */
.attestations-content {
    margin-top: 16px;
}

.attestation-entry {
    background: white;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px;
    margin-bottom: 12px;
    transition: box-shadow 0.2s ease;
}

.attestation-entry:hover {
    box-shadow: var(--shadow);
}

.attestation-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.inscription-id {
    font-family: 'Courier New', monospace;
    font-weight: bold;
    color: var(--accent);
    font-size: 14px;
}

.inscription-tag {
    background: var(--accent);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    text-transform: uppercase;
    font-weight: 500;
}

.inscription-title {
    margin: 8px 0;
    font-size: 1rem;
}

.inscription-title a {
    color: var(--text-primary);
    text-decoration: none;
    transition: color 0.2s ease;
}

.inscription-title a:hover {
    color: var(--accent);
}

.inscription-title.georgian-text {
    font-family: var(--primary-georgian-font);
}

.attestation-details {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 8px;
}

.detail-place,
.detail-date,
.detail-language,
.detail-role {
    display: flex;
    align-items: center;
    gap: 4px;
}

.detail-place.georgian-text {
    font-family: var(--primary-georgian-font);
}

/* Geographic Distribution */
.geographic-distribution {
    margin-bottom: 24px;
}

.geographic-distribution h4 {
    color: var(--primary);
    margin-bottom: 12px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.locations-list {
    background: var(--surface);
    border-radius: 4px;
    padding: 12px;
}

.location-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
}

.location-item:last-child {
    border-bottom: none;
}

.location-name {
    font-weight: 500;
    color: var(--text-primary);
}

.location-name.georgian-text {
    font-family: var(--primary-georgian-font);
}

.location-count {
    background: var(--primary);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    min-width: 20px;
    text-align: center;
}

/* Co-occurrence Section */
.co-occurrence-section {
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
}

.co-occurrence-section h4 {
    color: var(--primary);
    margin-bottom: 12px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.co-persons-list {
    background: var(--surface);
    border-radius: 4px;
    padding: 12px;
}

.co-occurrence-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
}

.co-occurrence-item:last-child {
    border-bottom: none;
}

.co-person-link {
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
}

.co-person-link:hover {
    color: var(--primary);
    text-decoration: underline;
}

.co-person-link.georgian-text {
    font-family: var(--primary-georgian-font);
}

.co-count {
    background: var(--warning);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
}

/* External References Section */
.external-references-section {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
}

.external-references-section h4 {
    color: var(--primary);
    margin-bottom: 12px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.refs-content {
    background: var(--surface);
    padding: 12px;
    border-radius: 4px;
    font-size: 14px;
    line-height: 1.6;
}

.external-link {
    color: var(--accent);
    text-decoration: none;
    transition: color 0.2s ease;
}

.external-link:hover {
    color: var(--primary);
    text-decoration: underline;
}

.nym-ref {
    margin-top: 8px;
    font-size: 13px;
    color: var(--text-secondary);
}

.nym-ref code {
    background: var(--surface-hover);
    padding: 2px 6px;
    border-radius: 2px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}

/* Citation Section */
.citation-section {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
}

.citation-section h4 {
    color: var(--primary);
    margin-bottom: 12px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.citation-text {
    background: white;
    padding: 16px;
    border-radius: 4px;
    border: 1px solid var(--border);
    font-size: 14px;
    line-height: 1.6;
    font-family: var(--font-secondary);
    color: var(--text-secondary);
}

/* Error States */
.no-attestations,
.no-locations,
.error-attestations,
.error-locations {
    text-align: center;
    color: var(--text-muted);
    font-style: italic;
    padding: 20px;
    background: var(--surface);
    border-radius: 4px;
    border: 1px solid var(--border);
}

/* Print Styles */
@media print {
    .person-actions {
        display: none;
    }
    
    .attestation-entry {
        break-inside: avoid;
        border: 1px solid #ccc;
        margin-bottom: 8px;
    }
    
    .co-occurrence-section,
    .external-references-section {
        break-inside: avoid;
    }
    
    .citation-text {
        background: #f9f9f9;
        border: 1px solid #ccc;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .attestation-details {
        flex-direction: column;
        gap: 8px;
    }
    
    .attestation-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
    }
    
    .location-item,
    .co-occurrence-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
    }
    
    .location-count,
    .co-count {
        align-self: flex-end;
    }
    
    .variants-list {
        flex-direction: column;
        gap: 4px;
    }
    
    .name-variant {
        text-align: center;
    }
}"""

        try:
            # Create JavaScript file
            with open(f"{self.output_dir}/static/js/persons.js", 'w', encoding='utf-8') as f:
                f.write(persons_js)
            
            # Append persons CSS to main CSS file
            with open(f"{self.output_dir}/static/css/style.css", 'a', encoding='utf-8') as f:
                f.write('\n\n/* Persons Index Styles */\n')
                f.write(persons_css)
                
            print("📜 Persons JavaScript and CSS created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating persons JavaScript/CSS: {e}")
            import traceback
            traceback.print_exc()

    def format_bilingual_text_with_lang(self, text_data, primary_language, fallback=""):
        """Format bilingual text with proper language attributes for Georgian fonts"""
        try:
            if isinstance(text_data, dict):
                ka_text = text_data.get('ka', '')
                en_text = text_data.get('en', '')
                default_text = text_data.get('default', '')

                # Create properly tagged bilingual display
                if ka_text and en_text:
                    return f'<div class="bilingual-text"><div class="text-ka" lang="ka">{ka_text}</div><div class="text-en" lang="en">{en_text}</div></div>'
                elif ka_text:
                    return f'<div class="text-ka" lang="ka">{ka_text}</div>'
                elif en_text:
                    return f'<div class="text-en" lang="en">{en_text}</div>'
                elif default_text:
                    # Apply language attribute based on primary language
                    lang_attr = f'lang="{primary_language}"' if primary_language in ['ka', 'en', 'hy'] else ''
                    return f'<div {lang_attr}>{default_text}</div>'
                else:
                    # Return first available language with proper tagging
                    for lang, text in text_data.items():
                        if text:
                            lang_attr = f'lang="{lang}"' if lang in ['ka', 'en', 'hy'] else ''
                            return f'<div {lang_attr}>{text}</div>'

            # Simple string case
            if text_data:
                lang_attr = f'lang="{primary_language}"' if primary_language in ['ka', 'en', 'hy'] else ''
                return f'<div {lang_attr}>{text_data}</div>'

            return fallback
        except Exception:
            return fallback






    # JavaScript ფაილების შექმნა იწყება
    

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
    
            const filteredPersons = personsArray.filter(person => {
                const name = person.dataset.name || '';
                const textContent = person.textContent.toLowerCase();
                
                return !searchTerm || 
                       name.includes(searchTerm) || 
                       textContent.includes(searchTerm);
            });
    
            filteredPersons.sort((a, b) => {
                switch(sortBy) {
                    case 'alphabetical':
                        return (a.dataset.name || '').localeCompare(b.dataset.name || '');
                    case 'inscriptions':
                        return parseInt(b.dataset.count || '0') - parseInt(a.dataset.count || '0');
                    case 'frequency':
                    default:
                        const countDiff = parseInt(b.dataset.count || '0') - parseInt(a.dataset.count || '0');
                        return countDiff !== 0 ? countDiff : (a.dataset.name || '').localeCompare(b.dataset.name || '');
                }
            });
    
            personsArray.forEach(person => {
                person.style.display = 'none';
            });
    
            if (personsList) {
                personsList.innerHTML = '';
                filteredPersons.forEach(person => {
                    person.style.display = 'block';
                    personsList.appendChild(person);
                });
            }
    
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
    
        if (searchInput) {
            searchInput.addEventListener('input', debouncedFilter);
        }
    
        if (sortSelect) {
            sortSelect.addEventListener('change', filterAndSortPersons);
        }
    
        filterAndSortPersons();
    
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
    
        persons_css = """
/* Persons Index Page Styles */
.persons-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    max-width: 870px;
    margin: 2rem auto;
}

.persons-controls .search-box {
    display: flex;
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
.person-page .person-header {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 2rem;
}

.person-page .person-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #1a1a1a;
}

.person-page .person-header h1.georgian-text {
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

    .person-page .person-header h1 {
        font-size: 2rem;
    }

    .person-page .person-header h1.georgian-text {
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
}/* Enhanced Person Page Styles - Traditional Scholarly Design */

/* Name Variants Section */
.name-variants-section {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
}

.name-variants-section h4 {
    color: var(--primary);
    margin-bottom: 10px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.variants-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.name-variant {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 4px 12px;
    border-radius: 2px;
    font-size: 14px;
    color: var(--text-secondary);
}

.name-variant.georgian-text {
    font-family: var(--primary-georgian-font);
}

/* Enhanced Attestations */
.attestations-content {
    margin-top: 16px;
}

.attestation-entry {
    background: white;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px;
    margin-bottom: 12px;
    transition: box-shadow 0.2s ease;
}

.attestation-entry:hover {
    box-shadow: var(--shadow);
}

.attestation-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.inscription-id {
    font-family: 'Courier New', monospace;
    font-weight: bold;
    color: var(--accent);
    font-size: 14px;
}

.inscription-tag {
    background: var(--accent);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    text-transform: uppercase;
    font-weight: 500;
}

.inscription-title {
    margin: 8px 0;
    font-size: 1rem;
}

.inscription-title a {
    color: var(--text-primary);
    text-decoration: none;
    transition: color 0.2s ease;
}

.inscription-title a:hover {
    color: var(--accent);
}

.inscription-title.georgian-text {
    font-family: var(--primary-georgian-font);
}

.attestation-details {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 8px;
}

.detail-place,
.detail-date,
.detail-language,
.detail-role {
    display: flex;
    align-items: center;
    gap: 4px;
}

.detail-place.georgian-text {
    font-family: var(--primary-georgian-font);
}

/* Geographic Distribution */
.geographic-distribution {
    margin-bottom: 24px;
}

.geographic-distribution h4 {
    color: var(--primary);
    margin-bottom: 12px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.locations-list {
    background: var(--surface);
    border-radius: 4px;
    padding: 12px;
}

.location-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
}

.location-item:last-child {
    border-bottom: none;
}

.location-name {
    font-weight: 500;
    color: var(--text-primary);
}

.location-name.georgian-text {
    font-family: var(--primary-georgian-font);
}

.location-count {
    background: var(--primary);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    min-width: 20px;
    text-align: center;
}

/* Co-occurrence Section */
.co-occurrence-section {
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
}

.co-occurrence-section h4 {
    color: var(--primary);
    margin-bottom: 12px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.co-persons-list {
    background: var(--surface);
    border-radius: 4px;
    padding: 12px;
}

.co-occurrence-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
}

.co-occurrence-item:last-child {
    border-bottom: none;
}

.co-person-link {
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
}

.co-person-link:hover {
    color: var(--primary);
    text-decoration: underline;
}

.co-person-link.georgian-text {
    font-family: var(--primary-georgian-font);
}

.co-count {
    background: var(--warning);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
}

/* External References Section */
.external-references-section {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
}

.external-references-section h4 {
    color: var(--primary);
    margin-bottom: 12px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.refs-content {
    background: var(--surface);
    padding: 12px;
    border-radius: 4px;
    font-size: 14px;
    line-height: 1.6;
}

.external-link {
    color: var(--accent);
    text-decoration: none;
    transition: color 0.2s ease;
}

.external-link:hover {
    color: var(--primary);
    text-decoration: underline;
}

.nym-ref {
    margin-top: 8px;
    font-size: 13px;
    color: var(--text-secondary);
}

.nym-ref code {
    background: var(--surface-hover);
    padding: 2px 6px;
    border-radius: 2px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}

/* Citation Section */
.citation-section {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
}

.citation-section h4 {
    color: var(--primary);
    margin-bottom: 12px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.citation-text {
    background: white;
    padding: 16px;
    border-radius: 4px;
    border: 1px solid var(--border);
    font-size: 14px;
    line-height: 1.6;
    font-family: var(--font-secondary);
    color: var(--text-secondary);
}

/* Error States */
.no-attestations,
.no-locations,
.error-attestations,
.error-locations {
    text-align: center;
    color: var(--text-muted);
    font-style: italic;
    padding: 20px;
    background: var(--surface);
    border-radius: 4px;
    border: 1px solid var(--border);
}

/* Print Styles */
@media print {
    .person-actions {
        display: none;
    }
    
    .attestation-entry {
        break-inside: avoid;
        border: 1px solid #ccc;
        margin-bottom: 8px;
    }
    
    .co-occurrence-section,
    .external-references-section {
        break-inside: avoid;
    }
    
    .citation-text {
        background: #f9f9f9;
        border: 1px solid #ccc;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .attestation-details {
        flex-direction: column;
        gap: 8px;
    }
    
    .attestation-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
    }
    
    .location-item,
    .co-occurrence-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
    }
    
    .location-count,
    .co-count {
        align-self: flex-end;
    }
    
    .variants-list {
        flex-direction: column;
        gap: 4px;
    }
    
    .name-variant {
        text-align: center;
    }
}"""
        try:
            # Create JavaScript file
            with open(f"{self.output_dir}/static/js/persons.js", 'w', encoding='utf-8') as f:
                f.write(persons_js)
            
            # Append persons CSS to main CSS file
            with open(f"{self.output_dir}/static/css/style.css", 'a', encoding='utf-8') as f:
                f.write(persons_css)
            
            print("📜 Persons JavaScript and CSS created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating persons JavaScript/CSS: {e}")
            import traceback
            traceback.print_exc()
    
    def create_javascript(self):
        """Create JavaScript files for tabs, browse functionality, and enhanced map"""
        # Tabs JavaScript
        tabs_js = """// Tab functionality for inscription pages
    function showTab(tabName) {
        // Hide all tab contents
        const contents = document.querySelectorAll('.tab-content');
        contents.forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tab buttons
        const buttons = document.querySelectorAll('.tabs button');
        buttons.forEach(button => {
            button.classList.remove('active');
        });

        // Show the selected tab content
        const selectedContent = document.getElementById('content-' + tabName);
        if (selectedContent) {
            selectedContent.classList.add('active');
        }

        // Activate the selected tab button
        const selectedButton = document.getElementById('tab-' + tabName);
        if (selectedButton) {
            selectedButton.classList.add('active');
        }
    }
    // Initialize the first tab as active when page loads
    document.addEventListener('DOMContentLoaded', function() {
        showTab('overview');
    });
    """

        # Browse page JavaScript - FIXED VERSION
        browse_js = """// Fixed Browse page functionality with better error handling
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🔍 Browse page JavaScript loaded');

        const searchInput = document.getElementById('searchInput');
        const languageFilter = document.getElementById('languageFilter');
        const sortSelect = document.getElementById('sortSelect');
        const inscriptionList = document.getElementById('inscriptionList');
        const allItems = document.querySelectorAll('.clean-inscription-item');

        console.log(`📊 Found ${allItems.length} inscription items in DOM`);

        // Convert NodeList to Array for easier manipulation
        let itemsArray = Array.from(allItems);

        function filterAndSortInscriptions() {
            console.log('🔍 Running filterAndSortInscriptions...');

            const searchTerm = (searchInput ? searchInput.value || '' : '').toLowerCase();
            const selectedLanguage = languageFilter ? languageFilter.value || '' : '';
            const sortBy = sortSelect ? sortSelect.value || 'id' : 'id';

            console.log(`🔍 Filter params: search="${searchTerm}", language="${selectedLanguage}", sort="${sortBy}"`);

            // Show loading state
            if (inscriptionList) {
                inscriptionList.dataset.loading = 'true';
            }

            // Small delay to show loading (smooth UX)
            setTimeout(() => {
                try {
                    // Filter items
                    const filteredItems = itemsArray.filter(item => {
                        const title = (item.dataset.title || '').toLowerCase();
                        const id = (item.dataset.id || '').toLowerCase();
                        const place = (item.dataset.place || '').toLowerCase();
                        const language = item.dataset.language || '';

                        const matchesSearch = !searchTerm ||
                                            title.includes(searchTerm) ||
                                            id.includes(searchTerm) ||
                                            place.includes(searchTerm);

                        const matchesLanguage = !selectedLanguage || language === selectedLanguage;

                        return matchesSearch && matchesLanguage;
                    });

                    console.log(`🔍 Filtered to ${filteredItems.length} items`);

                    // Sort items
                    filteredItems.sort((a, b) => {
                        let aValue, bValue;

                        switch(sortBy) {
                            case 'title':
                                aValue = (a.dataset.title || '').toLowerCase();
                                bValue = (b.dataset.title || '').toLowerCase();
                                return aValue.localeCompare(bValue);
                            case 'place':
                                aValue = (a.dataset.place || '').toLowerCase();
                                bValue = (b.dataset.place || '').toLowerCase();
                                return aValue.localeCompare(bValue);
                            case 'date':
                                aValue = (a.dataset.date || '').toLowerCase();
                                bValue = (b.dataset.date || '').toLowerCase();
                                return aValue.localeCompare(bValue);
                            case 'language':
                                aValue = (a.dataset.language || '').toLowerCase();
                                bValue = (b.dataset.language || '').toLowerCase();
                                return aValue.localeCompare(bValue);
                            case 'id':
                            default:
                                // Sort IDs numerically if they're numbers, alphabetically otherwise
                                aValue = a.dataset.id || '';
                                bValue = b.dataset.id || '';
                                const aNum = parseInt(aValue.replace(/[^0-9]/g, ''));
                                const bNum = parseInt(bValue.replace(/[^0-9]/g, ''));
                                if (!isNaN(aNum) && !isNaN(bNum)) {
                                    return aNum - bNum;
                                }
                                return aValue.localeCompare(bValue);
                        }
                    });

                    // Hide all items first
                    itemsArray.forEach(item => {
                        item.style.display = 'none';
                    });

                    // Clear the container and re-append filtered/sorted items
                    if (inscriptionList) {
                        inscriptionList.innerHTML = '';

                        // Add items with staggered animation
                        filteredItems.forEach((item, index) => {
                            item.style.display = 'block';
                            item.style.animationDelay = `${index * 10}ms`;
                            inscriptionList.appendChild(item);
                        });
                    }

                    // Update count display
                    updateResultCount(filteredItems.length, itemsArray.length);

                    // Remove loading state
                    if (inscriptionList) {
                        inscriptionList.dataset.loading = 'false';
                    }

                    console.log(`✅ Filtering complete, showing ${filteredItems.length} items`);

                } catch (error) {
                    console.error('❌ Error in filterAndSortInscriptions:', error);

                    // Fallback: show all items if filtering fails
                    itemsArray.forEach(item => {
                        item.style.display = 'block';
                        if (inscriptionList) {
                            inscriptionList.appendChild(item);
                        }
                    });

                    if (inscriptionList) {
                        inscriptionList.dataset.loading = 'false';
                    }
                    updateResultCount(itemsArray.length, itemsArray.length);
                }
            }, 50);
        }

        function updateResultCount(showing, total) {
            let countDisplay = document.getElementById('resultCount');
            if (!countDisplay && inscriptionList) {
                countDisplay = document.createElement('div');
                countDisplay.id = 'resultCount';
                countDisplay.className = 'result-count';
                inscriptionList.parentNode.insertBefore(countDisplay, inscriptionList);
            }

            if (countDisplay) {
                if (showing === total) {
                    countDisplay.innerHTML = `<strong>ნაჩვენებია ${total} წარწერა</strong>`;
                } else {
                    countDisplay.innerHTML = `
                        <strong>ნაჩვენებია ${showing} წარწერა ${total}-დან</strong>
                        ${(searchInput && searchInput.value) || (languageFilter && languageFilter.value) ?
                            `<br><small>Filtered by: ${getFilterDescription()}</small>` : ''}
                    `;
                }
            }
        }

        function getFilterDescription() {
            const filters = [];
            if (searchInput && searchInput.value) {
                filters.push(`search: "${searchInput.value}"`);
            }
            if (languageFilter && languageFilter.value) {
                const languageNames = {
                    'ka': 'Georgian',
                    'grc': 'Greek',
                    'hy': 'Armenian',
                    'arc': 'Aramaic',
                    'he': 'Hebrew',
                    'la': 'Latin',
                    'unknown': 'Unknown'
                };
                filters.push(`language: ${languageNames[languageFilter.value] || languageFilter.value}`);
            }
            return filters.join(', ');
        }

        // Debounce search input for better performance
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

        const debouncedFilter = debounce(filterAndSortInscriptions, 200);

        // Add event listeners with error handling
        try {
            if (searchInput) {
                searchInput.addEventListener('input', debouncedFilter);

                searchInput.addEventListener('focus', function() {
                    if (this.parentElement) {
                        this.parentElement.classList.add('focused');
                    }
                });

                searchInput.addEventListener('blur', function() {
                    if (this.parentElement) {
                        this.parentElement.classList.remove('focused');
                    }
                });
            }

            if (languageFilter) {
                languageFilter.addEventListener('change', filterAndSortInscriptions);
            }

            if (sortSelect) {
                sortSelect.addEventListener('change', filterAndSortInscriptions);
            }

            // Initialize the display
            console.log('🔍 Initializing display...');
            filterAndSortInscriptions();

            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Focus search with Ctrl/Cmd + F
                if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                    e.preventDefault();
                    if (searchInput) {
                        searchInput.focus();
                        searchInput.select();
                    }
                }

                // Clear search with Escape
                if (e.key === 'Escape' && document.activeElement === searchInput && searchInput) {
                    searchInput.value = '';
                    debouncedFilter();
                }
            });

            console.log('✅ Browse page JavaScript initialized successfully');

        } catch (error) {
            console.error('❌ Error initializing browse page:', error);

            // Fallback: ensure all items are visible
            itemsArray.forEach(item => {
                item.style.display = 'block';
            });
        }
    });
    """

        # Bibliography page JavaScript
        bibliography_js = """// Bibliography page functionality
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('bibliographySearch');
        const bibliographyList = document.getElementById('bibliographyList');
        const allEntries = document.querySelectorAll('.bibliography-entry');

        function filterBibliography() {
            const searchTerm = searchInput.value.toLowerCase();

            allEntries.forEach(entry => {
                const content = entry.querySelector('.bib-content').textContent.toLowerCase();
                const id = entry.querySelector('.bib-id').textContent.toLowerCase();

                if (content.includes(searchTerm) || id.includes(searchTerm)) {
                    entry.style.display = 'block';
                } else {
                    entry.style.display = 'none';
                }
            });
        }

        if (searchInput) {
            searchInput.addEventListener('input', filterBibliography);
        }

        if (window.location.hash) {
            const targetEntry = document.querySelector(window.location.hash);
            if (targetEntry) {
                setTimeout(() => {
                    targetEntry.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            }
        }
    });
    """



        # Write JavaScript files
        try:
            with open(f"{self.output_dir}/static/js/tabs.js", 'w', encoding='utf-8') as f:
                f.write(tabs_js)

            with open(f"{self.output_dir}/static/js/browse.js", 'w', encoding='utf-8') as f:
                f.write(browse_js)

            with open(f"{self.output_dir}/static/js/bibliography.js", 'w', encoding='utf-8') as f:
                f.write(bibliography_js)

            # NEW: Create the enhanced map JavaScript file
            with open(f"{self.output_dir}/static/js/map.js", 'w', encoding='utf-8') as f:
                f.write(map_js)

            print("📜 All JavaScript files created successfully!")
            print("✅ New map.js file fixes coordinate jumping issues")

        except Exception as e:
            print(f"❌ Error creating JavaScript files: {e}")
            import traceback
            traceback.print_exc()

    # JavaScript ფაილების შექმნა მთავრდება
    

if __name__ == "__main__":
    processor = RobustECGProcessorVanilla()
    processor.process_all()
