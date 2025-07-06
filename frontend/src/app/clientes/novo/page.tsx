"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

interface Cliente {
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

export default function NovoCliente() {
  const router = useRouter();
  const [formData, setFormData] = useState<Cliente>({
    razao_social: "",
    nome_fantasia: "",
    cnpj: "",
    inscricao_estadual: "",
    email: "",
    telefone: "",
    rua: "",
    numero: "",
    bairro: "",
    cidade: "",
    estado: "",
    cep: "",
    observacoes: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (res.ok) {
        alert("Cliente cadastrado!");
        router.push("/clientes");
      } else {
        const erro = await res.json();
        alert("Erro: " + JSON.stringify(erro));
      }
    } catch {
      alert("Erro ao salvar.");
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Novo Cliente</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {Object.keys(formData).map((campo) => (
          <div key={campo}>
            <label className="block text-sm font-medium capitalize">{campo.replace("_", " ")}</label>
            {campo === "observacoes" ? (
              <textarea
                name={campo}
                className="w-full border px-3 py-2 rounded"
                value={formData[campo as keyof Cliente] || ""}
                onChange={handleChange}
              />
            ) : (
              <input
                name={campo}
                type="text"
                className="w-full border px-3 py-2 rounded"
                value={formData[campo as keyof Cliente] || ""}
                onChange={handleChange}
              />
            )}
          </div>
        ))}
        <button type="submit" className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-600">
          Salvar
        </button>
      </form>
    </div>
  );
}
