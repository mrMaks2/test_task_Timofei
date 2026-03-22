import { useState, useEffect } from "react";
import api from "../api/client";
import CategoryList from "../components/CategoryList";
import ProductCard from "../components/ProductCard";
import { useNavigate } from "react-router-dom";

interface Product {
  id: number;
  name: string;
  price: number;
  description: string;
  images: { image: string }[];
}

export default function Catalog() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const url = selectedCategory
      ? `products/?category=${selectedCategory}`
      : "products/";
    let active = true;
    setLoading(true);
    setError(null);
    api
      .get(url)
      .then((res) => {
        if (!active) return;
        setProducts(Array.isArray(res.data) ? res.data : []);
      })
      .catch(() => {
        if (!active) return;
        setError("Не удалось загрузить товары. Проверьте доступность API.");
        setProducts([]);
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [selectedCategory, reloadToken]);

  const handleSelect = (categoryId: number | null) => {
    setSelectedCategory(categoryId);
    setReloadToken((value) => value + 1);
  };

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) return;
    tg.MainButton.setText("Корзина");
    tg.MainButton.show();
    const onClick = () => navigate("/cart");
    tg.MainButton.onClick(onClick);
    return () => {
      tg.MainButton.offClick(onClick);
      tg.MainButton.hide();
    };
  }, [navigate]);

  return (
    <div className="container">
      <CategoryList onSelect={handleSelect} />
      {error && <div className="card text-sm">{error}</div>}
      {loading && <div className="card text-sm">Загрузка...</div>}
      {!loading && !error && products.length === 0 && (
        <div className="card text-sm">Товары не найдены.</div>
      )}
      <div className="grid">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}

