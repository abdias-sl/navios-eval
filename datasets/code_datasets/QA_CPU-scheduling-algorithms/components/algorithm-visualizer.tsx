"use client"

import { useEffect, useRef, useState } from "react"
import type { SchedulingResult } from "@/lib/types"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Play, Pause, SkipBack, SkipForward } from "lucide-react"

const COLORS = [
  "#3b82f6", // blue-500
  "#ef4444", // red-500
  "#10b981", // emerald-500
  "#f59e0b", // amber-500
  "#8b5cf6", // violet-500
  "#ec4899", // pink-500
  "#06b6d4", // cyan-500
  "#f97316", // orange-500
]

export default function AlgorithmVisualizer({ result }: { result: SchedulingResult }) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [speed, setSpeed] = useState(1)
  const animationRef = useRef<number | null>(null)
  const lastTimeRef = useRef<number | null>(null)

  const maxTime = result.timeline.length > 0 ? result.timeline[result.timeline.length - 1].endTime : 0

  useEffect(() => {
    // Reset animation when result changes
    setCurrentTime(0)
    setIsPlaying(false)
    if (animationRef.current !== null) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = null
    }
  }, [result])

  useEffect(() => {
    if (isPlaying) {
      lastTimeRef.current = null
      animationRef.current = requestAnimationFrame(animate)
    } else if (animationRef.current !== null) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = null
    }

    return () => {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current)
      }
    }

    function animate(timestamp: number) {
      if (lastTimeRef.current === null) {
        lastTimeRef.current = timestamp
        animationRef.current = requestAnimationFrame(animate)
        return
      }

      const deltaTime = timestamp - lastTimeRef.current
      lastTimeRef.current = timestamp

      setCurrentTime((prevTime) => {
        const newTime = prevTime + (deltaTime * speed) / 1000
        if (newTime >= maxTime) {
          setIsPlaying(false)
          return maxTime
        }
        return newTime
      })

      if (currentTime < maxTime) {
        animationRef.current = requestAnimationFrame(animate)
      }
    }
  }, [isPlaying, speed, maxTime, currentTime])

  const getProcessColor = (processName: string) => {
    const index = Number.parseInt(processName.replace(/\D/g, "")) % COLORS.length
    return COLORS[index]
  }

  const getActiveEvents = () => {
    return result.timeline.filter((event) => event.startTime <= currentTime && event.endTime > currentTime)
  }

  const handleReset = () => {
    setCurrentTime(0)
    setIsPlaying(false)
  }

  const handleSkipForward = () => {
    const nextEvent = result.timeline.find((event) => event.startTime > currentTime)
    if (nextEvent) {
      setCurrentTime(nextEvent.startTime)
    } else {
      setCurrentTime(maxTime)
    }
  }

  const handleSkipBackward = () => {
    const prevEvents = result.timeline.filter((event) => event.startTime < currentTime)
    if (prevEvents.length > 0) {
      const lastPrevEvent = prevEvents[prevEvents.length - 1]
      setCurrentTime(lastPrevEvent.startTime)
    } else {
      setCurrentTime(0)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="text-sm font-medium">Current Time: {currentTime.toFixed(1)}</div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={handleSkipBackward} className="h-8 w-8">
            <SkipBack className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={() => setIsPlaying(!isPlaying)} className="h-8 w-8">
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          <Button variant="outline" size="icon" onClick={handleSkipForward} className="h-8 w-8">
            <SkipForward className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleReset} className="h-8">
            Reset
          </Button>
          <select
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            className="h-8 rounded-md border border-input bg-background px-3 py-1 text-sm"
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={4}>4x</option>
          </select>
        </div>
      </div>

      <div className="relative h-16 bg-muted rounded-md overflow-hidden">
        {result.timeline.map((event, index) => (
          <div
            key={index}
            className="absolute h-full flex items-center justify-center text-white font-medium"
            style={{
              left: `${(event.startTime / maxTime) * 100}%`,
              width: `${((event.endTime - event.startTime) / maxTime) * 100}%`,
              backgroundColor:
                event.processName === "idle"
                  ? "#94a3b8" // slate-400
                  : getProcessColor(event.processName),
              opacity: event.startTime <= currentTime && event.endTime > currentTime ? 1 : 0.7,
              borderLeft: index > 0 ? "1px solid rgba(255,255,255,0.3)" : "none",
            }}
          >
            {event.processName}
          </div>
        ))}

        {/* Current time indicator */}
        <div
          className="absolute h-full w-0.5 bg-black z-10"
          style={{
            left: `${(currentTime / maxTime) * 100}%`,
          }}
        />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {result.processes.map((process) => (
          <Card
            key={process.name}
            className={`p-3 ${
              getActiveEvents().some((e) => e.processName === process.name) ? "ring-2 ring-offset-2" : ""
            }`}
            style={{
              borderColor: getProcessColor(process.name),
              ringColor: getProcessColor(process.name),
            }}
          >
            <div className="font-medium">{process.name}</div>
            <div className="text-sm text-muted-foreground">
              Arrival: {process.arrivalTime} | Burst: {process.burstTime}
            </div>
            <div className="text-sm">
              Waiting: {process.waitingTime} | Turnaround: {process.turnaroundTime}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
