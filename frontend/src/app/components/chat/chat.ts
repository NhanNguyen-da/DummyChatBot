import { Component, ElementRef, OnInit, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatHeaderComponent } from '../chat-header/chat-header';
import { MessageComponent } from '../message/message';
import { TypingIndicatorComponent } from '../typing-indicator/typing-indicator';
import { QuickReplyComponent } from '../quick-reply/quick-reply';
import { DepartmentCardComponent } from '../department-card/department-card';
import { InputAreaComponent } from '../input-area/input-area';
import { ChatService } from '../../services/chat';
import { Message, QuickReply, DepartmentRecommendation, ConversationState } from '../../models/message.model';

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
        { id: '1', label: 'Dau dau', value: 'Toi bi dau dau' },
        { id: '2', label: 'Dau bung', value: 'Toi bi dau bung' },
        { id: '3', label: 'Sot', value: 'Toi bi sot' },
        { id: '4', label: 'Ho', value: 'Toi bi ho' }
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

    // Simulate bot response (replace with actual API call)
    this.sendMessageToBot(text);
  }

  onQuickReplySelected(reply: QuickReply): void {
    this.onMessageSent(reply.value);
  }

  onResetChat(): void {
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
    // Simulate API delay
    setTimeout(() => {
      this.conversationState.isTyping = false;

      // Demo response - replace with actual ChatService call
      const botResponse = this.generateDemoResponse(text);
      this.addMessage(botResponse);
    }, 1500);
  }

  private generateDemoResponse(userText: string): Message {
    const lowerText = userText.toLowerCase();

    // Check for red flags
    if (lowerText.includes('kho tho') || lowerText.includes('dau nguc') || lowerText.includes('bat tinh')) {
      return {
        id: this.generateMessageId(),
        text: 'CANH BAO: Cac trieu chung ban mo ta co the can cap cuu ngay lap tuc. Vui long den phong Cap Cuu hoac goi 115 ngay!',
        type: 'alert',
        alertLevel: 'danger',
        timestamp: new Date()
      };
    }

    // Check for symptoms and provide department recommendation
    if (lowerText.includes('dau dau') || lowerText.includes('chong mat')) {
      return {
        id: this.generateMessageId(),
        text: 'Dua tren cac trieu chung cua ban, toi de xuat ban den Khoa Than Kinh.',
        type: 'bot',
        timestamp: new Date(),
        departmentCard: {
          departmentId: 7,
          departmentName: 'Khoa Than Kinh',
          description: 'Chuyen kham va dieu tri cac benh lien quan den he than kinh',
          roomNumber: '401',
          floor: '4',
          waitTime: 'Khoang 15 phut'
        }
      };
    }

    if (lowerText.includes('dau bung') || lowerText.includes('buon non')) {
      return {
        id: this.generateMessageId(),
        text: 'Dua tren cac trieu chung cua ban, toi de xuat ban den Khoa Noi Tieu Hoa.',
        type: 'bot',
        timestamp: new Date(),
        departmentCard: {
          departmentId: 2,
          departmentName: 'Khoa Noi Tieu Hoa',
          description: 'Chuyen kham va dieu tri cac benh ve duong tieu hoa',
          roomNumber: '205',
          floor: '2',
          waitTime: 'Khoang 20 phut'
        }
      };
    }

    if (lowerText.includes('sot') || lowerText.includes('ho') || lowerText.includes('cam')) {
      return {
        id: this.generateMessageId(),
        text: 'Cam on ban da chia se. De giup ban tot hon, ban co the cho toi biet them:',
        type: 'bot',
        timestamp: new Date(),
        quickReplies: [
          { id: '1', label: 'Sot cao tren 39 do', value: 'Toi bi sot cao tren 39 do' },
          { id: '2', label: 'Sot nhe va ho', value: 'Toi bi sot nhe va ho' },
          { id: '3', label: 'Ho co dam', value: 'Toi bi ho co dam' }
        ]
      };
    }

    // Default follow-up
    return {
      id: this.generateMessageId(),
      text: 'Cam on ban da chia se. Ban co the mo ta them ve trieu chung cua minh duoc khong? Vi du: trieu chung bat dau tu khi nao, muc do dau nhu the nao?',
      type: 'bot',
      timestamp: new Date()
    };
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
