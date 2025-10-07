import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatHeaderProps {
  onNewChat?: () => void;
}

const ChatHeader = ({ onNewChat }: ChatHeaderProps) => {
  return (
    <header className="border-b border-border bg-background/95 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <img 
            src="/icon.png" 
            alt="Incentives AI" 
            className="w-8 h-8 object-contain"
          />
          <h1 className="text-lg font-semibold text-foreground">
            Incentives AI
          </h1>
        </div>
        {onNewChat && (
          <Button
            variant="outline"
            size="sm"
            onClick={onNewChat}
            className="rounded-full"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            New Chat
          </Button>
        )}
      </div>
    </header>
  );
};

export default ChatHeader;
