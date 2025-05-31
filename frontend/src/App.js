import React, { useState, useEffect } from "react";
import "./App.css";
import Axios from "axios";

import ReactMarkdown from 'react-markdown';



function App() {
    const [products, setProducts] = useState([]);
    const [inputValue, setInputValue] = useState("");
    const [pressEnter, setPressEnter] = useState(false);

    const [output, setOutput] = useState();
    const [intermediateElements, setIntermediateElements] = useState();


    const fetchProducts = async () => {
        const { data } = await Axios.get("http://127.0.0.1:8000/response/");
        const products = data;
        setProducts(products);
    };
    

    const sendData = async () => {

        const { data } = await Axios.post("http://127.0.0.1:8000/question/", {
            message: inputValue,
        });
        const products = data;
        setProducts(products);

    };

    useEffect(() => {
        console.log('response to go')
        try {
            console.log(products)
            const response = products.message;
            
            setOutput(response["output"])
            const intermediate_steps = response["intermediate_steps"] || [];

            const intermediateElements = [];

            for (let doc of intermediate_steps[0][1]) {
                intermediateElements.push(
                    <div>
                        <h3>{doc.metadata.origin_title} chunk number {doc.metadata.chunk_number}</h3>
                        <ReactMarkdown>{doc['page_content']}</ReactMarkdown>
                    </div>
                );
            }
            setIntermediateElements(intermediateElements);
           
        } catch (error) {
            console.log(error)
        }

    }, [pressEnter]);

    try {

        return (
            <div>
                <div className="response">

                    <div className="output">
                        <ReactMarkdown>{output}</ReactMarkdown>
                    </div>

                    <div className="docs">
                        {intermediateElements}
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
                            setPressEnter(prev => !prev);
                        }
                    }}
                    className="input-box"
                />
            </div>
        );

    } catch (error) {
        console.error('Error while logging response:', error);
        return (
            <div>
                <input
                    type="text"
                    placeholder="Type your query..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={async (e) => {
                        if (e.key === 'Enter') {
                            setInputValue('');
                            
                            await sendData();
                            setPressEnter(prev => !prev);
                        }
                    }}
                    className="input-box"
                />
            </div>
        );
    }
}

export default App;
