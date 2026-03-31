import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import {
  RefreshCw, Plus, Trash2, Users, MessagesSquare, CheckCircle2, XCircle, Clock,
  Play, Upload, AlertCircle,
} from 'lucide-react';

const API = 'http://localhost:8000/api/v1/target-groups';

type PostStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

interface TargetGroup {
  id: number;
  url: string;
  name: string;
  keywords: string[];
  is_active: boolean;
  created_at: string | null;
}

interface ScrapedPost {
  id: number;
  original_url: string;
  content: string;
  author: string;
  comments_count: number;
  reactions_count: number;
  target_group_id: number;
  status: PostStatus;
  created_at: string | null;
}

function PostStatusBadge({ status }: { status: PostStatus }) {
  const config: Record<PostStatus, { label: string; className: string; icon: React.ReactNode }> = {
    PENDING: {
      label: 'Pending',
      className: 'bg-yellow-500/10 text-yellow-500',
      icon: <Clock className="w-3 h-3" />,
    },
    APPROVED: {
      label: 'Approved',
      className: 'bg-green-500/10 text-green-500',
      icon: <CheckCircle2 className="w-3 h-3" />,
    },
    REJECTED: {
      label: 'Rejected',
      className: 'bg-destructive/10 text-destructive',
      icon: <XCircle className="w-3 h-3" />,
    },
  };
  const { label, className, icon } = config[status];
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${className}`}>
      {icon}
      {label}
    </span>
  );
}

type TabKey = 'groups' | 'posts';

export default function TargetGroups() {
  const token = useAuthStore((state) => state.token);
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  const [activeTab, setActiveTab] = useState<TabKey>('groups');

  // Groups state
  const [groups, setGroups] = useState<TargetGroup[]>([]);
  const [groupsLoading, setGroupsLoading] = useState(false);
  const [scrapingGroupId, setScrapingGroupId] = useState<number | null>(null);
  const [scrapeMsg, setScrapeMsg] = useState<string | null>(null);

  // "Add Group" dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [newName, setNewName] = useState('');
  const [newKeywords, setNewKeywords] = useState('');
  const [adding, setAdding] = useState(false);

  // Session upload state
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [sessionStatus, setSessionStatus] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  // Posts state
  const [posts, setPosts] = useState<ScrapedPost[]>([]);
  const [postsLoading, setPostsLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('PENDING');

  // -------- Fetch Groups --------
  const fetchGroups = useCallback(async () => {
    setGroupsLoading(true);
    try {
      const res = await fetch(`${API}/`, { headers: { Authorization: `Bearer ${token}` } });
      const json = await res.json();
      setGroups(Array.isArray(json) ? json : []);
    } catch (e) {
      console.error(e);
    } finally {
      setGroupsLoading(false);
    }
  }, [token]);

  // -------- Fetch Posts --------
  const fetchPosts = useCallback(async () => {
    setPostsLoading(true);
    try {
      let url = `${API}/posts/?limit=200`;
      if (statusFilter) url += `&status=${statusFilter}`;
      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      const json = await res.json();
      setPosts(Array.isArray(json) ? json : []);
    } catch (e) {
      console.error(e);
    } finally {
      setPostsLoading(false);
    }
  }, [token, statusFilter]);

  useEffect(() => {
    fetchGroups();
  }, [fetchGroups]);

  useEffect(() => {
    if (activeTab === 'posts') fetchPosts();
  }, [activeTab, fetchPosts]);

  // -------- Add Group --------
  const handleAddGroup = async () => {
    if (!newUrl.trim()) return;
    setAdding(true);
    try {
      const keywords = newKeywords
        .split(',')
        .map((k) => k.trim())
        .filter(Boolean);
      await fetch(`${API}/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ url: newUrl.trim(), name: newName.trim(), keywords }),
      });
      setDialogOpen(false);
      setNewUrl('');
      setNewName('');
      setNewKeywords('');
      await fetchGroups();
    } catch (e) {
      console.error(e);
    } finally {
      setAdding(false);
    }
  };

  // -------- Delete Group --------
  const handleDeleteGroup = async (id: number) => {
    if (!confirm('Remove this target group?')) return;
    try {
      await fetch(`${API}/${id}`, { method: 'DELETE', headers });
      await fetchGroups();
    } catch (e) {
      console.error(e);
    }
  };

  // -------- Scrape Now --------
  const handleScrapeNow = async (group: TargetGroup) => {
    setScrapingGroupId(group.id);
    setScrapeMsg(null);
    try {
      const res = await fetch(`${API}/${group.id}/scrape`, {
        method: 'POST',
        headers,
      });
      const json = await res.json();
      if (res.ok) {
        setScrapeMsg(`✓ Scrape dispatched for "${group.name || group.url}". Check the Posts tab in ~10-30s.`);
      } else {
        setScrapeMsg(`✗ ${json.detail || 'Error dispatching scrape'}`);
      }
    } catch (e) {
      setScrapeMsg('✗ Network error');
    } finally {
      setScrapingGroupId(null);
      setTimeout(() => setScrapeMsg(null), 8000);
    }
  };

  // -------- Upload FB Session --------
  const handleSessionUpload = async (file: File) => {
    setUploading(true);
    setSessionStatus(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API}/session`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const json = await res.json();
      setSessionStatus(res.ok ? `✓ ${json.message}` : `✗ ${json.detail}`);
    } catch (e) {
      setSessionStatus('✗ Upload failed');
    } finally {
      setUploading(false);
    }
  };

  // -------- Approve / Reject Post --------
  const handlePostStatus = async (id: number, status: PostStatus) => {
    try {
      const res = await fetch(`${API}/posts/${id}/status`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify({ status }),
      });
      if (res.ok) {
        setPosts((prev) =>
          prev.map((p) => (p.id === id ? { ...p, status } : p))
        );
      }
    } catch (e) {
      console.error(e);
    }
  };

  const tabClass = (key: TabKey) =>
    `px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
      activeTab === key
        ? 'border-primary text-primary'
        : 'border-transparent text-muted-foreground hover:text-foreground'
    }`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Users className="text-primary w-6 h-6" />
          Target Groups
        </h2>
        <p className="text-muted-foreground">
          Manage Facebook group targets and review scraped posts
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-border flex gap-0">
        <button id="tab-groups" className={tabClass('groups')} onClick={() => setActiveTab('groups')}>
          <span className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Configured Groups
            {groups.length > 0 && (
              <span className="rounded-full bg-primary/10 text-primary px-1.5 py-0.5 text-xs">
                {groups.length}
              </span>
            )}
          </span>
        </button>
        <button id="tab-posts" className={tabClass('posts')} onClick={() => setActiveTab('posts')}>
          <span className="flex items-center gap-2">
            <MessagesSquare className="w-4 h-4" />
            Scraped Posts
          </span>
        </button>
      </div>

      {/* === GROUPS TAB === */}
      {activeTab === 'groups' && (
        <div className="space-y-4">
          {/* Facebook Session Upload Card */}
          <Card className="bg-background/50 border-border border-dashed">
            <CardContent className="pt-4 pb-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <div className="flex-1">
                  <p className="text-sm font-medium flex items-center gap-2">
                    <Upload className="w-4 h-4 text-primary" />
                    Upload Facebook Session Cookies
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Required to bypass the Facebook login wall. Export from{' '}
                    <strong>Cookie-Editor</strong> extension while logged into facebook.com
                    (Export All → JSON), then upload here.
                  </p>
                  {sessionStatus && (
                    <p className={`text-xs mt-1 ${sessionStatus.startsWith('✓') ? 'text-green-500' : 'text-destructive'}`}>
                      {sessionStatus}
                    </p>
                  )}
                </div>
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".json,application/json"
                    className="hidden"
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      if (f) handleSessionUpload(f);
                      e.target.value = '';
                    }}
                  />
                  <Button
                    id="upload-session-btn"
                    variant="outline"
                    size="sm"
                    disabled={uploading}
                    onClick={() => fileInputRef.current?.click()}
                    className="gap-2 whitespace-nowrap"
                  >
                    <Upload className="w-4 h-4" />
                    {uploading ? 'Uploading...' : 'Upload cookies.json'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Scrape feedback banner */}
          {scrapeMsg && (
            <div className={`flex items-center gap-2 text-sm rounded-md px-4 py-2 border ${
              scrapeMsg.startsWith('✓')
                ? 'bg-green-500/10 border-green-500/30 text-green-500'
                : 'bg-destructive/10 border-destructive/30 text-destructive'
            }`}>
              <AlertCircle className="w-4 h-4 shrink-0" />
              {scrapeMsg}
            </div>
          )}

          <Card className="bg-background/50 border-border">
            <CardHeader>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <CardTitle className="text-lg">Target Groups</CardTitle>
                  <CardDescription>
                    {groups.length === 0
                      ? 'No target groups configured'
                      : `${groups.length} group(s) configured`}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    id="refresh-groups-btn"
                    variant="outline"
                    size="sm"
                    onClick={fetchGroups}
                    disabled={groupsLoading}
                    className="gap-2"
                  >
                    <RefreshCw className={`w-4 h-4 ${groupsLoading ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                  <Button
                    id="add-group-btn"
                    size="sm"
                    onClick={() => setDialogOpen(true)}
                    className="gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Add Group
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border border-border">
                <Table>
                  <TableHeader className="bg-muted/50">
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Group URL</TableHead>
                      <TableHead>Keywords</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Added</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {groups.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="h-32 text-center text-muted-foreground">
                          {groupsLoading ? (
                            'Loading...'
                          ) : (
                            <div className="space-y-1">
                              <p className="font-medium">No target groups configured</p>
                              <p className="text-sm">
                                Add a Facebook group URL and target keywords to begin scraping.
                              </p>
                            </div>
                          )}
                        </TableCell>
                      </TableRow>
                    ) : (
                      groups.map((g) => (
                        <TableRow key={g.id} className="hover:bg-muted/30">
                          <TableCell className="font-medium">{g.name || '—'}</TableCell>
                          <TableCell className="max-w-xs">
                            <a
                              href={g.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-primary underline underline-offset-2 truncate block"
                              title={g.url}
                            >
                              {g.url}
                            </a>
                          </TableCell>
                          <TableCell>
                            <div className="flex flex-wrap gap-1">
                              {g.keywords.length === 0 ? (
                                <span className="text-muted-foreground text-xs">All posts</span>
                              ) : (
                                g.keywords.map((kw) => (
                                  <span
                                    key={kw}
                                    className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded"
                                  >
                                    {kw}
                                  </span>
                                ))
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <span
                              className={`text-xs rounded-full px-2 py-1 ${
                                g.is_active
                                  ? 'bg-green-500/10 text-green-500'
                                  : 'bg-muted text-muted-foreground'
                              }`}
                            >
                              {g.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                            {g.created_at ? new Date(g.created_at).toLocaleDateString() : '—'}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-1">
                              <Button
                                id={`scrape-group-${g.id}`}
                                variant="outline"
                                size="sm"
                                disabled={scrapingGroupId === g.id}
                                onClick={() => handleScrapeNow(g)}
                                className="gap-1 text-primary border-primary/30 hover:bg-primary/10"
                                title="Scrape this group now"
                              >
                                <Play className={`w-3.5 h-3.5 ${scrapingGroupId === g.id ? 'animate-pulse' : ''}`} />
                                {scrapingGroupId === g.id ? 'Scraping...' : 'Scrape Now'}
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteGroup(g.id)}
                                className="text-muted-foreground hover:text-destructive"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* === POSTS TAB === */}
      {activeTab === 'posts' && (
        <Card className="bg-background/50 border-border">
          <CardHeader>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <CardTitle className="text-lg">Scraped Posts</CardTitle>
                <CardDescription>
                  {posts.length} post(s) found
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <select
                  id="post-status-filter"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="flex h-9 items-center rounded-md border border-input bg-background px-3 text-sm"
                >
                  <option value="">All Statuses</option>
                  <option value="PENDING">Pending</option>
                  <option value="APPROVED">Approved</option>
                  <option value="REJECTED">Rejected</option>
                </select>
                <Button
                  id="refresh-posts-btn"
                  variant="outline"
                  size="sm"
                  onClick={fetchPosts}
                  disabled={postsLoading}
                  className="gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${postsLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border border-border">
              <Table>
                <TableHeader className="bg-muted/50">
                  <TableRow>
                    <TableHead>Author</TableHead>
                    <TableHead>Content</TableHead>
                    <TableHead className="w-24">Comments</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Scraped</TableHead>
                    <TableHead>Link</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {posts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">
                        {postsLoading ? (
                          'Loading...'
                        ) : statusFilter === 'PENDING' ? (
                          <div className="space-y-1">
                            <p className="font-medium">No pending posts</p>
                            <p className="text-sm">
                              Go to Configured Groups → upload Facebook cookies → click "Scrape Now".
                            </p>
                          </div>
                        ) : (
                          'No posts found for the selected filter.'
                        )}
                      </TableCell>
                    </TableRow>
                  ) : (
                    posts.map((p) => (
                      <TableRow key={p.id} className="hover:bg-muted/30">
                        <TableCell className="font-medium whitespace-nowrap text-sm">
                          {p.author || '—'}
                        </TableCell>
                        <TableCell className="max-w-xs">
                          <p className="truncate text-sm text-muted-foreground" title={p.content}>
                            {p.content || '—'}
                          </p>
                        </TableCell>
                        <TableCell className="text-sm text-center">
                          {p.comments_count > 0 ? p.comments_count : '—'}
                        </TableCell>
                        <TableCell>
                          <PostStatusBadge status={p.status} />
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                          {p.created_at ? new Date(p.created_at).toLocaleDateString() : '—'}
                        </TableCell>
                        <TableCell>
                          <a
                            href={p.original_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-primary underline underline-offset-2"
                          >
                            View
                          </a>
                        </TableCell>
                        <TableCell className="text-right">
                          {p.status === 'PENDING' && (
                            <div className="flex justify-end gap-2">
                              <Button
                                id={`approve-post-${p.id}`}
                                size="sm"
                                variant="outline"
                                className="text-green-500 border-green-500/30 hover:bg-green-500/10 gap-1"
                                onClick={() => handlePostStatus(p.id, 'APPROVED')}
                              >
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                Approve
                              </Button>
                              <Button
                                id={`reject-post-${p.id}`}
                                size="sm"
                                variant="outline"
                                className="text-destructive border-destructive/30 hover:bg-destructive/10 gap-1"
                                onClick={() => handlePostStatus(p.id, 'REJECTED')}
                              >
                                <XCircle className="w-3.5 h-3.5" />
                                Reject
                              </Button>
                            </div>
                          )}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add Group Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Target Group</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1">
              <label className="text-sm font-medium">Facebook Group URL *</label>
              <Input
                id="new-group-url"
                placeholder="https://www.facebook.com/groups/..."
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">Group Name</label>
              <Input
                id="new-group-name"
                placeholder="e.g. Shopee Deals Vietnam"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">Keywords (comma-separated)</label>
              <Input
                id="new-group-keywords"
                placeholder="e.g. giảm giá, sale, voucher"
                value={newKeywords}
                onChange={(e) => setNewKeywords(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Only posts containing these keywords will be scraped. Leave empty to capture all posts.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              id="confirm-add-group-btn"
              onClick={handleAddGroup}
              disabled={adding || !newUrl.trim()}
            >
              {adding ? 'Adding...' : 'Add Group'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
