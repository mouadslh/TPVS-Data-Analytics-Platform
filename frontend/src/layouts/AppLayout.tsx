import { useState } from 'react';
import { Layout, Menu, Button, Dropdown, Space } from 'antd';
import {
  DashboardOutlined, TransactionOutlined, TeamOutlined, ScheduleOutlined,
  InboxOutlined, DesktopOutlined, CarOutlined, FileTextOutlined,
  AlertOutlined, LogoutOutlined, GlobalOutlined, BulbOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, labelKey: 'dashboard' },
  { key: '/transactions', icon: <TransactionOutlined />, labelKey: 'transactions' },
  { key: '/agents', icon: <TeamOutlined />, labelKey: 'agents' },
  { key: '/missions', icon: <ScheduleOutlined />, labelKey: 'missions' },
  { key: '/stock', icon: <InboxOutlined />, labelKey: 'stock' },
  { key: '/machines', icon: <DesktopOutlined />, labelKey: 'machines' },
  { key: '/motos', icon: <CarOutlined />, labelKey: 'motos' },
  { key: '/reports', icon: <FileTextOutlined />, labelKey: 'reports' },
  { key: '/anomalies', icon: <AlertOutlined />, labelKey: 'anomalies' },
];

export default function AppLayout() {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const { toggle } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  const langMenu = {
    items: [
      { key: 'fr', label: 'Français', onClick: () => { i18n.changeLanguage('fr'); localStorage.setItem('tpvs_lang', 'fr'); } },
      { key: 'en', label: 'English', onClick: () => { i18n.changeLanguage('en'); localStorage.setItem('tpvs_lang', 'en'); } },
    ],
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div className="logo">{collapsed ? 'T' : 'TPVS'}</div>
        <Menu theme="dark" mode="inline" selectedKeys={[location.pathname]}
          items={menuItems.map((m) => ({ key: m.key, icon: m.icon, label: t(m.labelKey), onClick: () => navigate(m.key) }))} />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Space>
            <span>{user?.prenom} {user?.nom} ({user?.role})</span>
            <Button icon={<BulbOutlined />} onClick={toggle}>{t('dark_mode')}</Button>
            <Dropdown menu={langMenu}><Button icon={<GlobalOutlined />} /></Dropdown>
            <Button icon={<LogoutOutlined />} onClick={() => { logout(); navigate('/login'); }}>{t('logout')}</Button>
          </Space>
        </Header>
        <Content className="app-content"><Outlet /></Content>
      </Layout>
    </Layout>
  );
}
