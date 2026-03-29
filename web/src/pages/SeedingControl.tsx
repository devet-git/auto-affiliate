import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Play, RefreshCw, Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';

interface Device {
  id: string;
  label: string;
  udid: string;
  status: string;
}

interface TaskResult {
  task_id: string;
  status: string;
  result?: Record<string, unknown>;
  error?: string;
  comment_text?: string;
  post_url?: string;
  triggered_at?: string;
}

const STATUS_CONFIG: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  queued:  { color: 'text-yellow-400', icon: <Clock className="w-4 h-4" />,  label: 'Đang chờ' },
  PENDING: { color: 'text-yellow-400', icon: <Clock className="w-4 h-4" />,  label: 'Đang chờ' },
  STARTED: { color: 'text-blue-400',   icon: <Loader2 className="w-4 h-4 animate-spin" />, label: 'Đang chạy' },
  SUCCESS: { color: 'text-green-400',  icon: <CheckCircle2 className="w-4 h-4" />, label: 'Thành công' },
  FAILURE: { color: 'text-red-400',    icon: <XCircle className="w-4 h-4" />, label: 'Thất bại' },
};

function TaskStatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.PENDING;
  return (
    <span className={`inline-flex items-center gap-1.5 text-sm font-medium ${cfg.color}`}>
      {cfg.icon} {cfg.label}
    </span>
  );
}

export default function SeedingControl() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loadingDevices, setLoadingDevices] = useState(true);

  const [postUrl, setPostUrl] = useState('');
  const [commentText, setCommentText] = useState('');
  const [selectedUdid, setSelectedUdid] = useState('');
  const [triggering, setTriggering] = useState(false);

  const [taskHistory, setTaskHistory] = useState<TaskResult[]>([]);
  const [checkingTask, setCheckingTask] = useState<string | null>(null);

  useEffect(() => {
    api.get('/devices').then(({ data }) => {
      setDevices(data);
      const online = data.find((d: Device) => d.status === 'online');
      if (online) setSelectedUdid(online.udid);
    }).finally(() => setLoadingDevices(false));
  }, []);

  const handleTrigger = async () => {
    if (!postUrl.trim() || !commentText.trim()) return;
    setTriggering(true);
    try {
      const { data } = await api.post('/sourcing/seed/comment', {
        post_url: postUrl.trim(),
        comment_text: commentText.trim(),
        udid: selectedUdid || undefined,
      });
      const newTask: TaskResult = {
        task_id: data.task_id,
        status: 'queued',
        comment_text: commentText.trim(),
        post_url: postUrl.trim(),
        triggered_at: new Date().toLocaleTimeString('vi-VN'),
      };
      setTaskHistory([newTask, ...taskHistory]);
      setPostUrl('');
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      alert(`Lỗi: ${axiosErr?.response?.data?.detail ?? 'Enqueue thất bại'}`);
    } finally {
      setTriggering(false);
    }
  };

  const checkStatus = async (task_id: string) => {
    setCheckingTask(task_id);
    try {
      // Poll task status via campaign task endpoint doesn't exist here for direct sourcing tasks
      // Use Flower or check via celery inspect
      alert(`Task ID: ${task_id}\nKiểm tra trạng thái trong Celery worker log hoặc Flower dashboard.`);
    } finally {
      setCheckingTask(null);
    }
  };

  const onlineDevices = devices.filter((d) => d.status === 'online');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Seeding Control</h1>
        <p className="text-zinc-400 text-sm mt-1">
          Trigger comment affiliate trực tiếp lên bài viết Facebook qua Appium.
        </p>
      </div>

      {/* Quick Trigger Panel */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 space-y-5">
        <h2 className="font-semibold text-zinc-200">🚀 Trigger Comment Đơn</h2>

        <div className="space-y-2">
          <label className="text-sm text-zinc-400">URL bài viết Facebook *</label>
          <Input
            value={postUrl}
            onChange={(e) => setPostUrl(e.target.value)}
            placeholder="https://www.facebook.com/permalink.php?story_fbid=..."
            className="bg-zinc-950 border-zinc-700 font-mono text-sm"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm text-zinc-400">Nội dung comment *</label>
          <textarea
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            placeholder="Sản phẩm ngon vl https://shope.ee/abc123..."
            rows={3}
            className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-50 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
          <p className="text-xs text-zinc-600">{commentText.length}/2000 ký tự</p>
        </div>

        <div className="space-y-2">
          <label className="text-sm text-zinc-400">Thiết bị thực thi</label>
          {loadingDevices ? (
            <div className="text-zinc-500 text-sm flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" /> Đang tải thiết bị...
            </div>
          ) : onlineDevices.length === 0 ? (
            <div className="bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 text-sm px-3 py-2 rounded-lg">
              ⚠️ Không có thiết bị nào đang online. Sẽ dùng UDID từ .env hoặc báo lỗi.
            </div>
          ) : (
            <select
              value={selectedUdid}
              onChange={(e) => setSelectedUdid(e.target.value)}
              className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">— Dùng thiết bị mặc định từ .env —</option>
              {onlineDevices.map((d) => (
                <option key={d.id} value={d.udid}>
                  {d.label} ({d.udid})
                </option>
              ))}
            </select>
          )}
        </div>

        <Button
          onClick={handleTrigger}
          disabled={triggering || !postUrl.trim() || !commentText.trim()}
          className="w-full bg-green-600 hover:bg-green-700 text-white gap-2 h-11"
        >
          {triggering ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          {triggering ? 'Đang enqueue...' : 'Chạy Comment Ngay'}
        </Button>

        <p className="text-xs text-zinc-600 text-center">
          Task sẽ được gửi vào hàng đợi <code className="bg-zinc-800 px-1 rounded">appium_phone</code> và Celery worker sẽ xử lý.
        </p>
      </div>

      {/* Task History */}
      {taskHistory.length > 0 && (
        <div className="space-y-3">
          <h2 className="font-semibold text-zinc-200">📋 Task Vừa Trigger</h2>
          <div className="space-y-2">
            {taskHistory.map((task) => (
              <div
                key={task.task_id}
                className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4 flex items-start justify-between gap-4"
              >
                <div className="space-y-1 min-w-0 flex-1">
                  <div className="flex items-center gap-3">
                    <TaskStatusBadge status={task.status} />
                    <span className="text-xs text-zinc-600">{task.triggered_at}</span>
                  </div>
                  <p className="text-xs text-zinc-500 truncate">
                    <span className="text-zinc-400">Post:</span> {task.post_url}
                  </p>
                  <p className="text-xs text-zinc-500 truncate">
                    <span className="text-zinc-400">Comment:</span> {task.comment_text}
                  </p>
                  <code className="text-xs text-zinc-600 font-mono">ID: {task.task_id}</code>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => checkStatus(task.task_id)}
                  disabled={checkingTask === task.task_id}
                  title="Refresh status"
                  className="shrink-0"
                >
                  <RefreshCw className={`w-4 h-4 text-zinc-400 ${checkingTask === task.task_id ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hint Card */}
      <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4 text-sm text-zinc-400 space-y-1">
        <p className="text-blue-300 font-medium">💡 Hướng dẫn sử dụng</p>
        <ul className="space-y-1 list-disc list-inside">
          <li>Đảm bảo Appium đang chạy tại <code className="bg-zinc-800 px-1 rounded">localhost:4723</code></li>
          <li>Điện thoại Android đã kết nối ADB và đang online</li>
          <li>App Facebook đã đăng nhập trên thiết bị</li>
          <li>Xem kết quả chi tiết trong Celery worker log</li>
        </ul>
      </div>
    </div>
  );
}
