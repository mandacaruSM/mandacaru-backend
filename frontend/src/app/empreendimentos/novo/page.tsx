/* File: app/empreendimentos/novo/page.tsx */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL!; // ex: "https://mandacaru-backend-i2ci.onrender.com"

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface EmpreendimentoFormData {
  nome: string;
  cliente: string;
  endereco: string;
  cidade: string;
  estado: string;
  cep: string;
  localizacao: string;
  descricao: string;
  distancia_km: string;
}

export default function NovoEmpreendimentoPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [formData, setFormData] = useState<EmpreendimentoFormData>({
    nome: "",
    cliente: "",
    endereco: "",
    cidade: "",
    estado: "",
    cep: "",
    localizacao: "",
    descricao: "",
    distancia_km: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/api/clientes`)
      .then(res => {
        if (!res.ok) throw new Error(`Status ${res.status}`);
        return res.json();
      })
      .then(setClientes)
      .catch(console.error);
  }, []);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData(old => ({ ...old, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...formData,
        cliente: Number(formData.cliente),
        distancia_km: parseFloat(formData.distancia_km),
      };
      const res = await fetch(`${API}/api/empreendimentos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Erro ${res.status}: ${text}`);
      }
      alert("Empreendimento cadastrado com sucesso!");
      router.push("/empreendimentos");
    } catch (err) {
      console.error(err);
      setError("Falha ao cadastrar empreendimento.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-4">Novo Empreendimento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Nome */}
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
        {/* Endereço */}
        <div>
          <label className="block mb-1">Endereço</label>
          <input
            name="endereco"
            value={formData.endereco}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        {/* Cidade / Estado / CEP */}
        <div className="grid grid-cols-3 gap-2">
          <input
            name="cidade"
            value={formData.cidade}
            onChange={handleChange}
            required
            placeholder="Cidade"
            className="border px-3 py-2 rounded"
          />
          <input
            name="estado"
            value={formData.estado}
            onChange={handleChange}
            required
            placeholder="Estado"
            className="border px-3 py-2 rounded"
          />
          <input
            name="cep"
            value={formData.cep}
            onChange={handleChange}
            required
            placeholder="CEP"
            className="border px-3 py-2 rounded"
          />
        </div>
        {/* Localização */}
        <div>
          <label className="block mb-1">Localização</label>
          <input
            name="localizacao"
            value={formData.localizacao}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        {/* Descrição */}
        <div>
          <label className="block mb-1">Descrição</label>
          <textarea
            name="descricao"
            value={formData.descricao}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        {/* Distância */}
        <div>
          <label className="block mb-1">Distância (km)</label>
          <input
            type="number"
            step="0.01"
            name="distancia_km"
            value={formData.distancia_km}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        {error && <p className="text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? "Cadastrando..." : "Cadastrar Empreendimento"}
        </button>
      </form>
    </div>
  );
}
