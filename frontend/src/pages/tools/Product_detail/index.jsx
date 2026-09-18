import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Grid, Typography, Divider, Collapse, Alert } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PageContainer from '../../../components/page/PageContainer';
import Band from '../../../components/page/Band';
import { ProductInfoBox, PageIcon, PageTitle, DetailItem, ProductIngredientsHeadingContainer, ExpandMore, DescriptionHeader } from "./styles";
import NutritionFactsTable from '../../../components/nutrition_facts_table/NutritionFactsTable';
import ProductImages from './ProductImages';
import CategoryDisplay from '../../../components/category_display/CategoryDisplay';
import SupplementedFoodFlags from '../../../components/supp_food_flags/SupplementedFoodFlags';
import { GetStoreProductByID } from '../../../api/services/ProductService';

const ProductDetail = () => {
    const { productId } = useParams();
    const [product, setProduct] = useState(null);
    const [isLoading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [descriptionExpanded, setDescriptionExpanded] = useState(false);

    useEffect(() => {
        const controller = new AbortController();

        const fetchProductData = async () => {
            setLoading(true);
            setError(null);
            console.log("Fetching product data...");
            const result = await GetStoreProductByID(productId, controller);
            console.log("API result:", result);
            if (result.error) {
                setError(result.message);
            } else {
                setProduct(result.data);
            }
            setLoading(false);
        };

        fetchProductData();

        return () => controller.abort();
    }, [productId]);

    if (isLoading) {
        return <Typography>Loading...</Typography>;
    }

    if (error) {
        return <Typography>Error: {error}</Typography>;
    }

    if (!product) {
        return <Typography>Error: Product not found.</Typography>;
    }

    const getAllergenData = (allergens) => {
        if (!allergens || !Array.isArray(allergens)) return null;

        let enList = [];
        let frList = [];

        allergens.forEach(item => {
            if (!item.contains_en && !item.may_contain_en && !item.contains_fr && !item.may_contain_fr) return;

            // English Formatting
            let enParts = [];
            if (item.contains_en) enParts.push(`Contains: ${item.contains_en}`);
            if (item.may_contain_en) enParts.push(`May contain: ${item.may_contain_en}`);
            if (enParts.length > 0) enList.push(enParts.join(". "));

            // French Formatting
            let frParts = [];
            if (item.contains_fr) frParts.push(`Contient : ${item.contains_fr}`);
            if (item.may_contain_fr) frParts.push(`Peut contenir : ${item.may_contain_fr}`);
            if (frParts.length > 0) frList.push(frParts.join(". "));
        });

        const enText = enList.length > 0 ? enList.join(" ") : null;
        const frText = frList.length > 0 ? frList.join(" ") : null;

        if (!enText && !frText) return null;

        return { en: enText, fr: frText };
    };
    const allergenData = getAllergenData(product.allergens_warnings);

    const getLinkedUpcs = (linkedProduct) => {
        if (!linkedProduct?.upcs || !Array.isArray(linkedProduct.upcs)) {
            return null;
        }
        return linkedProduct.upcs.map(item => item.code).join(", ");
    };

    // The `product` sub-object is now a deprecated compatibility shim; UPCs are a
    // top-level field on the store product (DetailedStoreProduct.upcs).
    const linkedUpcValue = getLinkedUpcs(product);

    // Brand / raw_brand, price, external_id, sku and site_url were dropped from the
    // store product in the FSDH migration and are no longer returned by the API.
    const productDescItems = [
        { name: "Product Name", value: product.site_name },
        { name: "Store", value: product.store },
        { name: "Source", value: product.source },
        { name: "Product Code", value: product.store_product_code || "None" },
        { name: "UPC", value: linkedUpcValue || "None" },
        { name: "Total Size", value: product.total_size || "Not specified" },
        { name: "Serving Size", value: product.raw_serving_size || "Not specified" },
        { name: "Storage Condition", value: product.storage_condition || "Not available" },
        { name: "Packaging (Primary)", value: product.primary_package_material || "Not available" },
        { name: "Packaging (Secondary)", value: product.secondary_package_material || "Not available" },
    ].filter(item => item.value); // null or undefined values are filtered out

    const isFlagged = product.needs_manual_verification === true || product.needs_manual_verification === 'true';
    const isVerified = product.verified === true || product.verified === 'true';

    const showWarningBanner = isFlagged && !isVerified;
    const showSuccessBanner = isVerified;
    const isTDS = product.source === "2025 Total Diet Study" && !isVerified;

    return (
        <div>
            <Band>
                <Grid container spacing={1} justifyContent="space-between" alignItems="center">
                    <PageIcon product={product.store} />
                    <PageTitle>{product.site_name}</PageTitle>
                </Grid>
            </Band>
            <PageContainer>
                {isTDS && (
                    <Alert severity="warning" sx={{ mb: 3 }}>
                        This product is part of the 2025 Total Diet study. The TDS products have not been completely entered into FLAIME or undergone quality control; may contain errors
                    </Alert>
                )}
                {showWarningBanner && (
                    <Alert severity="warning" sx={{ mb: 3 }}>
                        Automated QC has detected that there may be errors in this product record, and this product has not yet been manually verified. Expect some data fields to contain errors, and compare with the photos
                    </Alert>
                )}
                {showSuccessBanner && (
                    <Alert severity="success" sx={{ mb: 3 }}>
                        This product has been manually verified and all errors have been corrected.
                    </Alert>
                )}
                <ProductInfoBox>
                    <Grid container spacing={6} alignItems="flex-start">
                        <Grid item xs={12} md={6}>
                            {productDescItems.map(item => (
                                <DetailItem key={item.name}><b>{item.name}</b>: {item.value}</DetailItem>
                            ))}
                            {product.site_description && (
                                <DetailItem>
                                    <DescriptionHeader onClick={() => setDescriptionExpanded(!descriptionExpanded)}>
                                        <b>Site description or Package text (click to show)</b>
                                        <ExpandMore
                                            expand={descriptionExpanded}
                                            aria-expanded={descriptionExpanded}
                                            aria-label="show more"
                                        >
                                            <ExpandMoreIcon />
                                        </ExpandMore>
                                    </DescriptionHeader>
                                    <Collapse in={descriptionExpanded} timeout="auto" unmountOnExit>
                                        <Typography variant="body2" style={{ marginTop: '8px' }}>
                                            {product.site_description}
                                        </Typography>
                                    </Collapse>
                                </DetailItem>
                            )}
                            {product.categories &&
                            Object.values(product.categories).some(data =>
                            data.manual?.length > 0 || data.predicted?.length > 0
                            ) && (
                                    <div style={{ marginTop: '20px' }}>
                                    <ProductIngredientsHeadingContainer>
                                        <Divider> Categories </Divider>
                                    </ProductIngredientsHeadingContainer>
                                    <CategoryDisplay categories={product.categories} />
                                </div>
                            )}
                            {(product.ingredient_en || product.ingredient_fr) && (
                            <div>
                                <ProductIngredientsHeadingContainer>
                                    <Divider> Ingredients </Divider>
                                </ProductIngredientsHeadingContainer>
                                {product.ingredient_en && (
                                    <>
                                        <Typography variant="subtitle2" style={{ padding: '10px 10px 0 10px', fontWeight: 'bold', color: '#555' }}>
                                            English
                                        </Typography>
                                        <Typography variant="body2" style={{ padding: '0 10px 10px 10px', textTransform: 'capitalize' }}>
                                            {product.ingredient_en.toLowerCase()}
                                        </Typography>
                                    </>
                                )}
                                
                                {product.ingredient_fr && (
                                    <>
                                        <Typography variant="subtitle2" style={{ padding: '10px 10px 0 10px', fontWeight: 'bold', color: '#555' }}>
                                            French
                                        </Typography>
                                        <Typography variant="body2" style={{ padding: '0 10px 10px 10px', textTransform: 'capitalize' }}>
                                            {product.ingredient_fr.toLowerCase()}
                                        </Typography>
                                    </>
                                )}
                            </div>
                            )}

                            <div style={{ marginTop: '20px' }}>
                                <ProductIngredientsHeadingContainer>
                                    <Divider> Allergen Warnings </Divider>
                                </ProductIngredientsHeadingContainer>
                                {allergenData ? (
                                    <>
                                        {allergenData.en && (
                                            <>
                                                <Typography variant="subtitle2" style={{ padding: '10px 10px 0 10px', fontWeight: 'bold', color: '#555' }}>
                                                    English
                                                </Typography>
                                                <Typography variant="body2" style={{ padding: '0 10px 10px 10px' }}>
                                                    {allergenData.en}
                                                </Typography>
                                            </>
                                        )}
                                        {allergenData.fr && (
                                            <>
                                                <Typography variant="subtitle2" style={{ padding: '10px 10px 0 10px', fontWeight: 'bold', color: '#555' }}>
                                                    French
                                                </Typography>
                                                <Typography variant="body2" style={{ padding: '0 10px 10px 10px' }}>
                                                    {allergenData.fr}
                                                </Typography>
                                            </>
                                        )}
                                    </>
                                ) : (
                                    <Typography variant="body2" style={{ padding: '10px' }}>
                                        Not available
                                    </Typography>
                                )}
                            </div>
                            
                            {product.supplemented_food && product.label_flags && (
                                <div style={{ marginTop: '20px' }}>
                                    <ProductIngredientsHeadingContainer>
                                        <Divider> Supplemented Food Flags </Divider>
                                    </ProductIngredientsHeadingContainer>
                                    <SupplementedFoodFlags labelFlags={product.label_flags} />
                                </div>
                            )}
                        </Grid>
                        <Grid item xs={12} md={6} sx={{ maxWidth: 500 }}>
                            <NutritionFactsTable product={product} />
                            <ProductImages product={product} />
                        </Grid>
                    </Grid>
                </ProductInfoBox>
                <Divider variant="middle" />
            </PageContainer>
        </div>
    );
}

export default ProductDetail;