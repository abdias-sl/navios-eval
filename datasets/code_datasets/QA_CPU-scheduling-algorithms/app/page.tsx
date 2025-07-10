import CPUSchedulingVisualizer from "@/components/cpu-scheduling-visualizer"

export default function Home() {
  return (
    <main className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold text-center mb-8">CPU Scheduling Algorithms Visualizer</h1>
      <CPUSchedulingVisualizer />
    </main>
  )
}
