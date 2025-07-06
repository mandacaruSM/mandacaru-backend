// src/app/page.tsx
"use client";

import Link from "next/link";
import {
  Users,
  Building2,
  Wrench,
  Hammer,
  FileText,
  ActivitySquare,
  Boxes,
  DollarSign,
  Truck,
  BarChart3,
} from "lucide-react";

const modules = [
  { name: "Clientes", icon: <Users className="h-6 w-6" />, href: "/clientes" },
  { name: "Empreendimentos", icon: <Building2 className="h-6 w-6" />, href: "/empreendimentos" },
  { name: "Equipamentos", icon: <Wrench className="h-6 w-6" />, href: "/equipamentos" },
  { name: "Ordens de Serviço", icon: <Hammer className="h-6 w-6" />, href: "/ordens" },
  { name: "Orçamentos", icon: <FileText className="h-6 w-6" />, href: "/orcamentos" },
  { name: "Manutenção", icon: <ActivitySquare className="h-6 w-6" />, href: "/manutencao" },
  { name: "Almoxarifado", icon: <Boxes className="h-6 w-6" />, href: "/almoxarifado" },
  { name: "Financeiro", icon: <DollarSign className="h-6 w-6" />, href: "/financeiro" },
  { name: "Fornecedores", icon: <Truck className="h-6 w-6" />, href: "/fornecedores" },
  { name: "Relatórios", icon: <BarChart3 className="h-6 w-6" />, href: "/relatorios" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-[#fefcf9]">
      {/* Topbar */}
      <header className="bg-orange-500 text-white px-6 py-4 flex justify-between items-center shadow">
        <h1 className="text-xl font-bold">Mandacaru ERP 🌵</h1>
        <button className="bg-green-800 px-3 py-1 text-sm rounded-full hover:bg-green-700">
          Sair
        </button>
      </header>

      {/* Cards */}
      <main className="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto mt-4">
        {modules.map((mod, index) => (
          <Link
            key={index}
            href={mod.href}
            className="bg-white p-5 rounded-2xl shadow-md hover:shadow-xl border border-green-100 flex items-center gap-4"
          >
            <div>{mod.icon}</div>
            <div className="text-lg font-semibold text-green-900">{mod.name}</div>
          </Link>
        ))}
      </main>
    </div>
  );
}
