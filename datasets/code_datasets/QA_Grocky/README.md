
## 🧠 Grocky: AI-Powered Job Interview Preparation Platform

**Grocky** is a job interview preparation platform built using modern web technologies. It integrates AI voice agents to simulate real interview scenarios, giving users real-time feedback and transcripts to help them improve.

---

## ⚙️ Tech Stack

* **Next.js** – for building the frontend and backend logic
* **Tailwind CSS** – for modern, responsive styling
* **Firebase** – for authentication and backend services
* **Vapi AI** – for voice agent interactions
* **shadcn/ui** – for UI components
* **Google Gemini** – for AI-based feedback
* **Zod** – for input validation

---

## 🧰 Prerequisites

Make sure the following are installed on your machine:

* Git
* Node.js
* npm (Node Package Manager)

---

## 🚀 Installation Steps

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Install dependencies

```bash
npm install
```

### 3. Set up environment variables

Create a `.env.local` file in the root directory and add:

```env
NEXT_PUBLIC_VAPI_WEB_TOKEN=
NEXT_PUBLIC_VAPI_WORKFLOW_ID=

GOOGLE_GENERATIVE_AI_API_KEY=

NEXT_PUBLIC_BASE_URL=

NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=

FIREBASE_PROJECT_ID=
FIREBASE_CLIENT_EMAIL=
FIREBASE_PRIVATE_KEY=
```

Fill in the values based on your Firebase, Vapi, and Google Gemini configurations.

---

### 4. Run the development server

```bash
npm run dev
```

Open your browser and go to `http://localhost:3000` to view the project.

