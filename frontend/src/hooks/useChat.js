import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchChatHistory, streamChatMessage, confirmActionApi } from '../api/chat';

export function useChat() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingStatus, setStreamingStatus] = useState(null); // 'thinking' | 'executing_tool'
  const [currentTool, setCurrentTool] = useState(null);
  const [error, setError] = useState(null);

  // Load chat history on mount
  const loadHistory = useCallback(async (convId = null) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await fetchChatHistory(convId);
      if (data.conversations) {
        setConversations(data.conversations);
      }
      if (data.active_conversation) {
        setActiveConversationId(data.active_conversation.id);
        setMessages(data.active_conversation.messages || []);
      } else if (data.messages) {
        setMessages(data.messages);
        setActiveConversationId(convId);
      }
    } catch (err) {
      console.error('Failed to load chat history:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const sendMessage = useCallback(
    async (text, imageId = null) => {
      if (!text?.trim() && !imageId) return;

      setError(null);
      setStreamingStatus('thinking');
      setCurrentTool(null);

      // Optimistic user message
      const tempUserMsgId = `user_${Date.now()}`;
      const userMessage = {
        id: tempUserMsgId,
        role: 'user',
        content: text,
        image_id: imageId,
        created_at: new Date().toISOString(),
      };

      // Placeholder assistant message
      const tempAssistantId = `asst_${Date.now()}`;
      const assistantMessage = {
        id: tempAssistantId,
        role: 'assistant',
        content: '',
        blocks: [],
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);

      let accumulatedTokens = '';

      await streamChatMessage({
        message: text,
        conversationId: activeConversationId,
        imageId,
        onStatus: (payload) => {
          setStreamingStatus(payload.status || 'thinking');
        },
        onToolCall: (payload) => {
          setStreamingStatus('executing_tool');
          setCurrentTool(payload.tool);
        },
        onToolResult: (payload) => {
          // Tool finished executing
          setCurrentTool(null);
        },
        onToken: (token) => {
          accumulatedTokens += token;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === tempAssistantId
                ? {
                    ...msg,
                    content: accumulatedTokens,
                    blocks: [{ type: 'text', content: accumulatedTokens }],
                  }
                : msg
            )
          );
        },
        onDone: (payload) => {
          setStreamingStatus(null);
          setCurrentTool(null);
          if (payload.message) {
            setMessages((prev) =>
              prev.map((msg) => (msg.id === tempAssistantId ? payload.message : msg))
            );
            if (payload.message.conversation_id && !activeConversationId) {
              setActiveConversationId(payload.message.conversation_id);
            }
          }
        },
        onError: (err) => {
          setStreamingStatus(null);
          setCurrentTool(null);
          setError(err.message);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === tempAssistantId
                ? {
                    ...msg,
                    content: `Error: ${err.message}`,
                    blocks: [{ type: 'text', content: `Error: ${err.message}` }],
                  }
                : msg
            )
          );
        },
      });
    },
    [activeConversationId]
  );

  const confirmAction = useCallback(
    async (actionId, confirmed) => {
      if (!activeConversationId) return;
      try {
        setError(null);
        const data = await confirmActionApi(actionId, activeConversationId, confirmed);
        // Refresh conversation history to render the executed state
        await loadHistory(activeConversationId);
        return data;
      } catch (err) {
        setError(err.message);
        throw err;
      }
    },
    [activeConversationId, loadHistory]
  );

  return {
    conversations,
    activeConversationId,
    messages,
    isLoading,
    streamingStatus,
    currentTool,
    error,
    sendMessage,
    confirmAction,
    loadHistory,
  };
}
