import { useEffect, useState } from 'react'
import { Card, Button, Badge } from '../components/ui'
import { adminService } from '../services/adminService'

interface PendingUser {
  id: string
  email: string
  first_name?: string
  last_name?: string
  role?: string
  created_at?: string
}

export default function AdminApprovalsPage() {
  const [users, setUsers] = useState<PendingUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    const res = await adminService.getPendingUsers()
    if (res.success) {
      setUsers(res.data.pending_users || [])
    } else {
      setError(res.error || 'Failed to load')
    }
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const handleApprove = async (id: string) => {
    const res = await adminService.approveUser(id)
    if (!res.success) alert(res.error)
    await load()
  }

  const handleReject = async (id: string) => {
    const res = await adminService.rejectUser(id)
    if (!res.success) alert(res.error)
    await load()
  }

  return (
    <div className="space-y-8">
      <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200">
        <div className="p-8 sm:p-12 text-center text-white bg-gradient-to-br from-slate-600 via-gray-700 to-zinc-700">
          <h2 className="mb-3 text-4xl font-extrabold tracking-tight drop-shadow-md sm:text-5xl">🛡️ Admin Approvals</h2>
          <p className="text-lg font-medium text-slate-100 opacity-90 sm:text-xl">Review and approve pending user accounts</p>
        </div>
      </section>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>
      )}

      <Card>
        <h3 className="text-xl font-bold text-gray-900 mb-4">Pending Users ({users.length})</h3>
        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : users.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No pending approvals</div>
        ) : (
          <div className="space-y-3">
            {users.map((u) => (
              <div key={u.id} className="border rounded-lg p-4 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-gray-900">{u.email}</p>
                  <p className="text-xs text-gray-600">
                    {u.first_name || ''} {u.last_name || ''}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="warning">pending</Badge>
                  <Button size="sm" variant="primary" onClick={() => handleApprove(u.id)}>✅ Approve</Button>
                  <Button size="sm" variant="danger" onClick={() => handleReject(u.id)}>🗑️ Reject</Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}


