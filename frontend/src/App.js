import React, { useState, useEffect } from "react";
import "./App.css";
import Axios from "axios";

import ReactMarkdown from 'react-markdown';

function App() {
    const [products, setProducts] = useState([]);

    const fetchProducts = async () => {
        const { data } = await Axios.get("http://127.0.0.1:8000/response/");
        const products = data;
        setProducts(products);
    };

    useEffect(() => {
        fetchProducts();
    }, []);

    try {
        const response = products.response;

        const input = response.input;
        const output = response.output;
        const intermediate_steps = response.intermediate_steps || [];

        console.log('--- Response Logging Start ---');
        console.log('Input:', input);
        console.log('Output:', output);
        console.log('Intermediate Steps:', intermediate_steps[0][1]);
        console.log('--- Response Logging End ---');

        const intermediateElements = [];

        for (let doc of intermediate_steps[0][1]) {
            console.log(doc)
            intermediateElements.push(

                <div>
                    <h3>{doc.metadata.origin_title} chunk number {doc.metadata.chunk_number}</h3>
                    <ReactMarkdown>{doc['page_content']}</ReactMarkdown>
                </div>
            );
        }

        console.log(intermediateElements);
        return (
            <div className="response">

                <div className="output">
                    <ReactMarkdown>{output}</ReactMarkdown>
                </div>

                <div className="docs">
                    {intermediateElements}
                </div>
                
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
