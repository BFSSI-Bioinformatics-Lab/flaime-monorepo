import * as d3 from "d3";

const dim = {
    edgeCategoryWidth: 320,
    edgeCategoryHeight: 65,
    edgeCategoryImageBorderWidth: 95,
    edgeCategoryImageBorderThickness: 13,
    edgeCategoryLabelWidth: 65,
    edgeCategoryLabelHeight: 35,
    edgeCategoryTitleFontSize: 14,
    edgeCategoryLabelFontSize: 18,
    middleCategorySpacing: 60,
    middleCategorySectionWidth: 330,
    middleCategorySectionHeight: 40,
    middleCategoryStartX: 200,
    middleCategoryStartY: 200,
    middleCategoryWidth: 120,
    middleCategoryHeight: 50,
    middleCategoryImageWidth: 40,
    middleCategoryImageHeight: 40,
    middleCategoryLabelWidth: 35,
    middleCategoryLabelHeight: 25,
    middleCategoryTitleFontSize: 12,
    middleCategoryLabelFontSize: 18,


}

const edgeCategories = [
    {
        title: "Other Processed Meats & Poultry",
        image: "https://th.bing.com/th/id/OIP.PF84CrZV9Orqy0okToqG0AHaJ4?pid=ImgDet&rs=1",
        posX: 0,
        posY: 0,
        background: "#0E4B77",
        colour: "white",
        orientation: "h",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        direction: "e",
        label: "94%" 
    },
    {
        title: "Meats, Poultry & Seafood*",
        image: "https://th.bing.com/th/id/OIP.4aBEtOYuBfjUINUWzHjZRgHaFu?pid=ImgDet&rs=1",
        posX: dim.edgeCategoryWidth,
        posY: 0,
        background: "#347ABF",
        colour: "white",
        orientation: "h",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        direction: "e",
        label: "4%"  
    },
    {
        title: "Ground Meat & Poultry*",
        image: "https://th.bing.com/th/id/R.e1d709fc01d327cd5d8a429b27fc41b6?rik=KSdagOU4oA61ug&pid=ImgRaw&r=0",
        posX: 0,
        posY: dim.edgeCategoryHeight,
        background: "#BF1E2D",
        colour: "white",
        orientation: "v",
        width: dim.edgeCategoryHeight,
        height: dim.edgeCategoryWidth,
        direction: "s",
        label: "0%"  
    },
    {
        title: "Deli Meats",
        image: "https://th.bing.com/th/id/R.e1d709fc01d327cd5d8a429b27fc41b6?rik=KSdagOU4oA61ug&pid=ImgRaw&r=0",
        posX: 0,
        posY: dim.edgeCategoryHeight + dim.edgeCategoryWidth,
        background: "#551523",
        colour: "white",
        orientation: "v",
        width: dim.edgeCategoryHeight,
        height: dim.edgeCategoryWidth,
        direction: "s",
        label: "93%"  
    },
    {
        title: "Dairy",
        image: "https://th.bing.com/th/id/R.e1d709fc01d327cd5d8a429b27fc41b6?rik=KSdagOU4oA61ug&pid=ImgRaw&r=0",
        posX: dim.edgeCategoryWidth * 2,
        posY: 0,
        background: "#F5BA16",
        colour: "black",
        orientation: "h",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        direction: "e",
        label: "36%"  
    },
    {
        title: "Frozen Desserts",
        image: "https://th.bing.com/th/id/R.e1d709fc01d327cd5d8a429b27fc41b6?rik=KSdagOU4oA61ug&pid=ImgRaw&r=0",
        posX: dim.edgeCategoryWidth * 3 + 2 * dim.edgeCategoryWidth / 3,
        posY: dim.edgeCategoryHeight + dim.edgeCategoryWidth / 3,
        background: "#A4C6D2",
        colour: "black",
        orientation: "v",
        width: dim.edgeCategoryHeight,
        height: dim.edgeCategoryWidth - dim.edgeCategoryWidth / 6,
        direction: "e",
        label: "91%"  
    },
    {
        title: "Frozen Entrees & Sides",
        image: "https://th.bing.com/th/id/R.e1d709fc01d327cd5d8a429b27fc41b6?rik=KSdagOU4oA61ug&pid=ImgRaw&r=0",
        posX: dim.edgeCategoryWidth * 3 + 2 * dim.edgeCategoryWidth / 3 ,
        posY: dim.edgeCategoryHeight + dim.edgeCategoryWidth + dim.edgeCategoryWidth / 3 - dim.edgeCategoryWidth / 6,
        background: "#64B1C5",
        colour: "white",
        orientation: "v",
        width: dim.edgeCategoryHeight,
        height: dim.edgeCategoryWidth - dim.edgeCategoryWidth / 6,
        direction: "e",
        label: "74%"  
    },
    {
        title: "Produce",
        image: "https://th.bing.com/th/id/OIP.RPmmPtD6woy9rRDknjBIFAHaFz?pid=ImgDet&rs=1",
        posX: dim.edgeCategoryWidth * 1.9 + 2 * dim.edgeCategoryWidth / 3 + dim.edgeCategoryHeight,
        posY: dim.edgeCategoryHeight + dim.edgeCategoryWidth * 2,
        background: "#69C18E",
        colour: "black",
        orientation: "h",
        width: dim.edgeCategoryWidth * 1.1,
        height: dim.edgeCategoryHeight,
        direction: "s",
        label: "0%"  
    },
    {
        title: "Bakery",
        image: "https://th.bing.com/th/id/R.e1d709fc01d327cd5d8a429b27fc41b6?rik=KSdagOU4oA61ug&pid=ImgRaw&r=0",
        posX: 0,
        posY: dim.edgeCategoryHeight + dim.edgeCategoryWidth * 2,
        background: "#F89432",
        colour: "black",
        orientation: "h",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        direction: "e",
        label: "62%"  
    },
    {
        title: "Eggs",
        image: "",
        posX: dim.edgeCategoryWidth * 3,
        posY: 0,
        background: "#D4ECF6",
        colour: "black",
        orientation: "h",
        width: dim.edgeCategoryWidth - dim.edgeCategoryWidth / 3,
        height: dim.edgeCategoryHeight,
        direction: "e",
        label: "0%"  
    },
    {
        title: "",
        image: "https://th.bing.com/th/id/R.e1d709fc01d327cd5d8a429b27fc41b6?rik=KSdagOU4oA61ug&pid=ImgRaw&r=0",
        posX: dim.edgeCategoryWidth * 3 + 2 * dim.edgeCategoryWidth / 3,
        posY: 0,
        background: "#D4ECF6",
        orientation: "v",
        width: dim.edgeCategoryHeight,
        height: 1.75 * dim.edgeCategoryWidth / 3,
        direction: "e" 
    },
]

