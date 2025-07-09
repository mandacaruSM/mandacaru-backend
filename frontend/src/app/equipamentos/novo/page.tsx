/* File: app/equipamentos/novo/page.tsx */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL!;

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Empreendimento {
  id: number;
  nome: string;
}

interface EquipamentoFormData {
  nome: string;
  tipo: string;
  marca: string;
  modelo: string;
  numero_serie: string;
  horimetro: string;
  cliente: string;
  empreendimento: string;
}

export default function NovoEquipamentoPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [formData, setFormData] = useState<EquipamentoFormData>({
    nome: "",
    tipo: "",
    marca: "",
    modelo: "",
    numero_serie: "",
    horimetro: "",
    cliente: "",
    empreendimento: "",
  });
  const [loadingEmp, setLoadingEmp] = useState(false);

  // Carrega clientes
  useEffect(() => {
    fetch(`${API}/api/clientes/`)
      .then(res => {
        if (!res.ok) throw new Error(`Erro ao buscar clientes: ${res.status}`);
        return res.json();
      })
      .then(setClientes)
      .catch(console.error);
  }, []);

  // Carrega empreendimentos ao escolher cliente
  useEffect(() => {
    if (!formData.cliente) {
      setEmpreendimentos([]);
      setFormData(prev => ({ ...prev, empreendimento: "" }));
      return;
    }
    setLoadingEmp(true);
    fetch(`${API}/api/empreendimentos/?cliente=${formData.cliente}`)
      .then(res => {
        if (!res.ok) throw new Error(`Erro ao buscar empreendimentos: ${res.status}`);
        return res.json();
      })
      .then(data => {
        setEmpreendimentos(data);
        setFormData(prev => ({ ...prev, empreendimento: "" }));
      })
      .catch(console.error)
      .finally(() => setLoadingEmp(false));
  }, [formData.cliente]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        horimetro: parseFloat(formData.horimetro),
        cliente: Number(formData.cliente),
        empreendimento: Number(formData.empreendimento),
      };
      const res = await fetch(`${API}/api/equipamentos/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Erro ${res.status}: ${text}`);
      }
      alert("Equipamento cadastrado com sucesso!");
      router.push("/equipamentos");
    } catch (err) {
      console.error(err);
      alert("Falha ao cadastrar equipamento.");
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-4">Novo Equipamento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Tipo */}
        <div>
          <label className="block mb-1">Tipo</label>
          <select
            name="tipo"
            value={formData.tipo}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          >
            <option value="">Selecione um tipo</option>
            <option value="carregadeira">Carregadeira</option>
            <option value="escavadeira">Escavadeira</option>
            <option value="trator">Trator</option>
            <option value="gerador">Gerador</option>
            <option value="compressor">Compressor</option>
            <option value="caminhao">Caminhão</option>
            <option value="veiculo_leve">Veículo Leve</option>
          </select>
        </div>

        {/* Cliente */}
        <div>
          <label className="block mb-1">Cliente</label>
          <select
            name="cliente"
            value={formData.cliente}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          >
            <option value="">Selecione um cliente</option>
            {clientes.map(c => (
              <option key={c.id} value={c.id}>
                {c.nome_fantasia}
              </option>
            ))}
          </select>
        </div>

        {/* Empreendimento */}
        <div>
          <label className="block mb-1">Empreendimento</label>
          <select
            name="empreendimento"
            value={formData.empreendimento}
            onChange={handleChange}
            required
            disabled={!formData.cliente || loadingEmp}
            className="w-full border px-3 py-2 rounded disabled:opacity-50"
          >
            <option value="">
              {formData.cliente
                ? loadingEmp
                  ? "Carregando..."
                  : "Selecione um empreendimento"
                : "Escolha primeiro o cliente"}
            </option>
            {empreendimentos.map(e => (
              <option key={e.id} value={e.id}>
                {e.nome}
              </option>
            ))}
          </select>
        </div>

        {/* Demais campos do equipamento */}
        <div>
          <label className="block mb-1">Nome</label>
          <input
            name="nome"
            value={formData.nome}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Marca</label>
          <input
            name="marca"
            value={formData.marca}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Modelo</label>
          <input
            name="modelo"
            value={formData.modelo}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Número de Série</label>
          <input
            name="numero_serie"
            value={formData.numero_serie}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Horímetro</label>
          <input
            type="number"
            step="0.1"
            name="horimetro"
            value={formData.horimetro}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Cadastrar Equipamento
        </button>
      </form>
    </div>
  );
}
