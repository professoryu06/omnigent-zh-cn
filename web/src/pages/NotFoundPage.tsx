import { Link } from "@/lib/routing";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/i18n";

/**
 * Generic 404 page for unmatched client routes. Reached via React
 * Router's wildcard route inside the AppShell layout, so the sidebar
 * remains visible. The server's SPA fallback (`_SPAStaticFiles`) hands
 * any extensionless URL to the SPA, so a typed-in `/foo` lands here
 * after the bundle boots — not on a server-rendered 404.
 */
export function NotFoundPage() {
  const { t } = useTranslation();
  return (
    <div className="flex flex-1 items-center justify-center px-6">
      <div className="flex max-w-sm flex-col items-center gap-3 text-center">
        <h1 className="font-medium text-foreground text-lg">{t("notFound.heading")}</h1>
        <p className="text-muted-foreground text-sm">
          {t("notFound.description")}
        </p>
        <Button asChild variant="outline">
          <Link to="/">{t("notFound.backToHome")}</Link>
        </Button>
      </div>
    </div>
  );
}
