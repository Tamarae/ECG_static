
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
