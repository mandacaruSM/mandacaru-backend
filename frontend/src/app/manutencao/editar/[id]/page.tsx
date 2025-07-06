"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

interface Manutencao {
  id?: number;
  equipamento: number;
  tipo: string;
  data: string;
  horimetro: string;
  tecnico_responsavel: string;
  descricao: string;
  observacoes?: string;
  proxima_manutencao?: string | null;
}

export default function EditarManutencaoPage() {
  const { id } = useParams();
  const router = useRouter();
  const [formData, setFormData] = useState<Manutencao | null>(null);

  useEffect(() => {
    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`)
      .then((res) => res.json())
      .then((data) => setFormData(data))
      .catch(() => alert("Erro ao carregar manutenção."));
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    if (!formData) return;
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData) return;

    try {
      const res = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        alert("Manutenção atualizada com sucesso!");
        router.push("/manutencoes");
      } else {
        const erro = await res.json();
        alert("Erro: " + JSON.stringify(erro));
      }
    } catch {
      alert("Erro ao salvar manutenção.");
    }
  };

  if (!formData) return <div className="p-4">Carregando...</div>;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-green-700 mb-4">Editar Manutenção</h1>
      <form onSubmit={handleSubmit} className="space-y-4">

        <div>
          <label className="block mb-1">Tipo de Manutenção</label>
          <select
            name="tipo"
            value={formData.tipo}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded"
          >
            <option value="preventiva">Preventiva</option>
            <option value="corretiva">Corretiva</option>
          </select>
        </div>

        <div>
          <label className="block mb-1">Data</label>
          <input
            type="date"
            name="data"
            value={formData.data}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded"
          />
        </div>

        <div>
          <label className="block mb-1">Horímetro</label>
          <input
            type="number"
            step="0.01"
            name="horimetro"
            value={formData.horimetro}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded"
          />
        </div>

        {formData.tipo === "preventiva" && (
          <div>
            <label className="block mb-1">Próxima Manutenção Preventiva</label>
            <input
              type="date"
              name="proxima_manutencao"
              value={formData.proxima_manutencao || ""}
              onChange={handleChange}
              className="w-full border px-3 py-2 rounded"
            />
          </div>
        )}

        <div>
          <label className="block mb-1">Técnico Responsável</label>
          <input
            type="text"
            name="tecnico_responsavel"
            value={formData.tecnico_responsavel}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded"
          />
        </div>

        <div>
          <label className="block mb-1">Descrição</label>
          <textarea
            name="descricao"
            value={formData.descricao}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded"
          />
        </div>

        <div>
          <label className="block mb-1">Observações</label>
          <textarea
            name="observacoes"
            value={formData.observacoes || ""}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded"
          />
        </div>

        <div className="flex gap-2 justify-between">
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Salvar Alterações
          </button>
          <button
            type="button"
            onClick={() => router.push("/manutencoes")}
            className="bg-gray-300 text-gray-800 px-4 py-2 rounded hover:bg-gray-400"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
