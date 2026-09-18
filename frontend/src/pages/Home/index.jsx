import React from 'react'
import { Image } from 'mui-image'
import landing from "../../static/images/landing.jpg"
import { Typography } from '@mui/material'
import DataSourceCard from "../../components/cards/DataSourceCard";
import SearchCard from "../../components/cards/SearchCard";

import {
  HomePageContainer,
  PageTitleTypography,
  PageDescriptionTypography,
  SearchBarContainer,
  DataSourceContainer,
  HeadingContainer
} from "./styles";

const Home = () => {


  return (
    <HomePageContainer>
      <div className='landing-img' style={{ position: "relative" }}>
        <Image src={landing} height='550px' duration={0} easing='ease' opacity={0.5}></Image>
        
        <PageTitleTypography variant="h2">FLAIME</PageTitleTypography>
        <PageDescriptionTypography>
        The Food Label AI for Monitoring the food Environment (FLAIME) is a tool created to collect, organize, harmonize and simplify exploration of various food label datasets. Here you will find multiple ways to explore, query and export information related to the Canadian food supply. Customized reports, visualizations and dashboards are also available to offer informative insights on FND priorities such as the Sodium Reduction Strategy, Front of Pack Labelling, Supplemented Foods and Marketing to Kids.
        </PageDescriptionTypography>
      </div>
      <SearchBarContainer>
      <SearchCard
        title="Quick Search"
        content="The Product Browser is a user-friendly interface for rapid product, store, and general database queries."
        link="/tools/product-browser"
      />
      <SearchCard
        title="Advanced Search"
        content="An in-depth search tool with extended filtering options, including categories and nutrient content."
        link="/tools/advanced-search"
      />
      <SearchCard
        title="Product Finder"
        content="Specialised search for product lists using names, UPCs, or IDs. Supports file upload and filtering by date, store, and region."
        link="/tools/product-finder"
      />
      </SearchBarContainer>
      <div>
        <HeadingContainer maxWidth="sm">
          <Typography variant="h3" color="primary.dark" align="center">About the Data Sources</Typography>
        </HeadingContainer>

        <DataSourceContainer>
          <DataSourceCard
            title="FLIP Data"
            content="University of Toronto FLIP database of prepackaged food labels. The 2017 collection includes pictures and food information off labels from Sobeys, Loblaws and Metro in Toronto."
            link="about"
          />
          <DataSourceCard
            title="Nielsen Data"
            content="NielsenIQ label data. Presently only the 2017 Sodium collection is present. This includes barcode information, images with all sides of packaging as well as all food label data."
            link="about"
          />
          <DataSourceCard
            title="Web Scrape Data"
            content="Includes data collected from Canadian grocery store websites since 2019. The last web scrape was from 2023 and was a collaboration between FND and University of Toronto FLIP team."
            link="about"
          />
        </DataSourceContainer>
      </div>

      
      
    </HomePageContainer>
  )
}

export default Home