import React, { useEffect } from 'react'
import { Typography, Divider } from '@mui/material'
import { AboutPageContainer, InfoContainer, PageTitleTypography, SectionTitleTypography } from './styles'

const About = () => {

  useEffect(() => {
    window.scrollTo(0, 0); // Scroll to the top of the page when the component mounts
  }, []);

  return (
    <AboutPageContainer>
        
      <PageTitleTypography variant="h3">About FLAIME</PageTitleTypography>

      <div>
        <SectionTitleTypography variant="h4">Terms and Conditions of the data in the FLAIME database</SectionTitleTypography>
        <InfoContainer>
          <div id='flip'>
            <Typography variant='h5'>FLIP Data</Typography>
            <Typography variant='body1'>
            University of Toronto Food Label Information Program (FLIP) database of prepackaged food labels. Data accessed via data sharing agreement between the University of Toronto and Health Canada’s Bureau of Nutritional Sciences and Office of Nutrition Policy and Promotion expiring October 5, 2025. Data is confidential. For information about the data and its use, please contact Susan Trang (susan.trang@hc-sc.gc.ca; lead for data sharing agreement). Results from FLIP data used in non-confidential documents must be reviewed by Mary L’Abbé’s team and must include acknowledgement of all authors and grant funding. Mary’s team must also be notified of any errors the data entry of label Nutrition Facts table and Ingredient values. *University of Toronto Food Label Information and Price (FLIP)© database formerly known as “Food Label Information Program”.
            </Typography>
            <br/>
            <Typography variant='body1'>
            Since 2010, the L’Abbé Lab has maintained a database of packaged foods that is updated every 3-4 years for monitoring and testing hypotheses related to the Canadian food supply. The FLIP underwent its most recent collection in 2020. The FLIP contains food label information for more than 80,000 food products from top food retailers in Canada. This data allows for in-depth nutritional analyses of the Canadian food supply spanning 10 years. The 2017 collection includes pictures and food information off labels from Sobeys, Loblaws and Metro in Toronto. <br/>
            For more imformation on the FLIP database, please visit the University of Toronto’s 
            <a href="https://labbelab.utoronto.ca/projects/the-canadian-food-supply/" target="_blank" rel="noreferrer"> L’Abbé Lab website</a>.
            </Typography> 
          </div>

          <div id='nielsen' style={{marginTop: "20px"}}>
            <Typography variant='h5'>Nielsen Data</Typography>
            <Typography variant='body1'>
            2017 Health Canada and NielsenIQ data. Data is for internal use only. For information about the data and its use, please contact Konstantinia Arvaniti, M.Sc., Ph.D. (Konstantinia.arvaniti@hc-sc.gc.ca; Project Authority). In all cases, disclosed Information must show NielsenIQ’s copyright; be accurately labeled; and not be presented in a misleading manner. To inform NielsenIQ either before, or as soon as reasonably possible after, any such release, disclosure or sharing of Disclosable Information (label description, ingredients, and the nutrition facts table data).
            </Typography>
          </div>
        </InfoContainer>
      </div>
      <Divider style={{ width: '50%', margin: '30px auto 0 auto' }} />
      <div style={{paddingBottom: "5%"}}>
        <SectionTitleTypography variant='h4' >About the Team</SectionTitleTypography>
        <InfoContainer>
          <Typography variant='body1'>
          Bioinformatics and Data Science is a division of the Bureau of Data, Science and Knowledge Integration within Health Canada’s Food and Nutrition Directorate (FND). Initially set up to provide a bridge between biology and computer science, the Division has developed into a multidisciplinary team that harnesses the power of computer science to support the research needs of FND – effectively translating raw science data into more digestible forms.
          </Typography>
          <div  style={{marginTop: "20px"}}>
            <Typography variant='h5'>What services do we provide?</Typography>
            <Typography variant='body1'>
            The Bioinformatics and Data Science Division provides a wide range of services to support the complex needs of individual research teams within FND. These research teams often face unique challenges in analysing and processing the raw data provided by both government and academic sources. By leveraging a strong knowledge of both biological and computer sciences, members of the Division are able to assist research teams in more efficiently accessing and understanding their data - providing the analytical “grease” to keep the research wheels moving.
            </Typography>
          </div>
        </InfoContainer>
        
      </div>
        
    </AboutPageContainer>
  )
}

export default About