// app/layout.tsx
import "../styles/globals.css";
import Link from "next/link";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Mandacaru ERP",
  description: "Sistema de manutenção e gestão industrial",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-br">
      <body className={inter.className + " bg-[#fefcf9] min-h-screen"}>
        <header className="bg-green-800 text-white px-6 py-4 shadow-md flex justify-between items-center">
          <h1 className="text-xl font-bold">Mandacaru ERP</h1>
          <Link href="/" className="bg-white text-green-800 px-4 py-1 rounded hover:bg-gray-100">
            🏠 Início
          </Link>
        </header>
        <main className="p-4">{children}</main>
      </body>
    </html>
  );
}
