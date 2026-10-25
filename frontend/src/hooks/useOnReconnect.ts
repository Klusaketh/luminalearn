import { useEffect, useRef } from "react";
import { onReachabilityChange } from "@/services/apiClient";

/** Runs `callback` each time the LuminaLearn server becomes reachable again, e.g. to reload data. */
export function useOnReconnect(callback: () => void): void {
  const latest = useRef(callback);
  useEffect(() => {
    latest.current = callback;
  }, [callback]);
  useEffect(
    () =>
      onReachabilityChange((reachable) => {
        if (reachable) latest.current();
      }),
    []
  );
}
