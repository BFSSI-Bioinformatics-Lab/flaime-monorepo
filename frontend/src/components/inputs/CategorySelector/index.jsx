import React, { useState, useEffect, useReducer, useCallback } from 'react';
import { FormControl, FormControlLabel, Radio, RadioGroup, Card, CardContent, CardHeader, Divider, Button, CircularProgress } from '@mui/material';
import { GetAllCategories } from '../../../api/services/CategoryService';
import { IndeterminateCheckbox } from './IndeterminateCheckbox';


const categoryReducer = (state, action) => {
  switch (action.type) {
    case 'FETCH_CATEGORIES':
      return {
        ...state,
        categories: action.payload,
        isLoading: false,
      };
    case 'TOGGLE_CATEGORY':
      return {
        ...state,
        categories: state.categories.map(cat => {
          if (cat.id === action.payload) {
            return { ...cat, isExpanded: !cat.isExpanded };
          }
          return cat;
        }),
      };
    case 'SELECT_CATEGORY':
      return {
        ...state,
        selectedCategories: new Set(action.payload),
      };
    case 'CLEAR_SELECTION':
      return {
        ...state,
        selectedCategories: new Set(),
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: true,
      };
    default:
      return state;
  }
};

const fetchData = async (categoryScheme) => {
  try {
    const categoriesData = await GetAllCategories();
    const filteredCategories = categoriesData.categories.filter(cat => 
      cat.scheme.toLowerCase() === categoryScheme.toLowerCase()
    );
    console.log('Fetched categories:', filteredCategories);
    return filteredCategories;
  } catch (error) {
    console.error("Failed to fetch data:", error);
    return [];
  }
};

const CategorySelector = ({ onChange }) => {
  const [categoryScheme, setCategoryScheme] = useState("reference amount");

  const [state, dispatch] = useReducer(categoryReducer, { 
    categories: [], 
    selectedCategories: new Set(),
    isLoading: true,
  });

  const getSelectionState = useCallback((category) => {
    const subcategories = category.children || category.subcategories || [];
    const subcategoryIds = subcategories.map(sub => sub.id);
    const selectedSubcategoryCount = subcategoryIds.filter(id => state.selectedCategories.has(id)).length;
    return selectedSubcategoryCount === 0 ? 'none' :
           selectedSubcategoryCount === subcategoryIds.length ? 'full' : 'partial';
  }, [state.selectedCategories]);
  
  useEffect(() => {
    const loadCategories = async () => {
      dispatch({ type: 'SET_LOADING' });
      const categories = await fetchData(categoryScheme);
      dispatch({ type: 'FETCH_CATEGORIES', payload: categories });
    };
    loadCategories();
  }, [categoryScheme]);

  const handleCategorySchemeChange = (event) => {
    const newScheme = event.target.value;
    setCategoryScheme(newScheme);
    dispatch({ type: 'CLEAR_SELECTION' });
    onChange([]);
  };

  const handleCategorySelect = (category, isSubcategory = false) => {
    const newSelectedCategories = new Set(state.selectedCategories);

    if (!isSubcategory) {
      const subcategories = category.children || category.subcategories || [];
      if (subcategories.every(sub => newSelectedCategories.has(sub.id))) {
        subcategories.forEach(sub => newSelectedCategories.delete(sub.id));
      } else {
        subcategories.forEach(sub => newSelectedCategories.add(sub.id));
      }
    } else {
      if (newSelectedCategories.has(category.id)) {
        newSelectedCategories.delete(category.id);
      } else {
        newSelectedCategories.add(category.id);
      }
    }

    dispatch({
      type: 'SELECT_CATEGORY',
      payload: Array.from(newSelectedCategories),
    });
    onChange(Array.from(newSelectedCategories));
  }

  const toggleExpand = (category) => {
    dispatch({ type: 'TOGGLE_CATEGORY', payload: category.id });
  };
  
  return (
    <Card variant="outlined">
      <CardHeader title="Select Categories" />
      <CardContent style={{ paddingTop: '0' }}>
        <p>Select the categories to filter by. Top level categories can be expanded to sub-categories.</p>
        <p>Note that Nielsen data is categorized with the Sodium categories and most (but not all) of the web scraped data is categorized with the RA categories.</p>
        <Divider style={{ width: '300px', margin: ' 5px auto' }}/>
        <FormControl>
          <RadioGroup row value={categoryScheme} onChange={handleCategorySchemeChange} name="categoryScheme">
            <FormControlLabel value="reference amount" control={<Radio />} label="Reference Amount" />
            <FormControlLabel value="sodium" control={<Radio />} label="Sodium" />
          </RadioGroup>
        </FormControl>
        <Divider />
        <div style={{ height: '300px', overflowY: 'auto' }}>
          {state.isLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress size={24} style={{ marginRight: '10px' }} />
              <span>Loading...</span>
            </div>
          ) : (
          state.categories.map(category => (
            <div key={category.id} style={{ margin: '5px 0' }}>
              <IndeterminateCheckbox
                id={`category-${category.id}`}
                checked={getSelectionState(category) === 'full'}
                indeterminate={getSelectionState(category) === 'partial'}
                onChange={() => handleCategorySelect(category)}
                label={``}
              />
              <span style={{ fontSize: '15px', margin: '0 4px'}}>
              {category.name}
              </span>
              
              {(category.children || category.subcategories) && (
                <Button variant='outlined' size='small' style={{ marginLeft: '5px', minWidth: '22px', padding: '0' }}
                  onClick={() => toggleExpand(category)}
                  aria-label={category.isExpanded ? `Collapse ${category.name}` : `Expand ${category.name}`}
                >
                  {category.isExpanded ? '-' : '+'}
                </Button>
              )}
              {category.isExpanded && (category.children || category.subcategories) && (
                <div style={{ marginLeft: '20px' }}>
                  {(category.children || category.subcategories).map(sub => (
                    <div key={sub.id} style={{ display: 'block' }}>
                      <IndeterminateCheckbox
                        id={`subcategory-${sub.id}`}
                        checked={state.selectedCategories.has(sub.id)}
                        onChange={() => handleCategorySelect(sub, true)}
                        label={
                          <span style={{ fontSize: '12px', color: 'secondary', margin: '0 3px' }}>{sub.name}</span>
                        }
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default CategorySelector;
