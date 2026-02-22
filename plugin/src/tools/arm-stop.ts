import { BridgeClient } from "../bridge-client.js";

export function registerArmStop(api: any, client: BridgeClient) {
  api.registerTool({
    name: "arm_stop",
    description:
      "Stop the robotic arm. Use action='disable' for graceful stop, " +
      "or action='emergency_stop' for immediate halt (requires reset to resume). " +
      "Always prefer the physical E-stop button when available.",
    parameters: {
      type: "object",
      properties: {
        action: {
          type: "string",
          enum: ["disable", "emergency_stop"],
          description: "disable = graceful stop, emergency_stop = immediate halt",
          default: "disable",
        },
      },
    },
    async execute({ action }: { action?: string }) {
      try {
        const result = await client.stop(
          (action as "disable" | "emergency_stop") || "disable"
        );
        return {
          content: [{ type: "text", text: JSON.stringify(result) }],
        };
      } catch (err: any) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({ error: err.message }),
              advice: "If emergency stop fails, use the physical E-stop button immediately",
            },
          ],
        };
      }
    },
  });
}
