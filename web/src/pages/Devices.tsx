import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import { Pencil, Wifi, WifiOff, Loader2, RefreshCcw } from 'lucide-react';

interface Device {
  id: string;
  label: string;
  udid: string;
  status: string;
  notes: string | null;
  is_active: boolean;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  online: 'bg-green-500/15 text-green-400 border border-green-500/30',
  offline: 'bg-zinc-500/15 text-zinc-400 border border-zinc-500/30',
  busy: 'bg-yellow-500/15 text-yellow-400 border border-yellow-500/30',
};

const STATUS_ICONS: Record<string, React.ReactNode> = {
  online: <Wifi className="w-3 h-3" />,
  offline: <WifiOff className="w-3 h-3" />,
  busy: <Loader2 className="w-3 h-3 animate-spin" />,
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[status] ?? STATUS_COLORS.offline}`}>
      {STATUS_ICONS[status]}
      {status}
    </span>
  );
}

const EMPTY_FORM = { label: '', notes: '' };

export default function Devices() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState('');

  const [isOpen, setIsOpen] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);

  useEffect(() => { fetchDevices(); }, []);

  const fetchDevices = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/devices');
      setDevices(data);
    } catch {
      setError('Không thể tải danh sách thiết bị.');
    } finally {
      setLoading(false);
    }
  };

  const scanDevices = async () => {
    setScanning(true);
    try {
      const { data } = await api.post('/devices/scan');
      setDevices(data);
    } catch {
      setError('Quét thiết bị thất bại.');
    } finally {
      setScanning(false);
    }
  };

  const openEdit = (device: Device) => {
    setEditingDevice(device);
    setForm({ label: device.label, notes: device.notes ?? '' });
    setIsOpen(true);
  };

  const handleSave = async () => {
    if (!form.label.trim()) return;
    setSaving(true);
    try {
      if (editingDevice) {
        const { data } = await api.put(`/devices/${editingDevice.id}`, {
          label: form.label,
          notes: form.notes || null,
        });
        setDevices(devices.map((d) => (d.id === editingDevice.id ? data : d)));
      }
      setIsOpen(false);
    } catch {
      setError('Lưu thất bại. Kiểm tra lại thông tin.');
    } finally {
      setSaving(false);
    }
  };

  const toggleStatus = async (device: Device) => {
    const next = device.status === 'online' ? 'offline' : 'online';
    try {
      const { data } = await api.patch(`/devices/${device.id}/status`, { status: next });
      setDevices(devices.map((d) => (d.id === device.id ? data : d)));
    } catch {
      setError('Cập nhật trạng thái thất bại.');
    }
  };

  const toggleActive = async (device: Device) => {
    try {
      const { data } = await api.put(`/devices/${device.id}`, { is_active: !device.is_active });
      setDevices(devices.map((d) => (d.id === device.id ? data : d)));
    } catch {
      setError('Cập nhật cho phép chạy thất bại.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Thiết Bị</h1>
          <p className="text-zinc-400 text-sm mt-1">
            Quản lý điện thoại Android kết nối qua ADB + Appium.
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            onClick={scanDevices}
            disabled={scanning}
            variant="outline"
            className="border-zinc-700 hover:bg-zinc-800 text-zinc-300 gap-2"
          >
            <RefreshCcw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} /> Tự Động Quét
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        {(['online', 'offline', 'busy'] as const).map((s) => (
          <div key={s} className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4">
            <p className="text-xs text-zinc-500 uppercase tracking-wide mb-1">{s}</p>
            <p className="text-2xl font-bold">
              {devices.filter((d) => d.status === s).length}
            </p>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="border border-zinc-800 rounded-lg overflow-hidden bg-zinc-900/50">
        <Table>
          <TableHeader>
            <TableRow className="border-zinc-800 hover:bg-transparent">
              <TableHead>Tên Thiết Bị</TableHead>
              <TableHead>UDID</TableHead>
              <TableHead>Ghi Chú</TableHead>
              <TableHead>Kết Nối</TableHead>
              <TableHead>Cho Phép Chạy</TableHead>
              <TableHead className="text-right">Hành Động</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-12 text-zinc-500">
                  <Loader2 className="w-5 h-5 animate-spin inline mr-2" />Đang tải...
                </TableCell>
              </TableRow>
            ) : devices.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-12 text-zinc-500">
                  Chưa có thiết bị nào. Cắm điện thoại vào máy tính và nhấn "Tự Động Quét".
                </TableCell>
              </TableRow>
            ) : (
              devices.map((device) => (
                <TableRow key={device.id} className="border-zinc-800">
                  <TableCell className="font-medium text-blue-400">{device.label}</TableCell>
                  <TableCell>
                    <code className="text-xs bg-zinc-800 px-2 py-1 rounded font-mono text-zinc-300">
                      {device.udid}
                    </code>
                  </TableCell>
                  <TableCell className="text-zinc-400 text-sm max-w-xs truncate">
                    {device.notes ?? '—'}
                  </TableCell>
                  <TableCell>
                    <button
                      onClick={() => toggleStatus(device)}
                      title="Click để toggle online/offline giả lập"
                      className="focus:outline-none"
                    >
                      <StatusBadge status={device.status} />
                    </button>
                  </TableCell>
                  <TableCell>
                    <button
                      onClick={() => toggleActive(device)}
                      className={`px-3 py-1 rounded-full text-xs font-medium border ${device.is_active ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' : 'bg-zinc-800 text-zinc-500 border-zinc-700 hover:bg-zinc-700'}`}
                    >
                      {device.is_active ? 'Đang Bật' : 'Tạm Dừng'}
                    </button>
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEdit(device)}
                      title="Sửa thông tin"
                    >
                      <Pencil className="w-4 h-4 text-zinc-400" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Edit Dialog */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800 text-zinc-50 max-w-md">
          <DialogHeader>
            <DialogTitle>Sửa Thông Tin Thiết Bị</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label className="text-sm text-zinc-300">Tên thiết bị *</label>
              <Input
                value={form.label}
                onChange={(e) => setForm({ ...form, label: e.target.value })}
                placeholder="VD: Samsung A53 chính"
                className="bg-zinc-950 border-zinc-700"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-zinc-300">UDID (ADB)</label>
              <Input
                value={editingDevice?.udid || ''}
                disabled
                className="bg-zinc-900/50 border-zinc-800 font-mono text-sm text-zinc-500 cursor-not-allowed"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-zinc-300">Ghi chú (tùy chọn)</label>
              <Input
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                placeholder="VD: SIM 0987..., FB account: Nam Nguyen"
                className="bg-zinc-950 border-zinc-700"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setIsOpen(false)} className="text-zinc-400">
              Hủy
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving || !form.label.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Lưu thay đổi
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
