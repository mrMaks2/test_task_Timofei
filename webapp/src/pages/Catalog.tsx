import React, { useState, useEffect } from "react";
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
  const navigate = useNavigate();

  useEffect(() => {
    const url = selectedCategory
      ? `/products/?category=${selectedCategory}`
      : "/products/";
    api.get(url).then((res) => setProducts(res.data));
  }, [selectedCategory]);

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
      <CategoryList onSelect={setSelectedCategory} />
      <div className="grid">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
