"use client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Plus, Trash2, Play } from "lucide-react"
import type { Process } from "@/lib/types"

interface ProcessInputFormProps {
  processes: Process[]
  setProcesses: (processes: Process[]) => void
  timeQuantum: number
  setTimeQuantum: (timeQuantum: number) => void
  onRun: () => void
}

export default function ProcessInputForm({
  processes,
  setProcesses,
  timeQuantum,
  setTimeQuantum,
  onRun,
}: ProcessInputFormProps) {
  const addProcess = () => {
    const newId = processes.length > 0 ? Math.max(...processes.map((p) => p.id)) + 1 : 1
    setProcesses([...processes, { id: newId, name: `P${newId}`, arrivalTime: 0, burstTime: 1, priority: 1 }])
  }

  const removeProcess = (id: number) => {
    setProcesses(processes.filter((p) => p.id !== id))
  }

  const updateProcess = (id: number, field: keyof Process, value: number | string) => {
    setProcesses(processes.map((p) => (p.id === id ? { ...p, [field]: field === "name" ? value : Number(value) } : p)))
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="grid grid-cols-5 gap-4 font-medium text-sm">
          <div>Process</div>
          <div>Arrival Time</div>
          <div>Burst Time</div>
          <div>Priority</div>
          <div></div>
        </div>

        {processes.map((process) => (
          <div key={process.id} className="grid grid-cols-5 gap-4 items-center">
            <Input
              value={process.name}
              onChange={(e) => updateProcess(process.id, "name", e.target.value)}
              className="h-9"
            />
            <Input
              type="number"
              min="0"
              value={process.arrivalTime}
              onChange={(e) => updateProcess(process.id, "arrivalTime", e.target.value)}
              className="h-9"
            />
            <Input
              type="number"
              min="1"
              value={process.burstTime}
              onChange={(e) => updateProcess(process.id, "burstTime", e.target.value)}
              className="h-9"
            />
            <Input
              type="number"
              min="1"
              value={process.priority}
              onChange={(e) => updateProcess(process.id, "priority", e.target.value)}
              className="h-9"
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={() => removeProcess(process.id)}
              disabled={processes.length <= 1}
              className="h-9 w-9"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={addProcess} className="flex items-center gap-1">
          <Plus className="h-4 w-4" /> Add Process
        </Button>

        <div className="flex items-center gap-2 ml-auto">
          <Label htmlFor="timeQuantum" className="whitespace-nowrap">
            Time Quantum (RR):
          </Label>
          <Input
            id="timeQuantum"
            type="number"
            min="1"
            value={timeQuantum}
            onChange={(e) => setTimeQuantum(Number(e.target.value))}
            className="w-20 h-9"
          />
        </div>

        <Button onClick={onRun} className="flex items-center gap-1">
          <Play className="h-4 w-4" /> Run Algorithms
        </Button>
      </div>
    </div>
  )
}
