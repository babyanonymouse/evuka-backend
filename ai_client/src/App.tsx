import { useState, useEffect, useRef } from "react";
import axios from "axios";

interface Message {
  role: "user" | "model";
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "model",
      content: "Hello! I am Evuka AI. How can I help you today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [courseId, setCourseId] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const payload: any = { message: userMsg.content };
      if (courseId.trim()) payload.course_id = courseId;

      console.log("Sending payload:", payload);
      const res = await axios.post("/ai/ask/", payload);
      console.log("Response:", res.data);

      const aiMsg: Message = { role: "model", content: res.data.response };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      console.error(err);
      let errorText = "Error communicating with AI.";
      if (err.response) {
        errorText += ` (${err.response.status}: ${JSON.stringify(
          err.response.data
        )})`;
      }
      setMessages((prev) => [...prev, { role: "model", content: errorText }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100 font-sans text-gray-800">
      {/* Header */}
      <header className="bg-white shadow p-4 flex justify-between items-center z-10">
        <h1 className="text-xl font-bold text-blue-600">Evuka AI Tester</h1>
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-600">
            Course ID (Optional):
          </label>
          <input
            type="text"
            placeholder="Ex: 1"
            value={courseId}
            onChange={(e) => setCourseId(e.target.value)}
            className="border rounded px-2 py-1 w-20 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-white text-gray-800 shadow rounded-bl-none border border-gray-200"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-500 rounded-lg px-4 py-2 animate-pulse text-sm">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </main>

      {/* Input Area */}
      <footer className="p-4 bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white rounded-full px-6 py-2 font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;
