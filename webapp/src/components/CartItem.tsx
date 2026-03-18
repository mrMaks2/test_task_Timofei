import React from "react";

interface CartItem {
  id: number;
  product: {
    id: number;
    name: string;
    price: number;
    images: { image: string }[];
  };
  quantity: number;
  total_price: number;
}

interface Props {
  item: CartItem;
  onUpdate: (itemId: number, quantity: number) => void;
  onRemove: (itemId: number) => void;
}

export default function CartItem({ item, onUpdate, onRemove }: Props) {
  return (
    <div className="card">
      <div className="flex justify-between items-center">
        <div>
          <div className="text-lg">{item.product.name}</div>
          <div className="text-sm">{item.product.price} руб.</div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => onUpdate(item.id, item.quantity - 1)}>-</button>
          <div>{item.quantity}</div>
          <button onClick={() => onUpdate(item.id, item.quantity + 1)}>+</button>
          <button onClick={() => onRemove(item.id)}>Удалить</button>
        </div>
      </div>
      <div className="text-sm mt-4">Итого: {item.total_price} руб.</div>
    </div>
  );
}
