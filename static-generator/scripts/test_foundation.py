#!/usr/bin/env python3
"""
Fixed test script - removes XML encoding declarations from test strings
"""
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_config():
    """Test configuration module"""
    print("🧪 Testing ECGConfig...")

    try:
        from ecg_processor.config import ECGConfig

        config = ECGConfig()
        print(f"✅ Config created successfully")
        print(f"   📁 XML dir: {config.xml_dir}")
        print(f"   📁 Output dir: {config.output_dir}")
        print(f"   📁 Bibliography: {config.bibliography_path}")
        print(f"   📁 Images: {config.images_dir}")

        # Test path validation
        paths_valid = config.validate_paths()
        if paths_valid:
            print("✅ All paths validated")
        else:
            print("⚠️ Some paths missing (this is expected for first run)")

        return True

    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_xml_utils():
    """Test XML utilities"""
    print("\n🧪 Testing XMLUtils...")

    try:
        from ecg_processor.config import ECGConfig
        from ecg_processor.utils.xml_utils import XMLUtils
        from lxml import etree

        config = ECGConfig()
        xml_utils = XMLUtils(config)

        # Create a simple test XML WITHOUT encoding declaration
        test_xml = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <titleStmt>
                    <title xml:lang="ka">ტესტი</title>
                    <title xml:lang="en">Test</title>
                </titleStmt>
            </teiHeader>
        </TEI>"""

        root = etree.fromstring(test_xml)

        # Test safe_xpath
        titles = xml_utils.safe_xpath(root, './/tei:title')
        print(f"✅ Found {len(titles)} title elements")

        # Test safe_get_text
        if titles:
            title_text = xml_utils.safe_get_text(titles[0])
            print(f"✅ Extracted title text: '{title_text}'")

        # Test language detection
        lang = xml_utils.get_element_language(titles[0]) if titles else 'none'
        print(f"✅ Detected language: {lang}")

        return True

    except Exception as e:
        print(f"❌ XMLUtils test failed: {e}")
        return False

def test_metadata_extractor():
    """Test metadata extraction"""
    print("\n🧪 Testing MetadataExtractor...")

    try:
        from ecg_processor.config import ECGConfig
        from ecg_processor.utils.metadata_extractor import MetadataExtractor
        from lxml import etree

        config = ECGConfig()
        extractor = MetadataExtractor(config)

        # Create a more complex test XML WITHOUT encoding declaration
        test_xml = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <titleStmt>
                    <title xml:lang="ka">ტესტის წარწერა</title>
                    <title xml:lang="en">Test Inscription</title>
                </titleStmt>
            </teiHeader>
            <text>
                <body>
                    <div type="edition" xml:lang="ka">
                        <ab>ტესტის ტექსტი</ab>
                    </div>
                </body>
            </text>
        </TEI>"""

        root = etree.fromstring(test_xml)

        # Test title extraction
        titles = extractor.extract_title(root)
        print(f"✅ Extracted titles: {titles}")

        # Test language detection
        language = extractor.detect_language(root)
        print(f"✅ Detected language: {language}")

        return True

    except Exception as e:
        print(f"❌ MetadataExtractor test failed: {e}")
        return False

def test_real_xml_file():
    """Test with a real XML file from your corpus"""
    print("\n🧪 Testing with real XML file...")

    try:
        from ecg_processor.config import ECGConfig
        from ecg_processor.utils.metadata_extractor import MetadataExtractor
        from lxml import etree
        from pathlib import Path

        config = ECGConfig()

        # Try to find a real XML file
        xml_dir = Path(config.xml_dir)
        if not xml_dir.exists():
            print(f"⚠️ XML directory not found: {xml_dir}")
            return False

        xml_files = list(xml_dir.glob("ECG*.xml"))
        if not xml_files:
            print(f"⚠️ No ECG XML files found in: {xml_dir}")
            return False

        # Test with first XML file
        test_file = xml_files[0]
        print(f"📄 Testing with: {test_file.name}")

        parser = etree.XMLParser(recover=True)
        tree = etree.parse(str(test_file), parser)
        root = tree.getroot()

        extractor = MetadataExtractor(config)

        # Extract basic metadata
        title = extractor.extract_title(root)
        dating = extractor.extract_dating(root)
        origin = extractor.extract_origin(root)
        language = extractor.detect_language(root)

        print(f"✅ Title: {title}")
        print(f"✅ Dating: {dating}")
        print(f"✅ Origin: {origin}")
        print(f"✅ Language: {language}")

        return True

    except Exception as e:
        print(f"❌ Real XML test failed: {e}")
        return False

def main():
    """Run all foundation tests"""
    print("🚀 Testing ECG Processor Foundation Modules")
    print("=" * 50)

    tests = [
        test_config,
        test_xml_utils,
        test_metadata_extractor,
        test_real_xml_file
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test crashed: {e}")

    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All foundation tests passed! Ready for next step.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
