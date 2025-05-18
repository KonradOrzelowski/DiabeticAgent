import React, { useState, useEffect } from "react";
import "./App.css";
import Axios from "axios";

function App() {
  const [products, setProducts] = useState([]);

  const fetchProducts = async () => {
    const { data } = await Axios.get(
      "http://127.0.0.1:8000/response/"
    );
    const products = data;
    setProducts(products);
    console.log(products);
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return (
    <div>
       {JSON.stringify(products.response)}
    </div>
  );
}

export default App;