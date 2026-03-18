export function initTelegram() {
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.expand();
    tg.ready();
    tg.setHeaderColor("bg_color");
    tg.setBackgroundColor("secondary_bg_color");
    localStorage.setItem("tg_init_data", tg.initData);
  }
}
