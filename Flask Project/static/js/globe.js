const Globe = window.Globe;

(() => {
  let selectedId = null;
  let geoFeatures = [];
  let stadiumFeatures = [];

  const globeEl = document.getElementById('globeViz');
  const globe = Globe()(globeEl)
    .backgroundColor('#000')
    .showAtmosphere(true)
    .polygonsTransitionDuration(300)
    .pointAltitude(0.04)
    .pointColor(() => '#ffcc00')
    .pointRadius(0.25)
    .pointLabel(f => f.properties && f.properties.s_name ? f.properties.s_name : '')
    .pointsData([]);

  function idForFeature(f){
    return (f.properties && (f.properties.ISO_A3 || f.properties.iso_a3 || f.properties.ISO_A2)) || f.id || (f.properties && (f.properties.ADMIN || f.properties.name)) || JSON.stringify(f.bbox || f.geometry);
  }

  // Compute approximate geographic centroid of a (Multi)Polygon feature using
  // spherical averaging to handle longitude wrap-around.
  function centroidOfFeature(feature) {
    if (!feature || !feature.geometry) return { lat: 0, lng: 0 };
    const geom = feature.geometry;
    const points = [];

    function pushRing(ring) {
      for (let i = 0; i < ring.length; i++) {
        const p = ring[i];
        // GeoJSON ordering: [lng, lat]
        points.push([p[1], p[0]]);
      }
    }

    if (geom.type === 'Polygon') {
      geom.coordinates.forEach(ring => pushRing(ring));
    } else if (geom.type === 'MultiPolygon') {
      geom.coordinates.forEach(poly => poly.forEach(ring => pushRing(ring)));
    } else if (geom.type === 'Point') {
      return { lat: geom.coordinates[1], lng: geom.coordinates[0] };
    }

    if (points.length === 0) return { lat: 0, lng: 0 };

    // Convert lat/lng to Cartesian unit vectors, sum and normalize
    let x = 0, y = 0, z = 0;
    for (const [lat, lng] of points) {
      const latR = lat * Math.PI / 180;
      const lngR = lng * Math.PI / 180;
      const cx = Math.cos(latR) * Math.cos(lngR);
      const cy = Math.cos(latR) * Math.sin(lngR);
      const cz = Math.sin(latR);
      x += cx; y += cy; z += cz;
    }
    const m = Math.sqrt(x*x + y*y + z*z);
    if (m === 0) return { lat: 0, lng: 0 };
    x /= m; y /= m; z /= m;
    const lat = Math.asin(z) * 180 / Math.PI;
    const lng = Math.atan2(y, x) * 180 / Math.PI;
    return { lat, lng };
  }

  function updatePolygons(){
    globe
      .polygonCapColor(f => idForFeature(f) === selectedId ? 'rgba(28, 226, 87, 0.5)' : 'rgba(0, 120, 255, 0.6)')
      .polygonAltitude(0.02)
      .polygonSideColor(() => 'rgba(0,0,0,0.15)')
      .polygonStrokeColor(() => 'rgba(0, 0, 0, 0.5)')
      .polygonLabel(f => f.properties && (f.properties.ADMIN || f.properties.name) ? (f.properties.ADMIN || f.properties.name) : '')
      .polygonsData(geoFeatures);
  }

  function stadiumPoints(features) {
    return features.map(feature => {
      const coords = feature.geometry && feature.geometry.coordinates;
      const props = feature.properties || {};
      return {
        lat: coords ? coords[1] : 0,
        lng: coords ? coords[0] : 0,
        properties: props,
        ...props
      };
    });
  }

  function updateStadiums(){
    globe
      .pointsData(stadiumPoints(stadiumFeatures));
  }

  fetch('/data/countries.geojson')
    .then(r => r.json())
    .then(geojson => {
      geoFeatures = geojson.features || geojson;
      updatePolygons();

      globe.onPolygonClick(feature => {
        const fid = idForFeature(feature);
        selectedId = fid;

        updatePolygons();

        try {
            const c = centroidOfFeature(feature);
            globe.pointOfView({ lat: c.lat, lng: c.lng, altitude: 0.8 }, 1000);
        } catch (e) {
            console.warn('Failed to set camera POV', e);
        }

        console.log('country click', fid, feature.properties && feature.properties.SOV_A3, feature.properties && feature.properties.ADM0_A3);
        fetch('/api/country', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: fid, properties: feature.properties })
        })
        .then(res => res.json())
        .then(data => {
            stadiumFeatures = Array.isArray(data.stadiums) ? data.stadiums : [];
            console.log('stadiums loaded', stadiumFeatures.length, data);
            updateStadiums();
        })
        .catch(err => {
            console.warn('API request failed', err);
            stadiumFeatures = [];
            updateStadiums();
        });
      });

      globe.onPointClick(point => {
        if (!point || !point.properties) return;
        const props = point.properties;
        const info = [
          props.s_name || props.id || 'Stadium',
          props.city ? `City: ${props.city}` : null,
          props.team ? `Team: ${props.team}` : null,
          props.capacity ? `Capacity: ${props.capacity}` : null,
          props.year ? `Year: ${props.year}` : null
        ].filter(Boolean).join('\n');

        alert(info);
      });

      // small camera/scene tuning
      globe.controls().autoRotate = false;
    })
    .catch(err => {
      console.error('Failed to load GeoJSON:', err);
      globe.polygonsData([]);
    });

})();
