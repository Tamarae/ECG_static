import os
from lxml import etree
from pathlib import Path

def debug_xml_files():
    xml_dir = "../webapps/ROOT/content/xml/epidoc"
    xml_files = list(Path(xml_dir).glob("ECG*.xml"))[:5]  # Just first 5

    print(f"Found {len(list(Path(xml_dir).glob('ECG*.xml')))} total XML files")
    print("Examining first 5 files...\n")

    for xml_file in xml_files:
        print(f"=== {xml_file.name} ===")

        try:
            # Try to parse the XML
            tree = etree.parse(str(xml_file))
            root = tree.getroot()

            print(f"✅ XML is valid")
            print(f"Root element: {root.tag}")
            print(f"Namespaces: {list(root.nsmap.keys())}")

            # Look for text content
            all_text = ' '.join(root.itertext())
            print(f"Total text length: {len(all_text)}")
            print(f"Sample text: {all_text[:100]}...")

            # Look for common elements
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

            titles = root.xpath('.//tei:title', namespaces=ns)
            print(f"Title elements found: {len(titles)}")
            if titles:
                print(f"First title: {titles[0].text}")

            editions = root.xpath('.//tei:div[@type="edition"]', namespaces=ns)
            print(f"Edition divs: {len(editions)}")

        except etree.XMLSyntaxError as e:
            print(f"❌ XML syntax error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 50)

if __name__ == "__main__":
    debug_xml_files()
