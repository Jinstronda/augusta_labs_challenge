import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getCompanyDetail, ApiError } from "@/services/api";
import type { CompanyResult } from "@/types/api";
import { ArrowLeft, Building2, Award, ExternalLink, MapPin, Calendar, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";

const CompanyDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [company, setCompany] = useState<CompanyResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchCompany = async () => {
      try {
        setLoading(true);
        const data = await getCompanyDetail(parseInt(id));
        setCompany(data);
      } catch (err) {
        console.error("Error fetching company:", err);
        if (err instanceof ApiError) {
          setError(err.detail || err.message);
        } else {
          setError("Failed to load company details");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchCompany();
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

  if (error || !company) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="p-8 max-w-md text-center">
          <p className="text-destructive mb-4">{error || "Company not found"}</p>
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
          <h1 className="text-lg font-semibold text-foreground">Company Details</h1>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Main Info Card */}
        <Card className="p-6 mb-6">
          <div className="flex items-start gap-4 mb-4">
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
              <Building2 className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-foreground mb-2">{company.company_name}</h2>
              <div className="flex flex-wrap gap-2">
                {company.cae_classification && (
                  <Badge variant="secondary">CAE: {company.cae_classification}</Badge>
                )}
                {company.location_address && (
                  <Badge variant="outline" className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {company.location_address}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {company.activities && (
            <div className="mb-4">
              <h3 className="font-semibold text-foreground mb-2">Activities</h3>
              <p className="text-muted-foreground leading-relaxed">{company.activities}</p>
            </div>
          )}

          {company.website && (
            <div className="mt-4">
              <a
                href={company.website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
              >
                Visit Website <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          )}
        </Card>

        {/* Eligible Incentives */}
        {company.eligible_incentives.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-foreground mb-4">
              Eligible Incentives ({company.eligible_incentives.length})
            </h3>
            <div className="space-y-3">
              {company.eligible_incentives.map((incentive, index) => (
                <Card
                  key={incentive.incentive_id}
                  className="p-4 hover:shadow-md transition-smooth cursor-pointer"
                  onClick={() => navigate(`/incentive/${incentive.incentive_id}`)}
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold text-sm flex-shrink-0">
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-foreground mb-1">{incentive.title}</h4>
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
                      {incentive.company_score !== undefined && (
                        <div className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className="text-muted-foreground">Match Score</span>
                            <span className="font-medium">{(incentive.company_score * 100).toFixed(1)}%</span>
                          </div>
                          <Progress value={incentive.company_score * 100} className="h-2" />
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {company.eligible_incentives.length === 0 && (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground">No eligible incentives found for this company.</p>
          </Card>
        )}
      </div>
    </div>
  );
};

export default CompanyDetail;
