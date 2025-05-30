#!/usr/bin/env python3
"""
Fixed ECG Processor Launch Script
Adapts the enhanced processor to work with your existing directory structure
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import your original processor but with enhancements
from enhanced_ecg_processor import RobustECGProcessorEnhanced

def main():
    """Main entry point"""
    try:
        print("🚀 Launching Enhanced ECG Processor...")
        print("📁 Working directory:", current_dir)

        # Create and run the enhanced processor
        processor = RobustECGProcessorEnhanced()
        successful_count = processor.process_all()

        if successful_count > 0:
            print(f"\n🎉 Processing completed successfully!")
            print(f"✨ Enhanced academic design with sophisticated styling")
            print(f"📚 {successful_count} inscriptions processed with full metadata")
            return 0
        else:
            print(f"\n❌ Processing failed - no inscriptions were processed")
            return 1

    except Exception as e:
        print(f"❌ Fatal error in main processing: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
