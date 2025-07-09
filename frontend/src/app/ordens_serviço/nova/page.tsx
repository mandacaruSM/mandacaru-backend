// frontend/src/app/ordens-servico/novo/page.tsx

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface Cliente { id: number; nome_fantasia: string }
interface Equipamento { id: number; nome: string }

export default function NovaOSPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [form, setForm] = useState({ cliente: "", equipamento: "", descricao: "" });

  useEffect(() => {
    Promise.all([
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/clientes/`).then(res => res.json()),
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/equipamentos/`).then(res => res.json()),
    ])
      .then(([cli, eq]) => {
        setClientes(cli);
        setEquipamentos(eq);
      })
      .catch(() => alert("Erro ao carregar dados."));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/ordens-servico/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cliente: Number(form.cliente),
          equipamento: Number(form.equipamento),
          descricao: form.descricao,
        }),
      });
      if (!res.ok) throw new Error();
      router.push('/ordens-servico');
    } catch {
      alert("Erro ao criar OS.");
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Nova Ordem de Serviço</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <select name="cliente" value={form.cliente} onChange={handleChange} required>
          <option value="">Selecione Cliente</option>
          {clientes.map(c => (
            <option key={c.id} value={String(c.id)}>{c.nome_fantasia}</option>
          ))}
        </select>
        <select name="equipamento" value={form.equipamento} onChange={handleChange} required>
          <option value="">Selecione Equipamento</option>
          {equipamentos.map(eq => (
            <option key={eq.id} value={String(eq.id)}>{eq.nome}</option>
          ))}
        </select>
        <textarea
          name="descricao"
          value={form.descricao}
          onChange={e => setForm(prev => ({ ...prev, descricao: e.target.value }))}
          placeholder="Descrição"
          className="w-full h-24 border p-2 rounded"
        />
        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded">
          Criar OS
        </button>
      </form>
    </div>
  );
}