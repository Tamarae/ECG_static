#!/usr/bin/env python3
"""
Fixed GeoJSON Converter - Ensures proper data types for Mapbox
Run this to replace your existing GeoJSON with properly typed data
"""

import json
from pathlib import Path

def convert_to_geojson_fixed():
    """Convert ECG map data to GeoJSON with proper data types"""

    try:
        # Load the existing map data
        input_file = Path("map-data.json")
        if not input_file.exists():
            print("❌ map-data.json not found in current directory")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            map_data = json.load(f)

        print(f"🗺️ Converting {len(map_data)} locations with proper data types...")

        # Create GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        # Convert each location to a GeoJSON feature with proper types
        for location in map_data:
            # Get primary language for the location
            languages = location.get('languages', {})
            primary_language = get_primary_language(languages)

            # Convert language counts to integers
            languages_typed = {}
            for lang, count in languages.items():
                languages_typed[lang] = int(count)  # Ensure integer

            # Create inscriptions list with proper structure
            inscriptions = location.get('inscriptions', [])

            # Create the GeoJSON feature with PROPER DATA TYPES
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(location['lon']),  # Ensure float
                        float(location['lat'])   # Ensure float
                    ]
                },
                "properties": {
                    # STRING FIELDS
                    "place": str(location['place']),
                    "primary_language": str(primary_language),
                    "popup_title": str(location['place']),
                    "popup_subtitle": f"{location['count']} inscriptions",
                    "popup_languages": create_language_summary(languages),

                    # INTEGER FIELDS (critical for sizing!)
                    "count": int(location['count']),
                    "inscription_count": int(len(inscriptions)),

                    # BOOLEAN FIELDS
                    "has_multiple_languages": len(languages) > 1,
                    "is_major_site": int(location['count']) >= 10,

                    # NUMERIC FIELDS for styling
                    "size_category": calculate_size_category(int(location['count'])),
                    "language_diversity": len(languages),

                    # STRUCTURED DATA
                    "languages": languages_typed,  # Object with integer values
                    "inscriptions": inscriptions,  # Array

                    # Additional useful fields
                    "georgian_count": languages_typed.get('ka', 0),
                    "greek_count": languages_typed.get('grc', 0),
                    "armenian_count": languages_typed.get('hy', 0),
                    "aramaic_count": languages_typed.get('arc', 0),
                    "hebrew_count": languages_typed.get('he', 0),
                }
            }

            geojson["features"].append(feature)

        # Save fixed GeoJSON file
        output_file = Path("ecg-inscriptions-fixed.geojson")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)

        print(f"✅ Fixed GeoJSON created successfully!")
        print(f"📄 Output file: {output_file.absolute()}")
        print(f"📊 Features: {len(geojson['features'])}")

        # Validate data types
        validate_data_types(geojson["features"])

        print("\n🎯 Next steps:")
        print("1. Delete your current ECG tileset in Mapbox Studio")
        print("2. Upload the NEW ecg-inscriptions-fixed.geojson file")
        print("3. The numeric fields will now work properly for styling!")

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
    total = sum(int(count) for count in languages.values())
    for lang, count in languages.items():
        if int(count) / total > 0.7:  # If one language is >70%
            return lang

    # If mixed, return 'mixed'
    return 'mixed'

def calculate_size_category(count):
    """Calculate size category as integer for easier styling"""
    if count == 1:
        return 1  # small
    elif count <= 5:
        return 2  # medium
    elif count <= 10:
        return 3  # large
    else:
        return 4  # extra-large

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
    for lang, count in sorted(languages.items(), key=lambda x: int(x[1]), reverse=True):
        lang_name = language_names.get(lang, lang.upper())
        parts.append(f"{lang_name}: {count}")

    return ", ".join(parts)

def validate_data_types(features):
    """Validate that data types are correct"""
    print("\n🔍 Validating data types...")

    if not features:
        print("❌ No features to validate")
        return

    sample_feature = features[0]
    props = sample_feature["properties"]

    # Check critical numeric fields
    numeric_fields = ["count", "inscription_count", "size_category", "language_diversity"]
    for field in numeric_fields:
        if field in props:
            value = props[field]
            if isinstance(value, int):
                print(f"✅ {field}: {value} (integer)")
            else:
                print(f"❌ {field}: {value} (type: {type(value).__name__})")

    # Check string fields
    string_fields = ["place", "primary_language", "popup_title"]
    for field in string_fields:
        if field in props:
            value = props[field]
            if isinstance(value, str):
                print(f"✅ {field}: '{value}' (string)")
            else:
                print(f"❌ {field}: {value} (type: {type(value).__name__})")

    # Check boolean fields
    bool_fields = ["has_multiple_languages", "is_major_site"]
    for field in bool_fields:
        if field in props:
            value = props[field]
            if isinstance(value, bool):
                print(f"✅ {field}: {value} (boolean)")
            else:
                print(f"❌ {field}: {value} (type: {type(value).__name__})")

    print("🎯 Data type validation complete!")

def create_styling_guide():
    """Create a guide for styling in Mapbox Studio"""

    guide = """
# Mapbox Studio Styling Guide

## Color by Language (use primary_language field):
```
Expression for Color:
[
  "case",
  ["==", ["get", "primary_language"], "ka"], "#27ae60",
  ["==", ["get", "primary_language"], "grc"], "#3498db",
  ["==", ["get", "primary_language"], "hy"], "#e67e22",
  ["==", ["get", "primary_language"], "arc"], "#f39c12",
  ["==", ["get", "primary_language"], "he"], "#9b59b6",
  ["==", ["get", "primary_language"], "la"], "#34495e",
  ["==", ["get", "primary_language"], "mixed"], "#9b59b6",
  "#95a5a6"
]
```

## Size by Count (use count field - now properly numeric):
- Data field: `count`
- Style type: Interpolate
- Stops: 1→8px, 5→12px, 10→16px, 25→24px

## Alternative Size by Category (use size_category field):
- Data field: `size_category`
- Style type: Categorical
- 1→8px, 2→12px, 3→16px, 4→24px

## Useful Numeric Fields:
- `count` - total inscriptions (for sizing)
- `georgian_count` - number of Georgian inscriptions
- `greek_count` - number of Greek inscriptions
- `language_diversity` - number of different languages
- `is_major_site` - boolean for sites with 10+ inscriptions

## Popup Content:
- Title: `{{popup_title}}`
- Subtitle: `{{popup_subtitle}}`
- Languages: `{{popup_languages}}`
"""

    with open("mapbox-styling-guide.md", 'w', encoding='utf-8') as f:
        f.write(guide)

    print("📋 Created mapbox-styling-guide.md with styling instructions!")

if __name__ == "__main__":
    print("🔧 ECG GeoJSON Data Type Fixer")
    print("=" * 50)

    output_file = convert_to_geojson_fixed()

    if output_file:
        create_styling_guide()

        print("\n" + "=" * 50)
        print("🎉 Fixed GeoJSON ready!")
        print("\n📋 Key improvements:")
        print("   ✅ count field is now INTEGER (not string)")
        print("   ✅ Added size_category field (1-4)")
        print("   ✅ Added individual language counts")
        print("   ✅ Added boolean fields for filtering")
        print("   ✅ Proper data types for all fields")
        print("\n🔄 Next: Delete old tileset and upload the FIXED version!")
    else:
        print("\n❌ Fix failed!")
