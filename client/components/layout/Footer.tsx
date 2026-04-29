import Link from 'next/link';

const allLinks = [
  { label: 'Policies', href: '#' },
  { label: 'Contact', href: '#' },
  { label: 'Disclaimer', href: '#' },
];

export default function Footer() {
  return (
    <footer className="bg-[#11486b] text-white">
      <div className="mx-auto w-full max-w-7xl px-4 py-8">
        <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
          <div className="flex flex-col items-center gap-2 text-center md:items-start md:text-left">
            <span className="text-xs uppercase tracking-[0.25em] text-white/70">
              Government of India
            </span>
            <p className="text-sm font-semibold">National Internship Portal</p>
          </div>

          <nav className="flex flex-wrap justify-center gap-x-6 gap-y-2">
            {allLinks.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="text-xs font-medium text-white/80 transition hover:text-white"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="text-center text-xs text-white/70 md:text-right">
            © {new Date().getFullYear()} National Internship Portal
          </div>
        </div>
      </div>
    </footer>
  );
}
