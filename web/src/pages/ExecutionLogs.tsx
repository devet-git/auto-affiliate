import React, { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { RefreshCw, Activity, Terminal } from 'lucide-react';

export default function ExecutionLogs() {
  const token = useAuthStore((state) => state.token);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [retentionDays, setRetentionDays] = useState('7');
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [taskNameFilter, setTaskNameFilter] = useState('');

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      let url = 'http://localhost:8000/api/v1/worker/logs?limit=50';
      if (statusFilter) url += `&status=${statusFilter}`;
      if (taskNameFilter) url += `&task_name=${taskNameFilter}`;
      
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const json = await res.json();
      setLogs(json.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [token, statusFilter, taskNameFilter]);

  const fetchSettings = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/worker/settings/log_retention_days', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const json = await res.json();
      if (json.value) setRetentionDays(json.value);
    } catch (e) {
      console.error(e);
    }
  }, [token]);

  const updateSettings = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/worker/settings', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key: 'log_retention_days', value: retentionDays })
      });
      alert('Retention updated to ' + retentionDays + ' days');
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchLogs();
    fetchSettings();
  }, [fetchLogs, fetchSettings]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">System Execution Logs</h2>
        <p className="text-muted-foreground">Monitor background tasks and system jobs</p>
      </div>

      <div className="flex gap-4 items-end">
        <div>
          <label className="text-sm font-medium mb-1 block">Log Retention (Days)</label>
          <div className="flex gap-2">
            <Input 
              type="number" 
              value={retentionDays} 
              onChange={e => setRetentionDays(e.target.value)} 
              className="w-24 bg-background"
            />
            <Button variant="secondary" onClick={updateSettings}>Save</Button>
          </div>
        </div>
      </div>

      <Card className="bg-background/50 border-border">
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <CardTitle className="text-lg">Recent Traces</CardTitle>
              <CardDescription>Viewing the last 50 executions matching filters.</CardDescription>
            </div>
            
            <div className="flex gap-2 flex-wrap">
              <Input 
                placeholder="Filter Task Name..." 
                value={taskNameFilter}
                onChange={e => setTaskNameFilter(e.target.value)}
                className="w-48 bg-background"
              />
              <select 
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
                className="flex h-10 w-32 items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="">All Statuses</option>
                <option value="STARTED">STARTED</option>
                <option value="SUCCESS">SUCCESS</option>
                <option value="FAILED">FAILED</option>
              </select>
              <Button onClick={fetchLogs} disabled={loading} variant="outline" className="gap-2">
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
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
                  <TableHead>Time</TableHead>
                  <TableHead>Task Name</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Execution ID</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                      No execution logs found.
                    </TableCell>
                  </TableRow>
                ) : (
                  logs.map((log) => (
                    <TableRow key={log.id} className="hover:bg-muted/30">
                      <TableCell className="whitespace-nowrap">
                        {new Date(log.started_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="font-medium">{log.task_name.split('.').pop()}</TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                          log.status === 'SUCCESS' ? 'bg-green-500/10 text-green-500' :
                          log.status === 'FAILED' ? 'bg-destructive/10 text-destructive' :
                          'bg-primary/10 text-primary'
                        }`}>
                          {log.status}
                        </span>
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground truncate max-w-[120px]" title={log.task_id}>
                        {log.task_id}
                      </TableCell>
                      <TableCell>
                        {log.error_traceback && (
                           <Button variant="ghost" size="sm" onClick={() => alert(log.error_traceback)}>
                             <Terminal className="w-4 h-4 text-destructive" />
                           </Button>
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
    </div>
  );
}
