import { Link } from "react-router-dom";

function Header() {
  return (
    <header className="border-b border-ink/10 bg-card">
      <div className="mx-auto flex max-w-5xl items-baseline gap-3 px-4 py-4 sm:px-6 lg:px-8">
        <Link
          to="/"
          className="font-display text-xl font-bold tracking-tight text-ink no-underline"
        >
          Lost &amp; Found Desk
        </Link>
        <span className="font-stamp text-xs uppercase tracking-widest text-ink/40">
          Campus recovery office
        </span>
      </div>
    </header>
  );
}

export default Header;
