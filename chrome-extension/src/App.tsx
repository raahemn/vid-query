import { useState } from "react";
import "./index.css";

type Message = {
  text: string;
  sender: "user" | "bot";
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() === "") return;
    setMessages([
      ...messages,
      { text: input, sender: "user" },
      { text: "This is a bot response.", sender: "bot" } // Example static reply
    ]);
    setInput("");
  };

  return (
    <div className="flex flex-col h-[500px] w-[320px] bg-zinc-900 text-zinc-100 rounded-lg overflow-hidden shadow-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-zinc-800">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`
              max-w-[80%] px-4 py-2 rounded-xl text-sm break-words
              ${msg.sender === "user" 
                ? "bg-blue-600 text-white self-end ml-auto"
                : "bg-zinc-800 text-zinc-100 self-start mr-auto border border-zinc-700"
              }
            `}
          >
            {msg.text}
          </div>
        ))}
        {messages.length === 0 && (
          <p className="text-zinc-500 text-center mt-20 text-sm">
            Start the conversation...
          </p>
        )}
      </div>
      <div className="flex items-center gap-2 border-t border-zinc-800 bg-zinc-950 px-3 py-2">
        <input
          className="flex-1 bg-zinc-800 text-zinc-100 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button
          className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded-lg text-sm transition"
          onClick={handleSend}
        >
          Send
        </button>
      </div>
    </div>
  );
}
