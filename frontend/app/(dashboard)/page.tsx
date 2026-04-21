import { PageHeader } from "@/components/layout/PageHeader";

export default function DashboardPage() {
  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Resumen ejecutivo de tu actividad fiscal" />
      {/* KPI summary cards — implemented in Épica 9 */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {["Total CFDIs", "Ventas del mes", "Compras del mes", "Utilidad estimada"].map((label) => (
          <div key={label} className="bg-white rounded-lg p-5 shadow-sm border border-gray-200">
            <p className="text-sm text-gray-500">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">—</p>
          </div>
        ))}
      </div>
    </div>
  );
}
