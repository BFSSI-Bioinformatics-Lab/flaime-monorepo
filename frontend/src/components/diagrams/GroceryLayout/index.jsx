import { useEffect } from "react";
import GroceryLayoutSvgLogic from "./SvgLogic/GroceryLayoutSvgLogic";

const GroceryLayout = () => {

    useEffect(() => {
        GroceryLayoutSvgLogic("#GroceryLayoutDiagram");
    }, []);

    return (
        <div>
                        <img src="https://i.imgur.com/Qv3vnXm.png"></img>

            <h3>Grocery Layout</h3>
            <svg style={{overflow: "visible", margin: "50px"}} id="GroceryLayoutDiagram" width="700" height="700">
            </svg>
        </div>
    )
}

export default GroceryLayout;