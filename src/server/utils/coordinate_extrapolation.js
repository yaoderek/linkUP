// This utility provides a lightweight way to populate coordinates or a Google Maps link
// for opportunity entries after they are inserted/updated in the database.
// It is intentionally offline (no external API calls) and uses a small built-in map
// of known Seattle locations; for unknown addresses it will at minimum create a
// Google Maps URL so the frontend can resolve the place manually.

// Map of known location names to coordinates (longitude, latitude)
const KNOWN_PLACES = {
  'Jefferson Park': [-122.3147, 47.5371],
  'Seattle Art Center': [-122.3331, 47.6080],
  'Seattle Community Center': [-122.3355, 47.6101]
};

// Create a Google Maps URL from an address string
function makeGoogleMapsUrl(address) {
  // Encode the address for use in a URL
  const encoded = encodeURIComponent(address || 'Seattle');
  return `https://www.google.com/maps/search/?api=1&query=${encoded}`;
}

// Enrich an opportunity-like object with coordinates or google_maps_url.
// Accepts a plain object (not a Mongoose document) and returns the updated object.
async function enrichLocation(entry) {
  // If location object missing, nothing to do
  if (!entry.location) return entry;

  // If coordinates already present, do nothing
  if (entry.location.coordinates && Array.isArray(entry.location.coordinates.coordinates) && entry.location.coordinates.coordinates.length === 2) {
    // Ensure google_maps_url is set as well for convenience
    if (!entry.location.google_maps_url && entry.location.address) {
      entry.location.google_maps_url = makeGoogleMapsUrl(entry.location.address);
    }
    return entry;
  }

  // First try to match known place names
  const name = entry.location.name;
  if (name && KNOWN_PLACES[name]) {
    // Populate GeoJSON coordinates
    entry.location.coordinates = { type: 'Point', coordinates: KNOWN_PLACES[name] };
    entry.location.google_maps_url = makeGoogleMapsUrl(`${name} ${entry.location.address || ''}`.trim());
    return entry;
  }

  // If address contains a known place substring, match that too
  const addr = (entry.location.address || '').toLowerCase();
  for (const key of Object.keys(KNOWN_PLACES)) {
    if (addr.includes(key.toLowerCase())) {
      entry.location.coordinates = { type: 'Point', coordinates: KNOWN_PLACES[key] };
      entry.location.google_maps_url = makeGoogleMapsUrl(entry.location.address);
      return entry;
    }
  }

  // Fallback: set a Google Maps link based on address but leave coordinates undefined
  if (entry.location.address) {
    entry.location.google_maps_url = makeGoogleMapsUrl(entry.location.address);
  }
  return entry;
}

module.exports = { enrichLocation };
