CREATE TABLE IF NOT EXISTS dishes (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  canonical_dish_key TEXT,

  -- cuisines (합 ≤ 1)
  cuisine_korean REAL DEFAULT 0, cuisine_japanese REAL DEFAULT 0,
  cuisine_chinese REAL DEFAULT 0, cuisine_western REAL DEFAULT 0,
  cuisine_asian REAL DEFAULT 0, cuisine_other REAL DEFAULT 0,

  -- temperature/soup
  temperature_hot_0_1 REAL DEFAULT 0,
  soupiness_0_1 REAL DEFAULT 0,
  soup_cat_none SMALLINT DEFAULT 0,
  soup_cat_thin SMALLINT DEFAULT 0,
  soup_cat_stew SMALLINT DEFAULT 0,
  soup_cat_noodle SMALLINT DEFAULT 0,

  -- flavors
  spicy_0_1 REAL DEFAULT 0,
  flavor_salty REAL DEFAULT 0, flavor_sweet REAL DEFAULT 0,
  flavor_sour REAL DEFAULT 0, flavor_umami REAL DEFAULT 0,
  flavor_fatty REAL DEFAULT 0, flavor_garlic REAL DEFAULT 0,
  flavor_smoky REAL DEFAULT 0,

  -- proteins (합 ≤ 1)
  protein_beef REAL DEFAULT 0, protein_pork REAL DEFAULT 0,
  protein_chicken REAL DEFAULT 0, protein_seafood REAL DEFAULT 0,
  protein_plant REAL DEFAULT 0,

  -- carbs
  carb_rice SMALLINT DEFAULT 0, carb_noodle SMALLINT DEFAULT 0,
  carb_bread SMALLINT DEFAULT 0, carb_none SMALLINT DEFAULT 0,
  rice_form TEXT,  -- 'tteok' 등 세부

  -- others
  veggie_heavy_0_1 REAL DEFAULT 0,
  heaviness_0_1 REAL DEFAULT 0,
  shareable_0_1 REAL DEFAULT 0,
  price_tier_1_low_3_high SMALLINT,

  -- vector
  embedding vector(384),

  notes TEXT
);
