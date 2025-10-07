import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getIncentiveDetail, ApiError } from "@/services/api";
import type { IncentiveResult } from "@/types/api";
import { ArrowLeft, Award, Building2, ExternalLink, MapPin, Calendar, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";

const IncentiveDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [incentive, setIncentive] = useState<IncentiveResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchIncentive = async () => {
      try {
        setLoading(true);
        const data = await getIncentiveDetail(id);
        setIncentive(data);
      } catch (err) {
        console.error("Error fetching incentive:", err);
        if (err instanceof ApiError) {
          setError(err.detail || err.message);
        } else {
          setError("Failed to load incentive details");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchIncentive();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b border-border bg-background/95 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-3">
            <Skeleton className="h-9 w-9 rounded-lg" />
            <Skeleton className="h-6 w-48" />
          </div>
        </header>
        <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (error || !incentive) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="p-8 max-w-md text-center">
          <p className="text-destructive mb-4">{error || "Incentive not found"}</p>
          <Button onClick={() => navigate("/")}>Back to Search</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-background/95 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate("/")}
            className="rounded-lg"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-lg font-semibold text-foreground">Incentive Details</h1>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Main Info Card */}
        <Card className="p-6 mb-6">
          <div className="flex items-start gap-4 mb-4">
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
              <Award className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-foreground mb-2">{incentive.title}</h2>
              <div className="flex flex-wrap gap-2">
                {incentive.sector && (
                  <Badge variant="secondary">{incentive.sector}</Badge>
                )}
                {incentive.geo_requirement && (
                  <Badge variant="outline">{incentive.geo_requirement}</Badge>
                )}
              </div>
            </div>
          </div>

          {incentive.ai_description && (
            <div className="mb-4">
              <h3 className="font-semibold text-foreground mb-2">Description</h3>
              <p className="text-muted-foreground leading-relaxed">{incentive.ai_description}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            {incentive.funding_rate && (
              <div className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm">
                  <span className="font-medium">Funding Rate:</span> {incentive.funding_rate}
                </span>
              </div>
            )}
            {incentive.start_date && (
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm">
                  <span className="font-medium">Period:</span> {incentive.start_date}
                  {incentive.end_date && ` - ${incentive.end_date}`}
                </span>
              </div>
            )}
          </div>

          {incentive.eligible_actions && (
            <div className="mt-4">
              <h3 className="font-semibold text-foreground mb-2">Eligible Actions</h3>
              <p className="text-sm text-muted-foreground">{incentive.eligible_actions}</p>
            </div>
          )}

          {incentive.description && (
            <div className="mt-4">
              <h3 className="font-semibold text-foreground mb-2">Full Description</h3>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">{incentive.description}</p>
            </div>
          )}

          {incentive.source_link && (
            <div className="mt-4">
              <a
                href={incentive.source_link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
              >
                View Official Source <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          )}
        </Card>

        {/* Matched Companies */}
        {incentive.matched_companies.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-foreground mb-4">
              Top Matched Companies ({incentive.matched_companies.length})
            </h3>
            <div className="space-y-3">
              {incentive.matched_companies.map((company, index) => (
                <Card
                  key={company.id}
                  className="p-4 hover:shadow-md transition-smooth cursor-pointer"
                  onClick={() => navigate(`/company/${company.id}`)}
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold text-sm flex-shrink-0">
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-foreground mb-1">{company.name}</h4>
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
                      {company.company_score !== undefined && (
                        <div className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className="text-muted-foreground">Match Score</span>
                            <span className="font-medium">{(company.company_score * 100).toFixed(1)}%</span>
                          </div>
                          <Progress value={company.company_score * 100} className="h-2" />
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IncentiveDetail;
