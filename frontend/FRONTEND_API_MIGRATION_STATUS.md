# Frontend API compatibility fix — status (Elasticsearch removal done 2026-09-10)

Goal: update the React frontend so existing functionality keeps working against
the refactored Django/DRF API (FSDH migration: tables consolidated/removed,
serializer fields renamed, `product` table dropped). No new features, no UX
changes except where explicitly directed. `schema.yaml` (repo root) is the
written contract; real authenticated response samples were also provided and
supersede the schema where they disagree.

## Branch / working tree

- Branch: `export_verified`
- Uncommitted edits (earlier part of this task):
  - `src/pages/tools/Product_detail/index.jsx`
  - `src/components/nutrition_facts_table/NutritionFactsTable.jsx`
  - `src/components/nutrition_facts_table/nft_flaime_nutrients.js`
- Uncommitted edits (Elasticsearch removal, 2026-09-10): see the section at the
  bottom of this file.
- All edited files pass `eslint` (0 errors). No build run.

## Changes already made

### 1. `product.product` shim → top-level fields  (CONFIRMED against real payload)
The API still returns a deprecated `product` sub-object, but everything now also
lives at the top level of the store-product response.
- `src/pages/tools/Product_detail/index.jsx`
  - `getLinkedUpcs(product.product)` → `getLinkedUpcs(product)` (reads `product.upcs`)
  - `product.product?.categories` → `product.categories` (guard + `<CategoryDisplay>` prop)
  - `product.product?.supplemented_food` → `product.supplemented_food`
- `src/components/nutrition_facts_table/NutritionFactsTable.jsx`
  - `product.product?.supplemented_food` → `product.supplemented_food`
- `CategoryDisplay.jsx` unchanged — its expected `{scheme: {manual,predicted}}`
  shape and item fields (`id/name/code/scheme/level/verification_info`) match the
  real payload.

### 2. Removed dead fields from Product_detail  (USER-DIRECTED)
`brand` / `raw_brand`, `price` (was `reading_price`), `external_id`, `sku`,
`site_url` were dropped from the store product in the migration. Removed the
**Brand**, **External ID**, **Price**, and **URL** rows from `productDescItems`
in `src/pages/tools/Product_detail/index.jsx`.

### 3. Nutrient vocabulary change  (CONFIRMED via GET /api/nutrients/full/)
API nutrient names changed from cryptic USDA strings to human-readable labels
(`"PROTEIN"` → `"Protein"`, `"ENERGY (KILOCALORIES)"` → `"Calories"`,
`"FAT (TOTAL LIPIDS)"` → `"Total Fat"`, `"SUGARS, TOTAL"` → `"Sugars"`, etc.).
- `src/components/nutrition_facts_table/nft_flaime_nutrients.js`
  - `nutrientMatches`: each bilingual display key now maps to the new API name
    first, legacy USDA names retained as fallbacks. `nft_order` unchanged
    (keyed by the bilingual display label) — so ordering + bilingual labels
    are restored.
- `src/components/nutrition_facts_table/NutritionFactsTable.jsx`
  - calories now identified by `nutrient.symbol === "KCAL"` || `nutrient_code === 208`
    (|| legacy name), via a new `isCaloriesFact()` helper used both for the
    "Calories:" summary line and to exclude calories from the nutrient table.

## Item tracker (from the original 9 flags)

