import { useState } from 'react';
import { Button, Card, Form, Input, Typography, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      navigate('/');
    } catch {
      message.error('Identifiants invalides');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <Card title={t('app_title')} style={{ width: 400 }}>
        <Typography.Paragraph type="secondary">
          admin / changeme123 — Super Admin
        </Typography.Paragraph>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item name="username" label={t('username')} rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label={t('password')} rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            {t('login')}
          </Button>
        </Form>
      </Card>
    </div>
  );
}
