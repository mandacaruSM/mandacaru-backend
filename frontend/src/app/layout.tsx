import "../styles/globals.css";
import { Inter } from "next/font/google";
import Image from "next/image";
import logo from "../public/logo_mandacaru.png";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Mandacaru ERP",
  description: "Sistema de manutenção e gestão industrial",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-br">
      <body className={inter.className + " flex h-screen"}>
        <Sidebar />
        <div className="flex flex-col flex-1 bg-[#fefcf9]">
          <Topbar />
          <main className="p-6 overflow-y-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}

// Sidebar Component
function Sidebar() {
  const menu = [
    { name: "Clientes", icon: "👤", href: "/clientes" },
    { name: "Equipamentos", icon: "🛠️", href: "/equipamentos" },
    { name: "OS", icon: "📋", href: "/ordens" },
    { name: "Orçamentos", icon: "💰", href: "/orcamentos" },
    { name: "Financeiro", icon: "💵", href: "/financeiro" },
    { name: "Almoxarifado", icon: "📦", href: "/almoxarifado" },
  ];

  return (
    <aside className="w-60 bg-green-900 text-white flex flex-col items-center py-4">
      <div className="w-32 mb-4">
        <Image src={logo} alt="Mandacaru Logo" width={128} height={128} />
      </div>
      <h1 className="text-lg font-bold mb-6">Mandacaru ERP</h1>
      <nav className="flex flex-col gap-4 w-full px-4">
        {menu.map((item) => (
          <a key={item.name} href={item.href} className="flex items-center gap-2 hover:text-green-200">
            <span>{item.icon}</span>
            <span>{item.name}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
}

// Topbar Component
function Topbar() {
  return (
    <header className="bg-orange-500 text-white px-6 py-3 flex justify-between items-center">
      <div></div>
      <div className="flex items-center gap-4">
        <span className="text-sm">Usuário</span>
        <button className="bg-green-800 text-white px-3 py-1 rounded-full hover:bg-green-700">🌵 Sair</button>
      </div>
    </header>
  );
}
