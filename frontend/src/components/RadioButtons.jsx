import "../styles/App.css"
function RadioButtons({color,handleColorChange}){


    return(
        <div className="flex space-x-4">
            <label className="flex items-center space-x-2">
            <input
                type="radio"
                value="w"
                checked={color() === 'w'}
                onChange={handleColorChange}
                className="form-radio h-5 w-5 text-blue-600"
            />
            <span className="text-gray-700">White</span>
            </label>
            <label className="flex items-center space-x-2">
            <input
                type="radio"
                value="b"
                checked={color() === 'b'}
                onChange={handleColorChange}
                className="form-radio h-5 w-5 text-blue-600"
            />
            <span className="text-gray-700">Black</span>
            </label>
        </div>
    )
}

export default RadioButtons