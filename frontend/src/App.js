import React, { useState, useEffect } from "react";
import "./App.css";
import Axios from "axios";

import ReactMarkdown from 'react-markdown';

import { GlucoseHeatMap } from "./components/GlucoseHeatMap/GlucoseHeatMap";

import html2canvas from 'html2canvas';

async function getHeatmap(){
    const heatmapElement = document.querySelector('.GlucoseHeatMaps');
    if (!heatmapElement) return;

    const canvas = await html2canvas(heatmapElement);

    const newCanvas = document.createElement('canvas');
    const ctx = newCanvas.getContext('2d');
    const scale = 0.3;  // 30% of original size
    newCanvas.width = canvas.width * scale;
    newCanvas.height = canvas.height * scale;

    ctx.drawImage(canvas, 0, 0, newCanvas.width, newCanvas.height);

    const base64Image = canvas.toDataURL("image/jpeg");

    return base64Image
}


function App() {
    const [inputValue, setInputValue] = useState("");

    const [output, setOutput] = useState(false);
    const [intermediateSteps, setIntermediateSteps] = useState([]);

    async function sendData(){

        const imageToSend = await getHeatmap();

        console.log('data', imageToSend)

        const { data } = await Axios.post("http://127.0.0.1:8000/question/", {
            message: inputValue,
            // message: 'inputValue',
            image: imageToSend
        });
        console.log(data.message)
        // const response = data.message;
        // const steps = response.intermediate_steps?.[0]?.[1];
       
        // setOutput(response.output);
        // setIntermediateSteps(Array.isArray(steps) ? steps : []);

    };

    return (
        <div>


            <GlucoseHeatMap/>

            <div className="response">

                <div className="output">
                    <ReactMarkdown>{output || ''}</ReactMarkdown>
                </div>

                <div className="docs">
                     {intermediateSteps.map((doc, idx) => (
                        <div>
                            <h3>{doc.metadata.origin_title} chunk number {doc.metadata.chunk_number}</h3>
                            <ReactMarkdown>{doc['page_content']}</ReactMarkdown>
                        </div>
                     ))}
                </div>

            </div>

            <input
                type="text"
                placeholder="Type your query..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={async (e) => {
                    if (e.key === 'Enter') {
                        setInputValue('');
                        
                        await sendData();
                    }
                }}
                className="input-box"
            />
        </div>
    );

}

export default App;
