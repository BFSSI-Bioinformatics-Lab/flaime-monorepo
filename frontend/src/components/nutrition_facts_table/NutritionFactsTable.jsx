import React from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Typography, Divider, Box
} from '@mui/material';
import { nft_order, nutrientMatches } from './nft_flaime_nutrients';

const paddingStyle = { padding: '10px' };
const cellPaddingStyle = { padding: '0px' };
const smallFontSizeStyle = { textTransform: 'capitalize', fontSize: 'smaller' };

// The energy/calories fact is shown on its own line, not in the nutrient table.
// The API's nutrient naming changed in the FSDH migration ("ENERGY (KILOCALORIES)"
// -> "Calories"), so match on the stable USDA symbol/code and keep the old name
// as a fallback.
const isCaloriesFact = (nutritionFact) => {
  const nutrient = nutritionFact.nutrient || {};
  return nutrient.symbol === "KCAL"
    || nutrient.nutrient_code === 208
    || nutrient.name === "ENERGY (KILOCALORIES)"
    || nutrient.name === "Calories";
};

const getLocalizedNutrients = (nutritionFacts, supplementedOnly = false) => nutritionFacts
  .filter(nutritionFact =>
    !isCaloriesFact(nutritionFact) &&
    nutritionFact.supplemented === supplementedOnly
  )
  .map(nutritionFact => ({
    ...nutritionFact,
    localizedKey: Object.keys(nutrientMatches).find(key =>
      nutrientMatches[key].includes(nutritionFact.nutrient.name)
    ) || nutritionFact.nutrient.name
  }))
  .sort((a, b) => {
    const aOrder = nft_order[a.localizedKey] || 9999;
    const bOrder = nft_order[b.localizedKey] || 9999;
    return aOrder - bOrder;
  });

const NutritionFactsTable = ({ product }) => {
  const isSupplemented = product.supplemented_food === true;
  const supplementedNutrients = isSupplemented ? 
    getLocalizedNutrients(product.nutrition_facts, true) : [];

  return (
    <Box>
      <TableContainer component={Paper}>
        <Typography variant="h6" style={paddingStyle}>Nutrition Facts</Typography>
        <Typography variant="body2" style={paddingStyle}>
          Serving Size: Per {product.serving_size ? `${product.serving_size} ${product.serving_size_unit ?? ""}` : (product.raw_serving_size || "unit not specified")}
          <br />
          Total size: {product.total_size ?? "Not specified"}
        </Typography>
        {product.nutrition_facts && (
          <Typography variant="body2" style={paddingStyle}>
            {product.nutrition_facts
              .filter(isCaloriesFact)
              .map(nutritionFact => `Calories: ${nutritionFact.amount}${nutritionFact.amount_unit ? ` ${nutritionFact.amount_unit.name}` : ''}`)
              .join(', ')}
          </Typography>
        )}
        <Divider variant="middle" />
        {product.nutrition_facts && (
          <Table size="small" aria-label="a dense table">
            <TableHead>
              <TableRow>
                <TableCell>Nutrient</TableCell>
                <TableCell style={cellPaddingStyle}>Amount</TableCell>
                <TableCell style={cellPaddingStyle}>% Daily Value</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {getLocalizedNutrients(product.nutrition_facts, false).map((nutritionFact) => (
                <TableRow key={nutritionFact.nutrient.id}>
                  <TableCell>
                    <span style={smallFontSizeStyle}>
                      {nutritionFact.localizedKey}
                    </span>
                  </TableCell>
                  <TableCell>
                    {nutritionFact.amount !== null && `${nutritionFact.amount}${nutritionFact.amount_unit?.name ? ` ${nutritionFact.amount_unit.name}` : ''}`}
                  </TableCell>
                  <TableCell>
                    {nutritionFact.daily_value !== null ? `${nutritionFact.daily_value}%` : ""}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </TableContainer>

      {isSupplemented && supplementedNutrients.length > 0 && (
        <TableContainer component={Paper} sx={{ marginTop: 2 }}>
          <Typography variant="h6" style={paddingStyle}>Supplemented Food Facts</Typography>
          <Table size="small" aria-label="supplemented nutrients table">
            <TableHead>
              <TableRow>
                <TableCell>Nutrient</TableCell>
                <TableCell style={cellPaddingStyle}>Amount</TableCell>
                <TableCell style={cellPaddingStyle}>% Daily Value</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {supplementedNutrients.map((nutritionFact) => (
                <TableRow key={nutritionFact.nutrient.id}>
                  <TableCell>
                    <span style={smallFontSizeStyle}>
                      {nutritionFact.localizedKey}
                    </span>
                  </TableCell>
                  <TableCell>
                    {nutritionFact.amount !== null && `${nutritionFact.amount}${nutritionFact.amount_unit?.name ? ` ${nutritionFact.amount_unit.name}` : ''}`}
                  </TableCell>
                  <TableCell>
                    {nutritionFact.daily_value !== null ? `${nutritionFact.daily_value}%` : ""}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default NutritionFactsTable;