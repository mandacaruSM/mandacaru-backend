// File: src/app/orcamentos/novo/page.tsx

"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL!;

interface Item {
  tipo: "peca" | "deslocamento" | "mao_de_obra";
  almoxarifado_item?: number;
  descricao: string;
  quantidade: number;
  valor_unitario: number;
}

interface OrcamentoFormData {
  cliente: string;
  empreendimento: string;
  equipamento: string;
  status: string;
  items: Item[];
}

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Empreendimento {
  id: number;
  nome: string;
}

interface Equipamento {
  id: number;
  nome: string;
}

export default function NovoOrcamentoPage() {
  const router = useRouter();
  const [form, setForm] = useState<OrcamentoFormData>({
    cliente: "",
    empreendimento: "",
    equipamento: "",
    status: "pendente",
    items: [],
  });

  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);

  useEffect(() => {
    fetch(`${API}/api/clientes/`).then(res => res.json()).then(setClientes);
    fetch(`${API}/api/empreendimentos/`).then(res => res.json()).then(setEmpreendimentos);
    fetch(`${API}/api/equipamentos/`).then(res => res.json()).then(setEquipamentos);
  }, []);

  const handleFieldChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/api/orcamentos/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(`Erro: ${res.status} - ${JSON.stringify(errorData)}`);
      }
      alert("Orçamento criado com sucesso!");
      router.push("/orcamentos");
    } catch (error) {
      console.error(error);
      alert(`Erro ao criar orçamento.`);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Novo Orçamento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="cliente" className="block text-sm font-medium text-gray-700">Cliente</label>
            <select id="cliente" name="cliente" value={form.cliente} onChange={handleFieldChange} required className="mt-1 block w-full p-2 border border-gray-300 rounded-md">
              <option value="">Selecione um Cliente</option>
              {clientes.map(c => <option key={c.id} value={c.id}>{c.nome_fantasia}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="empreendimento" className="block text-sm font-medium text-gray-700">Empreendimento</label>
            <select id="empreendimento" name="empreendimento" value={form.empreendimento} onChange={handleFieldChange} required className="mt-1 block w-full p-2 border border-gray-300 rounded-md">
              <option value="">Selecione um Empreendimento</option>
              {empreendimentos.map(e => <option key={e.id} value={e.id}>{e.nome}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="equipamento" className="block text-sm font-medium text-gray-700">Equipamento</label>
            <select id="equipamento" name="equipamento" value={form.equipamento} onChange={handleFieldChange} required className="mt-1 block w-full p-2 border border-gray-300 rounded-md">
              <option value="">Selecione um Equipamento</option>
              {equipamentos.map(eq => <option key={eq.id} value={eq.id}>{eq.nome}</option>)}
            </select>
          </div>
        </div>

        {/* Seção de Itens (simplificada) */}
        <div>
          <h2 className="text-xl font-semibold mb-2">Itens do Orçamento</h2>
          <p className="text-gray-500">A adição de itens será implementada em uma versão futura.</p>
        </div>

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleFieldChange} required className="mt-1 block w-full p-2 border border-gray-300 rounded-md">
            <option value="pendente">Pendente</option>
            <option value="aprovado">Aprovado</option>
            <option value="rejeitado">Rejeitado</option>
          </select>
        </div>

        <div className="flex justify-end gap-4">
          <Link href="/orcamentos" className="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600">
            Cancelar
          </Link>
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            Salvar Orçamento
          </button>
        </div>
      </form>
    </div>
  );
}
