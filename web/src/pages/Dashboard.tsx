import { useAuthStore } from '@/store/authStore';
import { Outlet, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { LogOut, LayoutDashboard } from 'lucide-react';

export default function DashboardLayout() {
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 flex flex-col">
      <header className="border-b border-zinc-900 bg-zinc-950/50 backdrop-blur sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-lg">
            <LayoutDashboard className="text-zinc-400" /> Auto Affiliate Command Center
          </div>
          <nav className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-zinc-400 hover:text-white hover:bg-zinc-900">
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </nav>
        </div>
      </header>

      <main className="flex-1 container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
