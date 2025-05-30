#!/usr/bin/env python3
"""
Test the complete ECG processing pipeline
This tests the full modular system end-to-end
"""
import sys
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_complete_pipeline():
    """Test the complete processing pipeline with limited data for speed"""
    print("🚀 Testing Complete ECG Processing Pipeline")
    print("=" * 60)

    start_time = time.time()

    try:
        from ecg_processor.main import ECGProcessor

        # Create processor
        print("🔧 Initializing ECG processor...")
        processor = ECGProcessor()

        # Verify configuration
        print("✅ Configuration validated:")
        print(f"   📁 XML files: {processor.config.xml_dir}")
        print(f"   📁 Output: {processor.config.output_dir}")
        print(f"   📁 Images: {processor.config.images_dir}")

        # Override processing to limit files for testing
        original_process = processor.xml_processor.process_all_inscriptions

        def limited_process_for_testing():
            """Process only first 20 XML files for testing"""
            print("📄 Processing first 20 XML files for testing...")

            # Process bibliography
            processor.xml_processor._process_bibliography()

            # Get limited XML files
            xml_files = sorted(Path(processor.config.xml_dir).glob("*.xml"))[:20]
            print(f"📋 Selected {len(xml_files)} files for testing")

            # Process inscriptions
            inscriptions = []
            successful = 0

            for xml_file in xml_files:
                inscription = processor.xml_processor._process_single_inscription(xml_file)
                if inscription:
                    inscriptions.append(inscription)
                    successful += 1

            # Build bibliography references
            processor.xml_processor._build_bibliography_references(inscriptions)

            print(f"✅ Test processing complete: {successful} inscriptions")
            return inscriptions

        # Use limited processing for testing
        processor.xml_processor.process_all_inscriptions = limited_process_for_testing

        # Run the complete pipeline
        print("\n🏭 Running complete processing pipeline...")
        count = processor.process_all()

        elapsed_time = time.time() - start_time

        if count > 0:
            print(f"\n🎉 Complete pipeline test successful!")
            print(f"   ✅ Processed: {count} inscriptions")
            print(f"   ⏱️ Time: {elapsed_time:.1f} seconds")
            print(f"   📈 Speed: {count/elapsed_time:.1f} inscriptions/second")

            # Verify output files were created
            output_path = Path(processor.config.output_dir)

            expected_files = [
                "index.html",
                "browse.html",
                "bibliography.html",
                "search-data.json",
                "static/css/style.css",
                "static/js/tabs.js",
                "static/js/browse.js",
                "static/js/bibliography.js"
            ]

            print(f"\n📁 Verifying output files...")
            missing_files = []
            existing_files = []

            for file_path in expected_files:
                full_path = output_path / file_path
                if full_path.exists():
                    size = full_path.stat().st_size
                    existing_files.append(f"{file_path} ({size} bytes)")
                else:
                    missing_files.append(file_path)

            if existing_files:
                print("✅ Created files:")
                for file_info in existing_files:
                    print(f"   📄 {file_info}")

            if missing_files:
                print("⚠️ Missing files:")
                for file_path in missing_files:
                    print(f"   ❌ {file_path}")

            # Check inscription pages
            inscriptions_dir = output_path / "inscriptions"
            if inscriptions_dir.exists():
                inscription_files = list(inscriptions_dir.glob("*.html"))
                print(f"✅ Generated {len(inscription_files)} inscription pages")
            else:
                print("❌ No inscription pages directory found")

            # Check images
            images_dir = output_path / "static" / "images"
            if images_dir.exists():
                image_files = list(images_dir.rglob("*"))
                image_count = len([f for f in image_files if f.is_file()])
                print(f"✅ Copied {image_count} image files")
            else:
                print("⚠️ No images directory found")

            print(f"\n🌐 Test site ready at:")
            print(f"   file://{output_path.absolute()}/index.html")

            return True

        else:
            print("❌ Complete pipeline test failed - no inscriptions processed")
            return False

    except Exception as e:
        print(f"❌ Complete pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_modular_components():
    """Test individual modular components"""
    print("\n🧪 Testing Individual Modular Components")
    print("=" * 50)

    try:
        from ecg_processor.config import ECGConfig
        from ecg_processor.xml_processor import XMLProcessor
        from ecg_processor.generators.page_generator import PageGenerator
        from ecg_processor.generators.css_generator import CSSGenerator
        from ecg_processor.generators.js_generator import JSGenerator
        from ecg_processor.asset_manager import AssetManager

        config = ECGConfig()

        # Test XML processor
        print("📄 Testing XML processor...")
        xml_processor = XMLProcessor(config)
        xml_processor._process_bibliography()
        print(f"✅ XML processor: {len(xml_processor.bibliography)} bibliography entries")

        # Test generators
        print("🎨 Testing CSS generator...")
        css_gen = CSSGenerator(config)
        print("✅ CSS generator initialized")

        print("📜 Testing JS generator...")
        js_gen = JSGenerator(config)
        print("✅ JS generator initialized")

        print("🖼️ Testing asset manager...")
        asset_mgr = AssetManager(config)
        print("✅ Asset manager initialized")

        print("📄 Testing page generator...")
        page_gen = PageGenerator(config)
        print("✅ Page generator initialized")

        return True

    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 ECG Modular Processor - Complete Testing Suite")
    print("=" * 70)

    tests = [
        ("Modular Components", test_modular_components),
        ("Complete Pipeline", test_complete_pipeline)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test CRASHED: {e}")

    print("\n" + "=" * 70)
    print(f"🎯 Final Results: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! The modular ECG processor is working perfectly!")
        print("🚀 You can now run: python -m ecg_processor.main")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

    print("=" * 70)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
