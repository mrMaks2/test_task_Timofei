import { useState } from "react";
import api from "../api/client";

interface Product {
  id: number;
  name: string;
  price: number;
  description: string;
  images: { image: string }[];
}

interface Props {
  product: Product;
  onAdded?: () => void;
}

export default function ProductCard({ product, onAdded }: Props) {
  const [loading, setLoading] = useState(false);

  const addToCart = async () => {
    setLoading(true);
    try {
      await api.post("cart/add_item/", { product_id: product.id, quantity: 1 });
      window.Telegram?.WebApp.showToast?.("Добавлено в корзину");
      onAdded?.();
    } finally {
      setLoading(false);
    }
  };

  const imagePath = product.images?.[0]?.image;
  const apiBase = import.meta.env.VITE_API_URL;
  let apiOrigin = window.location.origin;
  if (apiBase) {
    try {
      apiOrigin = new URL(apiBase).origin;
    } catch {
      apiOrigin = window.location.origin;
    }
  }
  const imageUrl =
    imagePath && imagePath.startsWith("http")
      ? imagePath
      : imagePath
        ? `${apiOrigin}${imagePath.startsWith("/") ? "" : "/"}${imagePath}`
        : undefined;

  return (
    <div className="card product-card">
      {imageUrl && <img src={imageUrl} alt={product.name} />}
      <div className="text-lg">{product.name}</div>
      <div className="text-sm">{product.description}</div>
      <div className="flex justify-between items-center mt-4">
        <div className="text-lg">{product.price} руб.</div>
        <button disabled={loading} onClick={addToCart}>
          {loading ? "Добавляем..." : "В корзину"}
        </button>
      </div>
    </div>
  );
}

