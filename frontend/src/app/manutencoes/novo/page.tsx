"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Equipamento {
  id: number;
  nome: string;
}

export default function NovaManutencaoPage() {
  const router = useRouter();
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [formData, setFormData] = useState<{
  equipamento: string;
  tipo: string;
  data: string;
  horimetro: string;
  tecnico_responsavel: string;
  descricao: string;
  proxima_manutencao?: string; // ⮆️ agora é opcional
}>({
  equipamento: "",
  tipo: "corretiva",
  data: "",
  horimetro: "",
  tecnico_responsavel: "",
  descricao: "",
});

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/")
      .then((res) => res.json())
      .then(setEquipamentos);
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = { ...formData };

    // Remove próxima_manutencao se for corretiva
    if (payload.tipo === "corretiva") {
      delete payload.proxima_manutencao;
    }

    const response = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      router.push("/manutencoes");
    } else {
      alert("Erro ao cadastrar manutenção");
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Nova Manutenção</h1>
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
          required
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
          required
        />

        <textarea
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          placeholder="Descrição da manutenção"
          className="w-full border p-2 rounded"
        />

        {formData.tipo === "preventiva" && (
          <input
            type="date"
            name="proxima_manutencao"
            value={formData.proxima_manutencao}
            onChange={handleChange}
            className="w-full border p-2 rounded"
            placeholder="Próxima manutenção preventiva"
          />
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Cadastrar
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
