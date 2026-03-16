/// <reference types="vite/client" />

interface Window {
  Telegram?: {
    WebApp: {
      initData: string;
      initDataUnsafe: {
        query_id?: string;
        user?: {
          id: number;
          first_name: string;
          last_name?: string;
          username?: string;
          language_code?: string;
        };
        auth_date?: string;
        hash?: string;
      };
      version: string;
      platform: string;
      colorScheme: string;
      themeParams: {
        bg_color?: string;
        text_color?: string;
        hint_color?: string;
        link_color?: string;
        button_color?: string;
        button_text_color?: string;
        secondary_bg_color?: string;
      };
      isExpanded: boolean;
      viewportHeight: number;
      viewportStableHeight: number;
      headerColor: string;
      backgroundColor: string;
      BackButton: {
        isVisible: boolean;
        show: () => void;
        hide: () => void;
        onClick: (callback: () => void) => void;
        offClick: (callback: () => void) => void;
      };
      MainButton: {
        text: string;
        color: string;
        textColor: string;
        isVisible: boolean;
        isActive: boolean;
        isProgressVisible: boolean;
        setText: (text: string) => void;
        onClick: (callback: () => void) => void;
        offClick: (callback: () => void) => void;
        show: () => void;
        hide: () => void;
        enable: () => void;
        disable: () => void;
        showProgress: () => void;
        hideProgress: () => void;
        setParams: (params: {
          text?: string;
          color?: string;
          text_color?: string;
          is_active?: boolean;
          is_visible?: boolean;
        }) => void;
      };
      HapticFeedback: {
        impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
        notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
        selectionChanged: () => void;
      };
      expand: () => void;
      close: () => void;
      ready: () => void;
      setHeaderColor: (color: string) => void;
      setBackgroundColor: (color: string) => void;
      showConfirm: (message: string, callback?: (ok: boolean) => void) => void;
      showPopup: (params: {
        title?: string;
        message: string;
        buttons?: Array<{
          id?: string;
          type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
          text?: string;
        }>;
      }, callback?: (buttonId: string) => void) => void;
      showAlert: (message: string, callback?: () => void) => void;
      enableClosingConfirmation: () => void;
      disableClosingConfirmation: () => void;
      onEvent: (eventType: string, callback: () => void) => void;
      offEvent: (eventType: string, callback: () => void) => void;
      sendData: (data: string) => void;
      switchInlineQuery: (query: string, choose_chat_types?: string[]) => void;
      openLink: (url: string, options?: { try_instant_view?: boolean }) => void;
      openTelegramLink: (url: string) => void;
      openInvoice: (url: string, callback?: (status: 'paid' | 'cancelled' | 'failed' | 'pending') => void) => void;
    };
  };
}

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_BOT_TOKEN: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}