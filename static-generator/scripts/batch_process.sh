#!/bin/bash
# ECG Batch Processing Script
# Automated processing with error handling and backup

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="../output"
BACKUP_DIR="../backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="processing_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏛️ ECG Batch Processing Script${NC}"
echo -e "${BLUE}================================${NC}"

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    log "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -d "ecg_processor" ]]; then
    log "${RED}❌ ECG processor not found. Run this script from the scripts directory${NC}"
    exit 1
fi

# Create backup if output exists
if [[ -d "$OUTPUT_DIR" ]]; then
    log "${YELLOW}📋 Creating backup of existing output...${NC}"
    mkdir -p "$BACKUP_DIR"
    cp -r "$OUTPUT_DIR" "$BACKUP_DIR/"
    log "${GREEN}✅ Backup created: $BACKUP_DIR${NC}"
fi

# Run the processor
log "${BLUE}🚀 Starting ECG processing...${NC}"
start_time=$(date +%s)

if python3 run_ecg_processor.py --verbose 2>&1 | tee -a "$LOG_FILE"; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))

    log "${GREEN}🎉 Processing completed successfully!${NC}"
    log "${GREEN}⏱️ Total time: ${duration} seconds${NC}"

    # Show output statistics
    if [[ -d "$OUTPUT_DIR" ]]; then
        html_count=$(find "$OUTPUT_DIR" -name "*.html" | wc -l)
        css_count=$(find "$OUTPUT_DIR" -name "*.css" | wc -l)
        js_count=$(find "$OUTPUT_DIR" -name "*.js" | wc -l)
        img_count=$(find "$OUTPUT_DIR" -name "*.jpg" -o -name "*.png" -o -name "*.gif" | wc -l)

        log "${GREEN}📊 Generated files:${NC}"
        log "${GREEN}   📄 HTML files: $html_count${NC}"
        log "${GREEN}   🎨 CSS files: $css_count${NC}"
        log "${GREEN}   📜 JS files: $js_count${NC}"
        log "${GREEN}   🖼️ Images: $img_count${NC}"

        # Show website URL
        abs_path=$(cd "$OUTPUT_DIR" && pwd)
        log "${BLUE}🌐 Your website is ready:${NC}"
        log "${BLUE}   file://$abs_path/index.html${NC}"
    fi

else
    log "${RED}❌ Processing failed. Check the log for details.${NC}"
    exit 1
fi

# Cleanup old backups (keep last 5)
if [[ -d "../backups" ]]; then
    backup_count=$(find ../backups -maxdepth 1 -type d | wc -l)
    if [[ $backup_count -gt 6 ]]; then  # 6 because find includes the backups dir itself
        log "${YELLOW}🧹 Cleaning up old backups...${NC}"
        find ../backups -maxdepth 1 -type d | head -n -5 | xargs rm -rf
        log "${GREEN}✅ Old backups cleaned up${NC}"
    fi
fi

log "${GREEN}✅ Batch processing complete!${NC}"
log "${BLUE}📋 Log saved to: $LOG_FILE${NC}"
