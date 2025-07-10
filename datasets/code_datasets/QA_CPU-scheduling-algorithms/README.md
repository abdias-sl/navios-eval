# 🖥️ CPU Scheduling Visualizer

A **pure frontend web app** built with **Next.js** to simulate and visualize popular CPU scheduling algorithms:

- 🔹 FCFS (First Come First Serve)
- 🔹 RR (Round Robin)
- 🔹 SPN (Shortest Process Next)
- 🔹 SRT (Shortest Remaining Time)
- 🔹 HRRN (Highest Response Ratio Next)

---

## 🚀 Features

- Interactive process input UI
- Real-time visualization of scheduling using Gantt charts
- Shows Turnaround Time, Waiting Time, and Response Time for each process
- Round Robin supports custom time quantum
- Fully client-side (no backend or database)



---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/nikhil-200311/CPU-scheduling-algorithms.git
cd CPU-scheduling-algorithm

# Install dependencies
npm install
# or
yarn install
````

---

## 🧪 Running the App

```bash
npm run dev
# or
yarn dev
```

Then go to [http://localhost:3000](http://localhost:3000) in your browser.

---

## 💻 How It Works

All algorithm logic is implemented **directly in the frontend** (within React components). Users can:

* Add processes (PID, Arrival Time, Burst Time)
* Choose a scheduling algorithm
* See Gantt chart visualization instantly
* For Round Robin: specify time quantum before submitting

---

## 📊 Algorithms Comparison

| Algorithm | Preemptive | Criteria                |
| --------- | ---------- | ----------------------- |
| FCFS      | No         | Arrival Time            |
| RR        | Yes        | Time Quantum            |
| SPN       | No         | Shortest Burst Time     |
| SRT       | Yes        | Shortest Remaining Time |
| HRRN      | No         | Highest Response Ratio  |


---

## 🤝 Contributing

Contributions are welcome!

* Fork the repository
* Make your changes in a new branch
* Submit a pull request

