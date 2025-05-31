import React, { useState, useEffect } from "react";
import "./App.css";
import Axios from "axios";

import ReactMarkdown from 'react-markdown';
import CalendarHeatmap from 'react-calendar-heatmap';
import 'react-calendar-heatmap/dist/styles.css';



function App() {
    const [products, setProducts] = useState([]);
    const [inputValue, setInputValue] = useState("");

    const [output, setOutput] = useState(false);
    const [intermediateSteps, setIntermediateSteps] = useState([]);


    const fetchProducts = async () => {
        const { data } = await Axios.get("http://127.0.0.1:8000/response/");
        const products = data;
        setProducts(products);
    };
    

    const sendData = async () => {

        const { data } = await Axios.post("http://127.0.0.1:8000/question/", {
            message: inputValue,
        });

        const response = data.message;
        const steps = response.intermediate_steps?.[0]?.[1];
       
        setOutput(response.output);
        setIntermediateSteps(Array.isArray(steps) ? steps : []);

    };

    return (
        <div>

            <div style={{
            width: '50%',
            height: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid #ccc' // optional: just to see the border
            }}>
            <CalendarHeatmap
                startDate={new Date('2016-01-01')}
                endDate={new Date('2016-04-01')}
                values={[
                { date: '2016-01-01', count: 12 },
                { date: '2016-01-22', count: 122 },
                { date: '2016-01-30', count: 38 }
                ]}
            />
            </div>


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
