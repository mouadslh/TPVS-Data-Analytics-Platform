import { useEffect, useState } from 'react';
import { Button, Card, Select, Spin, Table, message } from 'antd';
import { useTranslation } from 'react-i18next';
import { reportsApi } from '../api/client';

const REPORT_TYPES = [
  'QUOTIDIEN', 'HEBDOMADAIRE', 'MENSUEL', 'PERFORMANCE', 'STOCK', 'TRANSACTION', 'STATION',
];

export default function ReportsPage() {
  const { t } = useTranslation();
  const [rapports, setRapports] = useState<Record<string, unknown>[]>([]);
  const [type, setType] = useState('QUOTIDIEN');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const load = () => {
    setLoading(true);
    reportsApi.list().then((r) => setRapports(r.data)).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await reportsApi.generate(type);
      message.success('Rapport généré');
      load();
    } catch {
      message.error('Erreur de génération');
    } finally {
      setGenerating(false);
    }
  };

  const handleExport = async (id: string) => {
    const { data } = await reportsApi.export(id);
    const url = window.URL.createObjectURL(new Blob([data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = `rapport_${id}.pdf`;
    a.click();
  };

  if (loading) return <Spin />;

  return (
    <div>
      <Card title={t('generate_report')}>
        <Select value={type} onChange={setType} style={{ width: 200, marginRight: 8 }}
          options={REPORT_TYPES.map((r) => ({ value: r, label: r }))} />
        <Button type="primary" onClick={handleGenerate} loading={generating}>
          {t('generate_report')}
        </Button>
      </Card>
      <Card title="Rapports générés" style={{ marginTop: 16 }}>
        <Table dataSource={rapports} rowKey="id" size="small"
          columns={[
            { title: 'Type', dataIndex: 'type_rapport' },
            { title: 'Période', render: (_, r) => `${r.periode_debut} — ${r.periode_fin}` },
            { title: 'Statut', dataIndex: 'statut_generation' },
            { title: 'Date', dataIndex: 'date_generation' },
            {
              title: t('export'),
              render: (_, r) => r.statut_generation === 'TERMINE' ? (
                <Button size="small" onClick={() => handleExport(r.id as string)}>{t('export')}</Button>
              ) : null,
            },
          ]} />
      </Card>
    </div>
  );
}
