import { useAuthStore } from '@/store/authStore';
import { Outlet, useNavigate, Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { LogOut, LayoutDashboard, CheckSquare, Target, Smartphone, Zap, Activity } from 'lucide-react';

export default function DashboardLayout() {
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const location = useLocation();

  const navItems = [
    { label: 'Approval Queue', path: '/dashboard/approval', icon: <CheckSquare className="w-4 h-4 mr-3" /> },
    { label: 'Campaigns', path: '/dashboard/campaigns', icon: <Target className="w-4 h-4 mr-3" /> },
    { label: 'Thiết Bị', path: '/dashboard/devices', icon: <Smartphone className="w-4 h-4 mr-3" /> },
    { label: 'Seeding', path: '/dashboard/seeding', icon: <Zap className="w-4 h-4 mr-3" /> },
    { label: 'System Logs', path: '/dashboard/logs', icon: <Activity className="w-4 h-4 mr-3" /> },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <header className="border-b border-border bg-background/80 backdrop-blur sticky top-0 z-50">
        <div className="px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-lg">
            <LayoutDashboard className="text-primary" /> 
            <span className="hidden sm:inline">Auto Affiliate</span> Command Center
          </div>
          <nav className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground hover:text-destructive hover:bg-muted pointer">
              <LogOut className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">Sign Out</span>
            </Button>
          </nav>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-64 border-r border-border bg-background/50 p-4 hidden md:block">
          <nav className="space-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.path);
              return (
                <Link key={item.path} to={item.path}>
                  <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    className={`w-full justify-start ${isActive ? 'bg-primary/10 text-primary hover:bg-primary/20' : 'text-muted-foreground hover:text-foreground'}`}
                  >
                    {item.icon}
                    {item.label}
                  </Button>
                </Link>
              );
            })}
          </nav>
        </aside>

        <main className="flex-1 overflow-auto p-4 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
