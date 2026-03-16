export function initTelegram() {
  const tg = window.Telegram?.WebApp
  if (tg) {
    tg.expand()
    tg.ready()
    tg.setHeaderColor('bg_color')
    tg.setBackgroundColor('secondary_bg_color')
    // Сохраняем initData для отправки на бэкенд
    localStorage.setItem('tg_init_data', tg.initData)
  }
}