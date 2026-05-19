import { useEffect, useState } from "react";

import { getHealth, type HealthResponse } from "@/api/client";

type ApiHealthState = {
  data: HealthResponse | null;
  status: "checking" | "online" | "offline";
};

export function useApiHealth(): ApiHealthState {
  const [state, setState] = useState<ApiHealthState>({
    data: null,
    status: "checking",
  });

  useEffect(() => {
    let isMounted = true;

    getHealth()
      .then((data) => {
        if (isMounted) {
          setState({ data, status: "online" });
        }
      })
      .catch(() => {
        if (isMounted) {
          setState({ data: null, status: "offline" });
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return state;
}

