import type { ReportType } from "../types";

const STYLES: Record<ReportType, string> = {
  lost: "border-stamp-red/40 text-stamp-red",
  found: "border-stamp-green/40 text-stamp-green",
};

function ReportTypeTag({ type }: { type: ReportType }) {
  return (
    <span
      className={`inline-flex items-center rounded border px-2 py-0.5 font-stamp text-[11px] uppercase tracking-widest ${STYLES[type]}`}
    >
      {type}
    </span>
  );
}

export default ReportTypeTag;
