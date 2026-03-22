import { useEffect, useState } from "react";
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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    api
      .get("categories/")
      .then((res) => {
        if (!active) return;
        setCategories(Array.isArray(res.data) ? res.data : []);
      })
      .catch(() => {
        if (!active) return;
        setError("Не удалось загрузить категории.");
        setCategories([]);
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });
    return () => {
      active = false;
    };
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
          type="button"
          className="chip"
          data-active={selected === null}
          onClick={() => handleSelect(null)}
        >
          Все
        </button>
        {categories.map((cat) => (
          <button
            type="button"
            key={cat.id}
            className="chip"
            data-active={selected === cat.id}
            onClick={() => handleSelect(cat.id)}
          >
            {cat.name}
          </button>
        ))}
      </div>
      {loading && <div className="text-sm mt-4">Загрузка...</div>}
      {error && <div className="text-sm mt-4">{error}</div>}
    </div>
  );
}