const middleSections = [
    {
        posX: dim.middleCategoryStartX,
        posY: dim.middleCategoryStartY
    },
    {
        posX: dim.middleCategoryStartX + dim.middleCategorySectionWidth + dim.middleCategoryWidth + dim.middleCategorySpacing,
        posY: dim.middleCategoryStartY,
    },
    {
        posX: dim.middleCategoryStartX,
        posY: dim.middleCategoryStartY + dim.middleCategoryHeight + dim.middleCategorySpacing   
    },
    {
        posX: dim.middleCategoryStartX + dim.middleCategorySectionWidth + dim.middleCategoryWidth + dim.middleCategorySpacing,
        posY: dim.middleCategoryStartY + dim.middleCategoryHeight + dim.middleCategorySpacing   
    },
    {
        posX: dim.middleCategoryStartX,
        posY: dim.middleCategoryStartY + 2 * dim.middleCategoryHeight + 2 * dim.middleCategorySpacing
    },
    {
        posX: dim.middleCategoryStartX + dim.middleCategorySectionWidth + dim.middleCategoryWidth + dim.middleCategorySpacing,
        posY: dim.middleCategoryStartY + 2 * dim.middleCategoryHeight + 2 * dim.middleCategorySpacing
    },
    {
        posX: dim.middleCategoryStartX,
        posY: dim.middleCategoryStartY + 3 * dim.middleCategoryHeight + 3 * dim.middleCategorySpacing 
    },
    {
        posX: dim.middleCategoryStartX + dim.middleCategorySectionWidth + dim.middleCategoryWidth + dim.middleCategorySpacing,
        posY: dim.middleCategoryStartY + 3 * dim.middleCategoryHeight + 3 * dim.middleCategorySpacing
    }
]
const middleCategories = [
    {
        title: "Chips & Snacks",
        image: "https://th.bing.com/th/id/OIP.3WFo6gCjVVKHRFAQPGMZuAHaD7?pid=ImgDet&rs=1",
        posX: middleSections[0].posX,
        posY: middleSections[0].posY,
        orientation: "u",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "s",
        label: "60%"  
    },
    {
        title: "Entree Sauces",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[0].posX + dim.middleCategorySectionWidth - dim.middleCategoryWidth,
        posY: middleSections[0].posX + dim.middleCategorySectionHeight,
        orientation: "d",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "e",
        label: "70%"  
    },
    {
        title: "Beverages",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[1].posX,
        posY: middleSections[1].posY + dim.middleCategorySectionHeight,
        orientation: "d",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "s",
        label: "72%"  
    },
    {
        title: "Candies & Sweets",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[1].posX + dim.middleCategorySectionWidth - dim.middleCategoryWidth,
        posY: middleSections[1].posY,
        orientation: "u",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "e",
        label: "91%"  
    },
    {
        title: "Condiments",
        image: "https://th.bing.com/th/id/OIP.3WFo6gCjVVKHRFAQPGMZuAHaD7?pid=ImgDet&rs=1",
        posX: middleSections[2].posX,
        posY: middleSections[2].posY,
        orientation: "u",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "s",
        label: "58%"  
    },
    {
        title: "Breakfast Spreads",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[2].posX  + dim.middleCategorySectionWidth - dim.middleCategoryWidth,
        posY: middleSections[2].posY + dim.middleCategorySectionHeight,
        orientation: "d",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "e",
        label: "33%"  
    },
    {
        title: "Canned Meats & Seafood",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[3].posX,
        posY: middleSections[3].posY + dim.middleCategorySectionHeight,
        orientation: "d",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "s" ,
        label: "43%" 
    },
    {
        title: "Salad Dressings & Vinegars",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[3].posX + dim.middleCategorySectionWidth - dim.middleCategoryWidth,
        posY: middleSections[3].posY,
        orientation: "u",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "e",
        label: "63%"  
    },
    {
        title: "Breakfast Cereals",
        image: "https://th.bing.com/th/id/OIP.3WFo6gCjVVKHRFAQPGMZuAHaD7?pid=ImgDet&rs=1",
        posX: middleSections[4].posX,
        posY: middleSections[4].posY,
        orientation: "u",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "s",
        label: "25%"  
    },
    {
        title: "Granola Bars",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[4].posX  + dim.middleCategorySectionWidth - dim.middleCategoryWidth,
        posY: middleSections[4].posY + dim.middleCategorySectionHeight,
        orientation: "d",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "e",
        label: "49%"  
    },
    {
        title: "Baking Ingredients & Spices",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[5].posX,
        posY: middleSections[5].posY + dim.middleCategorySectionHeight,
        orientation: "d",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "s",
        label: "56%"  
    },
    {
        title: "Soups",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[5].posX + dim.middleCategorySectionWidth - dim.middleCategoryWidth,
        posY: middleSections[5].posY,
        orientation: "u",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "e",
        label: "93%"  
    },
    {
        title: "Cookies & Crackers",
        image: "https://th.bing.com/th/id/OIP.3WFo6gCjVVKHRFAQPGMZuAHaD7?pid=ImgDet&rs=1",
        posX: middleSections[6].posX,
        posY: middleSections[6].posY,
        orientation: "u",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "s",
        label: "62%"  
    },
    {
        title: "Dried Fruits",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[7].posX,
        posY: middleSections[7].posY + dim.middleCategorySectionHeight,
        orientation: "d",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "s",
        label: "33%"  
    },
    {
        title: "Nuts & Seeds",
        image: "https://i5.walmartimages.com/asr/00b9e6c0-173f-427a-9567-639dc443b476.ca9c4a298cc7b7e155643bc5524c2f0b.jpeg",
        posX: middleSections[7].posX + dim.middleCategorySectionWidth - dim.middleCategoryWidth,
        posY: middleSections[7].posY,
        orientation: "u",
        width: dim.edgeCategoryWidth,
        height: dim.edgeCategoryHeight,
        sectionPos: "e",
        label: "0%"  
    },
]

