import { cn } from "@/lib/utils";
import { Bot, User, Building2, Award, ExternalLink, MapPin } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { QueryResponse, IncentiveResult, CompanyResult } from "@/types/api";
import { useNavigate } from "react-router-dom";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  isTyping?: boolean;
  data?: QueryResponse;
  error?: boolean;
}

const ChatMessage = ({ message, isUser, isTyping, data, error }: ChatMessageProps) => {
  const navigate = useNavigate();

  const renderIncentiveResults = (results: IncentiveResult[]) => {
    return (
      <div className="space-y-3 mt-3">
        {results.map((incentive) => (
          <Card
            key={incentive.incentive_id}
            className="p-4 hover:shadow-md transition-smooth cursor-pointer border-border"
            onClick={() => navigate(`/incentive/${incentive.incentive_id}`)}
          >
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Award className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-foreground mb-1 line-clamp-2">
                  {incentive.title}
                </h3>
                {incentive.ai_description && (
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                    {incentive.ai_description}
                  </p>
                )}
                <div className="flex flex-wrap gap-2 mb-2">
                  {incentive.sector && (
                    <Badge variant="secondary" className="text-xs">
                      {incentive.sector}
                    </Badge>
                  )}
                  {incentive.funding_rate && (
                    <Badge variant="outline" className="text-xs">
                      {incentive.funding_rate}
                    </Badge>
                  )}
                </div>
                {incentive.matched_companies.length > 0 && (
                  <p className="text-xs text-muted-foreground">
                    {incentive.matched_companies.length} matched companies
                  </p>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  };

  const renderCompanyResults = (results: CompanyResult[]) => {
    return (
      <div className="space-y-3 mt-3">
        {results.map((company) => (
          <Card
            key={company.company_id}
            className="p-4 hover:shadow-md transition-smooth cursor-pointer border-border"
            onClick={() => navigate(`/company/${company.company_id}`)}
          >
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Building2 className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-foreground mb-1">
                  {company.company_name}
                </h3>
                {company.activities && (
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                    {company.activities}
                  </p>
                )}
                <div className="flex flex-wrap gap-2 mb-2">
                  {company.cae_classification && (
                    <Badge variant="secondary" className="text-xs">
                      CAE: {company.cae_classification}
                    </Badge>
                  )}
                  {company.location_address && (
                    <Badge variant="outline" className="text-xs flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {company.location_address.split(',')[0]}
                    </Badge>
                  )}
                </div>
                {company.eligible_incentives.length > 0 && (
                  <p className="text-xs text-muted-foreground">
                    {company.eligible_incentives.length} eligible incentives
                  </p>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  };

  return (
    <div
      className={cn(
        "flex gap-4 mb-6 animate-slide-up",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-primary-foreground" />
        </div>
      )}
      
      <div
        className={cn(
          "rounded-3xl px-4 py-2.5 transition-smooth",
          isUser
            ? "bg-primary text-primary-foreground max-w-[85%]"
            : "bg-muted text-foreground max-w-[90%]",
          error && "bg-destructive/10 text-destructive"
        )}
      >
        {isTyping ? (
          <div className="flex gap-1 items-center h-5">
            <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-pulse-glow" style={{ animationDelay: '0s' }} />
            <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-pulse-glow" style={{ animationDelay: '0.2s' }} />
            <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-pulse-glow" style={{ animationDelay: '0.4s' }} />
          </div>
        ) : (
          <>
            <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{message}</p>
            {data && data.results.length > 0 && (
              <>
                {(data.query_type === "SPECIFIC_INCENTIVE" || data.query_type === "INCENTIVE_GROUP")
                  ? renderIncentiveResults(data.results as IncentiveResult[])
                  : renderCompanyResults(data.results as CompanyResult[])
                }
              </>
            )}
          </>
        )}
      </div>

      {isUser && (
        <div className="w-7 h-7 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-foreground" />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
