import { useState } from 'react';

export const useSearchFilters = (initialFilters) => {
  const [searchInputs, setSearchInputs] = useState(initialFilters);

  const handleInputChange = (field, value) => {
    setSearchInputs(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return [searchInputs, handleInputChange];
};

/**
 * Search request builders for POST /api/storeproducts/{search,store-counts,export}/.
 *
 * These replace the old Elasticsearch bool/DSL builders. The body shape is:
 *   {
 *     text: {
 *       site_name,            // case-insensitive substring (the "fuzzy" one)
 *       site_name_list,       // exact match, OR'd, <= 1000
 *       id_list, external_id_list, raw_upc_list, nielsen_upc_list
 *     },
 *     filters: {
 *       source, store, region, category: [ids],
 *       date_from, date_to,                       // scrape_batch datetime
 *       storage_condition, primary_package_material, secondary_package_material,  // slugs
 *       ingredients: { terms: [], mode: 'all' | 'any' },  // ingredient_en OR ingredient_fr
 *       allergens,                                // substring over contains_en OR may_contain_en
 *       nutrient: { id, min, max }
 *     }
 *   }
 * `page` / `page_size` / `sort` are added by the search hook.
 */

// Frontend column key -> API sort field (FieldEnum in schema.yaml).
export const SORT_FIELD_MAP = {
  id: 'id',
  external_id: 'external_id',
  name: 'site_name',
  price: 'price',
  source: 'source',
  store: 'store',
  date: 'date',
  region: 'region',
  storage_condition: 'storage_condition',
  primary_package_material: 'primary_package_material',
};

// trim, drop blanks, de-dupe
const cleanList = (values) => [...new Set(
  (values || [])
    .map(v => (v == null ? '' : String(v).trim()))
    .filter(v => v !== '')
)];

const toIntList = (values) => cleanList(values)
  .map(v => parseInt(v, 10))
  .filter(n => !Number.isNaN(n));

// 'Name' | 'ID' | 'UPC' | 'Nielsen_UPC' -> the exact-match list key on `text`.
export const getListKey = (inputMode) => {
  switch (inputMode) {
    case 'ID':          return 'id_list';
    case 'UPC':         return 'raw_upc_list';
    case 'Nielsen_UPC': return 'nielsen_upc_list';
    case 'Name':
    default:            return 'site_name_list';
  }
};

const addIfSet = (obj, key, value) => {
  if (value !== null && value !== undefined && value !== '' && value !== '-1') {
    obj[key] = value;
  }
};

// source / store / region / category / date range — shared by every tool.
const buildCommonFilters = (searchInputs) => {
  const filters = {};

  addIfSet(filters, 'source', searchInputs.Source?.value ?? null);
  addIfSet(filters, 'store', searchInputs.Store?.value ?? null);
  addIfSet(filters, 'region', searchInputs.Region?.value ?? null);

  const categoryIds = searchInputs.Categories?.value;
  if (Array.isArray(categoryIds) && categoryIds.length > 0) {
    filters.category = categoryIds;
  }

  addIfSet(filters, 'date_from', searchInputs.StartDate?.value ?? null);
  addIfSet(filters, 'date_to', searchInputs.EndDate?.value ?? null);

  return filters;
};

const isEmptyBody = (body) =>
  Object.keys(body.text || {}).length === 0 &&
  Object.keys(body.filters || {}).length === 0;

// --- Product Finder ---------------------------------------------------------
// A list of names / IDs / UPCs (up to 1000) plus source / region / store / date.
export const buildProductFinderBody = (searchInputs, inputMode) => {
  const listKey = getListKey(inputMode);
  const rawValues = searchInputs.TextEntries?.value || [];
  const values = listKey === 'id_list' ? toIntList(rawValues) : cleanList(rawValues);

  if (values.length === 0) return null;

  return {
    text: { [listKey]: values },
    filters: buildCommonFilters(searchInputs),
  };
};

// --- Advanced Search ------------------------------------------------------
export const buildAdvancedSearchBody = (searchInputs) => {
  const text = {};
  if (searchInputs.Names) text.site_name = searchInputs.Names.trim();

  const idInts = toIntList([searchInputs.IDs]);
  if (idInts.length) text.id_list = idInts;
  if (searchInputs.ExternalIDs) text.external_id_list = [searchInputs.ExternalIDs.trim()];
  if (searchInputs.UPCs) text.raw_upc_list = [searchInputs.UPCs.trim()];
  if (searchInputs.NielsenUPCs) text.nielsen_upc_list = [searchInputs.NielsenUPCs.trim()];

  const filters = buildCommonFilters(searchInputs);

  addIfSet(filters, 'storage_condition', searchInputs.Storage);
  addIfSet(filters, 'primary_package_material', searchInputs.Packaging);

  if (searchInputs.Allergens) filters.allergens = searchInputs.Allergens.trim();

  const ingredientTerms = (searchInputs.Ingredients || '')
    .split(',')
    .map(t => t.trim())
    .filter(Boolean);
  if (ingredientTerms.length > 0) {
    filters.ingredients = {
      terms: ingredientTerms,
      mode: searchInputs.IngredientsMatch === 'any' ? 'any' : 'all',
    };
  }

  const nutrition = searchInputs.Nutrition || {};
  if (nutrition.nutrient) {
    const nutrient = { id: parseInt(nutrition.nutrient, 10) };
    if (nutrition.minAmount !== '' && nutrition.minAmount != null) {
      nutrient.min = parseFloat(nutrition.minAmount);
    }
    if (nutrition.maxAmount !== '' && nutrition.maxAmount != null) {
      nutrient.max = parseFloat(nutrition.maxAmount);
    }
    if (!Number.isNaN(nutrient.id)) filters.nutrient = nutrient;
  }

  return { text, filters };
};

// --- Product Browser -------------------------------------------------------
// id / external_id (exact), product name (substring), source (id).
export const buildProductBrowserBody = (searchTerms) => {
  const text = {};
  const idInts = toIntList([searchTerms.id]);
  if (idInts.length) text.id_list = idInts;
  if (searchTerms.external_id) text.external_id_list = [String(searchTerms.external_id).trim()];
  if (searchTerms.siteName) text.site_name = searchTerms.siteName.trim();

  const filters = {};
  addIfSet(filters, 'source', searchTerms.sourceName);

  return { text, filters };
};

// True when the Advanced Search / Product Browser body carries no criteria at
// all (used to disable the download button / skip empty requests).
export const isEmptySearchBody = isEmptyBody;
