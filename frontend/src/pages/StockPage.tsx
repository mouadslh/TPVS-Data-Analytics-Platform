import { useEffect, useState } from 'react';
import { Alert, Card, Spin, Table, Tag } from 'antd';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { analyticsApi } from '../api/client';

export default function StockPage() {
  const [stock, setStock] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.stock().then((r) => setStock(r.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;
  const alerts = stock.filter((s) => s.alerte);
  const chartData = stock.slice(0, 20).map((s) => ({
    name: `${s.type_carte}-${String(s.station).slice(0, 10)}`,
    quantite: s.quantite_actuelle,
    seuil: s.seuil_alerte,
  }));

  return (
    <div>
      {alerts.length > 0 && (
        <Alert type="warning" message={`${alerts.length} alerte(s) de seuil`} showIcon style={{ marginBottom: 16 }} />
      )}
      <Card title="Niveaux de stock">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <XAxis dataKey="name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="quantite" fill="#1677ff" />
            <Bar dataKey="seuil" fill="#ff4d4f" />
          </BarChart>
        </ResponsiveContainer>
      </Card>
      <Card title="Détail stock" style={{ marginTop: 16 }}>
        <Table dataSource={stock} rowKey="id" size="small"
          columns={[
            { title: 'Type carte', dataIndex: 'type_carte' },
            { title: 'Station', dataIndex: 'station' },
            { title: 'Quantité', dataIndex: 'quantite_actuelle' },
            { title: 'Seuil', dataIndex: 'seuil_alerte' },
            { title: 'Défectueux', dataIndex: 'taux_defectueux', render: (v: number) => `${(v * 100).toFixed(2)}%` },
            { title: 'Rotation', dataIndex: 'taux_rotation' },
            { title: 'Alerte', dataIndex: 'alerte', render: (v: boolean) => v ? <Tag color="red">OUI</Tag> : <Tag>NON</Tag> },
          ]} pagination={{ pageSize: 20 }} />
      </Card>
    </div>
  );
}
