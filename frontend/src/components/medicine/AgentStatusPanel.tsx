import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Bot, Search, Brain, DollarSign, CheckCircle, Loader2, AlertCircle } from "lucide-react";

interface AgentStatus {
    agent: string;
    status: "idle" | "working" | "completed" | "error";
    message: string;
    progress: number;
}

interface AgentStatusPanelProps {
    updates: AgentStatus[];
    isProcessing: boolean;
}

const agentIcons: Record<string, React.ReactNode> = {
    "OCR Interpreter": <Search className="w-5 h-5" />,
    "Medicine Identifier": <Brain className="w-5 h-5" />,
    "Price Finder": <DollarSign className="w-5 h-5" />,
};

const agentColors: Record<string, string> = {
    "OCR Interpreter": "from-blue-500 to-cyan-500",
    "Medicine Identifier": "from-purple-500 to-pink-500",
    "Price Finder": "from-green-500 to-emerald-500",
};

const statusIcons: Record<string, React.ReactNode> = {
    idle: <div className="w-2 h-2 rounded-full bg-muted-foreground/50" />,
    working: <Loader2 className="w-4 h-4 text-primary animate-spin" />,
    completed: <CheckCircle className="w-4 h-4 text-green-500" />,
    error: <AlertCircle className="w-4 h-4 text-red-500" />,
};

export function AgentStatusPanel({ updates, isProcessing }: AgentStatusPanelProps) {
    const [agents, setAgents] = useState<Record<string, AgentStatus>>({
        "OCR Interpreter": { agent: "OCR Interpreter", status: "idle", message: "Waiting...", progress: 0 },
        "Medicine Identifier": { agent: "Medicine Identifier", status: "idle", message: "Waiting...", progress: 0 },
        "Price Finder": { agent: "Price Finder", status: "idle", message: "Waiting...", progress: 0 },
    });

    useEffect(() => {
        if (updates && updates.length > 0) {
            const newAgents = { ...agents };
            for (const update of updates) {
                newAgents[update.agent] = update;
            }
            setAgents(newAgents);
        }
    }, [updates]);

    useEffect(() => {
        if (!isProcessing) {
            // Reset when not processing
            setAgents({
                "OCR Interpreter": { agent: "OCR Interpreter", status: "idle", message: "Ready", progress: 0 },
                "Medicine Identifier": { agent: "Medicine Identifier", status: "idle", message: "Ready", progress: 0 },
                "Price Finder": { agent: "Price Finder", status: "idle", message: "Ready", progress: 0 },
            });
        }
    }, [isProcessing]);

    return (
        <Card variant="glass" className="w-full">
            <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                    <Bot className="w-5 h-5 text-primary" />
                    <CardTitle className="text-lg">AI Agent Crew</CardTitle>
                    {isProcessing && (
                        <Badge variant="secondary" className="ml-auto animate-pulse">
                            Processing
                        </Badge>
                    )}
                </div>
                <p className="text-sm text-muted-foreground">
                    Three AI agents working together to analyze your prescription
                </p>
            </CardHeader>
            <CardContent className="space-y-4">
                {Object.values(agents).map((agent) => (
                    <div
                        key={agent.agent}
                        className={`p-4 rounded-xl border transition-all duration-300 ${agent.status === "working"
                                ? "border-primary/50 bg-primary/5 shadow-lg shadow-primary/10"
                                : agent.status === "completed"
                                    ? "border-green-500/30 bg-green-500/5"
                                    : "border-border bg-card/50"
                            }`}
                    >
                        <div className="flex items-center gap-3 mb-2">
                            <div
                                className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agentColors[agent.agent] || "from-gray-500 to-gray-600"
                                    } flex items-center justify-center text-white shadow-lg`}
                            >
                                {agentIcons[agent.agent] || <Bot className="w-5 h-5" />}
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center justify-between">
                                    <h4 className="font-semibold text-sm">{agent.agent}</h4>
                                    {statusIcons[agent.status]}
                                </div>
                                <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                                    {agent.message}
                                </p>
                            </div>
                        </div>
                        {agent.status === "working" && (
                            <Progress value={agent.progress} className="h-1.5 mt-2" />
                        )}
                        {agent.status === "completed" && (
                            <Progress value={100} className="h-1.5 mt-2 [&>div]:bg-green-500" />
                        )}
                    </div>
                ))}

                {/* Agent workflow visualization */}
                <div className="flex items-center justify-center gap-2 pt-2 text-muted-foreground">
                    <span className="text-xs">🔍 OCR</span>
                    <span className="text-xs">→</span>
                    <span className="text-xs">💊 Identify</span>
                    <span className="text-xs">→</span>
                    <span className="text-xs">💰 Compare</span>
                </div>
            </CardContent>
        </Card>
    );
}
