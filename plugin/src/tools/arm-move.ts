import { BridgeClient } from "../bridge-client.js";

export function registerArmMove(api: any, client: BridgeClient) {
  api.registerTool({
    name: "arm_move",
    description:
      "Move the robotic arm. Supports joint-space (J), point-to-point (P), " +
      "linear (L), and arc (C) motion modes. Joint values are in radians, " +
      "Cartesian positions in meters, orientations in radians. " +
      "NERO has 7 joints, Piper has 6.",
    parameters: {
      type: "object",
      required: ["mode", "target"],
      properties: {
        mode: {
          type: "string",
          enum: ["J", "JS", "P", "L", "C"],
          description:
            "Motion mode: J=joint smooth, JS=joint fast (caution), " +
            "P=point-to-point cartesian, L=linear cartesian, C=circular arc",
        },
        target: {
          type: "array",
          items: { type: "number" },
          description:
            "For J/JS: joint angles [j1..jN] in radians. " +
            "For P/L: [x,y,z,roll,pitch,yaw] in meters/radians. " +
            "For C: start pose [x,y,z,r,p,y].",
        },
        mid_point: {
          type: "array",
          items: { type: "number" },
          description: "Mid-point pose for arc motion (mode=C only)",
        },
        end_point: {
          type: "array",
          items: { type: "number" },
          description: "End-point pose for arc motion (mode=C only)",
        },
        speed_percent: {
          type: "integer",
          minimum: 1,
          maximum: 100,
          description: "Speed override (1-100%). Safety layer may cap this.",
        },
        wait: {
          type: "boolean",
          description: "Wait for motion to complete (default true)",
          default: true,
        },
      },
    },
    async execute(params: {
      mode: string;
      target: number[];
      mid_point?: number[];
      end_point?: number[];
      speed_percent?: number;
      wait?: boolean;
    }) {
      try {
        const result = await client.move({
          mode: params.mode,
          target: params.target,
          mid_point: params.mid_point,
          end_point: params.end_point,
          speed_percent: params.speed_percent,
          wait: params.wait ?? true,
        });
        return {
          content: [{ type: "text", text: JSON.stringify(result) }],
        };
      } catch (err: any) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({ error: err.message }),
              advice:
                err.message.includes("Safety")
                  ? "The motion was rejected by the safety layer. Adjust target values."
                  : "Check bridge server and arm connection",
            },
          ],
        };
      }
    },
  });
}
