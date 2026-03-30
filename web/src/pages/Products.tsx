import { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { RefreshCw, Package, Plus, Trash2, Settings2, ShoppingBag } from 'lucide-react';

const API = 'http://localhost:8000/api/v1/crawler/shopee';

type ProductStatus = 'PENDING' | 'CONVERTED' | 'FAILED';
type SourceType = 'KEYWORD' | 'SHOP_URL';

interface Product {
  id: number;
  title: string;
  price: string | null;
  original_url: string;
  affiliate_url: string | null;
  image_urls: string[];
  status: ProductStatus;
  keyword: string | null;
  created_at: string | null;
}

interface CrawlerSource {
  id: number;
  source_type: SourceType;
  value: string;
  is_active: boolean;
}

interface CrawlerConfig {
  id: number;
  frequency_hours: number;
  next_run_time: string | null;
}

function StatusBadge({ status }: { status: ProductStatus }) {
  const styles: Record<ProductStatus, string> = {
    PENDING: 'bg-yellow-500/10 text-yellow-500',
    CONVERTED: 'bg-green-500/10 text-green-500',
    FAILED: 'bg-destructive/10 text-destructive',
  };
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${styles[status]}`}>
      {status}
    </span>
  );
}

export default function Products() {
  const token = useAuthStore((state) => state.token);

  // Products state
  const [products, setProducts] = useState<Product[]>([]);
  const [productLoading, setProductLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [keywordFilter, setKeywordFilter] = useState('');

  // Sources state
  const [sources, setSources] = useState<CrawlerSource[]>([]);
  const [newSourceType, setNewSourceType] = useState<SourceType>('KEYWORD');
  const [newSourceValue, setNewSourceValue] = useState('');
  const [sourcesLoading, setSourcesLoading] = useState(false);

  // Config state
  const [config, setConfig] = useState<CrawlerConfig | null>(null);
  const [frequencyInput, setFrequencyInput] = useState('24');

  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  // -------- Fetch Products --------
  const fetchProducts = useCallback(async () => {
    setProductLoading(true);
    try {
      let url = `${API}/products?limit=100`;
      if (statusFilter) url += `&status=${statusFilter}`;
      if (keywordFilter) url += `&keyword=${encodeURIComponent(keywordFilter)}`;
      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      const json = await res.json();
      setProducts(Array.isArray(json) ? json : []);
    } catch (e) {
      console.error(e);
    } finally {
      setProductLoading(false);
    }
  }, [token, statusFilter, keywordFilter]);

  // -------- Fetch Sources --------
  const fetchSources = useCallback(async () => {
    try {
      const res = await fetch(`${API}/sources`, { headers: { Authorization: `Bearer ${token}` } });
      const json = await res.json();
      setSources(Array.isArray(json) ? json : []);
    } catch (e) {
      console.error(e);
    }
  }, [token]);

  // -------- Fetch Config --------
  const fetchConfig = useCallback(async () => {
    try {
      const res = await fetch(`${API}/config`, { headers: { Authorization: `Bearer ${token}` } });
      const json: CrawlerConfig = await res.json();
      setConfig(json);
      setFrequencyInput(String(json.frequency_hours));
    } catch (e) {
      console.error(e);
    }
  }, [token]);

  useEffect(() => {
    fetchProducts();
    fetchSources();
    fetchConfig();
  }, [fetchProducts, fetchSources, fetchConfig]);

  // -------- Add Source --------
  const addSource = async () => {
    if (!newSourceValue.trim()) return;
    setSourcesLoading(true);
    try {
      await fetch(`${API}/sources`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ source_type: newSourceType, value: newSourceValue.trim() }),
      });
      setNewSourceValue('');
      await fetchSources();
    } catch (e) {
      console.error(e);
    } finally {
      setSourcesLoading(false);
    }
  };

  // -------- Delete Source --------
  const deleteSource = async (id: number) => {
    if (!confirm('Remove this source?')) return;
    try {
      await fetch(`${API}/sources/${id}`, { method: 'DELETE', headers });
      await fetchSources();
    } catch (e) {
      console.error(e);
    }
  };

  // -------- Update Config --------
  const saveConfig = async () => {
    const hours = parseInt(frequencyInput, 10);
    if (isNaN(hours) || hours < 1) return alert('Frequency must be at least 1 hour');
    try {
      const res = await fetch(`${API}/config`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify({ frequency_hours: hours }),
      });
      const json: CrawlerConfig = await res.json();
      setConfig(json);
      alert(`Crawler frequency updated to every ${hours} hour(s)`);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <ShoppingBag className="text-primary w-6 h-6" />
          Shopee Products
        </h2>
        <p className="text-muted-foreground">Manage crawler sources and browse scraped product catalog</p>
      </div>

      {/* Crawler Config + Sources */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Config Card */}
        <Card className="bg-background/50 border-border">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Settings2 className="w-4 h-4 text-primary" />
              Crawl Schedule
            </CardTitle>
            <CardDescription>
              {config?.next_run_time
                ? `Next run: ${new Date(config.next_run_time).toLocaleString()}`
                : 'First run will be dispatched on next scheduler tick'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium whitespace-nowrap">Every</label>
              <Input
                id="frequency-input"
                type="number"
                min={1}
                value={frequencyInput}
                onChange={(e) => setFrequencyInput(e.target.value)}
                className="w-24 bg-background"
              />
              <label className="text-sm font-medium whitespace-nowrap">hour(s)</label>
              <Button variant="secondary" onClick={saveConfig} size="sm">Save</Button>
            </div>
          </CardContent>
        </Card>

        {/* Sources Card */}
        <Card className="bg-background/50 border-border">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Package className="w-4 h-4 text-primary" />
              Crawler Sources ({sources.length})
            </CardTitle>
            <CardDescription>Keywords and shop URLs to scrape</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Add source */}
            <div className="flex gap-2">
              <select
                id="source-type-select"
                value={newSourceType}
                onChange={(e) => setNewSourceType(e.target.value as SourceType)}
                className="flex h-10 items-center rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="KEYWORD">Keyword</option>
                <option value="SHOP_URL">Shop URL</option>
              </select>
              <Input
                id="source-value-input"
                placeholder={newSourceType === 'KEYWORD' ? 'áo thun nam' : 'https://shopee.vn/...'}
                value={newSourceValue}
                onChange={(e) => setNewSourceValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addSource()}
                className="flex-1 bg-background"
              />
              <Button onClick={addSource} disabled={sourcesLoading || !newSourceValue.trim()} size="sm" className="gap-1">
                <Plus className="w-4 h-4" /> Add
              </Button>
            </div>

            {/* Sources list */}
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {sources.length === 0 ? (
                <p className="text-sm text-muted-foreground py-2 text-center">No sources configured yet.</p>
              ) : (
                sources.map((s) => (
                  <div key={s.id} className="flex items-center justify-between rounded-md px-3 py-2 bg-muted/30 text-sm">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="text-xs rounded bg-primary/10 text-primary px-1.5 py-0.5 shrink-0">{s.source_type}</span>
                      <span className="truncate text-foreground">{s.value}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteSource(s.id)}
                      className="shrink-0 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Products Table */}
      <Card className="bg-background/50 border-border">
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <CardTitle className="text-lg">Product Catalog</CardTitle>
              <CardDescription>
                {products.length} products found
              </CardDescription>
            </div>
            <div className="flex gap-2 flex-wrap">
              <Input
                id="keyword-filter"
                placeholder="Filter keyword..."
                value={keywordFilter}
                onChange={(e) => setKeywordFilter(e.target.value)}
                className="w-40 bg-background"
              />
              <select
                id="status-filter"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="flex h-10 w-36 items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="">All Statuses</option>
                <option value="PENDING">PENDING</option>
                <option value="CONVERTED">CONVERTED</option>
                <option value="FAILED">FAILED</option>
              </select>
              <Button onClick={fetchProducts} disabled={productLoading} variant="outline" className="gap-2">
                <RefreshCw className={`w-4 h-4 ${productLoading ? 'animate-spin' : ''}`} />
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
                  <TableHead className="w-16">Image</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Price</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Keyword</TableHead>
                  <TableHead>Added</TableHead>
                  <TableHead>Link</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                      {productLoading ? 'Loading...' : 'No products found. Add a source and wait for the crawler to run.'}
                    </TableCell>
                  </TableRow>
                ) : (
                  products.map((p) => (
                    <TableRow key={p.id} className="hover:bg-muted/30">
                      <TableCell>
                        {p.image_urls?.[0] ? (
                          <img
                            src={p.image_urls[0]}
                            alt={p.title}
                            className="w-12 h-12 object-cover rounded-md border border-border"
                            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                          />
                        ) : (
                          <div className="w-12 h-12 rounded-md bg-muted flex items-center justify-center">
                            <Package className="w-5 h-5 text-muted-foreground" />
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="font-medium max-w-xs">
                        <p className="truncate" title={p.title}>{p.title || '—'}</p>
                      </TableCell>
                      <TableCell className="whitespace-nowrap text-sm">{p.price || '—'}</TableCell>
                      <TableCell><StatusBadge status={p.status} /></TableCell>
                      <TableCell>
                        {p.keyword ? (
                          <span className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded">{p.keyword}</span>
                        ) : '—'}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                        {p.created_at ? new Date(p.created_at).toLocaleDateString() : '—'}
                      </TableCell>
                      <TableCell>
                        <a
                          href={p.affiliate_url || p.original_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-primary underline underline-offset-2"
                        >
                          {p.affiliate_url ? 'Affiliate' : 'Original'}
                        </a>
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
  );
}
