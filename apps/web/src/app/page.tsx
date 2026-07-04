import ChatBox from "@/components/ChatBox";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-100">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">LearnLens AI</h1>
        <p className="text-lg text-gray-600">Stop Searching. Start Learning.</p>
      </div>
      
      <div className="w-full max-w-4xl h-[600px]">
        <ChatBox />
      </div>
    </main>
  );
}
