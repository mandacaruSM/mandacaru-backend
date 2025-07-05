// frontend/app/clientes/page.tsx
"use client";

import { useEffect, useState } from "react";

interface Cliente {
  id: number;
  razao_social: string;
  cnpj: string;
  email: string;
  telefone: string;
  rua: string;
  numero: string;
  bairro: string;
  cidade: string;
  estado: string;
  cep: string;
}

export default function ClientesPage() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [form, setForm] = useState<Partial<Cliente>>({});

  const fetchClientes = async () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    const res = await fetch(`${apiUrl}/api/clientes/`);
    const data = await res.json();
    setClientes(data);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    await fetch(`${apiUrl}/api/clientes/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setForm({});
    fetchClientes();
  };

  useEffect(() => {
    fetchClientes();
  }, []);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Clientes</h1>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <input
          className="border p-2 rounded"
          placeholder="Razão Social"
          value={form.razao_social || ""}
          onChange={(e) => setForm({ ...form, razao_social: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="CNPJ"
          value={form.cnpj || ""}
          onChange={(e) => setForm({ ...form, cnpj: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="E-mail"
          value={form.email || ""}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="Telefone"
          value={form.telefone || ""}
          onChange={(e) => setForm({ ...form, telefone: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="Rua"
          value={form.rua || ""}
          onChange={(e) => setForm({ ...form, rua: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="Número"
          value={form.numero || ""}
          onChange={(e) => setForm({ ...form, numero: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="Bairro"
          value={form.bairro || ""}
          onChange={(e) => setForm({ ...form, bairro: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="Cidade"
          value={form.cidade || ""}
          onChange={(e) => setForm({ ...form, cidade: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="Estado"
          value={form.estado || ""}
          onChange={(e) => setForm({ ...form, estado: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="CEP"
          value={form.cep || ""}
          onChange={(e) => setForm({ ...form, cep: e.target.value })}
        />
        <button
          type="submit"
          className="col-span-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700"
        >
          Cadastrar Cliente
        </button>
      </form>

      <ul className="space-y-2">
        {clientes.map((cliente) => (
          <li key={cliente.id} className="p-4 border rounded shadow">
            <p className="font-bold">{cliente.razao_social}</p>
            <p>{cliente.cnpj} - {cliente.email} - {cliente.telefone}</p>
            <p>{cliente.rua}, {cliente.numero} - {cliente.bairro}, {cliente.cidade} - {cliente.estado} ({cliente.cep})</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
