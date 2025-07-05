// frontend/src/app/page.tsx
"use client"

import Link from "next/link";
import { Hammer, Users, Wrench, Building2, FileText } from "lucide-react";

const modules = [
  { name: "Clientes", icon: <Users className="h-6 w-6" />, href: "/clientes" },
  { name: "Empreendimentos", icon: <Building2 className="h-6 w-6" />, href: "/empreendimentos" },
  { name: "Equipamentos", icon: <Wrench className="h-6 w-6" />, href: "/equipamentos" },
  { name: "Ordens de Serviço", icon: <Hammer className="h-6 w-6" />, href: "/ordens" },
  { name: "Relatórios", icon: <FileText className="h-6 w-6" />, href: "/relatorios" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-[#fefcf9] p-6">
      <h1 className="text-3xl font-bold text-center text-green-800 mb-8">
        ERP Mandacaru 🌵
      </h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl mx-auto">
        {modules.map((mod, idx) => (
          <Link key={idx} href={mod.href} className="bg-white p-4 rounded-2xl shadow-md hover:shadow-xl transition">
            <div className="flex items-center gap-4">
              <div className="bg-green-100 p-3 rounded-full">{mod.icon}</div>
              <span className="text-lg font-semibold text-green-900">{mod.name}</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
