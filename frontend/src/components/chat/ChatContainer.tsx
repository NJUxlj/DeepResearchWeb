import ChatWindow from "./ChatWindow";
import { useChat } from "@/hooks/useChat";

export default function ChatContainer() {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    stopStream,
  } = useChat();

  return (
    <ChatWindow
      messages={messages}
      isLoading={isLoading}
      error={error}
      onSendMessage={sendMessage}
      onStop={stopStream}
    />
  );
}
