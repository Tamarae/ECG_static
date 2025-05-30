#!/usr/bin/env python3
"""
ECG Processor - Main Runner Script
Convenience script for running the complete ECG processing pipeline
"""
import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point with command line arguments"""
    parser = argparse.ArgumentParser(
        description='ECG Inscription Processor - Generate digital corpus website',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ecg_processor.py                    # Process all inscriptions
  python run_ecg_processor.py --config custom.json   # Use custom config
  python run_ecg_processor.py --test            # Test with limited files
  python run_ecg_processor.py --verbose         # Show detailed output
        """
    )

    parser.add_argument('--config', '-c',
                       help='Path to configuration file (JSON)')
    parser.add_argument('--test', '-t', action='store_true',
                       help='Test mode: process only first 50 inscriptions')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with detailed progress')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force processing even if output directory exists')

    args = parser.parse_args()

    try:
        # Import after path setup
        from ecg_processor.main import ECGProcessor
        from ecg_processor.config import ECGConfig

        # Show header
        print("🏛️ ECG - Epigraphic Corpus of Georgia")
        print("📜 Digital Inscription Processing Pipeline")
        print("=" * 50)

        # Create processor with optional config
        processor = ECGProcessor(args.config)

        # Test mode: limit processing
        if args.test:
            print("🧪 TEST MODE: Processing limited inscriptions...")
            original_process = processor.xml_processor.process_all_inscriptions

            def limited_process():
                print("📄 Processing first 50 XML files...")

                # Process bibliography
                processor.xml_processor._process_bibliography()

                # Get limited XML files
                xml_files = sorted(Path(processor.config.xml_dir).glob("*.xml"))[:50]

                # Process inscriptions
                inscriptions = []
                for xml_file in xml_files:
                    inscription = processor.xml_processor._process_single_inscription(xml_file)
                    if inscription:
                        inscriptions.append(inscription)

                # Build bibliography references
                processor.xml_processor._build_bibliography_references(inscriptions)

                return inscriptions

            processor.xml_processor.process_all_inscriptions = limited_process

        # Check if output directory exists
        output_path = Path(processor.config.output_dir)
        if output_path.exists() and not args.force:
            response = input(f"Output directory {output_path} exists. Continue? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("Processing cancelled.")
                return 0

        # Run processing
        count = processor.process_all()

        if count > 0:
            print(f"\n🎉 Processing completed successfully!")
            if args.test:
                print(f"🧪 Test mode: Processed {count} inscriptions")
            else:
                print(f"✅ Full processing: {count} inscriptions")

            # Show website URL
            print(f"\n🌐 Your ECG website is ready!")
            print(f"   📁 Location: {output_path.absolute()}")
            print(f"   🔗 Open: file://{output_path.absolute()}/index.html")

            return 0
        else:
            print("❌ Processing failed - no inscriptions were processed")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
