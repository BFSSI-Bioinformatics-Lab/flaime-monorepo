import PageContainer from "../PageContainer";
import { BannerBox } from "./styles";

const Band = ({children}) => {
    return (
        <BannerBox>
            <PageContainer>
                {children}
            </PageContainer>
        </BannerBox>
    )
}

export default Band;
