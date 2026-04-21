"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/cfdi", label: "CFDIs" },
  { href: "/dashboard/gmail", label: "Gmail Sync" },
  { href: "/dashboard/templates", label: "Plantillas" },
  { href: "/dashboard/batch", label: "Procesamiento Batch" },
  { href: "/dashboard/analytics", label: "Analítica" },
  { href: "/dashboard/exports", label: "Exportaciones" },
  { href: "/dashboard/settings", label: "Configuración" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <span className="text-lg font-bold text-brand-700">CFDI Intelligence</span>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={clsx(
              "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors",
              pathname === item.href || pathname.startsWith(item.href + "/")
                ? "bg-brand-50 text-brand-700"
                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            )}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
