import { useEffect } from "react";
import { HashRouter, Routes, Route } from "react-router-dom";
import { initTelegram } from "./utils/telegram";
import Catalog from "./pages/Catalog";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import TopNav from "./components/TopNav";

function App() {
  useEffect(() => {
    initTelegram()
  }, [])

  return (
    <HashRouter>
      <div className="app-shell">
        <TopNav />
        <main className="app-shell__content">
          <Routes>
            <Route path="/" element={<Catalog />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={<Checkout />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
  );
}

export default App;

