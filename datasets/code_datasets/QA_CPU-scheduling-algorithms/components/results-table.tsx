import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { SchedulingResult } from "@/lib/types"

export default function ResultsTable({ result }: { result: SchedulingResult }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Results</h3>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Process</TableHead>
            <TableHead>Arrival Time</TableHead>
            <TableHead>Burst Time</TableHead>
            <TableHead>Completion Time</TableHead>
            <TableHead>Turnaround Time</TableHead>
            <TableHead>Waiting Time</TableHead>
            <TableHead>Response Time</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {result.processes.map((process) => (
            <TableRow key={process.name}>
              <TableCell className="font-medium">{process.name}</TableCell>
              <TableCell>{process.arrivalTime}</TableCell>
              <TableCell>{process.burstTime}</TableCell>
              <TableCell>{process.completionTime}</TableCell>
              <TableCell>{process.turnaroundTime}</TableCell>
              <TableCell>{process.waitingTime}</TableCell>
              <TableCell>{process.responseTime}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div className="p-4 bg-muted rounded-md">
          <div className="font-medium">Average Waiting Time</div>
          <div className="text-lg">{result.averageWaitingTime.toFixed(2)}</div>
        </div>
        <div className="p-4 bg-muted rounded-md">
          <div className="font-medium">Average Turnaround Time</div>
          <div className="text-lg">{result.averageTurnaroundTime.toFixed(2)}</div>
        </div>
        <div className="p-4 bg-muted rounded-md">
          <div className="font-medium">Average Response Time</div>
          <div className="text-lg">{result.averageResponseTime.toFixed(2)}</div>
        </div>
      </div>
    </div>
  )
}