const getEdgeContainerImagePositionX = (d) => {
    if (d.orientation === "h") {
        return d.direction === "e" ? d.posX + d.width : d.posX
    } else {
        return d.posX + d.width / 2
    }
}

const getEdgeContainerImagePositionY = (d) => {
    if (d.orientation === "h") {
        return d.posY + d.height / 2;
    } else {
        return d.direction === "e" ? d.posY + d.height : d.posY
    }
}

const getMiddleCategoryHeadingWidth = (d) => {
    console.log(d)
    return dim.middleCategoryWidth / 1.5 + d.title.length * 2
}

const getEdgeCategoryLabelX = (d, numLines) => {
    console.log(numLines)
    return d.orientation === "h" ? d.posX + 40 + ((d3.max(numLines) + 4)) * dim.edgeCategoryTitleFontSize : d.posX
}

const getEdgeCategoryLabelY = (d, numLines) => {
    return d.orientation === "h" ? d.posY + (dim.edgeCategoryHeight - dim.edgeCategoryLabelHeight) / 2 : d.posY + dim.edgeCategoryWidth / 4 + (numLines[0] + 2) * dim.edgeCategoryTitleFontSize
}

const splitTextWidth = (textElement, text, width, fontSize, x, y, numLines = [0]) => {
    const words = text ? text.split(" ") : textElement.text().split(" ");
        words.reduce((arr, word) => {
            let textNode = arr[arr.length - 1];
            let line = textNode.text().split(" ");
            line.push(word);
            textNode.text(line.join(" "))
            if (textNode.node().getComputedTextLength() > width) {
                line.pop();
                textNode.text(line.join(" "));
                textNode = textElement.append("tspan")
                    .attr("y", y + (arr.length + 1) * fontSize)
                    .attr("x", x + width / 2)
                    .text(word);
                arr.push(textNode);
                numLines[0]++;
                numLines.push(textNode.text().length)
            } else {
                textNode.text(line.join(" "));
                arr[arr.length - 1] = textNode;
            }
            return arr;
        }, [textElement.append("tspan").attr("x", x + width / 2).attr("y", y + fontSize)])  
        numLines[0]++; 
        numLines.push(words.pop().length)
}  

