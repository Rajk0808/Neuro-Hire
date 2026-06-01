import { create } from 'zustand';

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}

export interface Modal {
  id: string;
  title: string;
  isOpen: boolean;
  component?: React.ReactNode;
}

interface UIStore {
  toasts: Toast[];
  modals: Record<string, Modal>;
  sidebarOpen: boolean;
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  openModal: (id: string, modal: Omit<Modal, 'isOpen'>) => void;
  closeModal: (id: string) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  toasts: [],
  modals: {},
  sidebarOpen: true,
  addToast: (toast) =>
    set((state) => {
      const id = Math.random().toString(36).substr(2, 9);
      const newToast = { ...toast, id };
      if (toast.duration) {
        setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), toast.duration);
      }
      return { toasts: [...state.toasts, newToast] };
    }),
  removeToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((toast) => toast.id !== id) })),
  openModal: (id, modal) =>
    set((state) => ({
      modals: { ...state.modals, [id]: { ...modal, isOpen: true } },
    })),
  closeModal: (id) =>
    set((state) => ({
      modals: { ...state.modals, [id]: { ...state.modals[id], isOpen: false } },
    })),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}));
