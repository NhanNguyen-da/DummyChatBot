/**
 * message.model.ts - Models cho tin nhan trong chat
 */

export type MessageType = 'bot' | 'user' | 'system' | 'alert';
export type AlertLevel = 'info' | 'warning' | 'danger' | 'success';

export interface Message {
  id?: string;
  text: string;
  type: MessageType;
  timestamp: Date;
  suggestedDepartment?: string;
  alertLevel?: AlertLevel;
  quickReplies?: QuickReply[];
  departmentCard?: DepartmentRecommendation;
}

export interface QuickReply {
  id: string;
  label: string;
  value: string;
}

export interface DepartmentRecommendation {
  departmentId: number;
  departmentName: string;
  doctorName?: string;
  roomNumber?: string;
  floor?: string;
  waitTime?: string;
  description?: string;
}

export interface ChatRequest {
  message: string;
  sessionId: string;
  conversationHistory?: Message[];
}

export interface ChatResponse {
  response: string;
  sessionId: string;
  suggestedDepartment?: string;
  confidence?: number;
  quickReplies?: QuickReply[];
  departmentRecommendation?: DepartmentRecommendation;
  alertLevel?: AlertLevel;
}

export interface ConversationState {
  sessionId: string;
  messages: Message[];
  isTyping: boolean;
  currentStep?: number;
  totalSteps?: number;
}