const edgeCategoryDrawTextAndLabel = (container, d) => {
    const numLines = [0];
    const textElement =  container.append("text")
                            .attr("text-anchor", "middle")
                            .attr("font-weight", "bold")
                            .attr("fill", d.colour)
                            .attr("font-size", dim.edgeCategoryTitleFontSize)
    splitTextWidth(
        textElement, 
        d.title, 
        d.orientation === "h" ? dim.edgeCategoryWidth / 3 : dim.edgeCategoryHeight * 0.8, 
        dim.edgeCategoryTitleFontSize, 
        d.orientation === "h" ? d.posX + dim.edgeCategoryWidth / 4 : d.posX + dim.edgeCategoryHeight * 0.1, 
        d.orientation === "h" ? d.posY - 3 : d.posY + dim.edgeCategoryWidth / 4,
        numLines
    )

    const translateY = (((dim.edgeCategoryHeight / (dim.edgeCategoryTitleFontSize)) - numLines[0]) / 2) * dim.edgeCategoryTitleFontSize
    d.orientation === "h" && textElement.attr("transform", `translate(0, ${translateY})`)
    if (d.label) {
        container.append("rect")
            .attr("fill", "#D4E2A5")
            .attr("stroke", d.background)
            .attr("stroke-width", 5)
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .attr("width", dim.edgeCategoryLabelWidth)
            .attr("height", dim.edgeCategoryLabelHeight)
            .attr("x", getEdgeCategoryLabelX(d, numLines))
            .attr("y", getEdgeCategoryLabelY(d, numLines))

        container.append("text")
            .attr("text-anchor", "middle")
            .attr("font-size", dim.edgeCategoryLabelFontSize)
            .attr("font-weight", "bold")
            .attr("fill", "black")
            .attr("x", getEdgeCategoryLabelX(d, numLines) + (dim.edgeCategoryLabelWidth) / 2 + 5)
            .attr("y", getEdgeCategoryLabelY(d, numLines) + (dim.edgeCategoryLabelHeight - 5 + dim.edgeCategoryLabelFontSize) / 2)
            .text(d.label ?? "0%")
    }
}

