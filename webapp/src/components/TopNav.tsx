import { NavLink, useLocation } from "react-router-dom";

export default function TopNav() {
  const location = useLocation();
  const isCheckout = location.pathname === "/checkout";

  return (
    <header className="top-nav">
      <div className="top-nav__inner">
        <div className="top-nav__brand">
          <div className="top-nav__title">Telegram Shop</div>
          <div className="top-nav__subtitle">
            {isCheckout ? "Оформление заказа" : "Каталог"}
          </div>
        </div>
        <nav className="top-nav__links">
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? "top-nav__link is-active" : "top-nav__link"
            }
          >
            Каталог
          </NavLink>
          <NavLink
            to="/cart"
            className={({ isActive }) =>
              isActive ? "top-nav__link is-active" : "top-nav__link"
            }
          >
            Корзина
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
