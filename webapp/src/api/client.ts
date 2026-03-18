import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use((config) => {
  const initData = localStorage.getItem("tg_init_data");
  if (initData) {
    config.headers["X-Telegram-Init-Data"] = initData;
  }
  const testId = import.meta.env.VITE_TEST_TELEGRAM_ID;
  if (testId) {
    config.headers["X-Telegram-Id"] = testId;
  }
  return config;
});

export default api;
