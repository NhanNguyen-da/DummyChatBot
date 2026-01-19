/**
 * chat.service.ts - Service xử lý chat API
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ChatRequest, ChatResponse } from '../models/message.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = `${environment.apiUrl}/chat`;

  constructor(private http: HttpClient) { }

  /**
   * Gửi tin nhắn đến chatbot
   * @param request - Request chứa tin nhắn và thông tin session
   * @returns Observable với response từ bot
   */
  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat`, request);
  }

  /**
   * Lấy lịch sử chat theo session ID
   * @param sessionId - ID của session
   * @returns Observable với lịch sử chat
   */
  getChatHistory(sessionId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/chat/history/${sessionId}`);
  }

  /**
   * Reset cuộc hội thoại
   * @param sessionId - ID của session cần reset
   * @returns Observable với kết quả reset
   */
  resetChat(sessionId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/chat/reset`, { sessionId });
  }

  /**
   * Tạo session ID mới
   * @returns Session ID dạng UUID
   */
  generateSessionId(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
}
