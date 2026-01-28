import { Component, ElementRef, OnInit, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatHeaderComponent } from '../chat-header/chat-header';
import { MessageComponent } from '../message/message';
import { TypingIndicatorComponent } from '../typing-indicator/typing-indicator';
import { QuickReplyComponent } from '../quick-reply/quick-reply';
import { DepartmentCardComponent } from '../department-card/department-card';
import { InputAreaComponent } from '../input-area/input-area';
import { ChatService } from '../../services/chat';
import { Message, QuickReply, DepartmentRecommendation, ConversationState, ChatResponse } from '../../models/message.model';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    ChatHeaderComponent,
    MessageComponent,
    TypingIndicatorComponent,
    QuickReplyComponent,
    DepartmentCardComponent,
    InputAreaComponent
  ],
  templateUrl: './chat.html',
  styleUrl: './chat.scss'
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('inputArea') private inputArea!: InputAreaComponent;

  conversationState: ConversationState = {
    sessionId: '',
    messages: [],
    isTyping: false
  };

  showWelcome = true;
  showScrollButton = false;
  private shouldScroll = false;

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.initializeSession();
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  private initializeSession(): void {
    this.conversationState.sessionId = this.chatService.generateSessionId();
  }

  startConversation(): void {
    this.showWelcome = false;

    // Add welcome message from bot
    const welcomeMessage: Message = {
      id: this.generateMessageId(),
      text: 'Xin chao! Toi la tro ly sang loc benh nhan. Toi se giup ban tim dung chuyen khoa. Ban dang gap van de gi?',
      type: 'bot',
      timestamp: new Date(),
      quickReplies: [
        { id: '1', label: 'Đau đầu', value: 'Tôi bị đau đầu' },
        { id: '2', label: 'Đau họng', value: 'Tôi bị đau họng' },
        { id: '3', label: 'Sốt', value: 'Tôi bị sốt' },
        { id: '4', label: 'Ho', value: 'Tôi bị ho' }
      ]
    };

    this.addMessage(welcomeMessage);
    setTimeout(() => this.inputArea?.focusInput(), 100);
  }

  onMessageSent(text: string): void {
    // Add user message
    const userMessage: Message = {
      id: this.generateMessageId(),
      text: text,
      type: 'user',
      timestamp: new Date()
    };
    this.addMessage(userMessage);

    // Show typing indicator
    this.conversationState.isTyping = true;
    this.shouldScroll = true;

    // Send to API
    this.sendMessageToBot(text);
  }

  onQuickReplySelected(reply: QuickReply): void {
    this.onMessageSent(reply.value);
  }

  onResetChat(): void {
    // Reset on server
    this.chatService.resetChat(this.conversationState.sessionId).subscribe({
      error: (err) => console.error('Error resetting chat:', err)
    });

    // Reset local state
    this.conversationState = {
      sessionId: this.chatService.generateSessionId(),
      messages: [],
      isTyping: false
    };
    this.showWelcome = true;
  }

  onLanguageToggle(lang: string): void {
    console.log('Language changed to:', lang);
    // Implement language switching logic
  }

  onBookAppointment(department: DepartmentRecommendation): void {
    console.log('Booking appointment for:', department);
    // Implement booking logic
    const systemMessage: Message = {
      id: this.generateMessageId(),
      text: 'Dang chuyen den trang dat lich hen...',
      type: 'system',
      timestamp: new Date()
    };
    this.addMessage(systemMessage);
  }

  onStartOver(): void {
    this.onResetChat();
    setTimeout(() => this.startConversation(), 100);
  }

  onScroll(event: Event): void {
    const container = event.target as HTMLElement;
    const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100;
    this.showScrollButton = !isNearBottom;
  }

  scrollToBottom(): void {
    try {
      const container = this.messagesContainer?.nativeElement;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    } catch (err) {
      console.error('Scroll error:', err);
    }
  }

  private addMessage(message: Message): void {
    this.conversationState.messages.push(message);
    this.shouldScroll = true;
  }

  private generateMessageId(): string {
    return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private sendMessageToBot(text: string): void {
    const request = this.chatService.createChatRequest(text, this.conversationState.sessionId);

    this.chatService.sendMessage(request).subscribe({
      next: (response: ChatResponse) => {
        this.conversationState.isTyping = false;
        const botMessage = this.createBotMessage(response);
        this.addMessage(botMessage);
      },
      error: (err) => {
        console.error('Error sending message:', err);
        this.conversationState.isTyping = false;

        // Show error message
        const errorMessage: Message = {
          id: this.generateMessageId(),
          text: 'Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại sau.',
          type: 'system',
          timestamp: new Date()
        };
        this.addMessage(errorMessage);
      }
    });
  }

  private createBotMessage(response: ChatResponse): Message {
    const message: Message = {
      id: this.generateMessageId(),
      text: response.response,
      type: response.alertLevel ? 'alert' : 'bot',
      timestamp: new Date(),
      alertLevel: response.alertLevel || undefined
    };

    // Add quick replies if present
    if (response.quickReplies && response.quickReplies.length > 0) {
      message.quickReplies = response.quickReplies;
    }

    // Add department recommendation if present
    if (response.departmentRecommendation) {
      message.departmentCard = response.departmentRecommendation;
    }

    // Set suggested department
    if (response.suggestedDepartment) {
      message.suggestedDepartment = response.suggestedDepartment;
    }

    return message;
  }

  get lastMessageQuickReplies(): QuickReply[] | undefined {
    const messages = this.conversationState.messages;
    if (messages.length === 0) return undefined;

    const lastBotMessage = [...messages].reverse().find(m => m.type === 'bot');
    return lastBotMessage?.quickReplies;
  }

  get lastMessageDepartmentCard(): DepartmentRecommendation | undefined {
    const messages = this.conversationState.messages;
    if (messages.length === 0) return undefined;

    const lastBotMessage = [...messages].reverse().find(m => m.type === 'bot');
    return lastBotMessage?.departmentCard;
  }

  get isInputDisabled(): boolean {
    return this.conversationState.isTyping || !!this.lastMessageDepartmentCard;
  }
}
