#!/usr/bin/env python3
"""
Convert ECG map-data.json to GeoJSON format for Mapbox upload
Run this in your output directory where map-data.json is located
"""

import json
from pathlib import Path

def convert_to_geojson():
    """Convert ECG map data to GeoJSON format"""

    try:
        # Load the existing map data
        input_file = Path("map-data.json")
        if not input_file.exists():
            print("❌ map-data.json not found in current directory")
            print(f"📁 Current directory: {Path.cwd()}")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            map_data = json.load(f)

        print(f"🗺️ Converting {len(map_data)} locations to GeoJSON...")

        # Create GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        # Convert each location to a GeoJSON feature
        for location in map_data:
            # Get primary language for the location
            languages = location.get('languages', {})
            primary_language = get_primary_language(languages)

            # Create language summary for popup
            language_summary = create_language_summary(languages)

            # Create inscriptions summary for popup
            inscriptions_summary = create_inscriptions_summary(location.get('inscriptions', []))

            # Create the GeoJSON feature
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(location['lon']),
                        float(location['lat'])
                    ]
                },
                "properties": {
                    # Basic info
                    "place": location['place'],
                    "count": location['count'],

                    # Language info
                    "primary_language": primary_language,
                    "languages": languages,
                    "language_summary": language_summary,

                    # For styling
                    "marker_color": get_language_color(primary_language),
                    "marker_size": calculate_marker_size(location['count']),

                    # For popups
                    "popup_title": location['place'],
                    "popup_subtitle": f"{location['count']} inscriptions",
                    "popup_languages": language_summary,
                    "inscriptions_summary": inscriptions_summary,

                    # Raw data for advanced use
                    "inscriptions": location.get('inscriptions', [])
                }
            }

            geojson["features"].append(feature)

        # Save GeoJSON file
        output_file = Path("ecg-inscriptions.geojson")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)

        print(f"✅ GeoJSON created successfully!")
        print(f"📄 Output file: {output_file.absolute()}")
        print(f"📊 Features: {len(geojson['features'])}")

        # Print summary statistics
        print_conversion_summary(geojson["features"])

        # Create a simplified version for faster loading
        create_simplified_geojson(geojson)

        print("\n🎯 Next steps:")
        print("1. Go to https://studio.mapbox.com")
        print("2. Create a new dataset or tileset")
        print("3. Upload the ecg-inscriptions.geojson file")
        print("4. Style your map with language-based colors")
        print("5. Publish and get your map style URL")

        return output_file

    except Exception as e:
        print(f"❌ Error converting to GeoJSON: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_primary_language(languages):
    """Determine the primary language for a location"""
    if not languages:
        return 'unknown'

    # If only one language, return it
    if len(languages) == 1:
        return list(languages.keys())[0]

    # If multiple languages, check if one dominates
    total = sum(languages.values())
    for lang, count in languages.items():
        if count / total > 0.7:  # If one language is >70%
            return lang

    # If mixed, return 'mixed'
    return 'mixed'

def get_language_color(primary_language):
    """Get color for language-based styling"""
    colors = {
        'ka': '#27ae60',      # Georgian - Green
        'grc': '#3498db',     # Greek - Blue
        'hy': '#e67e22',      # Armenian - Orange
        'he': '#9b59b6',      # Hebrew - Purple
        'ar': '#e74c3c',      # Arabic - Red
        'arc': '#f39c12',     # Aramaic - Orange
        'la': '#34495e',      # Latin - Dark Blue
        'ru': '#f39c12',      # Cyrillic - Orange
        'mixed': '#9b59b6',   # Mixed - Purple
        'unknown': '#95a5a6'  # Unknown - Gray
    }
    return colors.get(primary_language, colors['unknown'])

def calculate_marker_size(count):
    """Calculate marker size based on inscription count"""
    if count == 1:
        return 'small'
    elif count <= 5:
        return 'medium'
    elif count <= 10:
        return 'large'
    else:
        return 'extra-large'

def create_language_summary(languages):
    """Create a readable language summary"""
    if not languages:
        return "Unknown language"

    language_names = {
        'ka': 'Georgian',
        'grc': 'Greek',
        'hy': 'Armenian',
        'he': 'Hebrew',
        'ar': 'Arabic',
        'arc': 'Aramaic',
        'la': 'Latin',
        'ru': 'Russian',
        'unknown': 'Unknown'
    }

    parts = []
    for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
        lang_name = language_names.get(lang, lang.upper())
        parts.append(f"{lang_name}: {count}")

    return ", ".join(parts)

def create_inscriptions_summary(inscriptions):
    """Create a summary of inscriptions for popups"""
    if not inscriptions:
        return "No inscriptions data"

    # Limit to first 5 inscriptions for popup
    max_show = 5
    summary_parts = []

    for i, inscription in enumerate(inscriptions[:max_show]):
        title = inscription.get('title', f"Inscription {inscription.get('id', i+1)}")
        # Truncate long titles
        if len(title) > 60:
            title = title[:57] + "..."
        summary_parts.append(title)

    if len(inscriptions) > max_show:
        summary_parts.append(f"... and {len(inscriptions) - max_show} more")

    return " | ".join(summary_parts)

def create_simplified_geojson(full_geojson):
    """Create a simplified version with minimal properties for faster loading"""

    simplified = {
        "type": "FeatureCollection",
        "features": []
    }

    for feature in full_geojson["features"]:
        simplified_feature = {
            "type": "Feature",
            "geometry": feature["geometry"],
            "properties": {
                "place": feature["properties"]["place"],
                "count": feature["properties"]["count"],
                "primary_language": feature["properties"]["primary_language"],
                "marker_color": feature["properties"]["marker_color"],
                "marker_size": feature["properties"]["marker_size"],
                "popup_title": feature["properties"]["popup_title"],
                "popup_subtitle": feature["properties"]["popup_subtitle"]
            }
        }
        simplified["features"].append(simplified_feature)

    # Save simplified version
    with open("ecg-inscriptions-simple.geojson", 'w', encoding='utf-8') as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)

    print(f"📄 Also created simplified version: ecg-inscriptions-simple.geojson")

