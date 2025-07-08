"use client";

import { useEffect, useState, useMemo } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useDebounce } from "use-debounce";

interface Conta {
  id: number;
  descricao: string;
  valor: number;
  data_vencimento: string;
  tipo: string;
  status: string;
  cliente_nome?: string;
  fornecedor_nome?: string;
}

export default function RelatorioFinanceiroPage() {
  const [contas, setContas] = useState<Conta[]>([]);
  const [mes, setMes] = useState<string>((new Date().getMonth() + 1).toString());
  const [ano, setAno] = useState<string>(new Date().getFullYear().toString());
  const [clienteFiltro, setClienteFiltro] = useState("");
  const [fornecedorFiltro, setFornecedorFiltro] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [debouncedClienteFiltro] = useDebounce(clienteFiltro, 300);
  const [debouncedFornecedorFiltro] = useDebounce(fornecedorFiltro, 300);

  useEffect(() => {
    setIsLoading(true);
    axios
      .get<Conta[]>("https://mandacaru-backend-i2ci.onrender.com/api/financeiro/contas/")
      .then((res) => {
        setContas(res.data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Erro ao carregar contas:", err);
        setError("Falha ao carregar os dados. Tente novamente.");
        setIsLoading(false);
      });
  }, []);

  const contasFiltradas = useMemo(() => {
    return contas.filter((conta) => {
      const data = new Date(conta.data_vencimento);
      const mesAnoOK =
        data.getMonth() + 1 === parseInt(mes) &&
        data.getFullYear() === parseInt(ano);
      const clienteOK =
        !debouncedClienteFiltro ||
        (conta.cliente_nome &&
          conta.cliente_nome.toLowerCase().includes(debouncedClienteFiltro.toLowerCase()));
      const fornecedorOK =
        !debouncedFornecedorFiltro ||
        (conta.fornecedor_nome &&
          conta.fornecedor_nome.toLowerCase().includes(debouncedFornecedorFiltro.toLowerCase()));
      return mesAnoOK && clienteOK && fornecedorOK;
    });
  }, [contas, mes, ano, debouncedClienteFiltro, debouncedFornecedorFiltro]);

  const total = (filtro: Partial<Conta>) =>
    contasFiltradas
      .filter((conta) =>
        Object.entries(filtro).every(([k, v]) => conta[k as keyof Conta] === v)
      )
      .reduce((acc, conta) => acc + conta.valor, 0);

  const formatar = (valor: number) =>
    new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(valor);

  const escapeCsv = (value: string) => `"${value.replace(/"/g, '""')}"`;

  const exportarParaExcel = () => {
    const csv = [
      ["Descrição", "Valor", "Data", "Tipo", "Status"],
      ...contasFiltradas.map((c) => [
        escapeCsv(c.descricao),
        c.valor,
        c.data_vencimento,
        c.tipo,
        c.status,
      ]),
    ]
      .map((row) => row.join(";"))
      .join("\n");

    const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `relatorio-financeiro-${mes}-${ano}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const dadosGrafico = useMemo(
    () => [
      { nome: "Pagar", valor: total({ tipo: "pagar" }) },
      { nome: "Receber", valor: total({ tipo: "receber" }) },
      { nome: "Pagos", valor: total({ status: "pago" }) },
      { nome: "Pendentes", valor: total({ status: "pendente" }) },
    ],
    [total]
  );

  if (isLoading) return <div className="p-6">Carregando...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Relatório Financeiro</h1>

      <div className="flex flex-wrap gap-4 mb-6">
        <select value={mes} onChange={(e) => setMes(e.target.value)} className="border p-2 rounded">
          {Array.from({ length: 12 }, (_, i) => (
            <option key={i + 1} value={i + 1}>
              {i + 1}
            </option>
          ))}
        </select>
        <select value={ano} onChange={(e) => setAno(e.target.value)} className="border p-2 rounded">
          {["2024", "2025", "2026"].map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
        <input
          placeholder="Filtrar por cliente"
          value={clienteFiltro}
          onChange={(e) => setClienteFiltro(e.target.value)}
          className="border p-2 rounded"
        />
        <input
          placeholder="Filtrar por fornecedor"
          value={fornecedorFiltro}
          onChange={(e) => setFornecedorFiltro(e.target.value)}
          className="border p-2 rounded"
        />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="bg-white border shadow p-4 rounded">
          <p className="text-gray-600">Total a Pagar</p>
          <p className="text-lg font-bold text-red-600">{formatar(total({ tipo: "pagar" }))}</p>
        </div>
        <div className="bg-white border shadow p-4 rounded">
          <p className="text-gray-600">Total a Receber</p>
          <p className="text-lg font-bold text-green-600">{formatar(total({ tipo: "receber" }))}</p>
        </div>
        <div className="bg-white border shadow p-4 rounded">
          <p className="text-gray-600">Pagos</p>
          <p className="text-lg font-bold text-blue-600">{formatar(total({ status: "pago" }))}</p>
        </div>
        <div className="bg-white border shadow p-4 rounded">
          <p className="text-gray-600">Pendentes</p>
          <p className="text-lg font-bold text-orange-600">{formatar(total({ status: "pendente" }))}</p>
        </div>
      </div>

      <div className="bg-white p-4 mb-6 rounded shadow">
        <h2 className="text-lg font-semibold mb-2">Resumo em Gráfico</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={dadosGrafico}>
            <XAxis dataKey="nome" />
            <YAxis />
            <Tooltip formatter={(value: number) => formatar(value)} />
            <Bar dataKey="valor" fill="#22c55e" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <table className="w-full bg-white border shadow rounded text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 text-left">Descrição</th>
            <th className="p-2 text-left">Valor</th>
            <th className="p-2 text-left">Data</th>
            <th className="p-2 text-left">Tipo</th>
            <th className="p-2 text-left">Status</th>
            <th className="p-2 text-left">Cliente</th>
            <th className="p-2 text-left">Fornecedor</th>
          </tr>
        </thead>
        <tbody>
          {contasFiltradas.map((conta) => (
            <tr key={conta.id} className="border-t">
              <td className="p-2">{conta.descricao}</td>
              <td className="p-2">{formatar(conta.valor)}</td>
              <td className="p-2">{conta.data_vencimento}</td>
              <td className="p-2 capitalize">{conta.tipo}</td>
              <td className="p-2 capitalize">{conta.status}</td>
              <td className="p-2">{conta.cliente_nome || "-"}</td>
              <td className="p-2">{conta.fornecedor_nome || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex gap-4 mt-6">
        <button
          onClick={() => window.print()}
          className="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-800"
        >
          Exportar PDF
        </button>
        <button
          onClick={exportarParaExcel}
          className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800"
        >
          Exportar Excel
        </button>
      </div>
    </div>
  );
}
