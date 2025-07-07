"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

interface Equipamento {
  id: number;
  nome: string;
}

export default function EditarManutencaoPage() {
  const { id } = useParams();
  const router = useRouter();
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [formData, setFormData] = useState<{
    equipamento: string;
    tipo: string;
    data: string;
    horimetro: string;
    tecnico_responsavel: string;
    descricao: string;
    proxima_manutencao?: string;
  } | null>(null);

  useEffect(() => {
    if (typeof id !== "string") return;

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/")
      .then((res) => res.json())
      .then(setEquipamentos);

    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`)
      .then((res) => res.json())
      .then((data) => {
        setFormData({
          equipamento: String(data.equipamento),
          tipo: data.tipo,
          data: data.data,
          horimetro: String(data.horimetro),
          tecnico_responsavel: data.tecnico_responsavel,
          descricao: data.descricao || "",
          proxima_manutencao: data.proxima_manutencao || "",
        });
      });
  }, [id]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    if (!formData) return;
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData || typeof id !== "string") return;

    const payload = { ...formData };
    if (payload.tipo === "corretiva") {
      delete payload.proxima_manutencao;
    }

    const res = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      router.push("/manutencoes");
    } else {
      alert("Erro ao salvar manutenção");
    }
  };

  if (!formData) return <div className="p-6">Carregando...</div>;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Editar Manutenção</h1>
        <Link href="/" className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400">
          🏠 Início
        </Link>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <select
          name="equipamento"
          value={formData.equipamento}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        >
          <option value="">Selecione o equipamento</option>
          {equipamentos.map((e) => (
            <option key={e.id} value={e.id}>
              {e.nome}
            </option>
          ))}
        </select>

        <select
          name="tipo"
          value={formData.tipo}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        >
          <option value="corretiva">Corretiva</option>
          <option value="preventiva">Preventiva</option>
        </select>

        <input
          type="date"
          name="data"
          value={formData.data}
          onChange={handleChange}
          className="w-full border p-2 rounded"
          required
        />

        <input
          type="number"
          step="0.1"
          name="horimetro"
          value={formData.horimetro}
          onChange={handleChange}
          placeholder="Horímetro"
          className="w-full border p-2 rounded"
          required
        />

        <input
          type="text"
          name="tecnico_responsavel"
          value={formData.tecnico_responsavel}
          onChange={handleChange}
          placeholder="Técnico Responsável"
          className="w-full border p-2 rounded"
        />

        <textarea
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          placeholder="Descrição"
          className="w-full border p-2 rounded"
        />

        {formData.tipo === "preventiva" && (
          <input
            type="date"
            name="proxima_manutencao"
            value={formData.proxima_manutencao}
            onChange={handleChange}
            className="w-full border p-2 rounded"
            placeholder="Próxima Manutenção Preventiva"
          />
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Salvar Alterações
          </button>
          <button
            type="button"
            onClick={() => router.push("/manutencoes")}
            className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
