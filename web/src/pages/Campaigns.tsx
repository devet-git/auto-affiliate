import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger } from '@/components/ui/dialog';
import { Plus, Trash2, Settings } from 'lucide-react';

interface Campaign {
  id: string;
  name: string;
  status: string;
  created_at: string;
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCampaignName, setNewCampaignName] = useState('');

  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editCampaignName, setEditCampaignName] = useState('');
  const [editCampaignStatus, setEditCampaignStatus] = useState('');

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/campaigns');
      setCampaigns(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newCampaignName) return;
    try {
      const { data } = await api.post('/campaigns', { name: newCampaignName, status: 'active' });
      setCampaigns([...campaigns, data]);
      setIsModalOpen(false);
      setNewCampaignName('');
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/campaigns/${id}`);
      setCampaigns(campaigns.filter((c) => c.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleEditOpen = (campaign: Campaign) => {
    setEditingCampaign(campaign);
    setEditCampaignName(campaign.name);
    setEditCampaignStatus(campaign.status);
    setIsEditModalOpen(true);
  };

  const handleEditSave = async () => {
    if (!editingCampaign) return;
    try {
      const { data } = await api.put(`/campaigns/${editingCampaign.id}`, { name: editCampaignName, status: editCampaignStatus });
      setCampaigns(campaigns.map((c) => (c.id === editingCampaign.id ? data : c)));
      setIsEditModalOpen(false);
      setEditingCampaign(null);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Campaigns</h1>
          <p className="text-zinc-400">Manage your data scraping and seeding campaigns.</p>
        </div>
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogTrigger className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 bg-blue-600 text-white shadow hover:bg-blue-700 h-9 px-4 py-2">
            <Plus className="w-4 h-4 mr-2" /> New Campaign
          </DialogTrigger>
          <DialogContent className="bg-zinc-900 border-zinc-800 text-zinc-50">
            <DialogHeader>
              <DialogTitle>Create New Campaign</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm">Campaign Name</label>
                <Input
                  value={newCampaignName}
                  onChange={(e) => setNewCampaignName(e.target.value)}
                  placeholder="e.g. Trendy Tech Gadgets"
                  className="bg-zinc-950 border-zinc-800"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={!newCampaignName} className="bg-blue-600 hover:bg-blue-700 text-white">
                Create
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800 text-zinc-50">
          <DialogHeader>
            <DialogTitle>Configure Campaign</DialogTitle>
          </DialogHeader>
          {editingCampaign && (
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm">Campaign Name</label>
                <Input
                  value={editCampaignName}
                  onChange={(e) => setEditCampaignName(e.target.value)}
                  className="bg-zinc-950 border-zinc-800"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm">Status</label>
                <select
                  value={editCampaignStatus}
                  onChange={(e) => setEditCampaignStatus(e.target.value)}
                  className="flex h-10 w-full items-center justify-between rounded-md border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="paused">Paused</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="ghost" onClick={() => setIsEditModalOpen(false)}>Cancel</Button>
            <Button onClick={handleEditSave} disabled={!editCampaignName} className="bg-blue-600 hover:bg-blue-700 text-white">
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <div className="border border-zinc-800 rounded-lg overflow-hidden bg-zinc-900/50">
        <Table>
          <TableHeader>
            <TableRow className="border-zinc-800 hover:bg-transparent">
              <TableHead>Campaign Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-10 text-zinc-500">Loading...</TableCell>
              </TableRow>
            ) : campaigns.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-10 text-zinc-500">
                  No campaigns found. Create one to get started.
                </TableCell>
              </TableRow>
            ) : (
              campaigns.map((c) => (
                <TableRow key={c.id} className="border-zinc-800">
                  <TableCell className="font-medium text-blue-400">{c.name}</TableCell>
                  <TableCell>
                    <span className="px-2 py-1 rounded text-xs bg-green-500/10 text-green-400">
                      {c.status}
                    </span>
                  </TableCell>
                  <TableCell className="text-zinc-400">{new Date(c.created_at).toLocaleDateString()}</TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="ghost" size="icon" onClick={() => handleEditOpen(c)}>
                      <Settings className="w-4 h-4 text-zinc-400" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(c.id)}>
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
