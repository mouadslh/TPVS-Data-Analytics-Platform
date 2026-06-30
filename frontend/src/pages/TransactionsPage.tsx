import { useEffect, useState } from 'react';
import { Card, Col, Row, Select, Spin, Table, Tag } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { analyticsApi } from '../api/client';

export default function TransactionsPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [txList, setTxList] = useState<Record<string, unknown>[]>([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      analyticsApi.transactions(days),
      analyticsApi.transactionList(days),
    ]).then(([summary, list]) => {
      setData(summary.data);
      setTxList(list.data);
    }).finally(() => setLoading(false));
  }, [days]);

  if (loading) return <Spin />;
  const summary = data?.summary as Record<string, unknown>;
  const heatmap = (data?.heatmap as { hour: number; count: number }[]) || [];
  const nVsN1 = data?.n_vs_n1 as Record<string, number>;
  const anomalies = (data?.anomalies as Record<string, unknown>[]) || [];
  const paiements = (summary?.par_paiement as { type_paiement: string; count: number; ca: number }[]) || [];

  return (
    <div>
      <Select value={days} onChange={setDays} style={{ marginBottom: 16 }}
        options={[{ value: 7, label: '7 jours' }, { value: 30, label: '30 jours' }, { value: 90, label: '90 jours' }]} />
      <Row gutter={16}>
        <Col span={6}><Card>CA Total: €{Number(summary?.ca_total || 0).toFixed(2)}</Card></Col>
        <Col span={6}><Card>Volume: {summary?.volume as number}</Card></Col>
        <Col span={6}><Card>Ticket moyen: €{Number(summary?.ticket_moyen || 0).toFixed(2)}</Card></Col>
        <Col span={6}><Card>N vs N-1: {nVsN1?.variation_pct}%</Card></Col>
      </Row>
      <Card title="CA par mode de paiement" style={{ marginTop: 16 }}>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={paiements}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="type_paiement" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="ca" fill="#1677ff" />
          </BarChart>
        </ResponsiveContainer>
      </Card>
      <Card title="Heatmap horaire" style={{ marginTop: 16 }}>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={heatmap}>
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#722ed1" />
          </BarChart>
        </ResponsiveContainer>
      </Card>
      {anomalies.length > 0 && (
        <Card title="Anomalies détectées (Z-score > 3σ)" style={{ marginTop: 16 }}>
          <Table dataSource={anomalies} rowKey="transaction_id" size="small"
            columns={[
              { title: 'N°', dataIndex: 'numero' },
              { title: 'Montant', dataIndex: 'montant', render: (v: number) => `€${v}` },
              { title: 'Z-score', dataIndex: 'z_score' },
              { title: 'Agent', dataIndex: 'agent' },
            ]} pagination={{ pageSize: 5 }} />
        </Card>
      )}
      <Card title="Transactions" style={{ marginTop: 16 }}>
        <Table dataSource={txList} rowKey="id" size="small" scroll={{ x: 800 }}
          columns={[
            { title: 'N°', dataIndex: 'numero_transaction' },
            { title: 'Montant', dataIndex: 'montant', render: (v: number) => `€${v}` },
            { title: 'Paiement', dataIndex: 'type_paiement' },
            { title: 'Statut', dataIndex: 'statut_validation', render: (v: string) => <Tag>{v}</Tag> },
            { title: 'Station', dataIndex: 'station_nom' },
            { title: 'Date', dataIndex: 'timestamp' },
          ]} pagination={{ pageSize: 20 }} />
      </Card>
    </div>
  );
}
