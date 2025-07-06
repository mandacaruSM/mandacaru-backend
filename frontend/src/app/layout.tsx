// app/layout.tsx
import "../styles/globals.css";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Mandacaru ERP",
  description: "Sistema de manutenção e gestão industrial",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-br">
      <body className={inter.className + " bg-[#fefcf9]"}>
        {children}
      </body>
    </html>
  );
}
