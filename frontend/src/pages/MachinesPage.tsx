import { useEffect, useState } from 'react';
import { Card, Col, Row, Spin, Statistic, Table } from 'antd';
import { analyticsApi } from '../api/client';

export default function MachinesPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.machines().then((r) => setData(r.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;
  const parStation = (data?.par_station as Record<string, unknown>[]) || [];

  return (
    <div>
      <Row gutter={16}>
        <Col span={6}><Card><Statistic title="Total" value={data?.total as number} /></Card></Col>
        <Col span={6}><Card><Statistic title="Disponibles" value={data?.disponibles as number} /></Card></Col>
        <Col span={6}><Card><Statistic title="Disponibilité" value={`${((Number(data?.taux_disponibilite) || 0) * 100).toFixed(1)}%`} /></Card></Col>
        <Col span={6}><Card><Statistic title="Alertes batterie <20%" value={data?.alertes_batterie as number} valueStyle={{ color: '#cf1322' }} /></Card></Col>
      </Row>
      <Card title="Flotte par station" style={{ marginTop: 16 }}>
        <Table dataSource={parStation} rowKey="station__id" size="small"
          columns={[
            { title: 'Station', dataIndex: 'station__nom' },
            { title: 'Machines', dataIndex: 'count' },
            { title: 'CA', dataIndex: 'ca', render: (v: number) => v ? `€${Number(v).toFixed(2)}` : '—' },
          ]} />
      </Card>
    </div>
  );
}
