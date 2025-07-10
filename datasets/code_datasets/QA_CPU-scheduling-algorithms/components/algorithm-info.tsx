import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface AlgorithmInfoProps {
  algorithm: "fcfs" | "rr" | "spn" | "srt" | "hrrn"
}

export default function AlgorithmInfo({ algorithm }: AlgorithmInfoProps) {
  const algorithmInfo = {
    fcfs: {
      title: "First Come First Serve (FCFS)",
      description: "A non-preemptive scheduling algorithm that executes processes in the order they arrive.",
      details: [
        "Processes are executed in the order they arrive in the ready queue.",
        "It is a non-preemptive algorithm, meaning once a process starts executing, it continues until it completes.",
        "Simple to implement but can lead to the convoy effect where short processes wait behind long ones.",
        "Fair in terms of arrival time but can be unfair in terms of execution time.",
      ],
      pros: ["Simple to implement", "No overhead", "No starvation"],
      cons: ["High average waiting time", "Convoy effect", "Not suitable for interactive systems"],
    },
    rr: {
      title: "Round Robin (RR)",
      description:
        "A preemptive scheduling algorithm that allocates a fixed time quantum to each process in a circular queue.",
      details: [
        "Each process is assigned a fixed time slice called a time quantum.",
        "After a process executes for the time quantum, it is preempted and added to the end of the ready queue.",
        "The context switch overhead is higher due to frequent switching.",
        "The performance heavily depends on the time quantum size.",
      ],
      pros: ["Fair allocation of CPU", "Good for time-sharing systems", "Low response time for short processes"],
      cons: ["Higher context switch overhead", "Performance depends on time quantum", "Higher average turnaround time"],
    },
    spn: {
      title: "Shortest Process Next (SPN)",
      description: "A non-preemptive scheduling algorithm that selects the process with the shortest burst time.",
      details: [
        "Selects the process with the shortest burst time from the ready queue.",
        "It is a non-preemptive algorithm, so once a process starts, it runs to completion.",
        "Minimizes average waiting time but requires knowing the burst time in advance.",
        "Can lead to starvation of longer processes if shorter ones keep arriving.",
      ],
      pros: ["Minimizes average waiting time", "Good for batch systems", "Efficient for known workloads"],
      cons: [
        "Potential starvation of longer processes",
        "Requires knowing burst times in advance",
        "Not suitable for interactive systems",
      ],
    },
    srt: {
      title: "Shortest Remaining Time (SRT)",
      description: "A preemptive version of SPN that selects the process with the shortest remaining time.",
      details: [
        "Preemptive version of Shortest Process Next (SPN).",
        "Selects the process with the shortest remaining burst time.",
        "If a new process arrives with a shorter burst time than the remaining time of the current process, the current process is preempted.",
        "Minimizes average waiting time but has higher context switch overhead.",
      ],
      pros: ["Minimizes average waiting time", "Responsive to short processes", "Good for interactive systems"],
      cons: [
        "High context switch overhead",
        "Requires continuous monitoring",
        "Potential starvation of longer processes",
      ],
    },
    hrrn: {
      title: "Highest Response Ratio Next (HRRN)",
      description: "A non-preemptive scheduling algorithm that selects the process with the highest response ratio.",
      details: [
        "Non-preemptive algorithm that considers both the burst time and the waiting time.",
        "Calculates the response ratio as (waiting time + burst time) / burst time.",
        "Selects the process with the highest response ratio.",
        "Balances between favoring short processes and preventing starvation of longer ones.",
      ],
      pros: ["Prevents starvation", "Balances between SPN and FCFS", "Good for batch systems"],
      cons: [
        "Requires knowing burst times in advance",
        "More complex to implement",
        "Not suitable for interactive systems",
      ],
    },
  }

  const info = algorithmInfo[algorithm]

  return (
    <Card>
      <CardHeader>
        <CardTitle>{info.title}</CardTitle>
        <CardDescription>{info.description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-medium mb-2">How it works:</h4>
          <ul className="list-disc pl-5 space-y-1">
            {info.details.map((detail, index) => (
              <li key={index} className="text-sm">
                {detail}
              </li>
            ))}
          </ul>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium mb-2">Advantages:</h4>
            <ul className="list-disc pl-5 space-y-1">
              {info.pros.map((pro, index) => (
                <li key={index} className="text-sm">
                  {pro}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-2">Disadvantages:</h4>
            <ul className="list-disc pl-5 space-y-1">
              {info.cons.map((con, index) => (
                <li key={index} className="text-sm">
                  {con}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
