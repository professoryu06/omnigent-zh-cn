// Sidebar status indicator. Approval surfaces as a "Needs response" tag so
// it reads at a glance; running/unseen stay as compact dots. Verbose copy
// (incl. the approval count) lives in the tooltip.

import { RunningDot } from "@/components/RunningDot";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { SessionState } from "@/hooks/useSessionState";
import { cn } from "@/lib/utils";
import type { ReactElement } from "react";
import { useTranslation } from "@/i18n";

export interface SessionStateBadgeProps {
  state: SessionState;
}

interface Visual {
  kind: SessionState["kind"];
  ariaLabel: string;
  tooltip: string;
  render: () => ReactElement;
}

function describe(state: SessionState, t: (key: string, values?: Record<string, string | number>) => string): Visual {
  switch (state.kind) {
    case "awaiting": {
      const tooltip =
        state.count === 1 ? t("sessionState.oneApprovalWaiting") : t("sessionState.approvalPromptsWaiting", { count: state.count });
      return {
        kind: state.kind,
        ariaLabel: tooltip,
        tooltip,
        render: () => (
          <Badge className="border-transparent bg-warning/25 text-warning">{t("sessionState.needsResponse")}</Badge>
        ),
      };
    }
    case "running":
      return {
        kind: state.kind,
        ariaLabel: t("sessionState.sessionRunning"),
        tooltip: t("sessionState.sessionRunning"),
        render: () => <RunningDot />,
      };
    case "unseen":
      // Solid brand-pink dot — distinguished from the running indicator,
      // which is a grey spinner.
      return {
        kind: state.kind,
        ariaLabel: t("sessionState.newMessages"),
        tooltip: t("sessionState.newMessages"),
        render: () => <Dot tone="bg-brand-accent" />,
      };
  }
}

function Dot({ tone }: { tone: string }) {
  return <span aria-hidden className={cn("size-2 shrink-0 rounded-full", tone)} />;
}

export function SessionStateBadge({ state }: SessionStateBadgeProps) {
  const { t } = useTranslation();
  const visual = describe(state, t);
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span
          data-testid="session-state-badge"
          data-state={visual.kind}
          role="img"
          aria-label={visual.ariaLabel}
          className="inline-flex h-5 shrink-0 items-center justify-center"
        >
          {visual.render()}
        </span>
      </TooltipTrigger>
      <TooltipContent>{visual.tooltip}</TooltipContent>
    </Tooltip>
  );
}
