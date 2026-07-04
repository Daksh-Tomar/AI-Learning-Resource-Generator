"use client";

import { useState } from "react";

type Message = {
  role: "user" | "ai" | "system";
  content: string;
};

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "ai", content: "Hi! What are you preparing for?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<any>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const newMessages: Message[] = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      // Assuming FastAPI runs on 8000 locally
      const res = await fetch("http://localhost:8000/api/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: "test-session-1",
          message: input,
          history: messages.map(m => ({ role: m.role, content: m.content }))
        })
      });
      const data = await res.json();
      setMessages([...newMessages, { role: "ai", content: data.message }]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const generateProfile = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/chat/profile/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: "test-session-1",
          message: "Please generate my learning profile now.",
          history: messages.map(m => ({ role: m.role, content: m.content }))
        })
      });
      const data = await res.json();
      setProfile(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 border rounded-lg shadow-sm p-4 text-black w-full max-w-4xl mx-auto">
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 border rounded bg-white">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`px-4 py-2 rounded-lg max-w-[70%] ${msg.role === "user" ? "bg-blue-600 text-white" : "bg-gray-200 text-black"}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && <div className="text-gray-500 italic">Thinking...</div>}
      </div>
      
      {profile && (
        <div className="mb-4 p-4 bg-green-100 rounded text-sm text-green-900 border border-green-300">
          <strong>Extracted Profile:</strong>
          <pre>{JSON.stringify(profile, null, 2)}</pre>
        </div>
      )}

      <div className="flex space-x-2">
        <input 
          type="text" 
          className="flex-1 border p-2 rounded text-black"
          placeholder="Type your answer..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={sendMessage} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50" disabled={loading}>
          Send
        </button>
        <button onClick={generateProfile} className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50" disabled={loading}>
          Extract Profile
        </button>
      </div>
    </div>
  );
}
