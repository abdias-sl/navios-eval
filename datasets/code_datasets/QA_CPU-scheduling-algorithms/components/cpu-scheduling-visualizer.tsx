"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import ProcessInputForm from "./process-input-form"
import AlgorithmVisualizer from "./algorithm-visualizer"
import ResultsTable from "./results-table"
import AlgorithmInfo from "./algorithm-info"
import type { Process, SchedulingResult } from "@/lib/types"
import { runFCFS, runRoundRobin, runSPN, runSRT, runHRRN } from "@/lib/scheduling-algorithms"

export default function CPUSchedulingVisualizer() {
  const [processes, setProcesses] = useState<Process[]>([
    { id: 1, name: "P1", arrivalTime: 0, burstTime: 5, priority: 1 },
    { id: 2, name: "P2", arrivalTime: 1, burstTime: 3, priority: 2 },
    { id: 3, name: "P3", arrivalTime: 2, burstTime: 8, priority: 1 },
    { id: 4, name: "P4", arrivalTime: 3, burstTime: 2, priority: 3 },
  ])
  const [timeQuantum, setTimeQuantum] = useState<number>(2)
  const [results, setResults] = useState<Record<string, SchedulingResult | null>>({
    fcfs: null,
    rr: null,
    spn: null,
    srt: null,
    hrrn: null,
  })
  const [activeTab, setActiveTab] = useState("fcfs")

  const runAlgorithms = () => {
    setResults({
      fcfs: runFCFS([...processes]),
      rr: runRoundRobin([...processes], timeQuantum),
      spn: runSPN([...processes]),
      srt: runSRT([...processes]),
      hrrn: runHRRN([...processes]),
    })
  }

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle>Process Input</CardTitle>
          <CardDescription>Enter the details of processes to be scheduled</CardDescription>
        </CardHeader>
        <CardContent>
          <ProcessInputForm
            processes={processes}
            setProcesses={setProcesses}
            timeQuantum={timeQuantum}
            setTimeQuantum={setTimeQuantum}
            onRun={runAlgorithms}
          />
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-5 w-full">
          <TabsTrigger value="fcfs">FCFS</TabsTrigger>
          <TabsTrigger value="rr">Round Robin</TabsTrigger>
          <TabsTrigger value="spn">SPN</TabsTrigger>
          <TabsTrigger value="srt">SRT</TabsTrigger>
          <TabsTrigger value="hrrn">HRRN</TabsTrigger>
        </TabsList>

        {Object.entries({
          fcfs: { title: "First Come First Serve", result: results.fcfs },
          rr: { title: "Round Robin", result: results.rr },
          spn: { title: "Shortest Process Next", result: results.spn },
          srt: { title: "Shortest Remaining Time", result: results.srt },
          hrrn: { title: "Highest Response Ratio Next", result: results.hrrn },
        }).map(([key, { title, result }]) => (
          <TabsContent key={key} value={key} className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>{title}</CardTitle>
                <CardDescription>Visualization and results of the {title} algorithm</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {result ? (
                  <>
                    <AlgorithmVisualizer result={result} />
                    <ResultsTable result={result} />
                  </>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    Click "Run Algorithms" to see the results
                  </div>
                )}
                <AlgorithmInfo algorithm={key as "fcfs" | "rr" | "spn" | "srt" | "hrrn"} />
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}
