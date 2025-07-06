"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";

interface Cliente {
  id?: number;
  razao_social: string;
  nome_fantasia?: string;
  cnpj: string;
  inscricao_estadual?: string;
  email?: string;
  telefone?: string;
  rua: string;
  numero: string;
  bairro: string;
  cidade: string;
  estado: string;
  cep: string;
  observacoes?: string;
}

export default function EditarCliente() {
  const { id } = useParams();
  const router = useRouter();
  const [formData, setFormData] = useState<Cliente | null>(null);

  useEffect(() => {
    if (typeof id === "string") {
      fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`)
        .then((res) => res.json())
        .then((data) => setFormData(data))
        .catch(() => alert("Erro ao carregar cliente."));
    }
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (formData) {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData || typeof id !== "string") return;

    try {
      const res = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        alert("Cliente atualizado!");
        router.push("/clientes");
      } else {
        const erro = await res.json();
        alert("Erro: " + JSON.stringify(erro));
      }
    } catch {
      alert("Erro ao salvar.");
    }
  };

  if (!formData) return <div className="p-4">Carregando...</div>;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Editar Cliente</h2>
        <Link href="/" className="bg-gray-200 text-gray-800 px-3 py-1 rounded hover:bg-gray-300">
          🏠 Home
        </Link>
      </div>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(formData).map(([campo, valor]) => (
          <div key={campo} className="col-span-1">
            <label className="block text-sm font-medium capitalize mb-1">
              {campo.replace("_", " ")}
            </label>
            {campo === "observacoes" ? (
              <textarea
                name={campo}
                className="w-full border px-2 py-1 text-sm rounded"
                value={valor ?? ""}
                onChange={handleChange}
              />
            ) : (
              <input
                name={campo}
                type="text"
                className="w-full border px-2 py-1 text-sm rounded"
                value={valor ?? ""}
                onChange={handleChange}
              />
            )}
          </div>
        ))}
        <div className="col-span-2">
          <button
            type="submit"
            className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-600 w-full md:w-auto"
          >
            Atualizar
          </button>
        </div>
      </form>
    </div>
  );
}
