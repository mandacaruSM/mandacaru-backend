"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

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
    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`)
      .then((res) => res.json())
      .then((data: Cliente) => setFormData(data))
      .catch(() => alert("Erro ao carregar cliente."));
  }, [id]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    if (formData) {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData) return;

    try {
      const res = await fetch(
        `https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        }
      );

      if (res.ok) {
        alert("Cliente atualizado com sucesso!");
        router.push("/clientes");
      } else {
        const erro = await res.json();
        alert("Erro ao atualizar: " + JSON.stringify(erro));
      }
    } catch {
      alert("Erro ao enviar dados para o servidor.");
    }
  };

  if (!formData) return <div className="p-6">Carregando...</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Editar Cliente</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {Object.entries(formData).map(([campo, valor]) => {
          if (campo === "id") return null;

          const label = campo.replace(/_/g, " ").toUpperCase();

          return (
            <div key={campo}>
              <label className="block text-sm font-medium">{label}</label>
              {campo === "observacoes" ? (
                <textarea
                  name={campo}
                  className="w-full border px-3 py-2 rounded"
                  value={String(valor ?? "")}
                  onChange={handleChange}
                />
              ) : (
                <input
                  type="text"
                  name={campo}
                  className="w-full border px-3 py-2 rounded"
                  value={String(valor ?? "")}
                  onChange={handleChange}
                />
              )}
            </div>
          );
        })}

        <button
          type="submit"
          className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Atualizar
        </button>
      </form>
    </div>
  );
}