| # | Item | Status |
|---|------|--------|
| 1 | `product.verified` (Product_detail success/warning banners) | **DONE.** Backend added `verified` (bool) to `DetailedStoreProduct` (and `StoreProductSearchResult`). `Product_detail/index.jsx` already reads `product.verified` — the green "manually verified" banner now works; no code change needed there. |
| 2 | `site_url` | DONE — row removed. |
| 3/6 | `sources/{id}/collection-stats/` | DONE — real response has `total`, `with_fop`, `fop_percentage`, `manually_reviewed`, `reviewed_percentage`. `Collection_stats/index.jsx` already reads these exact names. No change needed; schema's `SimpleSource` response ref was a bad drf-spectacular guess. |
| 4 | `category-verifications/get_predictions/` | **OPEN — no sample received.** Undocumented in schema (`200: Success` only). `src/pages/tools/Category_verification/index.jsx` depends on: `results/count/next/previous`; per row `id`, `product_id`, `product_name`, `store_product_id`, `predictions[].{category_id,category_code,category_name,confidence}`, `category_id`, `problematic_flag`, `notes`; and `GetVerificationStats` needs `total_count`, `verified_count`. `product_*` keys are the prime suspects given the `product`→`store_product` rename. Also check `create_verification/` payload: frontend POSTs `{product: data.product_id, ...}` but schema marks `product` writeOnly/deprecated and wants `store_product`. NEED: real response body from this endpoint (verify + problematic + user-verifications + stats_only variants). |
| 5 | `/api/options/` | DONE — returns `{value,label}` arrays for `sources/stores/regions/storage/packaging`. `useSearchOptions` + `Advanced_search` already consume that. No change needed. |
| 7 | `CategoryTree.children` | RESOLVED — nested shape confirmed inline in store-product payload. |
| 8 | `CategoryListSerializer` item fields | RESOLVED — `id/name/code/scheme/level/verification_info/prediction_info/parent_category`. |
| 9 | `/api/users/` | RESOLVED — `{id, email, url}`, no `username`. `Category_verification_setup` now shows email (via existing `user.username || user.email || ...` fallback). Left as-is. |

## Still OPEN — need data or decisions

1. **`get_predictions/` response sample** (item 4) — `Category_verification` tool is
   entirely unverified. Biggest remaining risk.
2. **`total_size`** — user says it should still exist; absent from the sample
   product (likely just null/omitted). `product.total_size` left in place in
   `Product_detail` + `NutritionFactsTable`. Confirm field name.
3. **Elasticsearch `_source` shape** — RESOLVED. Elasticsearch has been removed
   from the frontend entirely — see the section at the bottom of this file.
4. **Advanced Search storage/packaging filters** — RESOLVED. New API filters take
   the `/api/options/` slug directly (`filters.storage_condition` /
   `filters.primary_package_material`), so these work now.

## Notes / non-issues

- Auth (`/api/token-auth/`, `/api/user-info/`) unchanged — `UserInfoResponse` still
  has `username`, `is_staff`, `email`; `Header`/`login` fine.
- `nutrients/`, `stores/`, `sources/`, `categoryschemes/`, `categories/` list
  endpoints: shapes match (`id` + `name`), no change needed.
- API service files (`src/api/services/*.js`) are thin pass-throughs of `res.data`;
  almost all fixes are in consumers, not the service layer.
- The DRF serializer omits null-valued keys, so treat every optional field as
  possibly-absent (most consumer code already uses `?.` / `||`).

---

## Elasticsearch removal (2026-09-10)

The browser no longer talks to Elasticsearch. All product search / aggregation /
export / image lookups go through new authenticated DRF endpoints. `@elastic/elasticsearch`
and `elasticsearch` are gone from `package.json` / `package-lock.json`;
`REACT_APP_ELASTIC_URL` / `REACT_APP_ELASTIC_IMG_URL` are gone from both `.env.*`.

### New / changed backend endpoints consumed

| Endpoint | Used by |
|---|---|
| `POST /api/storeproducts/search/` → `{count,next,previous,results:[StoreProductSearchResult]}` | Product Finder, Advanced Search, Product Browser, Collection Stats ingredient list |
| `POST /api/storeproducts/store-counts/` → `[{store,count}]` | Product Browser "products per store" cards |
| `POST /api/storeproducts/export/` → CSV blob (`columns`: `simple`/`full`/`full_supplemented`); 400 `{detail}` over `EXPORT_MAX_ROWS` (default 50000) | Download Results button (all tools) |
| `GET /api/storeproducts/collection-stats/?source=` → `CollectionStats` | Collection Stats report |
| `DetailedStoreProduct.store_product_images` (string[]) | `Product_detail/ProductImages.jsx` |
| `DetailedStoreProduct.verified` / `StoreProductSearchResult.verified` (bool) | Product Detail verified banner |

