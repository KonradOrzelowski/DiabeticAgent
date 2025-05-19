import React, { useState, useEffect } from "react";
import "./App.css";
import Axios from "axios";

import ReactMarkdown from 'react-markdown';



function App() {
    const [products, setProducts] = useState([]);
    const [inputValue, setInputValue] = useState("");
    const [pressEnter, setPressEnter] = useState(false);


    const fetchProducts = async () => {
        const { data } = await Axios.get("http://127.0.0.1:8000/response/");
        const products = data;
        setProducts(products);
    };
    

    useEffect(() => {
        fetchProducts();
        console.log('!!!!!!!!!!!!!!!!')
    }, [pressEnter]);

    try {
        const response = products.response;

        const output = response.output;
        const intermediate_steps = response.intermediate_steps || [];

        const intermediateElements = [];

        for (let doc of intermediate_steps[0][1]) {
            intermediateElements.push(
                <div>
                    <h3>{doc.metadata.origin_title} chunk number {doc.metadata.chunk_number}</h3>
                    <ReactMarkdown>{doc['page_content']}</ReactMarkdown>
                </div>
            );
        }

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
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            alert(inputValue);
                            setInputValue('');
                            setPressEnter(~pressEnter)
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
                An error occure
            </div>
        );
    }
}

export default App;
