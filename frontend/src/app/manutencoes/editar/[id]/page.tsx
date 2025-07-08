"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

interface Manutencao {
  equipamento: number;
  tipo: string;
  data: string;
  horimetro: string;
  tecnico_responsavel: string;
  descricao: string;
  proxima_manutencao: string;
}

interface PageProps {
  params: {
    id: string;
  };
}

export default function Page({ params }: PageProps) {
  const router = useRouter();
  const { id } = params;

  const [formData, setFormData] = useState<Manutencao>({
    equipamento: 0,
    tipo: "corretiva",
    data: "",
    horimetro: "",
    tecnico_responsavel: "",
    descricao: "",
    proxima_manutencao: "",
  });

  const [equipamentos, setEquipamentos] = useState<{ id: number; nome: string }[]>([]);

  useEffect(() => {
  fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/")
    .then((res) => res.json())
    .then((data: unknown) => {
      if (Array.isArray(data)) {
        setEquipamentos(data as { id: number; nome: string }[]);
      } else {
        console.error("Dados inesperados:", data);
      }
    })
    .catch((error) => {
      console.error("Erro ao buscar equipamentos:", error);
    });
}, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await axios.put(`https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`, formData);
      alert("Manutenção atualizada com sucesso");
      router.push("/manutencoes");
    } catch (error) {
      console.error("Erro ao salvar manutenção:", error);
      alert("Erro ao salvar manutenção");
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Editar Manutenção</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block">
          Equipamento:
          <select
            name="equipamento"
            value={formData.equipamento}
            onChange={handleChange}
            className="border p-2 w-full"
          >
            <option value="">Selecione</option>
            {equipamentos.map((eq) => (
              <option key={eq.id} value={eq.id}>{eq.nome}</option>
            ))}
          </select>
        </label>

        <label className="block">
          Tipo:
          <select
            name="tipo"
            value={formData.tipo}
            onChange={handleChange}
            className="border p-2 w-full"
          >
            <option value="corretiva">Corretiva</option>
            <option value="preventiva">Preventiva</option>
          </select>
        </label>

        <input type="date" name="data" value={formData.data} onChange={handleChange} className="w-full p-2 border" required />
        <input type="text" name="horimetro" value={formData.horimetro} onChange={handleChange} className="w-full p-2 border" placeholder="Horímetro" />
        <input type="text" name="tecnico_responsavel" value={formData.tecnico_responsavel} onChange={handleChange} className="w-full p-2 border" placeholder="Técnico Responsável" />
        <textarea name="descricao" value={formData.descricao} onChange={handleChange} className="w-full p-2 border" placeholder="Descrição" />
        {formData.tipo === "preventiva" && (
          <input type="date" name="proxima_manutencao" value={formData.proxima_manutencao} onChange={handleChange} className="w-full p-2 border" placeholder="Próxima manutenção" />
        )}

        <div className="flex gap-4">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Salvar</button>
          <button type="button" onClick={() => router.push("/manutencoes")} className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500">Cancelar</button>
        </div>
      </form>
    </div>
  );
}
