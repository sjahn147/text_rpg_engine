/**
 * WebSocket Hook
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketMessage } from '../types';

// WebSocket URL 설정
// 개발 환경에서는 백엔드 서버(8001)에 직접 연결
const getWebSocketUrl = (): string => {
  // 개발 환경: 백엔드 서버에 직접 연결
  if (import.meta.env.DEV) {
    return 'ws://localhost:8001/ws';
  }
  // 프로덕션: 환경 변수 또는 기본값 사용
  return process.env.VITE_WS_URL || 'ws://localhost:8001/ws';
};

export const useWebSocket = (onMessage?: (message: WebSocketMessage) => void) => {
  const [isConnected, setIsConnected] = useState(false);
  const [shouldConnect, setShouldConnect] = useState(true);
  const wsRef = useRef<WebSocket | null>(null);
  const onMessageRef = useRef(onMessage);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // onMessage 콜백을 ref로 저장하여 의존성 문제 해결
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    // 연결 비활성화되어 있으면 연결하지 않음
    if (!shouldConnect) {
      return;
    }

    // 이미 연결되어 있으면 재연결하지 않음
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const wsUrl = getWebSocketUrl();
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket 연결됨');
        // 재연결 타이머 클리어
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          if (onMessageRef.current) {
            onMessageRef.current(message);
          }
        } catch (error) {
          console.error('WebSocket 메시지 파싱 오류:', error);
        }
      };

      ws.onerror = (error) => {
        // WebSocket 에러는 조용히 처리 (서버가 시작 중이거나 선택적 기능)
        setIsConnected(false);
        // 연결 실패 시 재연결 시도하지 않음 (너무 많은 오류 방지)
        setShouldConnect(false);
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        // 정상 종료가 아닌 경우에만 재연결 시도 (하지만 shouldConnect가 false면 재연결 안 함)
        // WebSocket은 선택적 기능이므로 조용히 처리
        if (event.code !== 1000 && shouldConnect && !reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = window.setTimeout(() => {
            reconnectTimeoutRef.current = null;
            if (shouldConnect) {
              connect();
            }
          }, 10000); // 재연결 간격을 10초로 증가
        }
      };
    } catch (error) {
      // WebSocket 연결 실패는 조용히 처리 (선택적 기능)
      setIsConnected(false);
      setShouldConnect(false);
    }
  }, [shouldConnect]);

  useEffect(() => {
    if (shouldConnect) {
      connect();
    }

    // 정리 함수
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (wsRef.current) {
        try {
          wsRef.current.close(1000, 'Component unmounting');
        } catch (e) {
          // 이미 닫혀있을 수 있음
        }
        wsRef.current = null;
      }
    };
  }, [connect, shouldConnect]);

  const sendMessage = (message: WebSocketMessage) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket이 연결되지 않아 메시지를 보낼 수 없습니다.');
    }
  };

  return { 
    isConnected, 
    sendMessage,
    connected: isConnected,
  };
};

