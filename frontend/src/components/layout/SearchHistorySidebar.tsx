import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  History, 
  ChevronRight, 
  TrendingDown, 
  Calendar,
  Pill,
  X
} from "lucide-react";
import type { SearchHistory } from "@/types/pharmalens";

interface SearchHistorySidebarProps {
  isOpen: boolean;
  onClose: () => void;
  history: SearchHistory[];
  onSelectSearch: (search: SearchHistory) => void;
}

export function SearchHistorySidebar({ 
  isOpen, 
  onClose, 
  history, 
  onSelectSearch 
}: SearchHistorySidebarProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-foreground/20 backdrop-blur-sm z-40 animate-fade-in"
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-background border-l border-border shadow-xl z-50 animate-slide-in-right">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center">
                <History className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h2 className="font-display font-semibold">Search History</h2>
                <p className="text-xs text-muted-foreground">{history.length} previous searches</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {history.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 rounded-2xl bg-muted flex items-center justify-center mb-4">
                  <History className="w-8 h-8 text-muted-foreground" />
                </div>
                <h3 className="font-semibold mb-2">No Search History</h3>
                <p className="text-sm text-muted-foreground">
                  Your previous prescription searches will appear here
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {history.map((item) => (
                  <Card 
                    key={item.id}
                    variant="interactive"
                    className="cursor-pointer"
                    onClick={() => onSelectSearch(item)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="primary-light" className="text-xs">
                              <Pill className="w-3 h-3 mr-1" />
                              {item.medicinesCount} medicines
                            </Badge>
                            {item.totalSavings > 0 && (
                              <Badge variant="success-light" className="text-xs">
                                <TrendingDown className="w-3 h-3 mr-1" />
                                ₹{item.totalSavings} saved
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm font-medium truncate">{item.query}</p>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                            <Calendar className="w-3 h-3" />
                            <span>{formatDate(item.createdAt)}</span>
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {history.length > 0 && (
            <div className="p-4 border-t border-border">
              <Button variant="ghost" className="w-full text-destructive hover:text-destructive hover:bg-destructive/10">
                Clear All History
              </Button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function formatDate(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days} days ago`;
  
  return date.toLocaleDateString('en-IN', { 
    day: 'numeric', 
    month: 'short' 
  });
}