export default (svgId) => {

    const svg = d3.select(svgId);
        svg.selectAll("g").remove();

    const edgeContainer = svg.append("g")
        .attr("width", 600)
        .attr("height", 600)

    const edgeContainerImageClipPath = edgeContainer.append("clipPath")
        .attr("id", "circular")
        .append("circle")
        .attr("cx", dim.edgeCategoryImageBorderWidth / 2)
        .attr("cy", dim.edgeCategoryImageBorderWidth / 2)
        .attr("r", (dim.edgeCategoryImageBorderWidth - dim.edgeCategoryImageBorderThickness) / 2)

    edgeContainer.append("g").selectAll("rect")
        .data(edgeCategories)
        .enter()
        .append("rect")
            .attr("x", d => d.posX)
            .attr("y", d => d.posY)
            .attr("width", d => d.width)
            .attr("height", d => d.height)
            .attr("fill", d => d.background)

    
    edgeContainer.append("g").selectAll("circle")
        .data(edgeCategories)
        .enter()
        .append("circle")
            .attr("cx", d => getEdgeContainerImagePositionX(d))
            .attr("cy", d => getEdgeContainerImagePositionY(d))
            .attr("r", d => d.image ? dim.edgeCategoryImageBorderWidth / 2 : 0)
            .attr("fill", d => d.background)

    edgeContainer.append("g").selectAll("circle")
        .data(edgeCategories)
        .enter()
        .append("circle")   
            .attr("cx", d => getEdgeContainerImagePositionX(d))
            .attr("cy", d => getEdgeContainerImagePositionY(d))
            .attr("r", d => d.image ? (dim.edgeCategoryImageBorderWidth - dim.edgeCategoryImageBorderThickness)/ 2 : 0)
            .attr("fill", "white")

    edgeContainer.append("g").selectAll("image")
        .data(edgeCategories)
        .enter()
        .append("image")   
            .attr("x", 0)
            .attr("y", 0)
            .attr("transform", d => `translate(${d.orientation === "h" ? getEdgeContainerImagePositionX(d) - dim.edgeCategoryImageBorderWidth / 2 :  getEdgeContainerImagePositionX(d) - (dim.edgeCategoryImageBorderWidth) / 2},
            ${d.orientation === "h" ?  getEdgeContainerImagePositionY(d) - (dim.edgeCategoryImageBorderWidth) / 2 :  getEdgeContainerImagePositionY(d) - dim.edgeCategoryImageBorderWidth / 2})`)
            .attr("href", d => d.image)
            .attr("width", d => d.image ? dim.edgeCategoryImageBorderWidth : 0)
            .attr("height", dim.edgeCategoryImageBorderWidth)
            .attr("clip-path", "url(#circular)")

    const edgeContainerTitles = edgeContainer.append("g");
    edgeContainerTitles.selectAll("text")
        .data(edgeCategories)
        .enter()
        .each(
            d => {
                d.title && edgeCategoryDrawTextAndLabel(edgeContainerTitles, d)
            });

    const middleContainer = svg.append("g")
        .attr("width", 600)
        .attr("height", 600)

    middleContainer.append("g").selectAll("line")
        .data(middleSections)
        .enter()
        .append("line")
            .attr("x1", d => d.posX - 0.5)
            .attr("y1", d => d.posY + dim.middleCategorySectionHeight / 2)
            .attr("x2", d => d.posX + dim.middleCategorySectionWidth + 0.5)
            .attr("y2",  d => d.posY + dim.middleCategorySectionHeight / 2 )
            .attr("stroke", "black")
            .attr("stroke-width", dim.middleCategorySectionHeight + 2)
            .attr("stroke-linecap", "round")
    middleContainer.append("g").selectAll("line")
        .data(middleSections)
        .enter()
        .append("line")
            .attr("x1", d => d.posX)
            .attr("y1", d => d.posY + dim.middleCategorySectionHeight / 2)
            .attr("x2", d => d.posX + dim.middleCategorySectionWidth)
            .attr("y2",  d => d.posY + dim.middleCategorySectionHeight / 2)
            .attr("stroke", "#E5E6E8")
            .attr("stroke-width", dim.middleCategorySectionHeight)
            .attr("stroke-linecap", "round")

    middleContainer.append("g").selectAll("rect")
        .data(middleCategories)
        .enter()
        .append("rect")
            .attr("x", d => d.posX + (d.sectionPos === "e" ? dim.middleCategoryWidth - getMiddleCategoryHeadingWidth(d) : 0))
            .attr("y", d => d.posY - dim.middleCategoryTitleFontSize / 2)
            .attr("width", d => getMiddleCategoryHeadingWidth(d))
            .attr("height", dim.middleCategoryTitleFontSize)
            .attr("fill", "#F7CD43")
            .attr("stroke", "#F7CD43")
            .attr("stroke-width", 15)
            .attr("stroke-linejoin", "round")

    const middleContainerTitles = middleContainer.append("g")
    middleContainerTitles.selectAll("g")
        .data(middleCategories)
        .enter()
        .each(
            d => 
                splitTextWidth(
                    middleContainerTitles.append("text")
                        .attr("font-weight", 600)
                        .attr("font-size", dim.middleCategoryTitleFontSize), 
                    d.title.toUpperCase(), 
                    getMiddleCategoryHeadingWidth(d), 
                    dim.middleCategoryTitleFontSize, 
                    d.posX + (d.sectionPos === "e" ? dim.middleCategoryWidth - getMiddleCategoryHeadingWidth(d) : 0) - getMiddleCategoryHeadingWidth(d) / 2, 
                    d.posY - dim.middleCategoryTitleFontSize
                )
            );

    middleContainer.append("g").selectAll("image")
        .data(middleCategories)
        .enter()
        .append("image")   
            .attr("x", d => d.posX + (d.sectionPos === "e" ? dim.middleCategoryWidth - getMiddleCategoryHeadingWidth(d) : 0) - dim.middleCategoryImageWidth)
            .attr("y", d => d.posY - dim.middleCategoryImageHeight + dim.middleCategoryHeight / 4)
            .attr("href", d => d.image)
            .attr("width", dim.middleCategoryImageWidth)
            .attr("height", dim.middleCategoryImageHeight)
            .attr("preserveAspectRatio", "xMaxYMin slice")

    /* Percentage Labels */
    const middleCategoriesWithLabel = middleCategories.filter(d => d.label)
    middleContainer.append("g").selectAll("rect")
        .data(middleCategoriesWithLabel)
        .enter()
        .append("rect")
            .attr("x", d => d.posX + (d.sectionPos === "e" ? dim.middleCategoryWidth - getMiddleCategoryHeadingWidth(d) : 0) + getMiddleCategoryHeadingWidth(d) - dim.middleCategoryLabelWidth / 1.25) 
            .attr("y", d => d.posY + (d.orientation === "u" ? -dim.middleCategoryLabelHeight * 1.25 : dim.middleCategorySectionHeight / 2))
            .attr("width", dim.middleCategoryLabelWidth - dim.middleCategoryLabelHeight / 4)
            .attr("height", dim.middleCategoryLabelHeight / 2)
            .attr("fill", "black")
            .attr("stroke", "black")
            .attr("stroke-width", dim.middleCategoryLabelHeight / 1.5)
            .attr("stroke-linejoin", "round")    

    middleContainer.append("g").selectAll("rect")
        .data(middleCategoriesWithLabel)
        .enter()
        .append("rect")
            .attr("x", d => d.posX + (d.sectionPos === "e" ? dim.middleCategoryWidth - getMiddleCategoryHeadingWidth(d) : 0) + getMiddleCategoryHeadingWidth(d) - dim.middleCategoryLabelWidth / 1.25)
            .attr("y", d => d.posY + (d.orientation === "u" ? -dim.middleCategoryLabelHeight * 1.25 : dim.middleCategorySectionHeight / 2))
            .attr("width", dim.middleCategoryLabelWidth - dim.middleCategoryLabelHeight / 4)
            .attr("height", dim.middleCategoryLabelHeight / 2)
            .attr("fill", "#DAE5A9")
            .attr("stroke", "#DAE5A9")
            .attr("stroke-width", dim.middleCategoryLabelHeight / 2)
            .attr("stroke-linejoin", "round")

    middleContainer.append("g").selectAll("text")
        .data(middleCategoriesWithLabel)
        .enter()
        .append("text")
            .attr("x", d => d.posX + (d.sectionPos === "e" ? dim.middleCategoryWidth - getMiddleCategoryHeadingWidth(d) : 0) + getMiddleCategoryHeadingWidth(d)- dim.middleCategoryLabelWidth / 3)
            .attr("y", d => d.posY + (d.orientation === "u" ? - (dim.middleCategoryLabelHeight + dim.edgeCategoryLabelFontSize) / 2.25 : dim.middleCategorySectionHeight / 2 + (dim.middleCategoryLabelHeight + dim.edgeCategoryLabelFontSize) / 3.5))
            .text(d => d.label)
            .attr("text-anchor", "middle")
            .attr("font-size", dim.middleCategoryLabelFontSize)
            .attr("font-weight", "bold")
}