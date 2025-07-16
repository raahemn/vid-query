import { useState } from "react";

type Message = {
  text: string;
  sender: "user" | "bot";
};

export default function ChatInterface({ initialBotMessage }: { initialBotMessage: string | null }) {
  const [messages, setMessages] = useState<Message[]>(
    initialBotMessage ? [{ text: initialBotMessage, sender: "bot" }] : []
  );
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() === "") return;
    setMessages([
      ...messages,
      { text: input, sender: "user" },
      { text: "This is a placeholder bot response.", sender: "bot" },
    ]);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`
              max-w-[80%] rounded-lg px-3 py-2
              ${msg.sender === "user" ? "bg-blue-600 text-white self-end" : "bg-gray-700 text-white self-start"}
            `}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="flex border-t border-gray-700 p-2">
        <input
          className="flex-1 bg-zinc-800 border border-gray-600 rounded px-2 py-1 text-sm text-white"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button
          className="ml-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded"
          onClick={handleSend}
        >
          Send
        </button>
      </div>
    </div>
  );
}
