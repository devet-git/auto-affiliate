import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { LayoutGrid, List, Check, X, Edit2 } from 'lucide-react';

interface PendingPost {
  id: number;
  title: string;
  caption: string;
  thumbnail: string;
  status: string;
}

export default function ApprovalQueue() {
  const [posts, setPosts] = useState<PendingPost[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [loading, setLoading] = useState(true);

  const [editingPost, setEditingPost] = useState<PendingPost | null>(null);
  const [editCaption, setEditCaption] = useState('');

  useEffect(() => {
    fetchQueue();
  }, []);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/approval/queue');
      setPosts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id: number, action: 'approved' | 'rejected', caption?: string) => {
    try {
      await api.put(`/approval/${id}`, { status: action, caption: caption || '' });
      setPosts(posts.filter((p) => p.id !== id));
      if (editingPost?.id === id) setEditingPost(null);
    } catch (err) {
      console.error(err);
    }
  };

  const openEditDialog = (post: PendingPost) => {
    setEditingPost(post);
    setEditCaption(post.caption);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Approval Queue</h1>
          <p className="text-muted-foreground">Review and approve AI-generated posts.</p>
        </div>
        <div className="flex gap-2">
          <Button variant={viewMode === 'grid' ? 'secondary' : 'ghost'} size="icon" onClick={() => setViewMode('grid')}>
            <LayoutGrid className="w-5 h-5" />
          </Button>
          <Button variant={viewMode === 'table' ? 'secondary' : 'ghost'} size="icon" onClick={() => setViewMode('table')}>
            <List className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-10 text-zinc-500">Loading...</div>
      ) : posts.length === 0 ? (
        <div className="text-center py-10 border border-border rounded-lg bg-card/50 backdrop-blur-sm">
          <Check className="w-12 h-12 mx-auto text-green-500 mb-4" />
          <h2 className="text-xl font-bold">All caught up!</h2>
          <p className="text-muted-foreground">No pending posts in the queue.</p>
        </div>
      ) : viewMode === 'table' ? (
        <div className="border border-border rounded-lg overflow-hidden bg-card/50 backdrop-blur-sm">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="w-24">Media</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Caption</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {posts.map((post) => (
                <TableRow key={post.id} className="border-border">
                  <TableCell>
                    <img src={post.thumbnail} alt={post.title} className="w-16 h-16 object-cover rounded" />
                  </TableCell>
                  <TableCell className="font-medium">{post.title}</TableCell>
                  <TableCell className="max-w-xs truncate text-muted-foreground">{post.caption}</TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="ghost" size="icon" onClick={() => openEditDialog(post)}>
                      <Edit2 className="w-4 h-4 text-primary" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleAction(post.id, 'approved', post.caption)}>
                      <Check className="w-4 h-4 text-green-400" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleAction(post.id, 'rejected')}>
                      <X className="w-4 h-4 text-red-400" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {posts.map((post) => (
            <Card key={post.id} className="bg-card/50 backdrop-blur-sm border-border overflow-hidden flex flex-col">
              <div className="relative aspect-video">
                <img src={post.thumbnail} alt={post.title} className="w-full h-full object-cover" />
              </div>
              <CardContent className="p-4 flex-1 flex flex-col">
                <h3 className="font-bold line-clamp-1 mb-2 text-foreground">{post.title}</h3>
                <p className="text-sm text-muted-foreground line-clamp-3 mb-4 flex-1">{post.caption}</p>
                <div className="flex gap-2 justify-end mt-auto pt-4 border-t border-border">
                  <Button variant="ghost" size="sm" onClick={() => openEditDialog(post)} className="text-primary hover:text-primary/80">
                    <Edit2 className="w-4 h-4 mr-1" /> Edit
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => handleAction(post.id, 'rejected')} className="text-red-400 hover:text-red-300">
                    <X className="w-4 h-4 mr-1" /> Reject
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => handleAction(post.id, 'approved', post.caption)} className="bg-green-500/10 text-green-400 hover:bg-green-500/20">
                    <Check className="w-4 h-4 mr-1" /> Approve
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={!!editingPost} onOpenChange={(open) => !open && setEditingPost(null)}>
        <DialogContent className="bg-background border-border text-foreground sm:max-w-xl rounded-[var(--radius)]">
          <DialogHeader>
            <DialogTitle>Edit & Approve</DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            {editingPost && (
              <div className="aspect-video w-1/2 mx-auto mb-4 rounded overflow-hidden">
                <img src={editingPost.thumbnail} className="object-cover w-full h-full" alt="Preview" />
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-medium">Caption</label>
              <Textarea
                value={editCaption}
                onChange={(e) => setEditCaption(e.target.value)}
                rows={6}
                className="bg-input border-border font-mono text-sm"
              />
            </div>
          </div>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="ghost" onClick={() => setEditingPost(null)}>Cancel</Button>
            <Button onClick={() => handleAction(editingPost!.id, 'approved', editCaption)} className="bg-green-600 hover:bg-green-700">
              Approve & Post
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
