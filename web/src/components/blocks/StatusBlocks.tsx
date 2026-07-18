// Inline status indicators for non-tool, non-text, non-reasoning blocks.
// Each is small enough to live in one file.
//
// - ErrorBanner: destructive Alert with `[source]` + code + message.
// - RetryIndicator: muted one-liner about an in-flight retry.
// - CompactionMarker: permanent marker shown after compaction completes.
//   The in-progress state renders as a Shimmer in ChatPage, mirroring
//   the "Working…" indicator.

import {
  AlertCircleIcon,
  BrainCircuitIcon,
  ChevronRightIcon,
  RotateCcwIcon,
  ShieldXIcon,
  ShrinkIcon,
} from "lucide-react";
import { useMemo } from "react";
import { CodeBlock, CodeBlockHeader, CodeBlockTitle } from "@/components/ai-elements/code-block";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { shortModelName } from "@/components/CostRoutingControl";
import { cn } from "@/lib/utils";
import { useTranslation } from "@/i18n";
import { TOOL_SURFACE_WIDTH_CLASS } from "./toolSurface";

interface ErrorBannerProps {
  message: string;
  source: string;
  code: string;
}

/**
 * Loud destructive banner for `error` blocks. Falls back to `code` when
 * `message` is empty (matches the reducer's intent — never show a blank
 * panel even when the LLM error payload omits the message).
 */
export function ErrorBanner({ message, source, code }: ErrorBannerProps) {
  const { t } = useTranslation();
  const display = message || code || t("status.unknownError");
  return (
    <Alert
      variant="destructive"
      className="min-w-0 max-w-full overflow-hidden has-[>svg]:grid-cols-[auto_minmax(0,1fr)]"
    >
      <AlertCircleIcon />
      <AlertTitle className="min-w-0 break-words [overflow-wrap:anywhere]">
        {t("status.error")}{source ? ` · ${source}` : ""}
        {code && message ? ` · ${code}` : ""}
      </AlertTitle>
      <AlertDescription className="min-w-0 max-w-full overflow-hidden">
        <span className="block max-w-full whitespace-pre-wrap break-words [overflow-wrap:anywhere] [text-wrap:wrap]">
          {display}
        </span>
      </AlertDescription>
    </Alert>
  );
}

interface PolicyDeniedBannerProps {
  reason: string;
  phase: string;
}

/**
 * Warning banner for policy denials. Uses the `default` alert variant
 * (amber/warning tone) to distinguish from hard errors (destructive red).
 */
export function PolicyDeniedBanner({ reason, phase }: PolicyDeniedBannerProps) {
  const { t } = useTranslation();
  return (
    <Alert>
      <ShieldXIcon />
      <AlertTitle>{t("status.blockedByPolicy")}{phase ? ` · ${phase}` : ""}</AlertTitle>
      <AlertDescription>{reason}</AlertDescription>
    </Alert>
  );
}

interface RetryIndicatorProps {
  source: string;
  attempt: number;
  maxAttempts: number;
  delaySeconds: number;
}

/**
 * Compact line that signals "we hit a transient failure and the server
 * is going to retry." No banner; reads more like a log line.
 */
export function RetryIndicator({
  source,
  attempt,
  maxAttempts,
  delaySeconds,
}: RetryIndicatorProps) {
  const { t } = useTranslation();
  return (
    <div className="flex items-center gap-2 text-muted-foreground text-xs">
      <RotateCcwIcon className="size-3" />
      <span>
        {t("status.retrying", { source, attempt, max: maxAttempts, delay: delaySeconds.toFixed(1) })}
      </span>
    </div>
  );
}

/**
 * Subtle inline marker that the conversation was compacted (older
 * history was summarized to fit context). The in-progress state is
 * rendered as a `Shimmer` in `ChatPage` to match the "Working…"
 * indicator.
 */
export function CompactionMarker() {
  const { t } = useTranslation();
  return (
    <div className="flex items-center gap-2 text-muted-foreground text-xs italic">
      <ShrinkIcon className="size-3" />
      <span>{t("status.compacted")}</span>
    </div>
  );
}

interface RoutingDecisionChipProps {
  model: string;
  applied: boolean;
  rationale: string;
}

