#!/usr/bin/env python3
"""
Test the complete XML processing pipeline
This tests Steps 1-3 of the modular processor
"""
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_xml_processing_pipeline():
    """Test the complete XML processing pipeline"""
    print("🧪 Testing Complete XML Processing Pipeline")
    print("=" * 50)

    try:
        from ecg_processor.main import ECGProcessor

        # Create processor
        print("🔧 Creating ECG processor...")
        processor = ECGProcessor()

        # Test configuration
        print("✅ Configuration loaded")
        print(f"   📁 XML files: {processor.config.xml_dir}")
        print(f"   📁 Output: {processor.config.output_dir}")

        # Test XML processor initialization
        print("\n🔧 Testing XML processor initialization...")
        xml_processor = processor.xml_processor
        print("✅ XML processor initialized")

        # Test bibliography processing
        print("\n📚 Testing bibliography processing...")
        xml_processor._process_bibliography()
        if xml_processor.bibliography:
            print(f"✅ Bibliography processed: {len(xml_processor.bibliography)} entries")
            # Show first few entries
            for i, (bib_id, entry) in enumerate(list(xml_processor.bibliography.items())[:3]):
                content_preview = entry['content'][:60] + "..." if len(entry['content']) > 60 else entry['content']
                print(f"   {i+1}. {bib_id}: {content_preview}")
        else:
            print("⚠️ No bibliography entries found")

        # Test single inscription processing
        print("\n📄 Testing single inscription processing...")
        xml_files = list(Path(processor.config.xml_dir).glob("*.xml"))
        if xml_files:
            test_file = xml_files[0]
            print(f"   Testing with: {test_file.name}")

            inscription = xml_processor._process_single_inscription(test_file)
            if inscription:
                print("✅ Single inscription processed successfully:")
                print(f"   ID: {inscription.id}")
                print(f"   Title: {inscription.get_display_title()}")
                print(f"   Language: {inscription.language}")
                print(f"   Place: {inscription.get_primary_place()}")
                print(f"   Dating: {inscription.get_dating_text()}")
                print(f"   Images: {len(inscription.images)}")
                print(f"   Bibliography refs: {len(inscription.bibliography_refs)}")

                # Test text content
                if inscription.text_content:
                    print(f"   Text editions: {len(inscription.text_content)}")
                    for key, edition in inscription.text_content.items():
                        content_preview = edition['content'][:100] + "..." if len(edition['content']) > 100 else edition['content']
                        print(f"     {key}: {content_preview}")

            else:
                print("❌ Failed to process inscription")
                return False
        else:
            print("❌ No XML files found for testing")
            return False

        # Test processing multiple inscriptions (limited for testing)
        print(f"\n📊 Testing batch processing (first 5 files)...")
        test_files = xml_files[:5]
        successful = 0

        for xml_file in test_files:
            inscription = xml_processor._process_single_inscription(xml_file)
            if inscription:
                successful += 1

        print(f"✅ Batch test completed: {successful}/{len(test_files)} files processed")

        return True

    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_inscription_model():
    """Test the inscription data model"""
    print("\n🧪 Testing Inscription Model...")

    try:
        from ecg_processor.config import ECGConfig
        from ecg_processor.xml_processor import XMLProcessor
        from pathlib import Path

        config = ECGConfig()
        xml_processor = XMLProcessor(config)

        # Process bibliography first
        xml_processor._process_bibliography()

        # Find a test file
        xml_files = list(Path(config.xml_dir).glob("*.xml"))
        if not xml_files:
            print("❌ No XML files found")
            return False

        test_file = xml_files[0]
        inscription = xml_processor._process_single_inscription(test_file)

        if inscription:
            print("✅ Inscription model working:")
            print(f"   Display title: {inscription.get_display_title()}")
            print(f"   Has images: {inscription.has_images()}")
            print(f"   Primary place: {inscription.get_primary_place()}")
            print(f"   Dating text: {inscription.get_dating_text()}")

            return True
        else:
            print("❌ Failed to create inscription model")
            return False

    except Exception as e:
        print(f"❌ Inscription model test failed: {e}")
        return False

def test_limited_full_pipeline():
    """Test the full pipeline with a limited number of files"""
    print("\n🧪 Testing Limited Full Pipeline...")

    try:
        from ecg_processor.main import ECGProcessor

        # Temporarily modify config to process fewer files for testing
        processor = ECGProcessor()

        # Override the XML processor to limit files
        original_process = processor.xml_processor.process_all_inscriptions

        def limited_process():
            print("📄 Processing first 10 XML files for testing...")
            xml_files = sorted(Path(processor.config.xml_dir).glob("*.xml"))[:10]

            processor.xml_processor._process_bibliography()

            inscriptions = []
            for xml_file in xml_files:
                inscription = processor.xml_processor._process_single_inscription(xml_file)
                if inscription:
                    inscriptions.append(inscription)

            processor.xml_processor._build_bibliography_references(inscriptions)
            print(f"✅ Limited processing complete: {len(inscriptions)} inscriptions")
            return inscriptions

        processor.xml_processor.process_all_inscriptions = limited_process

        # Run the pipeline
        count = processor.process_all()

        if count > 0:
            print(f"✅ Limited pipeline successful: {count} inscriptions")
            return True
        else:
            print("❌ Limited pipeline failed")
            return False

    except Exception as e:
        print(f"❌ Limited pipeline test failed: {e}")
        return False

def main():
    """Run all pipeline tests"""
    print("🚀 Testing ECG XML Processing Pipeline")
    print("=" * 60)

    tests = [
        test_xml_processing_pipeline,
        test_inscription_model,
        test_limited_full_pipeline
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test crashed: {e}")

    print("\n" + "=" * 60)
    print(f"🎯 Pipeline Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All XML processing tests passed!")
        print("🔄 Ready for Step 4: Content Generation")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
