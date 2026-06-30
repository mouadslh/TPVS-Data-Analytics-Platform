import { useEffect, useState } from 'react';
import { Card, Col, Row, Spin, Statistic, Table } from 'antd';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { analyticsApi } from '../api/client';

export default function MotosPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.motos().then((r) => setData(r.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;
  const positions = (data?.positions as Record<string, unknown>[]) || [];

  return (
    <div>
      <Row gutter={16}>
        <Col span={8}><Card><Statistic title="Total motos" value={data?.total as number} /></Card></Col>
        <Col span={8}><Card><Statistic title="En mission" value={data?.en_mission as number} /></Card></Col>
        <Col span={8}><Card><Statistic title="Kilométrage total" value={data?.kilometrage_total as number} suffix="km" /></Card></Col>
      </Row>
      <Card title="Carte GPS temps réel" style={{ marginTop: 16 }}>
        <MapContainer center={[48.8566, 2.3522]} zoom={12} style={{ height: 400, width: '100%' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {positions.map((p) => (
            <CircleMarker key={p.id as string} center={[p.latitude as number, p.longitude as number]} radius={8} color="#1677ff">
              <Popup>
                <div>
                  <strong>{p.type_moto as string}</strong><br />
                  Agent: {p.agent as string || '—'}<br />
                  Batterie: {p.niveau_batterie as number}%<br />
                  Km: {p.kilometrage as number}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </Card>
      <Card title="Flotte motos" style={{ marginTop: 16 }}>
        <Table dataSource={positions} rowKey="id" size="small"
          columns={[
            { title: 'Type', dataIndex: 'type_moto' },
            { title: 'Statut', dataIndex: 'statut' },
            { title: 'Batterie', dataIndex: 'niveau_batterie', render: (v: number) => `${v}%` },
            { title: 'Km', dataIndex: 'kilometrage' },
            { title: 'Agent', dataIndex: 'agent' },
          ]} />
      </Card>
    </div>
  );
}