/**
 * Muted inline chip announcing the intelligent model router's pick at
 * the start of a turn.
 */
export function RoutingDecisionChip({ model, applied, rationale }: RoutingDecisionChipProps) {
  const { t } = useTranslation();
  const short = shortModelName(model);
  const lead = applied ? short : t("routing.wouldHavePicked", { model: short });
  const summary = t("routing.modelRouterTitle", { details: lead });
  return (
    <div
      className="my-1 flex flex-col items-center gap-0.5 text-muted-foreground text-xs"
      data-testid="routing-decision-chip"
      data-applied={applied ? "true" : "false"}
      title={rationale || summary}
    >
      <span className="flex items-center gap-1.5">
        <BrainCircuitIcon className="size-3 shrink-0" />
        <span>
          {t("routing.modelRouter")}{" · "}
          {applied ? (
            <span className="font-medium text-foreground">{short}</span>
          ) : (
            t("routing.wouldHavePicked", { model: short })
          )}
        </span>
      </span>
      {rationale ? <span className="text-muted-foreground/70">{rationale}</span> : null}
    </div>
  );
}

interface RoutingDecisionCardProps {
  model: string;
  applied: boolean;
  rationale: string;
  /** Sub-agent name when this card is shown in the parent session. */
  agent?: string;
}

/**
 * Collapsible card announcing the intelligent model router's session-level
 * pick. Mirrors the SmartRoutingCard style: same container, model pill,
 * rationale, and expandable raw verdict JSON.
 *
 * Shown in place of the muted chip when auto-routing fires at turn start
 * because the agent spec has no explicit model. When `agent` is provided
 * the card is being shown in the parent (orchestrator) session for a child
 * session's routing decision — the agent name is shown as the row label.
 */
export function RoutingDecisionCard({
  model,
  applied,
  rationale,
  agent,
}: RoutingDecisionCardProps) {
  const { t } = useTranslation();
  const short = shortModelName(model);
  const rowLabel = agent && agent.length > 0 ? agent : t("routing.session");
  const prettyOutput = useMemo(
    () => JSON.stringify({ model, applied, rationale, ...(agent ? { agent } : {}) }, null, 2),
    [model, applied, rationale, agent],
  );
  return (
    <Collapsible
      defaultOpen={false}
      className={cn(
        "group not-prose my-1 flex flex-col gap-1.5 rounded-md border border-border bg-muted/30 px-3 py-2",
        TOOL_SURFACE_WIDTH_CLASS,
      )}
      data-testid="routing-decision-card"
      data-applied={applied ? "true" : "false"}
    >
      <div className="flex items-center gap-1.5 text-xs">
        <BrainCircuitIcon className="size-3.5 shrink-0 text-muted-foreground" />
        <span className="font-medium">{t("routing.intelligentRouting")}</span>
        <span className="text-muted-foreground">{applied ? t("routing.applied") : t("routing.advisory")}</span>
        <CollapsibleTrigger
          className="ml-auto cursor-pointer rounded p-0.5 text-muted-foreground hover:text-foreground"
          aria-label={t("routing.showRawVerdict")}
          data-testid="routing-decision-raw-toggle"
        >
          <ChevronRightIcon className="size-3 transition-transform group-data-[state=open]:rotate-90" />
        </CollapsibleTrigger>
      </div>
      <div className="flex items-center gap-2 text-xs">
        <span className="min-w-0 truncate font-mono text-foreground">{rowLabel}</span>
        <span className="ml-auto shrink-0 inline-flex items-center whitespace-nowrap rounded-full border border-border bg-muted px-1.5 py-0.5 font-mono text-[10px] font-medium leading-none text-foreground">
          {short}
        </span>
      </div>
      {rationale.length > 0 && (
        <p className="text-xs leading-snug text-muted-foreground">{rationale}</p>
      )}
      <CollapsibleContent className="data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:animate-out data-[state=open]:animate-in">
        <CodeBlock code={prettyOutput} language="json">
          <CodeBlockHeader>
            <CodeBlockTitle className="min-w-0">
              <span className="truncate font-medium uppercase tracking-wide">{t("routing.verdict")}</span>
            </CodeBlockTitle>
          </CodeBlockHeader>
        </CodeBlock>
      </CollapsibleContent>
    </Collapsible>
  );
}
