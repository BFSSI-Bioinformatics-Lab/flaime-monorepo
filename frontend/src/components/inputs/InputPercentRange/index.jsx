import MultiSlider from "../MultiSlider"

const InputPercentRange = ({min, max, onChange}) => {
    const tickMarks = [0, 20, 40, 60, 80, 100].map(num => ({value: num, label: `${num}%`}))
    return (
        <div>
            <MultiSlider 
                tickMarks={tickMarks} 
                min={min}
                max={max}
                onChange={onChange}
            />
        </div>
    )

}

export default InputPercentRange;