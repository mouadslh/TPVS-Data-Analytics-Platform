import { useEffect, useState } from 'react';
import { Card, Col, Row, Spin, Statistic, Table } from 'antd';
import { useTranslation } from 'react-i18next';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { analyticsApi } from '../api/client';

export default function DashboardPage() {
  const { t } = useTranslation();
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.executive().then((r) => setData(r.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;
  const banner = data?.banner as Record<string, number>;
  const evolution = (data?.ca_evolution as { date: string; ca: number }[]) || [];
  const topAgents = (data?.top_agents as Record<string, unknown>[]) || [];
  const topStations = (data?.top_stations as Record<string, unknown>[]) || [];

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}><Card><Statistic title={t('ca_jour')} value={banner?.ca_jour} prefix="€" precision={2} /></Card></Col>
        <Col xs={24} sm={12} lg={6}><Card><Statistic title={t('tx_validees')} value={banner?.transactions_validees} /></Card></Col>
        <Col xs={24} sm={12} lg={6}><Card><Statistic title={t('agents_actifs')} value={banner?.agents_actifs} /></Card></Col>
        <Col xs={24} sm={12} lg={6}><Card><Statistic title={t('machines_op')} value={banner?.machines_operationnelles} /></Card></Col>
      </Row>
      <Card title="Évolution CA (30 jours)" style={{ marginTop: 16 }}>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={evolution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="ca" stroke="#1677ff" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Card>
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="Top 5 Agents">
            <Table dataSource={topAgents} rowKey="agent_id" size="small" pagination={false}
              columns={[
                { title: 'Agent', dataIndex: 'nom' },
                { title: 'CA', dataIndex: 'ca', render: (v: number) => `€${v.toFixed(2)}` },
                { title: 'Volume', dataIndex: 'volume' },
              ]} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Top 5 Stations">
            <Table dataSource={topStations} rowKey="station_id" size="small" pagination={false}
              columns={[
                { title: 'Station', dataIndex: 'nom' },
                { title: 'CA', dataIndex: 'ca', render: (v: number) => `€${v.toFixed(2)}` },
              ]} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
