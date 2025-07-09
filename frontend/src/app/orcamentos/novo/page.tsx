/* File: app/orcamentos/novo/page.tsx */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL!;

interface Cliente { id: number; nome_fantasia: string }
interface Empreendimento { id: number; nome: string; distancia_km: number }
interface Equipamento { id: number; nome: string }
interface AlmoxarifadoItem { id: number; nome: string; estoque: number; valor_venda: number }

interface Item {
  tipo: "peca" | "deslocamento" | "mao_de_obra";
  almox_id?: number;
  descricao: string;
  quantidade: number;
  valor_unitario: number;
  total: number;
}

interface OrcamentoFormData {
  cliente: string;
  empreendimento: string;
  equipamento: string;
  status: string;
  items: Item[];
}

export default function NovoOrcamentoPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [almoxItems, setAlmoxItems] = useState<AlmoxarifadoItem[]>([]);
  const [form, setForm] = useState<OrcamentoFormData>({
    cliente: "",
    empreendimento: "",
    equipamento: "",
    status: "pendente",
    items: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [cliRes, empRes, eqRes, oxRes] = await Promise.all([
          fetch(`${API}/api/clientes/`),
          fetch(`${API}/api/empreendimentos/`),
          fetch(`${API}/api/equipamentos/`),
          fetch(`${API}/api/almoxarifado/`),
        ]);
        const [cli, emp, eq, ox] = await Promise.all([
          cliRes.json(),
          empRes.json(),
          eqRes.json(),
          oxRes.json(),
        ]);
        setClientes(cli);
        setEmpreendimentos(emp);
        setEquipamentos(eq);
        setAlmoxItems(ox);
      } catch {
        alert("Erro ao carregar dados iniciais.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleFieldChange = (
    e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value } as any));
  };

  const updateItem = (index: number, field: keyof Item, value: any) => {
    setForm(prev => {
      const items = [...prev.items];
      items[index] = { ...items[index], [field]: value };
      items[index].total = parseFloat(
        (items[index].quantidade * items[index].valor_unitario).toFixed(2)
      );
      return { ...prev, items };
    });
  };

  const addItem = () => {
    setForm(prev => ({
      ...prev,
      items: [
        ...prev.items,
        { tipo: "peca", almox_id: undefined, descricao: "", quantidade: 1, valor_unitario: 0, total: 0 },
      ],
    }));
  };

  const removeItem = (index: number) => {
    setForm(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }));
  };

  const calculateDeslocamento = () => {
    const emp = empreendimentos.find(e => String(e.id) === form.empreendimento);
    const rate = 2; // R$ por km
    return emp ? parseFloat((emp.distancia_km * rate).toFixed(2)) : 0;
  };

  const calculateTotal = () => {
    const base = form.items.reduce((sum, it) => sum + it.total, 0);
    return base.toFixed(2);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let payloadItems = [...form.items];
      if (!payloadItems.some(it => it.tipo === "deslocamento")) {
        const desloc = calculateDeslocamento();
        payloadItems.push({
          tipo: "deslocamento",
          descricao: "Deslocamento",
          quantidade: 1,
          valor_unitario: desloc,
          total: desloc,
        });
      }

      const res = await fetch(`${API}/api/orcamentos/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cliente: Number(form.cliente),
          empreendimento: Number(form.empreendimento),
          equipamento: Number(form.equipamento),
          status: form.status,
          items: payloadItems.map(it => ({
            tipo: it.tipo,
            almoxarifado_item: it.almox_id,
            descricao: it.descricao,
            quantidade: it.quantidade,
            valor_unitario: it.valor_unitario,
          })),
        }),
      });
      if (!res.ok) throw new Error("Erro ao criar orçamento.");
      const orc = await res.json();

      if (form.status === "aprovado") {
        // Reservar peças
        await fetch(`${API}/api/almoxarifado/reservar/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            items: payloadItems
              .filter(it => it.tipo === "peca" && it.almox_id)
              .map(it => ({ almox_id: it.almox_id, quantidade: it.quantidade })),
            orcamento: orc.id,
          }),
        });
        // Criar OS
        const osRes = await fetch(`${API}/api/ordens-servico/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ orcamento: orc.id }),
        });
        if (osRes.ok) {
          const os = await osRes.json();
          // Registrar saída no almoxarifado vendedor
          await fetch(`${API}/api/almoxarifado/saida/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              items: payloadItems
                .filter(it => it.tipo === "peca" && it.almox_id)
                .map(it => ({ almox_id: it.almox_id, quantidade: it.quantidade })),
              venda: true,
              os_id: os.id,
            }),
          });
        }
      }

      router.push("/orcamentos");
    } catch (err) {
      console.error(err);
      alert("Erro ao salvar orçamento.");
    }
  };

  if (loading) return <p className="p-6">Carregando…</p>;

  return (
    <div className="p-6 max-w-lg mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Novo Orçamento</h1>
      {/* filtros seleção */}
      <div className="space-y-2">
        <select name="cliente" value={form.cliente} onChange={handleFieldChange} required>
          <option value="">Selecione Cliente</option>
          {clientes.map(c => <option key={c.id} value={String(c.id)}>{c.nome_fantasia}</option>)}
        </select>
        <select name="empreendimento" value={form.empreendimento} onChange={handleFieldChange} required>
          <option value="">Selecione Empreendimento</option>
          {empreendimentos.map(e => <option key={e.id} value={String(e.id)}>{e.nome}</option>)}
        </select>
        <select name="equipamento" value={form.equipamento} onChange={handleFieldChange} required>
          <option value="">Selecione Equipamento</option>
          {equipamentos.map(eq => <option key={eq.id} value={String(eq.id)}>{eq.nome}</option>)}
        </select>
      </div>
      {/* tabela itens */}
      <div>
        <h2 className="text-lg font-semibold mb-2">Itens do Orçamento</h2>
        <table className="w-full border">
          <thead className="bg-gray-100">
            <tr>
              <th className="border p-2">Tipo</th>
              <th className="border p-2">Peça Almox.</th>
              <th className="border p-2">Descrição</th>
              <th className="border p-2">Qtde</th>
              <th className="border p-2">Valor Unit.</th>
              <th className="border p-2">Total</th>
              <th className="border p-2">Ações</th>
            </tr>
          </thead>
          <tbody>
            {form.items.map((it, idx) => (
              <tr key={idx}>
                <td className="p-1">
                  <select value={it.tipo} onChange={e => updateItem(idx,'tipo',e.target.value)}>
                    <option value="peca">Peça</option>
                    <option value="deslocamento">Deslocamento</option>
                    <option value="mao_de_obra">Mão de Obra</option>
                  </select>
                </td>
                <td className="p-1">
                  <select value={it.almox_id} onChange={e => updateItem(idx,'almox_id',Number(e.target.value))}>
                    <option value="">Selecione Peça</option>
                    {almoxItems.map(ai => <option key={ai.id} value={ai.id}>
                      {ai.nome} (Estoque: {ai.estoque})
                    </option>)}
                  </select>
                </td>
                <td className="p-1"><input value={it.descricao} onChange={e => updateItem(idx,'descricao',e.target.value)} /></td>
                <td className="p-1"><input type="number" min="1" value={it.quantidade} onChange={e => updateItem(idx,'quantidade',parseInt(e.target.value))} /></td>
                <td className="p-1"><input type="number" step="0.01" value={it.valor_unitario} onChange={e => updateItem(idx,'valor_unitario',parseFloat(e.target.value))} /></td>
                <td className="p-1">{it.total.toFixed(2)}</td>
                <td className="p-1"><button type="button" onClick={() => removeItem(idx)}>Remover</button></td>
              </tr>
            ))}
          </tbody>
        </table>
        <button type="button" onClick={addItem} className="mt-2 bg-blue-600 text-white px-3 py-1 rounded">
          + Adicionar Item
        </button>
      </div>
      {/* status, total e ações */}
      <select name="status" value={form.status} onChange={handleFieldChange} required className="w-full border px-3 py-2 rounded">
        <option value="pendente">Pendente</option>
        <option value="aprovado">Aprovado</option>
        <option value="rejeitado">Rejeitado</option>
      </select>
      <div className="text-right font-bold">Total: R$ {calculateTotal()}</div>
      <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded">
        Salvar Orçamento
      </button>
      <Link href="/orcamentos" className="inline-block mt-4 text-green-600">Voltar</Link>
    </div>
  );
}
