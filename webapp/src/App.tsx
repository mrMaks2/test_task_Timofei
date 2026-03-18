import React, { useEffect } from "react";
import { HashRouter, Routes, Route } from "react-router-dom";
import { initTelegram } from "./utils/telegram";
import Catalog from "./pages/Catalog";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";

function App() {
  useEffect(() => {
    initTelegram()
  }, [])

  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Catalog />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/checkout" element={<Checkout />} />
      </Routes>
    </HashRouter>
  );
}

export default App;
