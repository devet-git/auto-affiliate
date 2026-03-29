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
import {
  Plus, Trash2, Settings, Play, CheckCircle2, XCircle, Clock, Loader2,
} from 'lucide-react';

interface Campaign {
  id: string;
  name: string;
  status: string;
  created_at: string;
  shopee_keyword: string | null;
  affiliate_link: string | null;
  comment_template: string | null;
  facebook_post_urls: string | null;
  target_device_udid: string | null;
  comment_delay_seconds: number;
}

interface Device {
  id: string;
  label: string;
  udid: string;
  status: string;
}

const STATUS_BADGE: Record<string, string> = {
  draft:    'bg-zinc-500/15 text-zinc-400 border border-zinc-600/30',
  active:   'bg-green-500/15 text-green-400 border border-green-500/30',
  paused:   'bg-yellow-500/15 text-yellow-400 border border-yellow-500/30',
  archived: 'bg-red-500/15 text-red-400 border border-red-500/30',
};

type TabKey = 'info' | 'automation';

function parsePostUrls(raw: string | null): string {
  if (!raw) return '';
  try {
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr.join('\n') : raw;
  } catch {
    return raw;
  }
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);

  // Create dialog
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newCampaignName, setNewCampaignName] = useState('');
  const [creating, setCreating] = useState(false);

  // Edit/Config dialog
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>('info');
  const [saving, setSaving] = useState(false);

  // Basic info fields
  const [editName, setEditName] = useState('');
  const [editStatus, setEditStatus] = useState('');

  // Automation config fields
  const [autoKeyword, setAutoKeyword] = useState('');
  const [autoLink, setAutoLink] = useState('');
  const [autoTemplate, setAutoTemplate] = useState('');
  const [autoPostUrls, setAutoPostUrls] = useState('');
  const [autoDevice, setAutoDevice] = useState('');
  const [autoDelay, setAutoDelay] = useState('30');

  // Run task state
  const [runningCampaignId, setRunningCampaignId] = useState<string | null>(null);
  const [taskResults, setTaskResults] = useState<Record<string, { task_id: string; status: string }>>({});

  useEffect(() => {
    Promise.all([fetchCampaigns(), fetchDevices()]);
  }, []);

  const fetchCampaigns = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/campaigns');
      setCampaigns(data);
    } finally {
      setLoading(false);
    }
  };

  const fetchDevices = async () => {
    try {
      const { data } = await api.get('/devices');
      setDevices(data);
    } catch { /* optional */ }
  };

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleCreate = async () => {
    if (!newCampaignName.trim()) return;
    setCreating(true);
    try {
      const { data } = await api.post('/campaigns', { name: newCampaignName.trim(), status: 'draft' });
      setCampaigns([...campaigns, data]);
      setIsCreateOpen(false);
      setNewCampaignName('');
    } finally {
      setCreating(false);
    }
  };

  const openEdit = (campaign: Campaign) => {
    setEditingCampaign(campaign);
    setActiveTab('info');

    setEditName(campaign.name);
    setEditStatus(campaign.status);

    setAutoKeyword(campaign.shopee_keyword ?? '');
    setAutoLink(campaign.affiliate_link ?? '');
    setAutoTemplate(campaign.comment_template ?? '');
    setAutoPostUrls(parsePostUrls(campaign.facebook_post_urls));
    setAutoDevice(campaign.target_device_udid ?? '');
    setAutoDelay(String(campaign.comment_delay_seconds ?? 30));

    setIsEditOpen(true);
  };

  const handleSaveInfo = async () => {
    if (!editingCampaign) return;
    setSaving(true);
    try {
      const { data } = await api.put(`/campaigns/${editingCampaign.id}`, {
        name: editName,
        status: editStatus,
      });
      setCampaigns(campaigns.map((c) => (c.id === editingCampaign.id ? data : c)));
      setIsEditOpen(false);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAutomation = async () => {
    if (!editingCampaign) return;
    setSaving(true);
    try {
      const postUrlsArray = autoPostUrls
        .split('\n')
        .map((u) => u.trim())
        .filter(Boolean);

      const { data } = await api.put(`/campaigns/${editingCampaign.id}/automation`, {
        shopee_keyword: autoKeyword || null,
        affiliate_link: autoLink || null,
        comment_template: autoTemplate || null,
        facebook_post_urls: postUrlsArray.length > 0 ? postUrlsArray : null,
        target_device_udid: autoDevice || null,
        comment_delay_seconds: parseFloat(autoDelay) || 30,
      });
      setCampaigns(campaigns.map((c) => (c.id === editingCampaign.id ? data : c)));
      setIsEditOpen(false);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Xóa campaign này?')) return;
    await api.delete(`/campaigns/${id}`);
    setCampaigns(campaigns.filter((c) => c.id !== id));
  };

  const handleRunComment = async (campaign: Campaign) => {
    setRunningCampaignId(campaign.id);
    try {
      const { data } = await api.post(`/campaigns/${campaign.id}/run-comment`, {});
      setTaskResults((prev) => ({
        ...prev,
        [campaign.id]: { task_id: data.task_id, status: 'queued' },
      }));
      alert(`✅ Đã enqueue!\nTask ID: ${data.task_id}\nSố post: ${data.post_count}`);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      alert(`❌ Lỗi: ${axiosErr?.response?.data?.detail ?? 'Không thể chạy task'}`);
    } finally {
      setRunningCampaignId(null);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  const hasAutomationConfig = (c: Campaign) =>
    !!(c.facebook_post_urls && c.comment_template);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Campaigns</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Quản lý và điều khiển chiến dịch affiliate + seeding.
          </p>
        </div>
        <Button
          onClick={() => setIsCreateOpen(true)}
          className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2"
        >
          <Plus className="w-4 h-4" /> New Campaign
        </Button>
      </div>

      {/* Campaign Table */}
      <div className="border border-border rounded-lg overflow-hidden bg-card/50 backdrop-blur-sm">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead>Tên Campaign</TableHead>
              <TableHead>Trạng Thái</TableHead>
              <TableHead>Automation</TableHead>
              <TableHead>Ngày tạo</TableHead>
              <TableHead className="text-right">Hành Động</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-12 text-zinc-500">
                  <Loader2 className="w-5 h-5 animate-spin inline mr-2" />Đang tải...
                </TableCell>
              </TableRow>
            ) : campaigns.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-12 text-zinc-500">
                  Chưa có campaign. Tạo mới để bắt đầu.
                </TableCell>
              </TableRow>
            ) : (
              campaigns.map((c) => (
                <TableRow key={c.id} className="border-border">
                  <TableCell className="font-medium text-primary">{c.name}</TableCell>
                  <TableCell>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_BADGE[c.status] ?? STATUS_BADGE.draft}`}>
                      {c.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    {hasAutomationConfig(c) ? (
                      <span className="inline-flex items-center gap-1.5 text-xs text-green-400">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Đã cấu hình
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-xs text-zinc-500">
                        <XCircle className="w-3.5 h-3.5" /> Chưa cấu hình
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="text-zinc-400 text-sm">
                    {new Date(c.created_at).toLocaleDateString('vi-VN')}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      {/* Run Comment */}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleRunComment(c)}
                        disabled={runningCampaignId === c.id || !hasAutomationConfig(c)}
                        title={hasAutomationConfig(c) ? 'Chạy comment seeding' : 'Cần cấu hình automation trước'}
                        className="text-green-400 hover:text-green-300 hover:bg-green-500/10"
                      >
                        {runningCampaignId === c.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Play className="w-4 h-4" />
                        )}
                      </Button>

                      {/* Task result indicator */}
                      {taskResults[c.id] && (
                        <span title={`Task: ${taskResults[c.id].task_id}`}>
                          <Clock className="w-4 h-4 text-yellow-400" />
                        </span>
                      )}

                      {/* Config */}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => openEdit(c)}
                        title="Cấu hình campaign"
                      >
                        <Settings className="w-4 h-4 text-muted-foreground" />
                      </Button>

                      {/* Delete */}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(c.id)}
                        title="Xóa campaign"
                      >
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* ── Create Dialog ── */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="bg-background border-border text-foreground max-w-sm rounded-[var(--radius)]">
          <DialogHeader>
            <DialogTitle>Tạo Campaign Mới</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label className="text-sm text-zinc-300">Tên campaign *</label>
              <Input
                value={newCampaignName}
                onChange={(e) => setNewCampaignName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
                placeholder="VD: Áo thun nam Q3/2024"
                className="bg-background border-input"
                autoFocus
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setIsCreateOpen(false)} className="text-zinc-400">
              Hủy
            </Button>
            <Button
              onClick={handleCreate}
              disabled={creating || !newCampaignName.trim()}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {creating && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Tạo
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Edit / Config Dialog ── */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="bg-background border-border text-foreground max-w-xl rounded-[var(--radius)]">
          <DialogHeader>
            <DialogTitle>
              {editingCampaign?.name}
            </DialogTitle>
          </DialogHeader>

          {/* Tabs */}
          <div className="flex border-b border-border -mx-6 px-6 mb-4">
            {(['info', 'automation'] as TabKey[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-2 px-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                {tab === 'info' ? '📋 Thông Tin' : '🤖 Automation'}
              </button>
            ))}
          </div>

          {/* Tab: Info */}
          {activeTab === 'info' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm text-zinc-300">Tên campaign</label>
                <Input
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="bg-zinc-950 border-zinc-700"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm text-zinc-300">Trạng thái</label>
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {['draft', 'active', 'paused', 'archived'].map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <DialogFooter>
                <Button variant="ghost" onClick={() => setIsEditOpen(false)} className="text-zinc-400">
                  Hủy
                </Button>
                <Button
                  onClick={handleSaveInfo}
                  disabled={saving}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Lưu
                </Button>
              </DialogFooter>
            </div>
          )}

          {/* Tab: Automation */}
          {activeTab === 'automation' && (
            <div className="space-y-4 overflow-y-auto max-h-[60vh] pr-1">
              <div className="space-y-2">
                <label className="text-sm text-zinc-300">Từ khoá Shopee</label>
                <Input
                  value={autoKeyword}
                  onChange={(e) => setAutoKeyword(e.target.value)}
                  placeholder="VD: áo thun nam"
                  className="bg-zinc-950 border-zinc-700"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm text-zinc-300">Link Affiliate *</label>
                <Input
                  value={autoLink}
                  onChange={(e) => setAutoLink(e.target.value)}
                  placeholder="https://shope.ee/..."
                  className="bg-zinc-950 border-zinc-700 font-mono text-sm"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm text-zinc-300">
                  Template Comment *
                  <span className="text-zinc-600 font-normal ml-2">
                    dùng <code className="bg-zinc-800 px-1 rounded">{'{{affiliate_link}}'}</code> để nhúng link
                  </span>
                </label>
                <textarea
                  value={autoTemplate}
                  onChange={(e) => setAutoTemplate(e.target.value)}
                  placeholder={'Sản phẩm chất lượng, mình dùng rồi! Link mua: {affiliate_link}'}
                  rows={3}
                  className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-50 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm text-zinc-300">
                  Danh sách URL bài Facebook *
                  <span className="text-zinc-600 font-normal ml-2">(mỗi URL một dòng)</span>
                </label>
                <textarea
                  value={autoPostUrls}
                  onChange={(e) => setAutoPostUrls(e.target.value)}
                  placeholder={"https://www.facebook.com/permalink.php?story_fbid=123\nhttps://www.facebook.com/groups/xyz/posts/456"}
                  rows={5}
                  className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-50 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-mono"
                />
                <p className="text-xs text-zinc-600">
                  {autoPostUrls.split('\n').filter((u) => u.trim()).length} URL đã nhập
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm text-zinc-300">Thiết bị mặc định</label>
                  <select
                    value={autoDevice}
                    onChange={(e) => setAutoDevice(e.target.value)}
                    className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">— Từ .env —</option>
                    {devices.map((d) => (
                      <option key={d.id} value={d.udid}>
                        {d.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm text-zinc-300">Delay giữa comment (giây)</label>
                  <Input
                    type="number"
                    value={autoDelay}
                    onChange={(e) => setAutoDelay(e.target.value)}
                    min="5"
                    max="300"
                    className="bg-zinc-950 border-zinc-700"
                  />
                </div>
              </div>

              <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-3 text-xs text-zinc-500">
                <span className="text-green-400 font-medium">Preview comment:</span>{' '}
                {autoTemplate && autoLink
                  ? autoTemplate.replace('{affiliate_link}', autoLink)
                  : 'Điền template và link affiliate để xem preview'}
              </div>

              <DialogFooter>
                <Button variant="ghost" onClick={() => setIsEditOpen(false)} className="text-zinc-400">
                  Hủy
                </Button>
                <Button
                  onClick={handleSaveAutomation}
                  disabled={saving}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Lưu Automation Config
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
