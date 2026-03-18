import React, { useState, useEffect } from "react";
import api from "../api/client";
import CartItem from "../components/CartItem";
import { useNavigate } from "react-router-dom";

interface CartItemType {
  id: number;
  quantity: number;
  total_price: number;
  product: {
    id: number;
    name: string;
    price: number;
    images: { image: string }[];
  };
}

export default function Cart() {
  const [items, setItems] = useState<CartItemType[]>([]);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  const loadCart = () => {
    api.get("/cart/").then((res) => {
      setItems(res.data.items || []);
      setTotal(res.data.total_amount || 0);
    });
  };

  useEffect(() => {
    loadCart();
  }, []);

  const updateQuantity = (itemId: number, quantity: number) => {
    api.post("/cart/update_item/", { item_id: itemId, quantity }).then(loadCart);
  };

  const removeItem = (itemId: number) => {
    api.post("/cart/remove_item/", { item_id: itemId }).then(loadCart);
  };

  const checkout = () => {
    navigate("/checkout");
  };

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) return;
    tg.BackButton.show();
    const onBack = () => navigate("/");
    tg.BackButton.onClick(onBack);
    tg.MainButton.setText("Оформить заказ");
    tg.MainButton.show();
    tg.MainButton.onClick(checkout);
    return () => {
      tg.BackButton.offClick(onBack);
      tg.BackButton.hide();
      tg.MainButton.offClick(checkout);
      tg.MainButton.hide();
    };
  }, [navigate]);

  return (
    <div className="container">
      {items.map((item) => (
        <CartItem
          key={item.id}
          item={item}
          onUpdate={updateQuantity}
          onRemove={removeItem}
        />
      ))}
      <div className="text-lg mt-4">Итого: {total} руб.</div>
      <button className="mt-4" onClick={checkout}>
        Оформить заказ
      </button>
    </div>
  );
}