def print_conversion_summary(features):
    """Print summary of the conversion"""

    # Count by language
    language_counts = {}
    size_counts = {'small': 0, 'medium': 0, 'large': 0, 'extra-large': 0}

    for feature in features:
        primary_lang = feature["properties"]["primary_language"]
        marker_size = feature["properties"]["marker_size"]

        language_counts[primary_lang] = language_counts.get(primary_lang, 0) + 1
        size_counts[marker_size] += 1

    print(f"\n📊 Conversion Summary:")
    print(f"   Languages:")
    for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(features)) * 100
        print(f"      {lang}: {count} locations ({percentage:.1f}%)")

    print(f"   Marker sizes:")
    for size, count in size_counts.items():
        if count > 0:
            print(f"      {size}: {count} locations")

def validate_geojson(geojson_file):
    """Basic validation of the created GeoJSON"""
    try:
        with open(geojson_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get("type") != "FeatureCollection":
            print("⚠️ Warning: Not a valid FeatureCollection")
            return False

        features = data.get("features", [])
        if not features:
            print("⚠️ Warning: No features found")
            return False

        # Check a few features
        for i, feature in enumerate(features[:3]):
            if feature.get("type") != "Feature":
                print(f"⚠️ Warning: Feature {i} is not a valid Feature")
                return False

            geometry = feature.get("geometry", {})
            if geometry.get("type") != "Point":
                print(f"⚠️ Warning: Feature {i} geometry is not a Point")
                return False

            coordinates = geometry.get("coordinates", [])
            if len(coordinates) != 2:
                print(f"⚠️ Warning: Feature {i} has invalid coordinates")
                return False

        print("✅ GeoJSON validation passed!")
        return True

    except Exception as e:
        print(f"❌ GeoJSON validation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔄 ECG Map Data to GeoJSON Converter")
    print("=" * 50)

    output_file = convert_to_geojson()

    if output_file:
        print("\n🔍 Validating GeoJSON...")
        validate_geojson(output_file)

        print("\n" + "=" * 50)
        print("🎉 Conversion complete!")
        print("\n📋 Files created:")
        print("   - ecg-inscriptions.geojson (full data)")
        print("   - ecg-inscriptions-simple.geojson (simplified)")
        print("\n🚀 Ready for Mapbox Studio upload!")
    else:
        print("\n❌ Conversion failed!")
