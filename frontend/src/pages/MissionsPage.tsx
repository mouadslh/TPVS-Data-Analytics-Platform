import { useEffect, useState } from 'react';
import { Card, Col, Progress, Row, Spin, Statistic, Table, Tag } from 'antd';
import { analyticsApi } from '../api/client';

export default function MissionsPage() {
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null);
  const [missions, setMissions] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([analyticsApi.missions(), analyticsApi.missionList()])
      .then(([s, m]) => { setSummary(s.data); setMissions(m.data); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;

  const statutColor: Record<string, string> = {
    TERMINEE: 'green', EN_COURS: 'blue', PLANIFIEE: 'default', ANNULEE: 'red',
  };

  return (
    <div>
      <Row gutter={16}>
        <Col span={6}><Card><Statistic title="Total missions" value={summary?.total as number} /></Card></Col>
        <Col span={6}><Card><Statistic title="Terminées" value={summary?.terminees as number} /></Card></Col>
        <Col span={6}><Card><Statistic title="En cours" value={summary?.en_cours as number} /></Card></Col>
        <Col span={6}><Card><Statistic title="Durée moyenne (min)" value={summary?.duree_moyenne_minutes as number} /></Card></Col>
      </Row>
      <Card title="Taux de complétion" style={{ marginTop: 16 }}>
        <Progress percent={Math.round(Number(summary?.taux_completion || 0) * 100)} status="active" />
      </Card>
      <Card title="Missions récentes" style={{ marginTop: 16 }}>
        <Table dataSource={missions} rowKey="id" size="small"
          columns={[
            { title: 'Agent', dataIndex: 'agent_nom' },
            { title: 'Station', dataIndex: 'station_nom' },
            { title: 'Début', dataIndex: 'date_debut' },
            { title: 'Fin', dataIndex: 'date_fin' },
            { title: 'Statut', dataIndex: 'statut', render: (v: string) => <Tag color={statutColor[v]}>{v}</Tag> },
            { title: 'Zone', dataIndex: 'zone_couverture' },
          ]} pagination={{ pageSize: 20 }} />
      </Card>
    </div>
  );
}
