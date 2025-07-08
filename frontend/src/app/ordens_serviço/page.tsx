"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface OrdemServico {
  id: number;
  cliente_nome: string;
  equipamento_nome: string;
  data_abertura: string;
  finalizada: boolean;
}

export default function OrdensPage() {
  const [ordens, setOrdens] = useState<OrdemServico[]>([]);
  const [loading, setLoading] = useState(true);
  const [mostrarFinalizadas, setMostrarFinalizadas] = useState(false);

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/ordens-servico/")
      .then((res) => res.json())
      .then((data) => {
        const filtradas = data.filter(
          (os: OrdemServico) => os.finalizada === mostrarFinalizadas
        );
        // Ordena pela data (mais recente primeiro)
        const ordenadas = filtradas.sort(
         (a: OrdemServico, b: OrdemServico) =>
            b.data_abertura.localeCompare(a.data_abertura)
        );
        setOrdens(ordenadas);
      })
      .catch((err) => {
        console.error("Erro ao carregar ordens:", err);
        alert("Erro ao carregar ordens de serviço.");
      })
      .finally(() => setLoading(false));
  }, [mostrarFinalizadas]);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">
          {mostrarFinalizadas ? "Ordens Finalizadas" : "Ordens em Aberto"}
        </h1>

        <div className="flex gap-2">
          <Link
            href="/ordens-servico/nova"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Nova Ordem
          </Link>
          <button
            onClick={() => setMostrarFinalizadas(!mostrarFinalizadas)}
            className="px-4 py-2 border rounded text-sm text-gray-700 hover:bg-gray-100"
          >
            {mostrarFinalizadas ? "Ver em Aberto" : "Ver Finalizadas"}
          </button>
        </div>
      </div>

      {loading ? (
        <p>Carregando...</p>
      ) : ordens.length === 0 ? (
        <p className="text-gray-600">Nenhuma ordem encontrada.</p>
      ) : (
        <ul className="space-y-2">
          {ordens.map((os) => (
            <li
              key={os.id}
              className="border p-4 rounded shadow-sm flex flex-col sm:flex-row sm:justify-between sm:items-center"
            >
              <div>
                <p><strong>Cliente:</strong> {os.cliente_nome}</p>
                <p><strong>Equipamento:</strong> {os.equipamento_nome}</p>
                <p><strong>Data:</strong> {os.data_abertura}</p>
              </div>
              <div className="mt-2 sm:mt-0 sm:text-right">
                <span
                  className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${
                    os.finalizada
                      ? "bg-green-200 text-green-800"
                      : "bg-yellow-100 text-yellow-800"
                  }`}
                >
                  {os.finalizada ? "Finalizada" : "Em Aberto"}
                </span>
                <br />
                <Link
                  href={`/ordens-servico/editar/${os.id}`}
                  className="text-blue-600 underline text-sm"
                >
                  Editar
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}

      <Link
        href="/"
        className="text-sm text-gray-500 underline block mt-6"
      >
        ⬅ Voltar ao Início
      </Link>
    </div>
  );
}
