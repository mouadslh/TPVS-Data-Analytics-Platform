import { useEffect, useState } from 'react';
import { Card, Select, Spin, Table } from 'antd';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from 'recharts';
import { analyticsApi } from '../api/client';

export default function AgentsPage() {
  const [agents, setAgents] = useState<Record<string, unknown>[]>([]);
  const [months, setMonths] = useState(3);
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    analyticsApi.agents(months).then((r) => {
      setAgents(r.data);
      if (r.data.length) setSelected(r.data[0].agent_id as string);
    }).finally(() => setLoading(false));
  }, [months]);

  if (loading) return <Spin />;
  const agent = agents.find((a) => a.agent_id === selected);

  const radarData = agent ? [
    { metric: 'CA', value: Math.min(Number(agent.ca) / 1000, 100) },
    { metric: 'Volume', value: Math.min(Number(agent.volume), 100) },
    { metric: 'Complétion', value: Number(agent.taux_completion) * 100 },
    { metric: 'Score', value: Math.min(Number(agent.score_performance) / 10, 100) },
  ] : [];

  return (
    <div>
      <Select value={months} onChange={setMonths} style={{ marginBottom: 16, marginRight: 8 }}
        options={[{ value: 3, label: '3 mois' }, { value: 6, label: '6 mois' }, { value: 12, label: '12 mois' }]} />
      <Card title="Classement agents">
        <Table dataSource={agents} rowKey="agent_id" size="small"
          onRow={(r) => ({ onClick: () => setSelected(r.agent_id as string), style: { cursor: 'pointer' } })}
          columns={[
            { title: 'Matricule', dataIndex: 'matricule' },
            { title: 'Nom', dataIndex: 'nom' },
            { title: 'Zone', dataIndex: 'zone' },
            { title: 'CA', dataIndex: 'ca', render: (v: number) => `€${v.toFixed(2)}`, sorter: (a, b) => Number(a.ca) - Number(b.ca) },
            { title: 'Score', dataIndex: 'score_performance', sorter: (a, b) => Number(a.score_performance) - Number(b.score_performance) },
            { title: 'Complétion', dataIndex: 'taux_completion', render: (v: number) => `${(v * 100).toFixed(1)}%` },
          ]} pagination={{ pageSize: 15 }} />
      </Card>
      {agent && (
        <Card title={`Profil — ${agent.nom}`} style={{ marginTop: 16 }}>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <Radar dataKey="value" stroke="#1677ff" fill="#1677ff" fillOpacity={0.4} />
            </RadarChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
}
