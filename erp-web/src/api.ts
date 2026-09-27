import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Transacao {
  id: number;
  descricao: string;
  valor: number;
  tipo: 'RECEITA' | 'DESPESA';
  status: 'PENDENTE' | 'PAGO' | 'ATRASADO' | 'CANCELADO';
  data_vencimento?: string;
}

export const getTransacoes = async (): Promise<Transacao[]> => {
  const response = await api.get<Transacao[]>('/financeiro/transacoes');
  return response.data;
};

export const solicitarRelatorio = async (): Promise<{ task_id: string; mensagem: string }> => {
  const response = await api.post('/financeiro/relatorios/solicitar');
  return response.data;
};