import { Oval } from "react-loader-spinner"

interface IProps {
    size?: number,
    color?: string
}

const LoadingButton = ({size=17, color="#B2E6E8"}: IProps) => {
    return (
        <Oval
            height={size}
            width={size}
            wrapperStyle={{
                display: "flex",
                justifyContent: "center",
            }}
            color={color}
            secondaryColor="#000"
            strokeWidth={5}
            strokeWidthSecondary={5}
        /> 
    )
}

export default LoadingButton