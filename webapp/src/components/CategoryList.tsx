import React, { useEffect, useState } from "react";
import api from "../api/client";

interface Category {
  id: number;
  name: string;
  children: Category[];
}

interface Props {
  onSelect: (categoryId: number | null) => void;
}

export default function CategoryList({ onSelect }: Props) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selected, setSelected] = useState<number | null>(null);

  useEffect(() => {
    api.get("/categories/").then((res) => setCategories(res.data));
  }, []);

  const handleSelect = (id: number | null) => {
    setSelected(id);
    onSelect(id);
  };

  return (
    <div className="card">
      <div className="text-lg mb-4">Категории</div>
      <div className="flex gap-2" style={{ flexWrap: "wrap" }}>
        <button
          className="chip"
          data-active={selected === null}
          onClick={() => handleSelect(null)}
        >
          Все
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            className="chip"
            data-active={selected === cat.id}
            onClick={() => handleSelect(cat.id)}
          >
            {cat.name}
          </button>
        ))}
      </div>
    </div>
  );
}
