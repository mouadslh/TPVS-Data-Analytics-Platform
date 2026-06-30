import { useEffect, useState } from 'react';
import { Card, Spin, Table, Tag } from 'antd';
import { useTranslation } from 'react-i18next';
import { analyticsApi } from '../api/client';

const SEVERITY_COLORS: Record<string, string> = {
  HIGH: 'red', MEDIUM: 'orange', LOW: 'blue',
};

export default function AnomaliesPage() {
  const { t } = useTranslation();
  const [anomalies, setAnomalies] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.anomalies().then((r) => setAnomalies(r.data.anomalies)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;

  return (
    <Card title={`${t('anomalies')} (${anomalies.length})`}>
      <Table dataSource={anomalies} rowKey={(r) => `${r.rule}-${r.entity_id}`} size="small"
        columns={[
          { title: t('rule'), dataIndex: 'rule' },
          { title: t('severity'), dataIndex: 'severity', render: (v: string) => <Tag color={SEVERITY_COLORS[v]}>{v}</Tag> },
          { title: t('message'), dataIndex: 'message' },
          { title: 'Entité', dataIndex: 'entity_type' },
        ]} pagination={{ pageSize: 20 }} />
    </Card>
  );
}
