import { Typography } from 'antd';
import './App.css';

const { Title, Paragraph } = Typography;

function App() {
  return (
    <div className="app-container">
      <Title level={2}>TPVS Analytics Platform</Title>
      <Paragraph>
        Plateforme d&apos;analyse de données — Phase 0 (infrastructure)
      </Paragraph>
      <Paragraph type="secondary">
        Les modules du tableau de bord seront disponibles à partir de la Phase 4.
      </Paragraph>
    </div>
  );
}

export default App;
