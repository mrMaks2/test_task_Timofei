import React, { useState, useEffect } from 'react'
import api from '../api/client'
import CategoryList from '../components/CategoryList'
import ProductCard from '../components/ProductCard'

interface Product {
  id: number
  name: string
  price: number
  description: string
  images: { image: string }[]
}

export default function Catalog() {
  const [products, setProducts] = useState<Product[]>([])
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)

  useEffect(() => {
    const url = selectedCategory ? `/products/?category=${selectedCategory}` : '/products/'
    api.get(url).then(res => setProducts(res.data))
  }, [selectedCategory])

  return (
    <div>
      <CategoryList onSelect={setSelectedCategory} />
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        {products.map(p => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  )
}