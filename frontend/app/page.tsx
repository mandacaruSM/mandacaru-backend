// app/page.tsx
import ClientesPage from "@/app/clientes/page";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <ClientesPage />
    </main>
  );
}
