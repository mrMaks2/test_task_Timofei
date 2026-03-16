import React, { useState } from 'react'
import api from '../api/client'
import { useNavigate } from 'react-router-dom'

export default function Checkout() {
  const [fullName, setFullName] = useState('')
  const [address, setAddress] = useState('')
  const navigate = useNavigate()

  const submit = async () => {
    const tg = window.Telegram?.WebApp
    try {
      await api.post('/orders/create/', { full_name: fullName, address })
      tg?.showAlert('Заказ оформлен!')
      navigate('/')
    } catch (error) {
      tg?.showAlert('Ошибка при оформлении')
    }
  }

  return (
    <div>
      <input placeholder="ФИО" value={fullName} onChange={e => setFullName(e.target.value)} />
      <input placeholder="Адрес" value={address} onChange={e => setAddress(e.target.value)} />
      <button onClick={submit}>Подтвердить</button>
    </div>
  )
}