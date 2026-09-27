import Dexie, { type Table } from 'dexie';

export interface ProdutoLocal {
  id: string;
  codigo_barras: string;
  nome: string;
  preco_venda: number;
  quantidade_estoque: number;
}

export interface ItemVendaLocal {
  produto_id: string;
  quantidade: number;
  preco_unitario: number;
}

export interface VendaOffline {
  id: string; // UUID gerado no navegador
  data_venda: string;
  valor_total: number;
  tipo_emissao: string; // '1' (Online) ou '9' (Contingência Offline)
  status: 'PENDENTE_SYNC' | 'SYNCED';
  itens: ItemVendaLocal[];
}

export class ERPLocalDatabase extends Dexie {
  produtos!: Table<ProdutoLocal>;
  vendasOffline!: Table<VendaOffline>;

  constructor() {
    super('ERP_PDV_OfflineDB');
    this.version(1).stores({
      produtos: 'id, codigo_barras, nome',
      vendasOffline: 'id, status, data_venda'
    });
  }
}

export const dbLocal = new ERPLocalDatabase();