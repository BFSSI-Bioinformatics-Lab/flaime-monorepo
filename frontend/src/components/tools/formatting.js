export const formatIngredients = (ingredientStr) => {
    return ingredientStr.toUpperCase().replaceAll(/,(\S)/g, `, $1`).replaceAll(/\s,/g, `,`)
}