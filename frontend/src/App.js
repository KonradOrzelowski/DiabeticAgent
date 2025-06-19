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
    const base64Image = canvas.toDataURL("image/jpeg");

    return base64Image
}


function App() {

    const [output, setOutput] = useState(false);
    const [intermediateSteps, setIntermediateSteps] = useState([]);

    async function sendData(inputValue){

        const imageToSend = await getHeatmap();

        console.log('data', imageToSend)

        const { data } = await Axios.post("http://127.0.0.1:8000/question/", {
            message: inputValue,
            image: imageToSend
        });
        console.log(data)
        console.log(data.message)

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

                onKeyDown={async (event) => {
                    if (event.key === 'Enter') {
                        const inputValue = event.target.value;
                        alert(inputValue)
                        // await sendData(inputValue);
                    }
                }}
                className="input-box"
            />
        </div>
    );

}

export default App;
