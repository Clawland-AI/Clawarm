/**
 * HTTP client for communicating with the ClawArm Python bridge server.
 */

export interface BridgeResult {
  ok: boolean;
  message: string;
  data?: Record<string, unknown>;
}

export interface BridgeStatus {
  connected: boolean;
  enabled: boolean;
  robot_type: string | null;
  dof: number | null;
  joint_angles: number[] | null;
  flange_pose: number[] | null;
  motion_status: number | null;
}

export class BridgeClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8420") {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const opts: RequestInit = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body !== undefined) {
      opts.body = JSON.stringify(body);
    }

    const resp = await fetch(url, opts);
    if (!resp.ok) {
      const text = await resp.text();
      let detail = text;
      try {
        const parsed = JSON.parse(text);
        detail = parsed.detail || text;
      } catch {}
      throw new Error(`Bridge ${method} ${path} failed (${resp.status}): ${detail}`);
    }
    return resp.json() as Promise<T>;
  }

  async connect(
    robot: string = "nero",
    channel: string = "can0",
    iface: string = "socketcan"
  ): Promise<BridgeResult> {
    return this.request("POST", "/connect", { robot, channel, interface: iface });
  }

  async disconnect(): Promise<BridgeResult> {
    return this.request("POST", "/disconnect");
  }

  async getStatus(): Promise<BridgeStatus> {
    return this.request("GET", "/status");
  }

  async move(params: {
    mode: string;
    target: number[];
    mid_point?: number[];
    end_point?: number[];
    speed_percent?: number;
    wait?: boolean;
    timeout?: number;
  }): Promise<BridgeResult> {
    return this.request("POST", "/move", params);
  }

  async enable(): Promise<BridgeResult> {
    return this.request("POST", "/enable");
  }

  async disable(): Promise<BridgeResult> {
    return this.request("POST", "/disable");
  }

  async stop(action: "disable" | "emergency_stop" = "disable"): Promise<BridgeResult> {
    return this.request("POST", "/stop", { action });
  }
}
