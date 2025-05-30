#!/usr/bin/env python3
"""
Map Debug Script - Analyze map-data.json to identify coordinate jumping issues
Run this script in your output directory to debug map issues
"""

import json
import math
from collections import defaultdict
from pathlib import Path

def analyze_map_data():
    """Analyze map-data.json for coordinate clustering and other issues"""

    try:
        # Load the map data
        map_data_file = Path("map-data.json")
        if not map_data_file.exists():
            print("❌ map-data.json not found in current directory")
            return

        with open(map_data_file, 'r', encoding='utf-8') as f:
            map_data = json.load(f)

        print(f"🗺️ Analyzing {len(map_data)} map locations...")

        # 1. Check coordinate validity
        print("\n1️⃣ COORDINATE VALIDITY CHECK:")
        invalid_coords = []
        for location in map_data:
            lat, lon = location.get('lat'), location.get('lon')
            place = location.get('place', 'Unknown')

            if lat is None or lon is None:
                invalid_coords.append(f"   ❌ {place}: Missing coordinates")
            elif not (35 <= lat <= 50 and 35 <= lon <= 50):
                invalid_coords.append(f"   ⚠️ {place}: Suspicious coordinates ({lat}, {lon})")

        if invalid_coords:
            print(f"Found {len(invalid_coords)} coordinate issues:")
            for issue in invalid_coords[:10]:  # Show first 10
                print(issue)
            if len(invalid_coords) > 10:
                print(f"   ... and {len(invalid_coords) - 10} more issues")
        else:
            print("✅ All coordinates are valid")

        # 2. Check for coordinate clustering
        print("\n2️⃣ COORDINATE CLUSTERING ANALYSIS:")
        coordinate_groups = defaultdict(list)

        for location in map_data:
            lat, lon = location.get('lat'), location.get('lon')
            if lat is not None and lon is not None:
                # Round to 4 decimal places for clustering detection
                coord_key = f"{lat:.4f},{lon:.4f}"
                coordinate_groups[coord_key].append(location['place'])

        # Find clusters
        clusters = {k: v for k, v in coordinate_groups.items() if len(v) > 1}

        if clusters:
            print(f"⚠️ Found {len(clusters)} coordinate clusters:")
            for coord, places in list(clusters.items())[:10]:  # Show first 10
                print(f"   📍 {coord}: {len(places)} places")
                for place in places[:3]:  # Show first 3 places
                    print(f"      - {place}")
                if len(places) > 3:
                    print(f"      - ... and {len(places) - 3} more")

            if len(clusters) > 10:
                print(f"   ... and {len(clusters) - 10} more clusters")

            print(f"\n💡 CLUSTERING IMPACT:")
            total_clustered = sum(len(places) for places in clusters.values())
            print(f"   - {total_clustered} locations are clustered")
            print(f"   - This affects {total_clustered/len(map_data)*100:.1f}% of all locations")
            print(f"   - May cause pin jumping when clicking between clustered locations")
        else:
            print("✅ No coordinate clustering detected")

        # 3. Check coordinate distribution
        print("\n3️⃣ COORDINATE DISTRIBUTION:")
        lats = [loc['lat'] for loc in map_data if loc.get('lat') is not None]
        lons = [loc['lon'] for loc in map_data if loc.get('lon') is not None]

        if lats and lons:
            lat_range = max(lats) - min(lats)
            lon_range = max(lons) - min(lons)

            print(f"   📏 Latitude range: {min(lats):.4f} to {max(lats):.4f} (span: {lat_range:.4f}°)")
            print(f"   📏 Longitude range: {min(lons):.4f} to {max(lons):.4f} (span: {lon_range:.4f}°)")
            print(f"   📐 Center point: {sum(lats)/len(lats):.4f}, {sum(lons)/len(lons):.4f}")

            # Check if coordinates are too tightly clustered
            if lat_range < 1.0 and lon_range < 1.0:
                print("   ⚠️ Coordinates are tightly clustered - may cause zoom/pan issues")
            elif lat_range > 20 or lon_range > 20:
                print("   ⚠️ Coordinates are very spread out - may cause fitting issues")
            else:
                print("   ✅ Coordinate distribution looks reasonable")

        # 4. Check inscription data quality
        print("\n4️⃣ INSCRIPTION DATA QUALITY:")
        total_inscriptions = sum(loc.get('count', 0) for loc in map_data)
        locations_with_inscriptions = sum(1 for loc in map_data if loc.get('inscriptions'))
        locations_with_languages = sum(1 for loc in map_data if loc.get('languages'))

        print(f"   📊 Total inscriptions: {total_inscriptions}")
        print(f"   📊 Locations with inscription data: {locations_with_inscriptions}/{len(map_data)}")
        print(f"   📊 Locations with language data: {locations_with_languages}/{len(map_data)}")

        # Check for missing inscription data
        missing_data = []
        for location in map_data:
            place = location.get('place', 'Unknown')
            if not location.get('inscriptions'):
                missing_data.append(f"   ❌ {place}: No inscription list")
            elif not location.get('languages'):
                missing_data.append(f"   ⚠️ {place}: No language data")

        if missing_data:
            print(f"\n   Data quality issues found:")
            for issue in missing_data[:5]:  # Show first 5
                print(issue)
            if len(missing_data) > 5:
                print(f"   ... and {len(missing_data) - 5} more issues")

        # 5. Language distribution
        print("\n5️⃣ LANGUAGE DISTRIBUTION:")
        all_languages = defaultdict(int)

        for location in map_data:
            languages = location.get('languages', {})
            for lang, count in languages.items():
                all_languages[lang] += count

        if all_languages:
            print("   Language breakdown:")
            for lang, count in sorted(all_languages.items(), key=lambda x: x[1], reverse=True):
                percentage = count / total_inscriptions * 100 if total_inscriptions > 0 else 0
                print(f"   📈 {lang}: {count} ({percentage:.1f}%)")

        # 6. Generate recommendations
        print("\n6️⃣ RECOMMENDATIONS:")
        recommendations = []

        if clusters:
            recommendations.append("🔧 Apply coordinate spreading to clustered locations")
            recommendations.append("🔧 Use the fixed map handler with coordinate offset logic")

        if invalid_coords:
            recommendations.append("🔧 Fix invalid coordinates in your coordinate mapping")

        if len(missing_data) > len(map_data) * 0.1:  # If >10% have missing data
            recommendations.append("🔧 Improve inscription data processing in your Python script")

        if lat_range < 0.5 or lon_range < 0.5:
            recommendations.append("🔧 Increase map padding to prevent over-zooming")

        if not recommendations:
            recommendations.append("✅ Map data looks good! Issue might be in JavaScript handling")

        for rec in recommendations:
            print(f"   {rec}")

        # 7. Generate coordinate fix suggestions
        if clusters:
            print(f"\n7️⃣ COORDINATE FIX SUGGESTIONS:")
            print("   Add this to your processor to fix clustering:")
            print("""
   # In your generate_map_data method, add coordinate spreading:
   if coord_key in coordinate_usage:
       offset_angle = len(coordinate_usage[coord_key]) * (2 * math.pi / 8)
       offset_distance = 0.008  # Small offset in degrees
       lat += offset_distance * math.cos(offset_angle)
       lon += offset_distance * math.sin(offset_angle)
            """)

        print(f"\n✅ Analysis complete! Check the recommendations above.")

    except Exception as e:
        print(f"❌ Error analyzing map data: {e}")
        import traceback
        traceback.print_exc()

def check_browser_console_issues():
    """Provide guidance for checking browser console issues"""
    print("\n🌐 BROWSER DEBUGGING TIPS:")
    print("""
   1. Open your browser's Developer Tools (F12)
   2. Go to the Console tab
   3. Reload your map page
   4. Look for these common issues:

   ❌ "Failed to fetch map-data.json"
      → Check if the file exists and is accessible

   ❌ "Invalid coordinates" or NaN errors
      → Check coordinate data types (should be numbers, not strings)

   ❌ "Cannot read property 'lat' of undefined"
      → Check map data structure

   ❌ Mapbox GL errors about bounds or coordinates
      → Check if coordinates are valid numbers in correct ranges

   5. In the Network tab, check if map-data.json loads successfully
   6. In the Console, try: console.log(mapHandler.mapData) to see loaded data
   """)

if __name__ == "__main__":
    print("🔍 ECG Map Debug Script")
    print("=" * 50)

    analyze_map_data()
    check_browser_console_issues()

    print("\n" + "=" * 50)
    print("🏁 Debug complete! Use the recommendations above to fix issues.")