Request body shape (search / store-counts / export share it) is built by
`buildProductFinderBody` / `buildAdvancedSearchBody` / `buildProductBrowserBody`
in `src/pages/tools/util.js`: `{ text:{site_name, *_list}, filters:{source,store,region,
category[],date_from,date_to,storage_condition,primary_package_material,
ingredients:{terms,mode},allergens,nutrient:{id,min,max}} }`. The search hook adds
`page` (1-based), `page_size`, `sort:{field,order}` (`field` ∈ FieldEnum).

### Files changed

- **new** `src/api/services/StoreProductSearchService.js` — `SearchStoreProducts`,
  `GetStoreCounts`, `GetCollectionStats`, `ExportStoreProducts`.
- **new** `src/hooks/useProductSearch.js` — replaces `useElasticsearch.js` (**deleted**),
  identical return shape (`results/isLoading/totalProducts/setResults/setTotalProducts/executeSearch`).
- `src/pages/tools/util.js` — ES bool/DSL builders replaced with the body builders above.
- `src/components/table/ToolTable/index.jsx` — rows are flat objects now (`item.id`,
  `item.site_name`, `item.source.name`, `item.store.name`, `item.scrape_batch.datetime`,
  `item.scrape_batch.region`); `price` replaces `reading_price`; `_id`/`_source` gone.
- `src/pages/tools/Product_finder/index.jsx`, `src/pages/tools/Advanced_search/index.jsx`
  — use `useProductSearch`, new body + `sort:{field,order}`. Advanced Search's
  `processAllergenHits` → `processAllergenRows` (flat objects).
- `src/pages/tools/Product_browser/index.jsx` — `SearchStoreProducts` + `GetStoreCounts`;
  dropped the `most_recent_flag` base clause (column removed in backend migration 0035);
  **dropped the "Store Name" and "category" free-text search fields** (no API equivalent —
  `filters.store`/`filters.category` are id-only; per user decision). Exact total count
  replaces the ES "over 10,000" cap message.
- `src/hooks/useProductExport.js` — CSV is built server-side now; hook just POSTs the
  search body + `columns` and downloads the returned blob. Client-side CSV assembly,
  the 5000-row cap, and `nutrition_details` field reads are gone.
- `src/pages/reports/Collection_stats/index.jsx` — single `GET .../collection-stats/`
  call; the ES-incompleteness warning banner is removed; FOP / reviewed cards now
  render for the all-sources view too (data is DB-backed). Local `NUTRIENT_CONFIG` /
  `ADDITIVES` constants dropped — server returns `label/unit/nutrient_ids` and
  `label/term`.
- `src/pages/tools/Product_detail/ProductImages.jsx` — reads `product.store_product_images`;
  no fetch, no axios.
- `src/api/services/SourceService.js` — removed dead `GetSourceCollectionStats`.

### Behavior changes (accepted)

- **Product name search**: ES `fuzziness:AUTO` + wildcard → Postgres `ILIKE '%term%'`.
  Substring still works; typo tolerance and relevance ranking are gone.
- **`category` filter** matches **manual categories only** (backend), not predicted.
- **Date range** excludes products with no `scrape_batch` (backend). Product Finder's
  reset sets a 1900→today range, so a post-reset search drops batch-less products —
  same as the old ES `range` clause did (missing field ⇒ excluded).
- **Advanced Search "Packaging"** now filters `primary_package_material` only; the old
  ES query also OR'd `secondary_package_material`.
- **Product Browser `price` sort**: lexical → numeric.
- Result columns still show storage/packaging **display labels** ("Shelf Stable",
  "Plastic - PET - 1"); filter inputs still take **slugs** — unchanged from ES.

### Not done / verify

- No build run (Node 12 in this env); `eslint` passes with 0 errors on all changed files.
- `node_modules` still physically contains the elastic packages until a fresh `npm ci`.
- Confirm `EXPORT_MAX_ROWS` value and the exact 400 body key (`detail`) against the
  running server; `ExportStoreProducts` reads `error.response.data` (blob → text → JSON).
