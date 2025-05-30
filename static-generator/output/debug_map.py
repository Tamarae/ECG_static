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
            print(f"📁 Current directory: {Path.cwd()}")
            print("📁 Files in directory:", list(Path.cwd().glob("*.json")))
            return

        with open(map_data_file, 'r', encoding='utf-8') as f:
            map_data = json.load(f)

        print(f"🗺️ Analyzing {len(map_data)} map locations...")

        # 1. Check coordinate validity
        print("\n1️⃣ COORDINATE VALIDITY CHECK:")
        invalid_coords = []
        valid_coords = []

        for location in map_data:
            lat, lon = location.get('lat'), location.get('lon')
            place = location.get('place', 'Unknown')

            if lat is None or lon is None:
                invalid_coords.append(f"   ❌ {place}: Missing coordinates")
            elif not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                invalid_coords.append(f"   ❌ {place}: Invalid coordinate types ({type(lat)}, {type(lon)})")
            elif not (35 <= lat <= 50 and 35 <= lon <= 50):
                invalid_coords.append(f"   ⚠️ {place}: Suspicious coordinates ({lat}, {lon})")
            else:
                valid_coords.append((lat, lon, place))

        if invalid_coords:
            print(f"Found {len(invalid_coords)} coordinate issues:")
            for issue in invalid_coords[:10]:  # Show first 10
                print(issue)
            if len(invalid_coords) > 10:
                print(f"   ... and {len(invalid_coords) - 10} more issues")
        else:
            print("✅ All coordinates are valid")

        # 2. Check for coordinate clustering (MAIN CAUSE OF JUMPING)
        print("\n2️⃣ COORDINATE CLUSTERING ANALYSIS:")
        coordinate_groups = defaultdict(list)

        for location in map_data:
            lat, lon = location.get('lat'), location.get('lon')
            if lat is not None and lon is not None and isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                # Round to 4 decimal places for clustering detection
                coord_key = f"{lat:.4f},{lon:.4f}"
                coordinate_groups[coord_key].append(location['place'])

        # Find clusters
        clusters = {k: v for k, v in coordinate_groups.items() if len(v) > 1}

        if clusters:
            print(f"⚠️ Found {len(clusters)} coordinate clusters (THIS IS THE MAIN CAUSE OF JUMPING!):")
            cluster_count = 0
            for coord, places in clusters.items():
                cluster_count += 1
                print(f"   📍 {coord}: {len(places)} places")
                for place in places[:5]:  # Show first 5 places
                    print(f"      - {place}")
                if len(places) > 5:
                    print(f"      - ... and {len(places) - 5} more")

                if cluster_count >= 10:  # Limit output
                    break

            if len(clusters) > 10:
                print(f"   ... and {len(clusters) - 10} more clusters")

            print(f"\n💡 CLUSTERING IMPACT:")
            total_clustered = sum(len(places) for places in clusters.values())
            print(f"   - {total_clustered} locations are clustered")
            print(f"   - This affects {total_clustered/len(map_data)*100:.1f}% of all locations")
            print(f"   - ⚠️ THIS IS WHY YOUR PINS ARE JUMPING! ⚠️")
            print(f"   - Multiple pins at same coordinates cause map to jump between them")
        else:
            print("✅ No coordinate clustering detected")

        # 3. Check coordinate distribution
        print("\n3️⃣ COORDINATE DISTRIBUTION:")
        if valid_coords:
            lats = [coord[0] for coord in valid_coords]
            lons = [coord[1] for coord in valid_coords]

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

        # 6. Generate specific recommendations
        print("\n6️⃣ SPECIFIC RECOMMENDATIONS TO FIX JUMPING:")

        if clusters:
            print("🚨 PRIMARY ISSUE: COORDINATE CLUSTERING")
            print("   The pin jumping is caused by multiple locations sharing identical coordinates.")
            print("   When you click between pins at the same location, the map 'jumps' between them.")
            print()
            print("🔧 SOLUTION 1: Update your processor to spread coordinates")
            print("   Add coordinate offset logic to your generate_map_data method:")
            print("""
   # Add this logic in your generate_map_data method:
   coord_key = f"{lat:.4f},{lon:.4f}"
   if coord_key in coordinate_usage:
       offset_count = len(coordinate_usage[coord_key])
       offset_angle = offset_count * (2 * math.pi / 8)
       offset_distance = 0.008  # ~900m offset
       lat += offset_distance * math.cos(offset_angle)
       lon += offset_distance * math.sin(offset_angle)
            """)
            print()
            print("🔧 SOLUTION 2: Use the improved map handler JavaScript")
            print("   The new map.js should automatically detect and fix clustering.")
            print()

        if invalid_coords:
            print("🔧 Fix invalid coordinates in your coordinate mapping")

        if len(missing_data) > len(map_data) * 0.1:  # If >10% have missing data
            print("🔧 Improve inscription data processing in your Python script")

        if not clusters and not invalid_coords:
            print("✅ Map data structure looks good!")
            print("🔧 The jumping issue might be in JavaScript event handling")
            print("   Try the new map.js handler with better popup management")

        # 7. Show most problematic clusters
        if clusters:
            print(f"\n7️⃣ MOST PROBLEMATIC COORDINATE CLUSTERS:")
            sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
            print("   These coordinates have the most overlapping pins:")

            for i, (coord, places) in enumerate(sorted_clusters[:5]):
                print(f"   🎯 {coord} ({len(places)} places): {', '.join(places[:3])}{'...' if len(places) > 3 else ''}")

            print(f"\n   ⚠️ These {len(sorted_clusters[:5])} clusters cause the most jumping!")

        print(f"\n✅ Analysis complete!")

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
    print("🏁 Debug complete! Follow the recommendations above to fix pin jumping.")
