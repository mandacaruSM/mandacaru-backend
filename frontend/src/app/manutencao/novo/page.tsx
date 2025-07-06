"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Equipamento {
  id: number;
  nome: string;
}

export default function NovaManutencao() {
  const router = useRouter();
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [formData, setFormData] = useState({
    equipamento: "",
    tipo: "preventiva",
    data: "",
    horimetro: "",
    tecnico_responsavel: "",
    descricao: "",
    observacoes: "",
    proxima_manutencao: "",
  });

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/")
      .then((res) => res.json())
      .then((data) => setEquipamentos(data));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const dataToSend = {
      ...formData,
      horimetro: parseFloat(formData.horimetro.replace(",", ".")),
    };

    const res = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dataToSend),
    });

    if (res.ok) {
      alert("Manutenção registrada com sucesso!");
      router.push("/manutencoes");
    } else {
      const erro = await res.json();
      alert("Erro: " + JSON.stringify(erro));
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-blue-800 mb-4">Nova Manutenção</h1>
      <form onSubmit={handleSubmit} className="space-y-4">

        <select
          name="equipamento"
          value={formData.equipamento}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        >
          <option value="">Selecione o Equipamento</option>
          {equipamentos.map((eq) => (
            <option key={eq.id} value={eq.id}>{eq.nome}</option>
          ))}
        </select>

        <select
          name="tipo"
          value={formData.tipo}
          onChange={handleChange}
          className="w-full border rounded p-2"
        >
          <option value="preventiva">Preventiva</option>
          <option value="corretiva">Corretiva</option>
        </select>

        <input
          type="date"
          name="data"
          value={formData.data}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        />

        <input
          type="number"
          step="0.01"
          name="horimetro"
          value={formData.horimetro}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Horímetro (ex: 12542.60)"
          required
        />

        <input
          type="text"
          name="tecnico_responsavel"
          value={formData.tecnico_responsavel}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Técnico Responsável"
          required
        />

        <textarea
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Descrição da Manutenção"
        />

        <textarea
          name="observacoes"
          value={formData.observacoes}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Observações"
        />

        {formData.tipo === "preventiva" && (
          <input
            type="date"
            name="proxima_manutencao"
            value={formData.proxima_manutencao}
            onChange={handleChange}
            className="w-full border rounded p-2"
            placeholder="Próxima Manutenção Preventiva"
          />
        )}

        <div className="flex justify-between">
          <button
            type="submit"
            className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
          >
            Salvar
          </button>
          <button
            type="button"
            onClick={() => router.push("/manutencoes")}
            className="bg-gray-400 text-white px-6 py-2 rounded hover:bg-gray-500"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
