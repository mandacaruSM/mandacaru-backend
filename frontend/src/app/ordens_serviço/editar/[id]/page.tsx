// frontend/src/app/ordens-servico/editar/[id]/page.tsx

"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";

interface OrdemServico {
  id: number;
  descricao: string;
  finalizada: boolean;
}

export default function EditarOSPage() {
  const { id } = useParams();
  const router = useRouter();
  const [os, setOs] = useState<OrdemServico | null>(null);
  const [form, setForm] = useState({ descricao: "", finalizada: false });

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/ordens-servico/${id}/`)
      .then(res => res.json())
      .then(data => {
        setOs(data);
        setForm({ descricao: data.descricao, finalizada: data.finalizada });
      })
      .catch(() => alert("Erro ao carregar OS."));
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (e.target instanceof HTMLInputElement) {
      const { name, type, checked, value } = e.target;
      setForm(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value,
      }));
    } else {
      const { name, value } = e.target;
      setForm(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/ordens-servico/${id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error();
      router.push('/ordens-servico');
    } catch {
      alert("Erro ao atualizar OS.");
    }
  };

  if (!os) return <p className="p-6">Carregando…</p>;

  return (
    <div className="p-6 max-w-lg mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Editar OS #{os.id}</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          name="descricao"
          value={form.descricao}
          onChange={handleChange}
          className="w-full h-24 border p-2 rounded"
        />
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            name="finalizada"
            checked={form.finalizada}
            onChange={handleChange}
          />
          Finalizada
        </label>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
          Salvar
        </button>
      </form>
    </div>
  );
}
