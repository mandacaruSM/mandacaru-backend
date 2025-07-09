// File: src/app/orcamentos/editar/[id]/page.tsx

"use client";
import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL!;

interface Item {
  tipo: "peca" | "deslocamento" | "mao_de_obra";
  almoxarifado_item?: number;
  descricao: string;
  quantidade: number;
  valor_unitario: number;
  total: number;
}

interface OrcamentoFormData {
  cliente: string;
  empreendimento: string;
  equipamento: string;
  status: string;
  items: Item[];
}

type FormField = keyof Omit<OrcamentoFormData, "items">;

export default function EditarOrcamentoPage() {
  const { id } = useParams();
  const router = useRouter();

  const [form, setForm] = useState<OrcamentoFormData>({ cliente: "", empreendimento: "", equipamento: "", status: "", items: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API}/api/orcamentos/${id}/`);
        if (!res.ok) throw new Error(`Erro: ${res.status}`);
        const data = await res.json();
        setForm({
          cliente: String(data.cliente),
          empreendimento: String(data.empreendimento),
          equipamento: String(data.equipamento),
          status: data.status,
          items: data.items,
        });
      } catch {
        alert("Erro ao carregar orçamento.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleFieldChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const name = e.target.name as FormField;
    const value = e.target.value;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/api/orcamentos/${id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error(`Erro: ${res.status}`);
      router.push("/orcamentos");
    } catch {
      alert("Erro ao atualizar orçamento.");
    }
  };

  if (loading) return <p className="p-6">Carregando…</p>;

  return (
    <form onSubmit={handleSubmit} className="p-6 max-w-lg mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Editar Orçamento</h1>

      <div className="space-y-2">
        <select name="cliente" value={form.cliente} onChange={handleFieldChange} required>
          <option value="">Selecione Cliente</option>
        </select>
        <select name="empreendimento" value={form.empreendimento} onChange={handleFieldChange} required>
          <option value="">Selecione Empreendimento</option>
        </select>
        <select name="equipamento" value={form.equipamento} onChange={handleFieldChange} required>
          <option value="">Selecione Equipamento</option>
        </select>
      </div>

      {/* Itens não editáveis nesta versão; se necessário, renderize tabela aqui */}

      <select name="status" value={form.status} onChange={handleFieldChange} required>
        <option value="pendente">Pendente</option>
        <option value="aprovado">Aprovado</option>
        <option value="rejeitado">Rejeitado</option>
      </select>

      <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Salvar Alterações</button>
    </form>
  );
}