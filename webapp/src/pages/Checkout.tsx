import { useState, useEffect } from "react";
import api from "../api/client";
import { useNavigate } from "react-router-dom";

export default function Checkout() {
  const [fullName, setFullName] = useState("");
  const [address, setAddress] = useState("");
  const [phone, setPhone] = useState("");
  const navigate = useNavigate();

  const submit = async () => {
    const tg = window.Telegram?.WebApp;
    try {
      await api.post("orders/", {
        full_name: fullName,
        address,
        phone,
      });
      tg?.showAlert("Заказ оформлен!");
      navigate("/");
    } catch (error) {
      tg?.showAlert("Ошибка при оформлении");
    }
  };

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) return;
    tg.BackButton.show();
    const onBack = () => navigate("/cart");
    tg.BackButton.onClick(onBack);
    tg.MainButton.setText("Подтвердить");
    tg.MainButton.show();
    tg.MainButton.onClick(submit);
    return () => {
      tg.BackButton.offClick(onBack);
      tg.BackButton.hide();
      tg.MainButton.offClick(submit);
      tg.MainButton.hide();
    };
  }, [navigate, fullName, address, phone]);

  return (
    <div className="container">
      <div className="card">
        <div className="text-lg mb-4">Оформление заказа</div>
        <input
          placeholder="ФИО"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
        />
        <input
          placeholder="Адрес"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
        />
        <input
          placeholder="Телефон"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
        <button className="mt-4" onClick={submit}>
          Подтвердить
        </button>
      </div>
    </div>
  );
}

