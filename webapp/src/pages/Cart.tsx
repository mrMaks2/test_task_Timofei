import React, { useState, useEffect } from 'react'
import api from '../api/client'
import CartItem from '../components/CartItem'
import { useNavigate } from 'react-router-dom'

export default function Cart() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/cart/').then(res => {
      setItems(res.data.items)
      setTotal(res.data.total)
    })
  }, [])

  const updateQuantity = (itemId: number, delta: number) => {
    api.post(`/cart/item/${itemId}/update/`, { delta }).then(() => {
      // reload cart
    })
  }

  const checkout = () => {
    navigate('/checkout')
  }

  return (
    <div>
      {items.map((item: any) => (
        <CartItem key={item.id} item={item} onUpdate={updateQuantity} />
      ))}
      <div>Итого: {total} руб.</div>
      <button onClick={checkout}>Оформить заказ</button>
    </div>
  )
}