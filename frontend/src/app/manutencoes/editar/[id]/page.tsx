// /src/app/manutencoes/editar/[id]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
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

const ManutencaoEditPage = () => {
  const params = useParams();
  const id = Array.isArray(params.id) ? params.id[0] : params.id;
  const router = useRouter();

  const [formData, setFormData] = useState<Manutencao>({
    equipamento: 0,
    tipo: "corretiva",
    data: "",
    horimetro: "",
    tecnico_responsavel: "",
    descricao: "",
    proxima_manutencao: "",
  });

  useEffect(() => {
    axios
      .get<Manutencao>(`https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`)
      .then((res) => setFormData(res.data))
      .catch((err) => console.error("Erro ao carregar dados da manutenção:", err));
  }, [id]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await axios.put(`https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`, formData);
      router.push("/manutencoes");
    } catch (error) {
      console.error("Erro ao atualizar manutenção:", error);
      alert("Erro ao salvar. Verifique os dados.");
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Editar Manutenção</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input name="equipamento" value={formData.equipamento} onChange={handleChange} className="w-full p-2 border rounded" />
        <select name="tipo" value={formData.tipo} onChange={handleChange} className="w-full p-2 border rounded">
          <option value="corretiva">Corretiva</option>
          <option value="preventiva">Preventiva</option>
        </select>
        <input type="date" name="data" value={formData.data} onChange={handleChange} className="w-full p-2 border rounded" />
        <input name="horimetro" value={formData.horimetro} onChange={handleChange} className="w-full p-2 border rounded" />
        <input name="tecnico_responsavel" value={formData.tecnico_responsavel} onChange={handleChange} className="w-full p-2 border rounded" />
        <textarea name="descricao" value={formData.descricao} onChange={handleChange} className="w-full p-2 border rounded" />
        {formData.tipo === "preventiva" && (
          <input type="date" name="proxima_manutencao" value={formData.proxima_manutencao} onChange={handleChange} className="w-full p-2 border rounded" />
        )}

        <div className="flex gap-4">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Salvar</button>
          <button type="button" onClick={() => router.push("/manutencoes")} className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500">Cancelar</button>
        </div>
      </form>
    </div>
  );
};

export default ManutencaoEditPage;
