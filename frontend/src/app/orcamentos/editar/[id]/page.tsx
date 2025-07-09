/* File: app/orcamentos/editar/[id]/page.tsx */

"use client";
import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL!;

interface Cliente { id: number; nome_fantasia: string }
interface Empreendimento { id: number; nome: string; distancia_km: number }
interface Equipamento { id: number; nome: string }
interface AlmoxarifadoItem { id: number; nome: string; estoque: number; valor_venda: number }

interface Item {
  tipo: "peca" | "deslocamento" | "mao_de_obra";
  almox_id?: number; // referência ao almoxarifado
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

export default function EditarOrcamentoPage() {
  const { id } = useParams();
  const router = useRouter();

  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [almoxItems, setAlmoxItems] = useState<AlmoxarifadoItem[]>([]);
  const [form, setForm] = useState<OrcamentoFormData>({ cliente: "", empreendimento: "", equipamento: "", status: "", items: [] });
  const [loading, setLoading] = useState(true);

  // Carrega dados iniciais
  useEffect(() => {
    async function fetchData() {
      try {
        const [cliRes, empRes, eqRes, oxRes, orcRes] = await Promise.all([
          fetch(`${API}/api/clientes/`),
          fetch(`${API}/api/empreendimentos/`),
          fetch(`${API}/api/equipamentos/`),
          fetch(`${API}/api/almoxarifado/`),
          fetch(`${API}/api/orcamentos/${id}/`),
        ]);
        if (!cliRes.ok || !empRes.ok || !eqRes.ok || !oxRes.ok || !orcRes.ok) throw new Error("Erro no fetch inicial");
        const [cliData, empData, eqData, oxData, orcData] = await Promise.all([
          cliRes.json(), empRes.json(), eqRes.json(), oxRes.json(), orcRes.json()
        ]);
        setClientes(cliData);
        setEmpreendimentos(empData);
        setEquipamentos(eqData);
        setAlmoxItems(oxData);
        setForm({
          cliente: String(orcData.cliente),
          empreendimento: String(orcData.empreendimento),
          equipamento: String(orcData.equipamento),
          status: orcData.status,
          items: orcData.items.map((it: any) => ({
            tipo: it.tipo,
            almox_id: it.almoxarifado_item || undefined,
            descricao: it.descricao,
            quantidade: it.quantidade,
            valor_unitario: it.valor_unitario,
            total: it.total,
          })),
        });
      } catch (err) {
        console.error(err);
        alert("Erro ao carregar dados.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  const handleFieldChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value } as any));
  };

  const updateItem = (index: number, field: keyof Item, value: any) => {
    setForm(prev => {
      const items = [...prev.items];
      items[index] = { ...items[index], [field]: value };
      items[index].total = parseFloat((items[index].quantidade * items[index].valor_unitario).toFixed(2));
      return { ...prev, items };
    });
  };

  const addItem = () => {
    setForm(prev => ({
      ...prev,
      items: [...prev.items, { tipo: "peca", almox_id: undefined, descricao: "", quantidade: 1, valor_unitario: 0, total: 0 }],
    }));
  };

  const removeItem = (index: number) => {
    setForm(prev => ({ ...prev, items: prev.items.filter((_, i) => i !== index) }));
  };

  const calculateDeslocamento = () => {
    const emp = empreendimentos.find(e => String(e.id) === form.empreendimento);
    const rate = 2;
    return emp ? parseFloat((emp.distancia_km * rate).toFixed(2)) : 0;
  };

  const calculateTotal = () => form.items.reduce((sum, it) => sum + it.total, 0).toFixed(2);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // reservar itens do almoxarifado
      const pecas = form.items.filter(it => it.tipo === "peca" && it.almox_id).map(it => ({ almox_id: it.almox_id, quantidade: it.quantidade }));
      if (pecas.length) {
        await fetch(`${API}/api/almoxarifado/reservar/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ items: pecas, orcamento: Number(id) }),
        });
      }
      // atualiza orçamento
      const res = await fetch(`${API}/api/orcamentos/${id}/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cliente: Number(form.cliente),
          empreendimento: Number(form.empreendimento),
          equipamento: Number(form.equipamento),
          status: form.status,
          items: form.items.map(it => ({
            tipo: it.tipo,
            almoxarifado_item: it.almox_id,
            descricao: it.descricao,
            quantidade: it.quantidade,
            valor_unitario: it.valor_unitario,
          })),
        }),
      });
      if (!res.ok) throw new Error(`Erro ${res.status}`);
      // se aprovado, criar OS e dar saída
      if (form.status === "aprovado") {
        const osRes = await fetch(`${API}/api/ordens-servico/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ orcamento: Number(id) }),
        });
        if (osRes.ok) {
          await fetch(`${API}/api/almoxarifado/saida/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ items: pecas, venda: true, os_id: (await osRes.json()).id }),
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
    <form onSubmit={handleSubmit} className="p-6 max-w-lg mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Editar Orçamento</h1>
      {/* filtros... */}
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
      {/* tabela de itens */}
      <div>
        <h2 className="text-lg font-semibold mb-2">Itens do Orçamento</h2>
        <table className="w-full border">
          <thead>
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
                <td><select value={it.tipo} onChange={e => updateItem(idx,'tipo',e.target.value)}>
                  <option value="peca">Peça</option>
                  <option value="deslocamento">Deslocamento</option>
                  <option value="mao_de_obra">Mão de Obra</option>
                </select></td>
                <td><select value={it.almox_id} onChange={e => updateItem(idx,'almox_id',Number(e.target.value))}>
                  <option value="">Selecione Peça</option>
                  {almoxItems.map(ai => <option key={ai.id} value={ai.id}>{ai.nome} (Estoque: {ai.estoque})</option>)}
                </select></td>
                <td><input type="text" value={it.descricao} onChange={e => updateItem(idx,'descricao',e.target.value)} /></td>
                <td><input type="number" min="1" value={it.quantidade} onChange={e => updateItem(idx,'quantidade',parseInt(e.target.value))} /></td>
                <td><input type="number" step="0.01" value={it.valor_unitario} onChange={e => updateItem(idx,'valor_unitario',parseFloat(e.target.value))} /></td>
                <td>{it.total.toFixed(2)}</td>
                <td><button type="button" onClick={() => removeItem(idx)}>Remover</button></td>
              </tr>
            ))}
          </tbody>
        </table>
        <button type="button" onClick={addItem}>+ Adicionar Item</button>
      </div>
      <select name="status" value={form.status} onChange={handleFieldChange} required>
        <option value="pendente">Pendente</option>
        <option value="aprovado">Aprovado</option>
        <option value="rejeitado">Rejeitado</option>
      </select>
      <div className="text-right font-bold">Total: R$ {calculateTotal()}</div>
      <button type="submit">Salvar Alterações</button>
    </form>
  );
}